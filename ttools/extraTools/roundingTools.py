#!/usr/bin/env python
# coding: utf-8

### Modules
# standard
from __future__ import print_function
from builtins import next
import importlib
from lib.tools.bezierTools import intersectCubicCircle, intersectCircleLine
from collections import namedtuple
from math import cos, sin, radians
from mojo.roboFont import CurrentGlyph, version
from mojo.UI import UpdateCurrentGlyphView

# custom
from . import calcFunctions
importlib.reload(calcFunctions)
from calcFunctions import calcAngle, getLinearRelation

### Constants
Relation = namedtuple('Relation', ['angleDegrees', 'radius', 'bcpLength'])
Point = namedtuple('Point', ['x', 'y'])
BPT = namedtuple('BPT', ['bcpIn', 'anchor', 'bcpOut', 'anchorName'])
Cubic = namedtuple('Cubic', ['pt1', 'bcp1', 'bcp2', 'pt2'])

Segment = namedtuple('Segment', ['bcp1', 'bcp2', 'anchor', 'labels', 'isCurve'])


### Functions & Procedures
def sliceBezier(curve, tt):

    x = (curve.bcp1.x-curve.pt1.x)*tt+curve.pt1.x
    y = (curve.bcp1.y-curve.pt1.y)*tt+curve.pt1.y
    lftBcp1 = Point(x, y)

    x = (curve.bcp2.x-curve.bcp1.x)*tt+curve.bcp1.x
    y = (curve.bcp2.y-curve.bcp1.y)*tt+curve.bcp1.y
    tang = Point(x, y)

    x = (curve.pt2.x-curve.bcp2.x)*tt+curve.bcp2.x
    y = (curve.pt2.y-curve.bcp2.y)*tt+curve.bcp2.y
    rgtBcp2 = Point(x, y)

    x = (tang.x-lftBcp1.x)*tt+lftBcp1.x
    y = (tang.y-lftBcp1.y)*tt+lftBcp1.y
    lftBcp2 = Point(x, y)

    x = (rgtBcp2.x-tang.x)*tt+tang.x
    y = (rgtBcp2.y-tang.y)*tt+tang.y
    rgtBcp1 = Point(x, y)

    x = (rgtBcp1.x-lftBcp2.x)*tt+lftBcp2.x
    y = (rgtBcp1.y-lftBcp2.y)*tt+lftBcp2.y
    midPt = Point(x, y)

    lftCurve = Cubic(pt1=curve.pt1, bcp1=lftBcp1, bcp2=lftBcp2, pt2=midPt)
    rgtCurve = Cubic(pt1=midPt, bcp1=rgtBcp1, bcp2=rgtBcp2, pt2=curve.pt2)

    return lftCurve, rgtCurve


def attachLabelToSelectedPoints(labelName):
    myGlyph = CurrentGlyph()
    for eachContour in myGlyph:
        for eachPt in eachContour.points:
            if eachPt.selected is True:
                eachPt.name = labelName
    if version[0] == '2':
        myGlyph.changed()
    else:
        myGlyph.update()
    UpdateCurrentGlyphView()


def makeGlyphRound(aGlyph, roundingsData, sourceLayerName, targetLayerName, circleLayerName=None):
    """
    roundingsData is a list of dictionaries. Each dictionary has this structure:
        dict(labelName='standard',
             fortyFiveRad=32,
             fortyFiveBcp=16,
             ninetyRad=24,
             ninetyBcp=16,
             hundredThirtyFiveRad=32,
             hundredThirtyFiveBcp=26)
    """

    # will be returned in order to color the glyph if requested
    corrected = False

    # access glyph data
    targetLayer = aGlyph.getLayer(targetLayerName, clear=True)
    sourceLayer = aGlyph.getLayer(sourceLayerName, clear=False)

    # filter data
    roundingsData = [aDict for aDict in roundingsData if aDict['labelName']]

    # extract labels
    possibleLabels = [aDict['labelName'] for aDict in roundingsData]

    if circleLayerName:
        circleLayer = aGlyph.getLayer(circleLayerName, clear=True)

    # iterate over glyph contours
    for eachContour in sourceLayer:

        # collect segments into a custom data type
        segments = {}
        prevAnchor = Point(eachContour[-1].onCurve.x, eachContour[-1].onCurve.y)
        for indexSegment, eachSegment in enumerate(eachContour):
            anchor = Point(eachSegment.onCurve.x, eachSegment.onCurve.y)
            if eachSegment.offCurve:
                bcp1 = Point(eachSegment.offCurve[0].x, eachSegment.offCurve[0].y)
                bcp2 = Point(eachSegment.offCurve[1].x, eachSegment.offCurve[1].y)
                mySegment = Segment(bcp1=bcp1, bcp2=bcp2, anchor=anchor, labels=eachSegment.onCurve.labels, isCurve=True)
            else:
                mySegment = Segment(bcp1=None, bcp2=None, anchor=anchor, labels=eachSegment.onCurve.labels, isCurve=False)
            segments[indexSegment] = mySegment
            prevAnchor = anchor

        # then we calc which have to be inserted
        indexKeys = list(segments.keys())
        indexKeys.sort()
        maxIndex = max(indexKeys)

        for indexSegment in indexKeys:
            prevSegment = segments[indexKeys[indexSegment-1]]
            eachSegment = segments[indexSegment]
            nextSegment = segments[indexKeys[(indexSegment+1) % len(indexKeys)]]

            # if they have to be rounded...
            if set(eachSegment.labels) & set(possibleLabels):
                thisCorner = next((aDict for aDict in roundingsData if aDict["labelName"] in eachSegment.labels))
                if thisCorner is None:
                    print('no data for this label: {}'.format(eachSegment.labels))
                    raise Exception

                # define which radius amount and which bcpLength
                prevAngleRel = calcAngle(eachSegment.anchor, prevSegment.anchor, 'degrees', makePositive=True)
                nextAngleRel = calcAngle(eachSegment.anchor, nextSegment.anchor, 'degrees', makePositive=True)

                overallAngle = abs(prevAngleRel-nextAngleRel)
                if overallAngle > 180:
                    overallAngle = 360 - overallAngle

                # how should the script deal with the corner?
                if overallAngle <= 90:
                    radius = getLinearRelation((45, thisCorner['fortyFiveRad']),
                                               (90, thisCorner['ninetyRad']), overallAngle)
                    bcpLength = getLinearRelation((45, thisCorner['fortyFiveBcp']),
                                                  (90, thisCorner['ninetyBcp']), overallAngle)
                else:
                    radius = getLinearRelation(( 90, thisCorner['ninetyRad']),
                                               (135, thisCorner['hundredThirtyFiveRad']), overallAngle)
                    bcpLength = getLinearRelation(( 90, thisCorner['ninetyBcp']),
                                                  (135, thisCorner['hundredThirtyFiveBcp']), overallAngle)

                # switch flag to true, so the mark color will be changed
                corrected = True

                if eachSegment.isCurve is True:
                    prevCurve = Cubic(prevSegment.anchor, eachSegment.bcp1, eachSegment.bcp2, eachSegment.anchor)
                    prevIntersection = intersectCubicCircle(*prevCurve,
                                                            c=eachSegment.anchor, r=radius)
                    if prevIntersection.status == 'No Intersection':
                        print(prevIntersection.status)
                        print('GlyphName: {}'.format(eachGlyphName))
                        print(prevCurve)
                        print('Circle center: {0}, {1}'.format(eachSegment.anchor.x, eachSegment.anchor.y))
                        print('Radius: {0}'.format(radius))
                        raise Exception

                    prevSlicedCurve = sliceBezier(prevCurve, prevIntersection.t[0])[0]
                    prevAngle = 180 + calcAngle(prevSlicedCurve.pt2, prevSlicedCurve.bcp2, makePositive=True)
                else:
                    prevIntersection = intersectCircleLine(eachSegment.anchor, radius,
                                                           prevSegment.anchor, eachSegment.anchor)
                    prevAngle = calcAngle(eachSegment.anchor, prevSegment.anchor, makePositive=True)

                if nextSegment.isCurve is True:
                    nextCurve = Cubic(eachSegment.anchor, nextSegment.bcp1, nextSegment.bcp2, nextSegment.anchor)
                    nextIntersection = intersectCubicCircle(*nextCurve,
                                                            c=eachSegment.anchor, r=radius)
                    if nextIntersection.status == 'No Intersection':
                        print(prevIntersection.status)
                        print('GlyphName: {}'.format(eachGlyphName))
                        print(nextCurve)
                        print('Circle center: {0}, {1}'.format(eachSegment.anchor.x, eachSegment.anchor.y))
                        print('Radius: {0}'.format(radius))
                        raise Exception

                    nextSlicedCurve = sliceBezier(nextCurve, nextIntersection.t[0])[1]
                    nextAngle = 180 + calcAngle(nextSlicedCurve.pt1, nextSlicedCurve.bcp1, makePositive=True)
                else:
                    nextIntersection = intersectCircleLine(eachSegment.anchor, radius,
                                                           eachSegment.anchor, nextSegment.anchor)
                    nextAngle = calcAngle(eachSegment.anchor, nextSegment.anchor, makePositive=True)

                if eachSegment.isCurve is True:
                    cornerPrevBcp1 =   prevSlicedCurve.bcp1
                    cornerPrevBcp2 =   prevSlicedCurve.bcp2
                    cornerPrevAnchor = prevSlicedCurve.pt2
                    cornerPrev = Segment(bcp1=cornerPrevBcp1, bcp2=cornerPrevBcp2, anchor=cornerPrevAnchor, labels=None, isCurve=True)
                else:
                    cornerPrevAnchor = Point(eachSegment.anchor.x+cos(radians(prevAngle))*radius, eachSegment.anchor.y+sin(radians(prevAngle))*radius)
                    cornerPrev = Segment(bcp1=None, bcp2=None, anchor=cornerPrevAnchor, labels=None, isCurve=False)

                if eachSegment.isCurve is True:
                    cornerNextBcp1 =   Point(prevSlicedCurve.pt2.x+cos(radians(prevAngle))*bcpLength, prevSlicedCurve.pt2.y+sin(radians(prevAngle))*bcpLength)
                else:
                    cornerNextBcp1 =   Point(cornerPrevAnchor.x+cos(radians(prevAngle+180))*bcpLength, cornerPrevAnchor.y+sin(radians(prevAngle+180))*bcpLength)

                if nextSegment.isCurve is True:
                    cornerNextBcp2 =   Point(nextSlicedCurve.pt1.x+cos(radians(nextAngle))*bcpLength, nextSlicedCurve.pt1.y+sin(radians(nextAngle))*bcpLength)
                    cornerNextAnchor = nextSlicedCurve.pt1
                else:
                    cornerNextAnchor = Point(eachSegment.anchor.x+cos(radians(nextAngle))*radius, eachSegment.anchor.y+sin(radians(nextAngle))*radius)
                    cornerNextBcp2   = Point(cornerNextAnchor.x+cos(radians(nextAngle+180))*bcpLength, cornerNextAnchor.y+sin(radians(nextAngle+180))*bcpLength)

                cornerNext = Segment(bcp1=cornerNextBcp1, bcp2=cornerNextBcp2, anchor=cornerNextAnchor, labels=None, isCurve=True)

                if nextSegment.isCurve is True:
                    newNextBcp1 =   nextSlicedCurve.bcp1
                    newNextBcp2 =   nextSlicedCurve.bcp2
                    newNextAnchor = nextSlicedCurve.pt2
                    newNext = Segment(bcp1=newNextBcp1, bcp2=newNextBcp2, anchor=newNextAnchor, labels=nextSegment.labels, isCurve=True)
                else:
                    newNext = Segment(bcp1=None, bcp2=None, anchor=nextSegment.anchor, labels=nextSegment.labels, isCurve=False)

                del segments[indexSegment]
                segments[indexSegment-.25] = cornerPrev
                segments[indexSegment] = cornerNext
                if indexSegment != maxIndex:
                    segments[indexSegment+1] = newNext

                # drawing circles
                if circleLayerName:
                    drawCircle(circleLayer,
                               (eachSegment.anchor.x, eachSegment.anchor.y, radius*2),
                               label=eachSegment.labels)

        references = list(segments.keys())
        references.sort()

        cornerPen = targetLayer.getPen()
        prevAnchor = segments[references[-1]].anchor
        cornerPen.moveTo(prevAnchor)
        for eachReference in references:
            eachSegment = segments[eachReference]
            anchor = eachSegment.anchor.x, eachSegment.anchor.y
            if eachSegment.isCurve is False:
                cornerPen.lineTo(anchor)
            else:
                bcp1 = eachSegment.bcp1.x, eachSegment.bcp1.y
                bcp2 = eachSegment.bcp2.x, eachSegment.bcp2.y
                cornerPen.curveTo(bcp1, bcp2, anchor)
            prevAnchor = anchor
        cornerPen.closePath()

    return corrected
