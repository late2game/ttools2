#!/usr/bin/env python
# -*- coding: utf-8 -*-

from math import radians, cos, sin
from calcFunctions import calcDistance, calcAngle, calcMidPoint

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
