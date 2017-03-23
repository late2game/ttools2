#!/usr/bin/env python
# -*- coding: utf-8 -*-


# WIP
def connectPointsWithWavyLine(glyph, centerX, centerY, angle, length, thickness, howManyWaves, waveHeight, squaring):
    waveLength = length/howManyWaves
    bcpLength = waveLength/2.*squaring

    wavePoints = []
    for eachX in range(howManyWaves*2+1):
        if eachX % 2 == 0: #high point
            eachY = centerY+waveHeight/2.
        else:              #low point
            eachY = centerY-waveHeight/2.

        bothX = eachX*waveLength/2.
        wavePoints.append(topPoint)

    return wavePoints