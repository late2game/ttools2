#!/usr/bin/env python
# coding: utf-8

"""A collection of handy functions to calculate things"""
from __future__ import division

from builtins import range
from math import degrees, atan2, sqrt

def intersectionBetweenSegments(pt_a, pt_b, pt_c, pt_d):
    (ax, ay) = pt_a
    (bx, by) = pt_b
    (cx, cy) = pt_c
    (dx, dy) = pt_d
    upx = (ax * by - ay * bx) * (cx - dx) - (ax - bx) * ((cx*dy) - (cy*dx))
    dwx = (ax - bx) * (cy - dy) - (ay - by) * (cx - dx)
    upy = (ax * by - ay * bx) * (cy - dy) - (ay-by) * (cx*dy-cy*dx)
    dwy = (ax-bx) * (cy-dy) - (ay-by) * (cx-dx)
    if dwx == 0 or dwy == 0:
        return None
    ix = upx / dwx
    iy = upy / dwy
    return ix, iy

def calcAngle(pt1, pt2):
    ang = degrees(atan2((pt2[1] - pt1[1]), (pt2[0] - pt1[0])))
    return ang

def calcDistance(pt1, pt2):
    return sqrt((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2)

def calcDistanceBetweenPTs(pt1, pt2):
    return sqrt((pt1.x - pt2.x)**2 + (pt1.y - pt2.y)**2)

def calcMidPoint(pt1, pt2):
    return (pt1[0]+pt2[0])/2, (pt1[1]+pt2[1])/2

def interpolateValue(poleOne, poleTwo, factor):
    desiredValue = poleOne + factor*(poleTwo-poleOne)
    return desiredValue

def isBlackInBetween(glyph, pt1, pt2):
    distance = int(round(calcDistanceBetweenPTs(pt1, pt2), 0))
    for index in range(distance):
        eachX = interpolateValue(pt1.x, pt2.x, index/float(distance))
        eachY = interpolateValue(pt1.y, pt2.y, index/float(distance))
        if glyph.pointInside((eachX, eachY)) is False:
            return False
        else:
            pass
    return True

def calcStemsData(glyph, pluginKey):
    stemsData = []
    for ID1, ID2 in glyph.lib[pluginKey]:
        ptsToDisplay = []
        for eachContour in glyph:
            for eachSegment in eachContour:
                currentID = eachSegment.onCurve.naked().uniqueID
                if currentID == ID1 or currentID == ID2:
                    ptsToDisplay.append(eachSegment.onCurve)
        assert len(ptsToDisplay) == 2, 'the points to display are not 2: %s' % ptsToDisplay

        pt1, pt2 = ptsToDisplay
        middlePoint = (pt2.x+pt1.x)/2, (pt2.y+pt1.y)/2
        horDiff = abs(pt1.x - pt2.x)
        verDiff = abs(pt1.y - pt2.y)
        stemsData.append(((pt1, pt2), (horDiff, verDiff), middlePoint))
    return stemsData

def calcDiagonalsData(glyph, pluginKey):
    diagonalsData = []
    for ID1, ID2 in glyph.lib[pluginKey]:
        ptsToDisplay = []
        for eachContour in glyph:
            for eachSegment in eachContour:
                currentID = eachSegment.onCurve.naked().uniqueID
                if currentID == ID1 or currentID == ID2:
                    ptsToDisplay.append((eachSegment.onCurve.x, eachSegment.onCurve.y))
        assert len(ptsToDisplay) == 2
        pt1, pt2 = ptsToDisplay
        angle = calcAngle(pt1, pt2)
        distance = calcDistance(pt1, pt2)
        diagonalsData.append((ptsToDisplay, angle, distance))
    return diagonalsData
