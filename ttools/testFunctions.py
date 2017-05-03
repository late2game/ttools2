#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############
# Widths test #
###############

### Modules
from types import *
from mojo.roboFont import RFont, RGlyph
from string import lowercase
from itertools import product
from mojo.tools import IntersectGlyphWithLine
from types import IntType

import testsData
reload(testsData)
from testsData import accentedDict, figuresDict, verticalGlyphSets
from testsData import fractionBase, interpunctionSets #, NEW2OLD
from testsData import UCExtraSets, LCextraSets, LCligaturesSets
from testsData import dnomNumrSubsSupsTable, flippedMarginsSet


### Constants
SEP = '-'*10
START_ERROR = "%(sep)s %(funcName)s %(sep)s" # {'funcName': , 'sep': }
END_ERROR = "%(sep)s END %(sep)s" # {'sep'}
WIDTH_ERROR = "\t%(glyphName)s width: %(width)s" # {'glyphName': , 'width': }
LEFT_DIFFER_ERROR = "%(glyphOne)s and %(glyphTwo)s left margins differ" # {'glyphOne': , 'glyphTwo': }
RIGHT_DIFFER_ERROR = "%(glyphOne)s and %(glyphTwo)s right margins differ" #  {'glyphOne': , 'glyphTwo': }
WIDTH_DIFFER_ERROR = "%(glyphOne)s and %(glyphTwo)s width differ (%(widthOne)s vs. %(widthTwo)s)"  # {'glyphOne': , 'glyphTwo': , 'widthOne': , 'widthTwo': }
MOST_FREQUENT_ERROR = "The most frequent width is %(mostOccur)s (%(times)s times)" # {'mostOccur': , 'times': }
FLIPPED_ERROR = "%(glyphOne)s and %(glyphTwo)s have not flipped sidebearings" #  {'glyphOne': , 'glyphTwo': }

### Functions
def occurDict(items):
    d = {}
    for i in items:
        if i in d:
            d[i] = d[i]+1
        else:
            d[i] = 1
    return d


def convertToOLD(newNames):
    oldNames = []
    for newName in newNames:
        if newName in NEW2OLD:
            oldNames.append(NEW2OLD[newName])
        else:
            oldNames.append(newName)
    return oldNames


def isWidthEqual(glyph1, glyph2):
    assert isinstance(glyph1, RGlyph), "%r is not a RGlyph object" % glyph1
    assert isinstance(glyph2, RGlyph), "%r is not a RGlyph object" % glyph2

    if glyph1.width == glyph2.width:
        return True
    else:
        return False

def areSidebearingsFlipped(glyph1, glyph2):
    assert isinstance(glyph1, RGlyph), "%r is not a RGlyph object" % glyph1
    assert isinstance(glyph2, RGlyph), "%r is not a RGlyph object" % glyph2

    if glyph1.leftMargin == glyph2.rightMargin and glyph1.rightMargin == glyph2.leftMargin:
        return True
    else:
        return False

def isSidebearingEqual(glyph1, glyph2, position, height):
    # checking arguments qualities
    assert position == 'left' or position == 'right'
    assert type(height) is IntType

    intersections1 = IntersectGlyphWithLine(glyph1,
                                            ((0, height), (glyph1.width, height)),
                                            canHaveComponent=True,
                                            addSideBearings=True)
    intersections1 = sorted(intersections1, key=lambda coor: coor[0])

    intersections2 = IntersectGlyphWithLine(glyph2,
                                            ((0, height), (glyph2.width, height)),
                                            canHaveComponent=True,
                                            addSideBearings=True)
    intersections2 = sorted(intersections2, key=lambda coor: coor[0])

    if position == 'left':
        if int(intersections1[1][0]) != int(intersections2[1][0]):
            return False
        else:
            return True
    else:
        if int(intersections1[-2][0]) != int(intersections2[-2][0]):
            return False
        else:
            return True


def areVerticalExtremesEqual(glyphs):
    glyphsData = {}

    for eachGlyph in glyphs:
        xMin, yMin, xMax, yMax = eachGlyph.box
        glyphsData[eachGlyph.name] = (yMin, yMax)

    if len(set(glyphsData.values())) <= 1:
        return True, {}

    else:
        return False, glyphsData


def checkVerticalExtremes(sourceFont, nameScheme='new'):
    assert isinstance(sourceFont, RFont), "%r is not a RFont object" % sourceFont
    assert nameScheme in ['new', 'old'], "%r is neither 'new' or 'old'" % nameScheme

    errorLines = [START_ERROR % {'sep': SEP, 'funcName': checkVerticalExtremes.__name__}]
    missingGlyphs = []

    for eachSetToCheck in verticalGlyphSets:
        if nameScheme == 'old':
            eachSetToCheck = convertToOLD(eachSetToCheck)

        glyphs = []
        for eachName in eachSetToCheck:
            if eachName in sourceFont:
                glyphs.append(sourceFont[eachName])
            else:
                missingGlyphs.append(eachName)
        areEqual, glyphsData = areVerticalExtremesEqual(glyphs)

        if areEqual is False:
            subErrorLines = ['The following glyphs are not vertically aligned']
            for eachKey in eachSetToCheck:
                eachValue = glyphsData[eachKey]
                subErrorLines.append('\t%s, bottom: %s, top: %s' % (eachKey, eachValue[0], eachValue[1]))

            errorLines.append(subErrorLines)

    errorLines.append(END_ERROR % {'sep': SEP})
    return errorLines, missingGlyphs


def checkLCextra(sourceFont, nameScheme='new'):
    assert isinstance(sourceFont, RFont), "%r is not a RFont object" % sourceFont
    assert nameScheme in ['new', 'old'], "%r is neither 'new' or 'old'" % nameScheme

    errorLines = [START_ERROR % {'sep': SEP, 'funcName': checkLCextra.__name__}]
    missingGlyphs = []

    for subName, parentName, whichCheck in LCextraSets:
        assert whichCheck == 'widthAndPosition' or whichCheck == 'width' or whichCheck == 'left' or whichCheck == 'right'

        if nameScheme == 'old':
            subName, parentName = convertToOLD([subName, parentName])

        if subName not in sourceFont:
            missingGlyphs.append(subName)
            continue

        subGlyph = sourceFont[subName]
        parentGlyph = sourceFont[parentName]

        if whichCheck == 'widthAndPosition':
            if isWidthEqual(subGlyph, parentGlyph) is False:
                errorLines.append(WIDTH_DIFFER_ERROR % {'glyphOne': parentGlyph.name,
                                                        'glyphTwo': subGlyph.name,
                                                        'widthOne': parentGlyph.width,
                                                        'widthTwo': subGlyph.width})

            if isSidebearingEqual(subGlyph, parentGlyph, 'left', int(sourceFont.info.xHeight/4)) is False:
                errorLines.append(LEFT_DIFFER_ERROR % {'glyphOne': parentGlyph.name, 'glyphTwo': subGlyph.name})

            # check right
            if isSidebearingEqual(subGlyph, parentGlyph, 'right', int(sourceFont.info.xHeight/4)) is False:
                errorLines.append(RIGHT_DIFFER_ERROR % {'glyphOne': parentGlyph.name, 'glyphTwo': subGlyph.name})

        elif whichCheck == 'width':
            if isWidthEqual(subGlyph, parentGlyph) is False:
                errorLines.append(WIDTH_DIFFER_ERROR % {'glyphOne': parentGlyph.name,
                                                        'glyphTwo': subGlyph.name,
                                                        'widthOne': parentGlyph.width,
                                                        'widthTwo': subGlyph.width})

        elif whichCheck == 'left':
            if isSidebearingEqual(subGlyph, parentGlyph, 'left', int(10)) is False:
                errorLines.append(LEFT_DIFFER_ERROR % {'glyphOne': parentGlyph.name, 'glyphTwo': subGlyph.name})

        else:   # right
            if subGlyph.rightMargin != parentGlyph.rightMargin:
                errorLines.append(RIGHT_DIFFER_ERROR % {'glyphOne': parentGlyph.name, 'glyphTwo': subGlyph.name})

    errorLines.append(END_ERROR % {'sep': SEP})
    return errorLines, missingGlyphs


def checkUCextra(sourceFont, nameScheme='new'):
    assert isinstance(sourceFont, RFont), "%r is not a RFont object" % sourceFont
    assert nameScheme in ['new', 'old'], "%r is neither 'new' or 'old'" % nameScheme

    errorLines = [START_ERROR % {'sep': SEP, 'funcName': checkUCextra.__name__}]
    missingGlyphs = []

    for parentName, subName, position in UCExtraSets:

        if nameScheme == 'old':
            parentName, subName = convertToOLD([parentName, subName])

        if subName not in sourceFont:
            missingGlyphs.append(subName)
            continue

        parentGlyph = sourceFont[parentName]
        subGlyph = sourceFont[subName]

        assert position == 'middle' or position == 'bottom'
        if position == 'middle':
            height = int(sourceFont.info.capHeight/2)
        else:
            height = int(2)

        if parentGlyph.width != subGlyph.width:
            errorLines.append(WIDTH_DIFFER_ERROR % {'glyphOne': parentGlyph.name,
                                              'glyphTwo': subGlyph.name,
                                              'widthOne': parentGlyph.width,
                                              'widthTwo': subGlyph.width})

        if isSidebearingEqual(subGlyph, parentGlyph, 'left', height) is False:
            errorLines.append(LEFT_DIFFER_ERROR % {'glyphOne': parentGlyph.name, 'glyphTwo': subGlyph.name})

        if isSidebearingEqual(subGlyph, parentGlyph, 'right', height) is False:
            errorLines.append(RIGHT_DIFFER_ERROR % {'glyphOne': parentGlyph.name, 'glyphTwo': subGlyph.name})

    errorLines.append(END_ERROR % {'sep': SEP})
    return errorLines, missingGlyphs


def checkLCligatures(sourceFont, nameScheme='new'):
    assert isinstance(sourceFont, RFont), "%r is not a RFont object" % sourceFont
    assert nameScheme in ['new', 'old'], "%r is neither 'new' or 'old'" % nameScheme

    errorLines = [START_ERROR % {'sep': SEP, 'funcName': checkLCligatures.__name__}]
    missingGlyphs = []

    for leftParentName, ligatureName, rightParentName in LCligaturesSets:

        if nameScheme == 'old':
            leftParentName, ligatureName, rightParentName = convertToOLD([leftParentName, ligatureName, rightParentName])

        if ligatureName not in sourceFont:
            missingGlyphs.append(ligatureName)
            continue

        leftParent = sourceFont[leftParentName]
        ligature = sourceFont[ligatureName]
        rightParent = sourceFont[rightParentName]

        if leftParent.leftMargin != ligature.leftMargin:
            errorLines.append(LEFT_DIFFER_ERROR % {'glyphOne': ligature.name, 'glyphTwo': leftParent.name})

        if rightParent.rightMargin != ligature.rightMargin:
            errorLines.append(RIGHT_DIFFER_ERROR % {'glyphOne': ligature.name, 'glyphTwo': rightParent.name})

    errorLines.append(END_ERROR % {'sep': SEP})
    return errorLines, missingGlyphs


def checkUCligatures(sourceFont, nameScheme='new'):
    assert isinstance(sourceFont, RFont), "%r is not a RFont object" % sourceFont
    assert nameScheme in ['new', 'old'], "%r is neither 'new' or 'old'" % nameScheme

    errorLines = [START_ERROR % {'sep': SEP, 'funcName': checkUCligatures.__name__}]
    missingGlyphs = []

    # AE
    ligaName = 'AE'
    rightParentName = 'E'

    if nameScheme == 'old':
        ligaName, rightParentName = convertToOLD([ligaName, rightParentName])

    if ligaName in sourceFont:
        liga = sourceFont[ligaName]
        rightParent = sourceFont[rightParentName]
        if liga.rightMargin != rightParent.rightMargin:
            errorLines.append(RIGHT_DIFFER_ERROR % {'glyphOne': liga.name, 'glyphTwo': rightParent.name})
    else:
        missingGlyphs.append(ligaName)

    # OE
    ligaName = 'OE'
    leftParentName = 'O'
    rightParentName = 'E'

    if nameScheme == 'old':
        ligaName, leftParentName, rightParentName = convertToOLD([ligaName, leftParentName, rightParentName])

    if ligaName in sourceFont:
        liga = sourceFont[ligaName]
        leftParent = sourceFont[leftParentName]
        rightParent = sourceFont[rightParentName]

        if liga.leftMargin != leftParent.leftMargin:
            errorLines.append(LEFT_DIFFER_ERROR % {'glyphOne': liga.name, 'glyphTwo': leftParent.name})

        if liga.rightMargin != rightParent.rightMargin:
            errorLines.append(RIGHT_DIFFER_ERROR % {'glyphOne': liga.name, 'glyphTwo': rightParent.name})

    else:
        missingGlyphs.append(ligaName)

    errorLines.append(END_ERROR % {'sep': SEP})
    return errorLines, missingGlyphs


def checkFigures(sourceFont, nameScheme='new'):
    assert isinstance(sourceFont, RFont), "%r is not a RFont object" % sourceFont
    assert nameScheme in ['new', 'old'], "%r is neither 'new' or 'old'" % nameScheme

    errorLines = [START_ERROR % {'sep': SEP, 'funcName': checkFigures.__name__}]
    missingGlyphs = []

    checksToBeDone = ['tabularLining', 'tabularOS', 'tabularSC', 'math', 'mathSC']
    for eachCheck in checksToBeDone:
        digitsNames = figuresDict[eachCheck]

        if nameScheme == 'old':
            digitsNames = convertToOLD(digitsNames)

        widths = {}
        for eachFigureName in digitsNames:
            if eachFigureName in sourceFont:
                glyph = sourceFont[eachFigureName]
                widths[eachFigureName] = glyph.width
            else:
                missingGlyphs.append(eachFigureName)

        if len(set(widths.values())) > 1:
            subErrorLines = ['Some %s figures have different width' % eachCheck]

            # calc most frequent width
            widthsOccurrences = occurDict(widths.values())
            items = [(item[0], item[1]) for item in widthsOccurrences.items()]
            mostOccurrentWidth, occurrencesAmount = sorted(items, key=lambda item: item[1], reverse=True)[0]
            subErrorLines.append(MOST_FREQUENT_ERROR % {'mostOccur': mostOccurrentWidth, 'times': occurrencesAmount})

            # print widths
            for eachFigureName in digitsNames:
                if eachFigureName in sourceFont:
                    glyph = sourceFont[eachFigureName]
                    if glyph.width != mostOccurrentWidth:
                        subErrorLines.append(WIDTH_ERROR % {'glyphName': glyph.name, 'width': glyph.width})
            errorLines.append(subErrorLines)

    errorLines.append(END_ERROR % {'sep': SEP})
    return errorLines, missingGlyphs


def checkDnomNumrSubsSups(sourceFont, nameScheme='new'):
    """DnomNumrSubsSups figures are check as monospaced
       then margins are checked --> a.dnom.leftMargin  == uni2090.leftMargin
                                    a.dnom.rightMargin == uni2090.rightMargin
    """
    assert isinstance(sourceFont, RFont), "%r is not a RFont object" % sourceFont
    assert nameScheme in ['new', 'old'], "%r is neither 'new' or 'old'" % nameScheme

    errorLines = [START_ERROR % {'sep': SEP, 'funcName': checkDnomNumrSubsSups.__name__}]
    missingGlyphs = []

    # filter tabular dnoms
    tabularRows = []
    for eachDigitName in figuresDict['tabularLining']:
        if eachDigitName == 'figurespace':
            continue
        for eachRow in dnomNumrSubsSupsTable[1:]:
            if eachRow[0] == eachDigitName:
                tabularRows.append(eachRow)

    widths = {}
    for eachRow in tabularRows:
        eachDnomName = eachRow[1]
        if eachDnomName in sourceFont:
            glyph = sourceFont[eachDnomName]
            widths[eachDnomName] = glyph.width
        else:
            missingGlyphs.append(eachDnomName)

    if len(set(widths.values())) > 1:   # dnom have to be fixed
        subErrorLines = ['Some dnom figures have different width']

        # calc most frequent width
        widthsOccurrences = occurDict(widths.values())
        items = [(item[0], item[1]) for item in widthsOccurrences.items()]
        mostOccurrentWidth, occurrencesAmount = sorted(items, key=lambda item: item[1], reverse=True)[0]
        subErrorLines.append(MOST_FREQUENT_ERROR % {'mostOccur': mostOccurrentWidth, 'times': occurrencesAmount})

        # print widths
        for eachRow in tabularRows:
            eachDnomName = eachRow[1]
            if eachDnomName in sourceFont:
                glyph = sourceFont[eachDnomName]
                subErrorLines.append(WIDTH_ERROR % {'glyphName': glyph.name, 'width': glyph.width})
        errorLines.append(subErrorLines)
        errorLines.append('[WARNING] Please fix the DNOMs then check again NUMR SUBS and SUPS')

    else:   # dnom are fine, let's see the rest

        for eachRow in dnomNumrSubsSupsTable[1:]:
            eachDnomName = eachRow[1]
            for eachColIndex in range(2, 5):
                numInfSupName = eachRow[eachColIndex]

                if numInfSupName in sourceFont:
                    parentGlyph = sourceFont[eachDnomName]
                    subGlyph = sourceFont[numInfSupName]

                    # check set width
                    if isWidthEqual(subGlyph, parentGlyph) is False:
                        errorLines.append(WIDTH_DIFFER_ERROR % {'glyphOne': parentGlyph.name,
                                                                'glyphTwo': subGlyph.name,
                                                                'widthOne': parentGlyph.width,
                                                                'widthTwo': subGlyph.width})

                    # check left
                    if subGlyph.leftMargin != parentGlyph.leftMargin:
                        errorLines.append(LEFT_DIFFER_ERROR % {'glyphOne': parentGlyph.name, 'glyphTwo': subGlyph.name})

                    # check right
                    if subGlyph.rightMargin != parentGlyph.rightMargin:
                        errorLines.append(RIGHT_DIFFER_ERROR % {'glyphOne': parentGlyph.name, 'glyphTwo': subGlyph.name})

                else:
                    missingGlyphs.append(numInfSupName)

    errorLines.append(END_ERROR % {'sep': SEP})
    return errorLines, missingGlyphs


def checkFlippedMargins(sourceFont, nameScheme='new'):
    assert isinstance(sourceFont, RFont), "%r is not a RFont object" % sourceFont
    assert nameScheme in ['new', 'old'], "%r is neither 'new' or 'old'" % nameScheme

    errorLines = [START_ERROR % {'sep': SEP, 'funcName': checkFlippedMargins.__name__}]
    missingGlyphs = []

    for eachLftName, eachRgtName in flippedMarginsSet:
        if sourceFont.has_key(eachLftName) and sourceFont.has_key(eachRgtName):
            eachLftGlyph = sourceFont[eachLftName]
            eachRgtGlyph = sourceFont[eachRgtName]
            if areSidebearingsFlipped(eachLftGlyph, eachRgtGlyph) is False:
                errorLines.append(FLIPPED_ERROR % {'glyphOne': eachLftName, 'glyphTwo': eachRgtName})
        else:
            if sourceFont.has_key(eachLftName) is False:
                missingGlyphs.append(eachLftName)
            elif sourceFont.has_key(eachRgtName) is False:
                missingGlyphs.append(eachRgtName)

    errorLines.append(END_ERROR % {'sep': SEP})
    return errorLines, missingGlyphs


def checkFractions(sourceFont, nameScheme='new'):
    assert isinstance(sourceFont, RFont), "%r is not a RFont object" % sourceFont
    assert nameScheme in ['new', 'old'], "%r is neither 'new' or 'old'" % nameScheme

    errorLines = [START_ERROR % {'sep': SEP, 'funcName': checkFractions.__name__}]
    missingGlyphs = []

    if nameScheme == 'old':
        fractionNames = convertToOLD(fractionBase)
    else:
        fractionNames = fractionBase

    widths = {}
    for eachFractionName in fractionNames:
        if eachFractionName in sourceFont:
            glyph = sourceFont[eachFractionName]
            widths[eachFractionName] = glyph.width
        else:
            missingGlyphs.append(eachFractionName)

    if len(set(widths.values())) > 1:
        errorLines.append('Some fractions have different width')

        # calc most frequent width
        widthsOccurrences = occurDict(widths.values())
        items = [(item[0], item[1]) for item in widthsOccurrences.items()]
        mostOccurrentWidth, occurrencesAmount = sorted(items, key=lambda item:item[1], reverse=True)[0]
        errorLines.append(MOST_FREQUENT_ERROR % {'mostOccur': mostOccurrentWidth, 'times': occurrencesAmount})

        # print widths
        for eachFractionName in fractionNames:
            if eachFractionName in sourceFont:
                glyph = sourceFont[eachFractionName]
                if glyph.width != mostOccurrentWidth:
                    errorLines.append(WIDTH_ERROR % {'glyphName': glyph.name, 'width': glyph.width})

    errorLines.append(END_ERROR % {'sep': SEP})
    return errorLines, missingGlyphs


def checkInterpunction(sourceFont, nameScheme='new'):
    assert isinstance(sourceFont, RFont), "%r is not a RFont object" % sourceFont
    assert nameScheme in ['new', 'old'], "%r is neither 'new' or 'old'" % nameScheme

    errorLines = [START_ERROR % {'sep': SEP, 'funcName': checkInterpunction.__name__}]
    missingGlyphs = []

    for eachSetToCheck in interpunctionSets:
        glyphs = []

        if nameScheme == 'old':
            eachSetToCheck = convertToOLD(eachSetToCheck)

        for eachName in eachSetToCheck:
            if eachName in sourceFont:
                glyphs.append(sourceFont[eachName])
            else:
                missingGlyphs.append(eachName)

        glyphWidthAndMargins = {}
        for eachGlyph in glyphs:
            if 'right' in eachGlyph.name:
                glyphWidthAndMargins[eachGlyph.name] = (eachGlyph.width,
                                                        eachGlyph.rightMargin,
                                                        eachGlyph.leftMargin)
            else:
                glyphWidthAndMargins[eachGlyph.name] = (eachGlyph.width,
                                                        eachGlyph.leftMargin,
                                                        eachGlyph.rightMargin)

        if len(set(glyphWidthAndMargins.values())) > 1:
            errorLines.append('\nThe following glyphs differ in width or position:')
            for eachGlyph in glyphs:
                errorLines.append('\t%s: width:%s, leftMargin:%s, rightMargin:%s' % (eachGlyph.name,
                                                                                     eachGlyph.width,
                                                                                     eachGlyph.leftMargin,
                                                                                     eachGlyph.rightMargin))

    errorLines.append(END_ERROR % {'sep': SEP})
    return errorLines, missingGlyphs


def checkAccented(sourceFont, nameScheme='new'):
    assert isinstance(sourceFont, RFont), "%r is not a RFont object" % sourceFont
    assert nameScheme in ['new', 'old'], "%r is neither 'new' or 'old'" % nameScheme

    errorLines = [START_ERROR % {'sep': SEP, 'funcName': checkAccented.__name__}]
    missingGlyphs = []

    for eachAccentedGlyphName, eachAccentedData in accentedDict.items():
        if eachAccentedGlyphName in sourceFont:
            accentedName = eachAccentedGlyphName
            parentName = eachAccentedData[0]

            if nameScheme == 'old':
                accentedName, parentName = convertToOLD([accentedName, parentName])

            accentedGlyph = sourceFont[accentedName]
            parentGlyph = sourceFont[parentName]

            # check set width
            if isWidthEqual(accentedGlyph, parentGlyph) is False:
                errorLines.append(WIDTH_DIFFER_ERROR % {'glyphOne': parentGlyph.name,
                                                  'glyphTwo': accentedGlyph.name,
                                                  'widthOne': parentGlyph.width,
                                                  'widthTwo': accentedGlyph.width})

            # check left
            if isSidebearingEqual(accentedGlyph, parentGlyph, 'left', int(sourceFont.info.xHeight/2)) is False:
                errorLines.append(LEFT_DIFFER_ERROR % {'glyphOne': parentGlyph.name, 'glyphTwo': accentedGlyph.name})

            # check right
            if isSidebearingEqual(accentedGlyph, parentGlyph, 'right', int(sourceFont.info.xHeight/2)) is False:
                errorLines.append(RIGHT_DIFFER_ERROR % {'glyphOne': parentGlyph.name, 'glyphTwo': accentedGlyph.name})

    errorLines.append(END_ERROR % {'sep': SEP})
    return errorLines, missingGlyphs

