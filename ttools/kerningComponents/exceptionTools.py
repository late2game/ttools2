#!/usr/bin/env python
# coding: utf-8

### Modules
# standard
from __future__ import division
from builtins import range
from defconAppKit.tools.textSplitter import splitText
from math import cos, sin, atan2, sqrt, radians
from collections import namedtuple

### Constants
Point = namedtuple('Point', ['x', 'y'])

### Classes and functions
def checkGlyphPresenceInMultipleGroups(glyphName, location, aFont):

    locationPrefixes = {
            'left': '@MMK_L_',
            'right': '@MMK_R_'}

    whichAreTheGroups = []
    for eachGroupName, eachGroupContent in aFont.groups.items():
        if locationPrefixes[location] in eachGroupName:
            if glyphName in eachGroupContent:
                whichAreTheGroups.append(eachGroupName)

    if len(whichAreTheGroups) == 1:
        return True, None
    else:
        return False, '{} in the following groups: {}'.format(glyphName, ' '.join(whichAreTheGroups))

def checkGroupConflicts(aFont):
    glyphsInvolvedInLft = []
    glyphsInvolvedInRgt = []
    for eachGroupName, eachGroupContent in aFont.groups.items():
        if '@MMK_L' in eachGroupName:
            _ = [glyphsInvolvedInLft.append(glyphName) for glyphName in eachGroupContent if glyphName not in glyphsInvolvedInLft]
        elif '@MMK_R' in eachGroupName:
            _ = [glyphsInvolvedInRgt.append(glyphName) for glyphName in eachGroupContent if glyphName not in glyphsInvolvedInRgt]

    report = []
    for eachGlyphName in glyphsInvolvedInLft:
        status, error = checkGlyphPresenceInMultipleGroups(eachGlyphName, 'left', aFont)
        if status is False:
            report.append(error)

    for eachGlyphName in glyphsInvolvedInRgt:
        status, error = checkGlyphPresenceInMultipleGroups(eachGlyphName, 'right', aFont)
        if status is False:
            report.append(error)

    if report:
        return False, report
    else:
        return True, None


def whichGroup(targetGlyphName, aLocation, aFont):
    assert aLocation in ['left', 'right']

    locationPrefixes = {'left': '@MMK_L_',
                        'right': '@MMK_R_'}

    filteredGroups = {name: content for name, content in aFont.groups.items() if name.startswith(locationPrefixes[aLocation])}
    for eachGroupName, eachGroupContent in filteredGroups.items():
        if targetGlyphName in eachGroupContent:
            return eachGroupName
    return None


def collectPairMapping(aPair, aFont):
    """here I assume aPair is made of two glyphnames, no classes"""
    lftGlyphName, rgtGlyphName = aPair
    lftGroup = whichGroup(lftGlyphName, 'left', aFont)
    rgtGroup = whichGroup(rgtGlyphName, 'right', aFont)

    pairsDB = [{'kind': 'gl2gl', 'key': (lftGlyphName, rgtGlyphName)},
               {'kind': 'gl2gr', 'key': (lftGlyphName, rgtGroup)    },
               {'kind': 'gr2gl', 'key': (lftGroup,     rgtGlyphName)},
               {'kind': 'gr2gr', 'key': (lftGroup,     rgtGroup)    }]
    for pair in pairsDB:
        if None not in pair['key']:
            pair['amount'] = aFont.kerning.get(pair['key'])
        else:
            pair['amount'] = None
    pairsDB = [pair for pair in pairsDB if pair['amount'] is not None]
    return pairsDB


def checkPairConflicts(aPair, aFont):
    pairsDB = collectPairMapping(aPair, aFont)

    # for sure conflicts
    if len(pairsDB) == 4:
        return False, pairsDB

    # 2 or 3 pairs are ok, only if...
    elif 2 < len(pairsDB) < 4:
        groupToGlyph = [pair for pair in pairsDB if pair['kind'] in ('gl2gr', 'gr2gl')]
        if len(groupToGlyph) == 2:
            return False, pairsDB

    # one pair, no possible conflicts
    else:
        return True, pairsDB


def isPairException(kerningReference, aFont):
    """here kerningReference could be made by classes"""
    lftReference, rgtReference = kerningReference

    if aFont.kerning.get(kerningReference) is not None:
        doesExists = True
    else:
        doesExists = False

    if lftReference.startswith('@MMK_L_') and rgtReference.startswith('@MMK_R_'):
        return False, doesExists, None

    elif lftReference.startswith('@MMK_L_'):
        rgtGroup = whichGroup(rgtReference, 'right', aFont)
        if rgtGroup:
            if aFont.kerning.get((lftReference, rgtGroup)) is not None:
                return True, doesExists, [(lftReference, rgtGroup)]

    elif rgtReference.startswith('@MMK_R_'):
        lftGroup = whichGroup(lftReference, 'left', aFont)
        if lftGroup:
            if aFont.kerning.get((lftGroup, rgtReference)) is not None:
                return True, doesExists, [(lftGroup, rgtReference)]

    else:
        status, pairsDB = checkPairConflicts(kerningReference, aFont)
        if len(pairsDB) > 1:
            return True, doesExists, [pair['key'] for pair in pairsDB if pair['key'] != kerningReference]

    return False, doesExists, None


def possibleExceptions(aPair, kerningReference, aFont):
    # two checks before starting
    if aPair == kerningReference:
        return []

    aPairStatus, aPairExistance, aPairParents = isPairException(aPair, aFont)
    if aPairStatus is True and aPairExistance is True:
        return []

    # here we start with possible exceptions
    lftGlyphName, rgtGlyphName = aPair
    lftReference, rgtReference = kerningReference

    status, pairsDB = checkPairConflicts(aPair, aFont)

    # building options
    options = {'gl2gl': (lftGlyphName, rgtGlyphName)}
    if rgtReference.startswith('@MMK_R_'):
        options['gl2gr'] = (lftGlyphName, rgtReference)
    if lftReference.startswith('@MMK_L_'):
        options['gr2gl'] = (lftReference, rgtGlyphName)

    # filtering options
    for eachPair in pairsDB:
        if eachPair['kind'] in options:
            del options[eachPair['kind']]
        if eachPair['kind'] == 'gr2gl':
            if 'gl2gr' in options:
                del options['gl2gr']
        if eachPair['kind'] == 'gl2gr':
            if 'gr2gl' in options:
                del options['gl2gr']

    possiblePairKinds = ('gl2gl',
                         'gl2gr',
                         'gr2gl',
                         'gr2gr')

    sortedOptions = [options[kind] for kind in possiblePairKinds if kind in options]
    return sortedOptions

def calcWiggle(pt1, pt2, waveLength, waveHeight, curveSquaring=.57):
    """used for highlighting exceptions in the editor"""

    assert 0 <= curveSquaring <= 1, 'curveSquaring should be a value between 0 and 1: {}'.format(curveSquaring)
    assert waveLength > 0, 'waveLength smaller or equal to zero: {}'.format(waveLength)

    diagonal = calcDistance(pt1, pt2)
    angleRad = calcAngle(pt1, pt2)

    howManyWaves = diagonal//int(waveLength)
    waveInterval = diagonal/float(howManyWaves)
    maxBcpLength = sqrt((waveInterval/4.)**2+(waveHeight/2.)**2)
    bcpLength = maxBcpLength*curveSquaring
    bcpInclination = calcAngle(Point(0,0), Point(waveInterval/4., waveHeight/2.))

    wigglePoints = [pt1]
    prevFlexPt = pt1
    polarity = 1
    for waveIndex in range(0, int(howManyWaves*2)):
        bcpOutAngle = angleRad+bcpInclination*polarity
        bcpOut = Point(prevFlexPt.x+cos(bcpOutAngle)*bcpLength, prevFlexPt.y+sin(bcpOutAngle)*bcpLength)
        flexPt = Point(prevFlexPt.x+cos(angleRad)*waveInterval/2., prevFlexPt.y+sin(angleRad)*waveInterval/2.)

        bcpInAngle = angleRad+(radians(180)-bcpInclination)*polarity
        bcpIn = Point(flexPt.x+cos(bcpInAngle)*bcpLength, flexPt.y+sin(bcpInAngle)*bcpLength)

        wigglePoints.append((bcpOut, bcpIn, flexPt))

        polarity *= -1
        prevFlexPt = flexPt

    return wigglePoints

# used in calcWiggle
def calcAngle(pt1, pt2):
    return atan2((pt2.y - pt1.y), (pt2.x - pt1.x))

def calcDistance(pt1, pt2):
    return sqrt((pt1.x - pt2.x)**2 + (pt1.y - pt2.y)**2)

