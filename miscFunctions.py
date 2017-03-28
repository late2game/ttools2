#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""handy functions for dealing with a bit of anything"""

import calcFunctions
reload(calcFunctions)
from calcFunctions import isBlackInBetween, calcDistanceBetweenPTs

def getOpenedFontFromPath(openedFonts, pth):
    for eachFont in openedFonts:
        if eachFont.path == pth:
            return eachFont
    return None

def collectIDsFromSelectedPoints(glyph):
    selectedIDs = []
    for eachContour in glyph:
        for eachSegment in eachContour:
            if eachSegment.onCurve.selected is True:
                selectedIDs.append(eachSegment.onCurve.naked().uniqueID)
    selectedIDs.sort()
    return selectedIDs

def getPointFromID(glyph, ID):
    for eachContour in glyph:
        for eachPt in eachContour:
            if eachPt.onCurve.naked().uniqueID == ID:
                return eachPt.onCurve
    return None

def guessStemPoints(glyph):
    guessedStems = []
    selectedIDs = collectIDsFromSelectedPoints(glyph)
    remainingIDs = list(selectedIDs)
    for eachSelectedID in selectedIDs:
        if len(remainingIDs) == 1:
            return guessedStems

        if eachSelectedID in remainingIDs:
            eachSelectedPT = getPointFromID(glyph, eachSelectedID)
            remainingIDs.remove(eachSelectedID)

            possibleCombinations = []
            for eachRemainingID in remainingIDs:
                eachRemainingPT = getPointFromID(glyph, eachRemainingID)
                if isBlackInBetween(glyph, eachSelectedPT, eachRemainingPT) is True:
                    distance = calcDistanceBetweenPTs(eachSelectedPT, eachRemainingPT)
                    possibleCombinations.append((distance, eachRemainingID))

            possibleCombinations = sorted(possibleCombinations, key=lambda item:item[0])
            nearestID = possibleCombinations[0][1]
            remainingIDs.remove(nearestID)

            stem = [eachSelectedID, nearestID]
            stem.sort()
            guessedStems.append(tuple(stem))

    return guessedStems
