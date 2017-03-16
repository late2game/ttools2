#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A collection of handy functions to calculate things"""

from math import degrees, atan2, sqrt

def intersectionBetweenSegments((ax, ay), (bx, by), (cx, cy), (dx, dy)):
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


def interpolateValue(poleOne, poleTwo, factor):
    desiredValue = poleOne + factor*(poleTwo-poleOne)
    return desiredValue


def isBlackInBetween(glyph, pt1, pt2):
    distance = int(round(calcDistance(pt1, pt2), 0))
    for index in xrange(distance):
        eachX = interpolateValue(pt1.x, pt2.x, index/float(distance))
        eachY = interpolateValue(pt1.y, pt2.y, index/float(distance))
        if glyph.pointInside((eachX, eachY)) is False:
            return False
        else:
            pass
    return True
