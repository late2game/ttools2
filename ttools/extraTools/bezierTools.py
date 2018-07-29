#!/usr/bin/env python
# coding: utf-8

"""handy function for bezier management"""
from .calcFunctions import calcDistance
from fontTools.misc.bezierTools import calcCubicParameters

def calcPointOnBezier(a, b, c, d, tValue):
    ax, ay = a
    bx, by = b
    cx, cy = c
    dx, dy = d
    return ax*tValue**3 + bx*tValue**2 + cx*tValue + dx, ay*tValue**3 + by*tValue**2 + cy*tValue + dy


def collectsPointsOnBezierCurve(pt1, pt2, pt3, pt4, tStep):
    """Adapted from calcCubicBounds in fontTools
       by Just van Rossum https://github.com/behdad/fonttools"""
    a, b, c, d = calcCubicParameters(pt1, pt2, pt3, pt4)
    steps = [t/float(tStep) for t in xrange(tStep)]

    pointsWithT = [(pt1, 0)]
    for eachT in steps:
        pt = calcPointOnBezier(a, b, c, d, eachT)
        pointsWithT.append((pt, eachT))
    pointsWithT.append((pt4, 1))
    return pointsWithT


def collectsPointsOnBezierCurveWithFixedDistance(pt1, pt2, pt3, pt4, distance):
    tStep = 1000
    rawPoints = collectsPointsOnBezierCurve(pt1, pt2, pt3, pt4, tStep)

    index = 0
    cleanPoints = []
    while index < len(rawPoints):
        eachPt, tStep = rawPoints[index]
        cleanPoints.append((eachPt, tStep))

        for progress in xrange(1, len(rawPoints) - index):
            if calcDistance(eachPt, rawPoints[index+progress][0]) >= distance:
                index = index + progress
                break
        else:
            break
    return cleanPoints