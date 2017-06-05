#!/usr/bin/env python
# -*- coding: utf-8 -*-

import types
from mojo.roboFont import RGlyph
from extraTools import findPossibleOverlappingSegmentsPen
from fontTools.misc.arrayTools import offsetRect, sectRect
from lib.tools.bezierTools import intersectCubicCubic, intersectCubicLine, intersectLineLine


def checkPairFormat(value):
    assert isinstance(value, types.TupleType), 'wrong pair format'
    assert len(value) == 2, 'wrong pair format'
    assert isinstance(value[0], types.UnicodeType), 'wrong pair format'
    assert isinstance(value[1], types.UnicodeType), 'wrong pair format'

def whichGroup(targetGlyphName, aLocation, aFont):
    assert aLocation in ['lft', 'rgt']
    possibleLocations = {'lft': '@MMK_L__',
                         'rgt': '@MMK_R__'}
    filteredGroups = {name: content for name, content in aFont.groups.items() if name.startswith(possibleLocations[aLocation])}
    for eachGroupName, eachGroupContent in filteredGroups.items():
        for eachGlyphName in eachGroupContent:
            if eachGlyphName == targetGlyphName:
                return eachGroupName
    return None

def getCorrection(aPair, aFont, getKey=False, checkWithFlatKerning=False):
    key = None
    correction = 0

    # pair to pair
    if aPair in aFont.kerning:
        correction = aFont.kerning.get(aPair)
        key = aPair

    # looking for class kernin
    else:
        lftGlyphName, rgtGlyphName = aPair

        # looking for groups
        lftGroup = whichGroup(lftGlyphName, 'lft', aFont)
        rgtGroup = whichGroup(rgtGlyphName, 'rgt', aFont)

        # group to group
        if lftGroup and rgtGroup and (lftGroup, rgtGroup) in aFont.kerning:
            correction = aFont.kerning.get((lftGroup, rgtGroup))
            key = (lftGroup, rgtGroup)

        # group to pair
        if lftGroup and (lftGroup, rgtGlyphName) in aFont.kerning:
            correction = aFont.kerning.get((lftGroup, rgtGlyphName))
            key = (lftGroup, rgtGlyphName)

        # pair to group
        if rgtGroup and (lftGroup, rgtGlyphName) in aFont.kerning:
            correction = aFont.kerning.get((lftGlyphName, rgtGroup))
            key = (lftGlyphName, rgtGroup)

    if checkWithFlatKerning is True:
        if aPair in aFont.naked().flatKerning:
            reference = aFont.naked().flatKerning[aPair]
        else:
            reference = 0

        if reference != correction:
            print u'We have a problem with %s, %s from %s font' % (lftGlyphName, rgtGlyphName, aFont)
            print u'flat: %s, correction: %s' % (reference, correction)
            print u'flat kerning is different ¯\_(ツ)_/¯'
            raise StandardError

    if getKey is True:
        return correction, key
    else:
        return correction


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
    pen1 = findPossibleOverlappingSegmentsPen.FindPossibleOverlappingSegmentsPen(g1.getParent(), bounds2)
    g1.draw(pen1)

    # create a pen for g2 with a shifted rect and move each found segment with the width and kerning
    pen2 = findPossibleOverlappingSegmentsPen.FindPossibleOverlappingSegmentsPen(g2.getParent(), bounds1, (g1.width+kern, 0))
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
