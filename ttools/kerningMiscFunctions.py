#!/usr/bin/env python
# -*- coding: utf-8 -*-

import types
from mojo.roboFont import RGlyph

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
            print u'flat: %s, correction: %s' % (reference, correction)
            print u'flat kerning is different ¯\_(ツ)_/¯'
            raise StandardError

    if getKey is True:
        return correction, key
    else:
        return correction

