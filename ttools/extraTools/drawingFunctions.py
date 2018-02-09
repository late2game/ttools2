#!/usr/bin/env python
# coding: utf-8

from math import radians, cos, sin
from calcFunctions import calcDistance, calcAngle, calcMidPoint
from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])

def calcWavyLine(pt1, pt2, waveLength, waveHeight, pseudoSquaring=.57):
    diagonal = calcDistance(pt1, pt2)
    angleRad = radians(calcAngle(pt1, pt2))

    howManyWaves = int(diagonal/float(waveLength))
    waveLengthAdj = diagonal/float(howManyWaves/2.)
    bcpLength = waveLength/2.*pseudoSquaring

    wavePoints = [pt1]
    prevAnchor = pt1
    for waveIndex in range(1, howManyWaves+1):

        if waveIndex != 1:
            prevAnchor = wavePoints[-1][-1]

        flexPoint = prevAnchor[0]+cos(angleRad)*waveLengthAdj, prevAnchor[1]+sin(angleRad)*waveLengthAdj

        if waveIndex % 2 == 0:
            projAngleRad = radians(90)
        else:
            projAngleRad = radians(-90)

        waveMidPoint = calcMidPoint(prevAnchor, flexPoint)
        waveMidPointProj = waveMidPoint[0]+cos(angleRad+projAngleRad)*waveHeight/2., waveMidPoint[1]+sin(angleRad+projAngleRad)*waveHeight/2.

        bcpOut = prevAnchor[0]+cos(angleRad)*bcpLength, prevAnchor[1]+sin(angleRad)*bcpLength
        bcpIn = waveMidPointProj[0]+cos(radians(180)+angleRad)*bcpLength, waveMidPointProj[1]+sin(radians(180)+angleRad)*bcpLength
        wavePoints.append((bcpOut, bcpIn, waveMidPointProj))

    # bcps for the final point
    prevAnchor = wavePoints[-1][-1]
    bcpOut = prevAnchor[0]+cos(angleRad)*bcpLength, prevAnchor[1]+sin(angleRad)*bcpLength
    bcpIn = pt2[0]+cos(radians(180)+angleRad)*bcpLength, pt2[1]+sin(radians(180)+angleRad)*bcpLength
    wavePoints.append((bcpOut, bcpIn, pt2))

    return wavePoints


def drawCircle(aGlyph, posSize, squaring=.58, label=None):
    centerX, centerY, diameter = posSize
    bcpLength = diameter/2*squaring

    pt1 =     Point(centerX, centerY-diameter/2)
    pt1_in  = Point(pt1.x-bcpLength, pt1.y)
    pt1_out = Point(pt1.x+bcpLength, pt1.y)

    pt2 =     Point(centerX+diameter/2, centerY)
    pt2_in  = Point(pt2.x, pt2.y-bcpLength)
    pt2_out = Point(pt2.x, pt2.y+bcpLength)

    pt3 =     Point(centerX, centerY+diameter/2)
    pt3_in  = Point(pt3.x+bcpLength, pt3.y)
    pt3_out = Point(pt3.x-bcpLength, pt3.y)

    pt4 =     Point(centerX-diameter/2, centerY)
    pt4_in  = Point(pt4.x, pt4.y+bcpLength)
    pt4_out = Point(pt4.x, pt4.y-bcpLength)

    pen = aGlyph.getPen()
    pen.moveTo(pt1)
    pen.curveTo(pt1_out, pt2_in, pt2)
    pen.curveTo(pt2_out, pt3_in, pt3)
    pen.curveTo(pt3_out, pt4_in, pt4)
    pen.curveTo(pt4_out, pt1_in, pt1)
    pen.closePath()

    if label:
        for eachPt in aGlyph[-1].points:
            if eachPt.type != 'offCurve':
                eachPt.name = label

