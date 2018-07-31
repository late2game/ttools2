#!/usr/bin/env python
# coding: utf-8

"""handy functions for dealing with a bit of anything"""
### Modules
# standard
from __future__ import absolute_import
import importlib
import os
import sys
import codecs
from collections import OrderedDict
from mojo.roboFont import CurrentFont, OpenFont, version
from vanilla.dialogs import getFile

# custom
from . import calcFunctions
importlib.reload(calcFunctions)
from .calcFunctions import isBlackInBetween, calcDistanceBetweenPTs

### Constants
SMART_SETS_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'resources', 'smartSets')

### Functions
def catchFilesAndFolders(path, extension):
    """Return all the files in a path with a specific extension"""
    items = [os.path.join(path, item) for item in os.listdir(path) if item.endswith(extension)]
    return items

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
                selectedIDs.append(eachSegment.onCurve.getIdentifier())
    selectedIDs.sort()
    return selectedIDs

def getPointFromID(glyph, ID):
    for eachContour in glyph:
        for eachPt in eachContour:
            if eachPt.onCurve.getIdentifier() == ID:
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

def loadGlyphNamesTable(aPath):
    names = []
    with codecs.open(aPath, 'r', 'utf-8') as tableFile:
        for row in tableFile:
            names.append([cell.strip() for cell in row.strip().split('\t') if cell != ''])
    return names

def sortFontAccordingToSmartSets(aFont):
    smartSetsPaths = catchFilesAndFolders(SMART_SETS_FOLDER, '.txt')
    smartSetsPaths.sort()
    smartSetsGlyphOrder = []
    for eachPath in smartSetsPaths:
        smartSetsGlyphOrder.extend([name.strip() for name in codecs.open(eachPath, 'r', 'utf-8').readlines()])
    commonGlyphs = set(aFont.glyphOrder) & set(smartSetsGlyphOrder)
    extraStandardGlyphNames = set(aFont.glyphOrder) - set(smartSetsGlyphOrder)
    newGlyphOrder = [gl for gl in smartSetsGlyphOrder if gl in commonGlyphs]
    newGlyphOrder.extend(gl for gl in aFont.glyphOrder if gl in extraStandardGlyphNames)
    aFont.glyphOrder = newGlyphOrder
    return extraStandardGlyphNames

def importFontInfoFromUFOtoCurrentFont():
    aFontPath = getFile(messageText='Please, choose a UFO file', fileTypes=['ufo'])[0]
    if aFontPath.endswith('.ufo'):
        if version[0] == '2':
            sourceFont = OpenFont(aFontPath, showInterface=False)
        else:
            sourceFont = OpenFont(aFontPath, showUI=False)
        sourceFontInfos = sourceFont.info.asDict()
        for eachAttribute, eachValue in sourceFontInfos.items():
            setattr(CurrentFont().info, eachAttribute, eachValue)
