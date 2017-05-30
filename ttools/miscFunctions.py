#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""handy functions for dealing with a bit of anything"""

### Modules
# custom
import calcFunctions
reload(calcFunctions)
from calcFunctions import isBlackInBetween, calcDistanceBetweenPTs

# standard
import os
import sys
import codecs
import types
from collections import OrderedDict

### Functions
def catchFilesAndFolders(path, extension):
    """Return all the files in a path with a specific extension"""
    items = [os.path.join(path, item) for item in os.listdir(path) if item.endswith(extension)]
    return items

def buildPairsFromString(uniString):
    assert isinstance(uniString, types.UnicodeType) is True

    pairs = []
    for eachI in range(1, len(uniString)):
        myPair = (u'%s' % uniString[eachI-1], u'%s' % uniString[eachI])
        pairs.append(myPair)
    return pairs

def loadKerningTexts(kerningTextFolder):
    kerningWordDB = OrderedDict()
    kerningTextBaseNames = [pth for pth in os.listdir(kerningTextFolder) if pth.endswith('.txt')]
    kerningTextBaseNames.sort()
    for eachKerningTextBaseName in kerningTextBaseNames:
        kerningWords = [u'%s' % word.strip() for word in codecs.open(os.path.join(kerningTextFolder, eachKerningTextBaseName), 'r', 'utf-8').readlines()]
        uniqueKerningWords = []
        _ = [uniqueKerningWords.append(word) for word in kerningWords if word not in uniqueKerningWords]
        kerningWordDB[eachKerningTextBaseName[3:]] = [{'word': word, 'done?': 0} for word in uniqueKerningWords]
    return kerningWordDB

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

def selectAnchorByName(glyphObj, name):
    for eachAnchor in glyphObj.anchors:
        if eachAnchor.name == name:
            return eachAnchor
    return None
