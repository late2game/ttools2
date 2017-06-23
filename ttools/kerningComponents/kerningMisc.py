#!/usr/bin/env python
# -*- coding: utf-8 -*-

# custom modules
# from ..userInterfaceValues import vanillaControlsSize
# from ..extraTools import findPossibleOverlappingSegmentsPen


# standard modules
import os
import types
import codecs
from defconAppKit.tools.textSplitter import splitText
from ..extraTools.findPossibleOverlappingSegmentsPen import FindPossibleOverlappingSegmentsPen
from mojo.roboFont import RGlyph
from fontTools.misc.arrayTools import offsetRect, sectRect
from lib.tools.bezierTools import intersectCubicCubic, intersectCubicLine, intersectLineLine
from vanilla import Window, RadioGroup, Button
from collections import OrderedDict

# constants
MARGIN_VER = 8
MARGIN_HOR = 8
MARGIN_COL = 4

MAJOR_STEP = 20
MINOR_STEP = 4

CANVAS_SCALING_FACTOR_INIT = 1.6

# functions
def checkPairFormat(value):
    assert isinstance(value, types.TupleType), 'wrong pair format'
    assert len(value) == 2, 'wrong pair format'
    assert isinstance(value[0], types.UnicodeType), 'wrong pair format'
    assert isinstance(value[1], types.UnicodeType), 'wrong pair format'

def buildPairsFromString(uniString, aFont):
    pairs = []
    splittedText = splitText(uniString, aFont.naked().unicodeData)
    for eachI in range(1, len(splittedText)):
        myPair = (u'%s' % splittedText[eachI-1], u'%s' % splittedText[eachI])
        pairs.append(myPair)
    return pairs

def loadKerningTexts(kerningTextFolder):
    kerningWordDB = OrderedDict()
    kerningTextBaseNames = [pth for pth in os.listdir(kerningTextFolder) if pth.endswith('.txt')]
    kerningTextBaseNames.sort()
    for eachKerningTextBaseName in kerningTextBaseNames:
        kerningWordsDoc = codecs.open(os.path.join(kerningTextFolder, eachKerningTextBaseName), 'r', 'utf-8').readlines()

        kerningWords = []
        for rawWord in kerningWordsDoc:
            if '#' in rawWord:
                word = u'%s' % rawWord[:rawWord.index('#')].strip()
            else:
                word = u'%s' % rawWord.strip()

            if word:
                kerningWords.append(word)

        uniqueKerningWords = []
        _ = [uniqueKerningWords.append(word) for word in kerningWords if word not in uniqueKerningWords]
        kerningWordDB[eachKerningTextBaseName[3:]] = [{'word': word, 'done?': 0} for word in uniqueKerningWords]
    return kerningWordDB

def whichGroup(targetGlyphName, aLocation, aFont):
    assert aLocation in ['lft', 'rgt']

    locationPrefixes = {'lft': '@MMK_L_',
                        'rgt': '@MMK_R_'}

    filteredGroups = {name: content for name, content in aFont.groups.items() if name.startswith(locationPrefixes[aLocation])}
    for eachGroupName, eachGroupContent in filteredGroups.items():
        if targetGlyphName in eachGroupContent:
            return eachGroupName
    return None

def whichKindOfPair(aPair):
    lftReference, rgtReference = aPair

    if lftReference.startswith('@MMK_L_') and rgtReference.startswith('@MMK_R_'):
        return 'gr2gr'
    elif lftReference.startswith('@MMK_L_'):
        return 'gr2gl'
    elif rgtReference.startswith('@MMK_R_'):
        return 'gl2gr'
    else:
        return 'gl2gl'

def collectPairMapping(aPair, aFont):
    """here I assume aPair is made of two glyphnames, no classes"""
    lftGlyphName, rgtGlyphName = aPair
    lftGroup = whichGroup(lftGlyphName, 'lft', aFont)
    rgtGroup = whichGroup(rgtGlyphName, 'rgt', aFont)

    pairsDB = [{'kind': 'gl2gl', 'key': (lftGlyphName, rgtGlyphName), 'amount': aFont.kerning.get((lftGlyphName, rgtGlyphName))},
               {'kind': 'gl2gr', 'key': (lftGlyphName, rgtGroup)    , 'amount': aFont.kerning.get((lftGlyphName, rgtGroup))},
               {'kind': 'gr2gl', 'key': (lftGroup,     rgtGlyphName), 'amount': aFont.kerning.get((lftGroup,     rgtGlyphName))},
               {'kind': 'gr2gr', 'key': (lftGroup,     rgtGroup)    , 'amount': aFont.kerning.get((lftGroup,     rgtGroup))}]
    pairsDB = [pair for pair in pairsDB if pair['amount'] is not None]
    return pairsDB

def setRawCorrection(kerningReference, aFont, amount):
    """sometimes, we don't need any intelligence applied, this in mainly used to set exception"""
    aFont.kerning[kerningReference] = amount

def setCorrection(aPair, aFont, correctionAmount):
    lftGlyphName, rgtGlyphName = aPair

    # if pair already in kerning dict, we have to find the right one
    pairMapping = collectPairMapping(aPair, aFont)
    if pairMapping:
        chosenPair = pairMapping[0]['key']

    # if not, we should prefer class kerning, single pairs are last choice
    else:
        lftGroup = whichGroup(lftGlyphName, 'lft', aFont)
        rgtGroup = whichGroup(rgtGlyphName, 'rgt', aFont)

        if lftGroup:
            lftReference = lftGroup
        else:
            lftReference = lftGlyphName

        if rgtGroup:
            rgtReference = rgtGroup
        else:
            rgtReference = rgtGlyphName
        chosenPair = lftReference, rgtReference

    if chosenPair in aFont.kerning and correctionAmount == 0:
        aFont.kerning.remove(chosenPair)
    elif chosenPair not in aFont.kerning and correctionAmount == 0:
        pass
    else:
        aFont.kerning[chosenPair] = correctionAmount

def getCorrection(aPair, aFont):
    """here I should receive only glyphNames"""

    pairsDB = collectPairMapping(aPair, aFont)
    if pairsDB:
        chosenPair = pairsDB[0]
        return chosenPair['amount'], chosenPair['key'], whichKindOfPair(chosenPair['key'])
    else:
        return 0, None, None

def checkIfPairOverlaps(g1, g2):
    assert g1.getParent() is g2.getParent(), 'the two glyphs do not belong to the same font'

    """Checking method from Touche!
    Returns a Boolean if overlapping.
    """

    kern = g1.getParent().naked().flatKerning.get((g1.name, g2.name), 0)

    # Check sidebearings first (PvB's idea)
    if g1.rightMargin + g2.leftMargin + kern > 0:
        return False

    # get the bounds and check them
    bounds1 = g1.box
    if bounds1 is None:
        return False
    bounds2 = g2.box
    if bounds2 is None:
        return False

    # shift bounds2
    bounds2 = offsetRect(bounds2, g1.width+kern, 0)
    # check for intersection bounds
    intersectingBounds, _ = sectRect(bounds1, bounds2)
    if not intersectingBounds:
        return False
    # move bounds1 back, moving bounds is faster then moving all coordinates in a glyph
    bounds1 = offsetRect(bounds1, -g2.width-kern, 0)

    # create a pen for g1 with a shifted rect, draw the glyph into the pen
    pen1 = FindPossibleOverlappingSegmentsPen(g1.getParent(), bounds2)
    g1.draw(pen1)

    # create a pen for g2 with a shifted rect and move each found segment with the width and kerning
    pen2 = FindPossibleOverlappingSegmentsPen(g2.getParent(), bounds1, (g1.width+kern, 0))
    # draw the glyph into the pen
    g2.draw(pen2)

    for segment1 in pen1.segments:
        for segment2 in pen2.segments:
            if len(segment1) == 4 and len(segment2) == 4:
                a1, a2, a3, a4 = segment1
                b1, b2, b3, b4 = segment2
                result = intersectCubicCubic(a1, a2, a3, a4, b1, b2, b3, b4)
            elif len(segment1) == 4:
                p1, p2, p3, p4 = segment1
                a1, a2 = segment2
                result = intersectCubicLine(p1, p2, p3, p4, a1, a2)
            elif len(segment2) == 4:
                p1, p2, p3, p4 = segment2
                a1, a2 = segment1
                result = intersectCubicLine(p1, p2, p3, p4, a1, a2)
            else:
                a1, a2 = segment1
                b1, b2 = segment2
                result = intersectLineLine(a1, a2, b1, b2)
            if result.status == "Intersection":
                return True

    return False
