#!/usr/bin/env python
# coding: utf-8

###############
# Widths test #
###############

### Modules
# standard
from __future__ import absolute_import
import os, importlib
from mojo.roboFont import RFont, RGlyph, version
from itertools import product
from mojo.tools import IntersectGlyphWithLine

# custom
from . import miscFunctions
importlib.reload(miscFunctions)
from .miscFunctions import loadGlyphNamesTable


### Constants
# glyphLists
BASIC_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'tables')

DNOM_NUMR_SUBS_SUPS_PATH = os.path.join(BASIC_PATH, 'dnomNumrSubsSups.csv')
DNOM_NUMR_SUBS_SUPS = loadGlyphNamesTable(DNOM_NUMR_SUBS_SUPS_PATH)

ACCENTED_LETTERS_PATH = os.path.join(BASIC_PATH, 'accentedLettersTable.csv')
ACCENTED_LETTERS = loadGlyphNamesTable(ACCENTED_LETTERS_PATH)

INTERPUNCTION_GROUPS_PATH = os.path.join(BASIC_PATH, 'interpunctionGroups.csv')
INTERPUNCTION_GROUPS = loadGlyphNamesTable(INTERPUNCTION_GROUPS_PATH)

VERTICAL_GROUPS_PATH = os.path.join(BASIC_PATH, 'verticalGroups.csv')
VERTICAL_GROUPS = loadGlyphNamesTable(VERTICAL_GROUPS_PATH)

INTERPUNCTION_FLIPPED_SIDEBEARINGS_PATH = os.path.join(BASIC_PATH, 'interpunctionFlippedSidebearings.csv')
INTERPUNCTION_FLIPPED_SIDEBEARINGS = loadGlyphNamesTable(INTERPUNCTION_FLIPPED_SIDEBEARINGS_PATH)

FRACTIONS_PATH = os.path.join(BASIC_PATH, 'fractions.csv')
FRACTIONS = loadGlyphNamesTable(FRACTIONS_PATH)
FRACTIONS_BASE = [item[0] for item in FRACTIONS]

TABULAR_FIGURES_PATH = os.path.join(BASIC_PATH, 'tabularFigures.csv')
TABULAR_FIGURES = loadGlyphNamesTable(TABULAR_FIGURES_PATH)
TABULAR_LINING = [row[0] for row in TABULAR_FIGURES]
TABULAR_OLDSTYLE = [row[1] for row in TABULAR_FIGURES]
TABULAR_SC = [row[2] for row in TABULAR_FIGURES if len(row) < 2]

MATH_SC_PATH = os.path.join(BASIC_PATH, 'mathSC.csv')
MATH_SC = [row[0] for row in loadGlyphNamesTable(MATH_SC_PATH)]
MATH = [row[1] for row in loadGlyphNamesTable(MATH_SC_PATH)]

LC_EXTRA_PATH = os.path.join(BASIC_PATH, 'LCextrasTests.csv')
LC_EXTRA = loadGlyphNamesTable(LC_EXTRA_PATH)

UC_EXTRA_PATH = os.path.join(BASIC_PATH, 'UCextrasTests.csv')
UC_EXTRA = loadGlyphNamesTable(UC_EXTRA_PATH)

LC_LIGATURES_PATH = os.path.join(BASIC_PATH, 'LCligaturesTests.csv')
LC_LIGATURES = loadGlyphNamesTable(LC_LIGATURES_PATH)

# Error messages
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
    aDict = {}
    for eachItem in items:
        if eachItem in aDict:
            aDict[eachItem] = aDict[eachItem]+1
        else:
            aDict[eachItem] = 1
    return aDict


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
    assert position == '*left' or position == '*right'
    assert type(height) is int

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

    if position == '*left':
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
        if version[0] == '2':
            glyphBounds = eachGlyph.bounds
        else:
            glyphBounds = eachGlyph.box

        if glyphBounds is None:
            glyphsData[eachGlyph.name] = 'empty'
        else:
            xMin, yMin, xMax, yMax = glyphBounds
            glyphsData[eachGlyph.name] = (yMin, yMax)

    if len(set(glyphsData.values())) <= 1:
        return True, {}

    else:
        return False, glyphsData


def checkVerticalExtremes(sourceFont):
    assert isinstance(sourceFont, RFont), "%r is not a RFont object" % sourceFont

    errorLines = [START_ERROR % {'sep': SEP, 'funcName': checkVerticalExtremes.__name__}]
    missingGlyphs = []

    for eachSetToCheck in VERTICAL_GROUPS:
        glyphs = []
        for eachName in eachSetToCheck:
            if sourceFont.has_key(eachName):
                glyphs.append(sourceFont[eachName])
            else:
                missingGlyphs.append(eachName)
        areEqual, glyphsData = areVerticalExtremesEqual(glyphs)

        if areEqual is False:
            if glyphsData == 'empty':
                missingGlyphs.append(eachName)
                continue

            subErrorLines = ['The following glyphs are not vertically aligned']
            for eachKey in eachSetToCheck:
                eachValue = glyphsData[eachKey]
                subErrorLines.append('\t%s, bottom: %s, top: %s' % (eachKey, eachValue[0], eachValue[1]))

            errorLines.append(subErrorLines)

    errorLines.append(END_ERROR % {'sep': SEP})
    return errorLines, missingGlyphs


def checkLCextra(sourceFont):
    assert isinstance(sourceFont, RFont), "%r is not a RFont object" % sourceFont

    errorLines = [START_ERROR % {'sep': SEP, 'funcName': checkLCextra.__name__}]
    missingGlyphs = []

    for subName, parentName, whichCheck in LC_EXTRA:
        assert whichCheck == '*widthAndPosition' or whichCheck == '*width' or whichCheck == '*left' or whichCheck == '*right', whichCheck

        if subName not in sourceFont:
            missingGlyphs.append(subName)
            continue

        subGlyph = sourceFont[subName]
        parentGlyph = sourceFont[parentName]

        if whichCheck == '*widthAndPosition':
            if isWidthEqual(subGlyph, parentGlyph) is False:
                errorLines.append(WIDTH_DIFFER_ERROR % {'glyphOne': parentGlyph.name,
                                                        'glyphTwo': subGlyph.name,
                                                        'widthOne': parentGlyph.width,
                                                        'widthTwo': subGlyph.width})

            if isSidebearingEqual(subGlyph, parentGlyph, '*left', int(sourceFont.info.xHeight/4)) is False:
                errorLines.append(LEFT_DIFFER_ERROR % {'glyphOne': parentGlyph.name, 'glyphTwo': subGlyph.name})

            # check right
            if isSidebearingEqual(subGlyph, parentGlyph, '*right', int(sourceFont.info.xHeight/4)) is False:
                errorLines.append(RIGHT_DIFFER_ERROR % {'glyphOne': parentGlyph.name, 'glyphTwo': subGlyph.name})

        elif whichCheck == '*width':
            if isWidthEqual(subGlyph, parentGlyph) is False:
                errorLines.append(WIDTH_DIFFER_ERROR % {'glyphOne': parentGlyph.name,
                                                        'glyphTwo': subGlyph.name,
                                                        'widthOne': parentGlyph.width,
                                                        'widthTwo': subGlyph.width})

        elif whichCheck == '*left':
            if isSidebearingEqual(subGlyph, parentGlyph, '*left', int(10)) is False:
                errorLines.append(LEFT_DIFFER_ERROR % {'glyphOne': parentGlyph.name, 'glyphTwo': subGlyph.name})

        else:   # right
            if subGlyph.rightMargin != parentGlyph.rightMargin:
                errorLines.append(RIGHT_DIFFER_ERROR % {'glyphOne': parentGlyph.name, 'glyphTwo': subGlyph.name})

    errorLines.append(END_ERROR % {'sep': SEP})
    return errorLines, missingGlyphs


def checkUCextra(sourceFont):
    assert isinstance(sourceFont, RFont), "%r is not a RFont object" % sourceFont

    errorLines = [START_ERROR % {'sep': SEP, 'funcName': checkUCextra.__name__}]
    missingGlyphs = []

    for parentName, subName, position in UC_EXTRA:

        if subName not in sourceFont:
            missingGlyphs.append(subName)
            continue

        parentGlyph = sourceFont[parentName]
        subGlyph = sourceFont[subName]

        assert position == '*middle' or position == '*bottom'
        if position == '*middle':
            height = int(sourceFont.info.capHeight/2)
        else:
            height = int(2)

        if parentGlyph.width != subGlyph.width:
            errorLines.append(WIDTH_DIFFER_ERROR % {'glyphOne': parentGlyph.name,
                                              'glyphTwo': subGlyph.name,
                                              'widthOne': parentGlyph.width,
                                              'widthTwo': subGlyph.width})

        if isSidebearingEqual(subGlyph, parentGlyph, '*left', height) is False:
            errorLines.append(LEFT_DIFFER_ERROR % {'glyphOne': parentGlyph.name, 'glyphTwo': subGlyph.name})

        if isSidebearingEqual(subGlyph, parentGlyph, '*right', height) is False:
            errorLines.append(RIGHT_DIFFER_ERROR % {'glyphOne': parentGlyph.name, 'glyphTwo': subGlyph.name})

    errorLines.append(END_ERROR % {'sep': SEP})
    return errorLines, missingGlyphs


def checkLCligatures(sourceFont):
    assert isinstance(sourceFont, RFont), "%r is not a RFont object" % sourceFont

    errorLines = [START_ERROR % {'sep': SEP, 'funcName': checkLCligatures.__name__}]
    missingGlyphs = []

    for leftParentName, ligatureName, rightParentName in LC_LIGATURES:

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


def checkUCligatures(sourceFont):
    assert isinstance(sourceFont, RFont), "%r is not a RFont object" % sourceFont

    errorLines = [START_ERROR % {'sep': SEP, 'funcName': checkUCligatures.__name__}]
    missingGlyphs = []

    # AE
    ligaName = 'AE'
    rightParentName = 'E'

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


def checkFigures(sourceFont):
    assert isinstance(sourceFont, RFont), "%r is not a RFont object" % sourceFont

    errorLines = [START_ERROR % {'sep': SEP, 'funcName': checkFigures.__name__}]
    missingGlyphs = []

    checksToBeDone = {'tabularLining': TABULAR_LINING,
                      'tabularOS': TABULAR_OLDSTYLE,
                      'tabularSC': TABULAR_SC,
                      'math': MATH,
                      'mathSC': MATH_SC}

    for eachCheckName, digitsNames in checksToBeDone.items():
        widths = {}
        for eachFigureName in digitsNames:
            if sourceFont.has_key(eachFigureName):
                glyph = sourceFont[eachFigureName]
                widths[eachFigureName] = glyph.width
            else:
                missingGlyphs.append(eachFigureName)

        if len(set(widths.values())) > 1:
            subErrorLines = ['Some %s figures have different width' % eachCheckName]

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


def checkDnomNumrSubsSups(sourceFont):
    """DnomNumrSubsSups figures are check as monospaced
       then margins are checked --> a.dnom.leftMargin  == uni2090.leftMargin
                                    a.dnom.rightMargin == uni2090.rightMargin
    """
    assert isinstance(sourceFont, RFont), "%r is not a RFont object" % sourceFont

    errorLines = [START_ERROR % {'sep': SEP, 'funcName': checkDnomNumrSubsSups.__name__}]
    missingGlyphs = []

    # filter tabular dnoms
    tabularRows = []
    for eachDigitName in TABULAR_LINING:
        if eachDigitName == 'figurespace':
            continue
        for eachRow in DNOM_NUMR_SUBS_SUPS[1:]:
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

        for eachRow in DNOM_NUMR_SUBS_SUPS[1:]:
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


def checkFlippedMargins(sourceFont):
    assert isinstance(sourceFont, RFont), "%r is not a RFont object" % sourceFont

    errorLines = [START_ERROR % {'sep': SEP, 'funcName': checkFlippedMargins.__name__}]
    missingGlyphs = []

    for eachLftName, eachRgtName in INTERPUNCTION_FLIPPED_SIDEBEARINGS:
        if eachLftName in sourceFont and eachRgtName in sourceFont:
            eachLftGlyph = sourceFont[eachLftName]
            eachRgtGlyph = sourceFont[eachRgtName]
            if areSidebearingsFlipped(eachLftGlyph, eachRgtGlyph) is False:
                errorLines.append(FLIPPED_ERROR % {'glyphOne': eachLftName, 'glyphTwo': eachRgtName})
        else:
            if (eachLftName in sourceFont) is False:
                missingGlyphs.append(eachLftName)
            elif (eachRgtName in sourceFont) is False:
                missingGlyphs.append(eachRgtName)

    errorLines.append(END_ERROR % {'sep': SEP})
    return errorLines, missingGlyphs


def checkFractions(sourceFont):
    assert isinstance(sourceFont, RFont), "%r is not a RFont object" % sourceFont

    errorLines = [START_ERROR % {'sep': SEP, 'funcName': checkFractions.__name__}]
    missingGlyphs = []
    widths = {}
    for eachFractionName in FRACTIONS_BASE:
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
        for eachFractionName in FRACTIONS_BASE:
            if eachFractionName in sourceFont:
                glyph = sourceFont[eachFractionName]
                if glyph.width != mostOccurrentWidth:
                    errorLines.append(WIDTH_ERROR % {'glyphName': glyph.name, 'width': glyph.width})

    errorLines.append(END_ERROR % {'sep': SEP})
    return errorLines, missingGlyphs


def checkInterpunction(sourceFont):
    assert isinstance(sourceFont, RFont), "%r is not a RFont object" % sourceFont

    errorLines = [START_ERROR % {'sep': SEP, 'funcName': checkInterpunction.__name__}]
    missingGlyphs = []

    for eachSetToCheck in INTERPUNCTION_GROUPS:
        glyphs = []
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


def checkAccented(sourceFont):
    assert isinstance(sourceFont, RFont), "%r is not a RFont object" % sourceFont

    errorLines = [START_ERROR % {'sep': SEP, 'funcName': checkAccented.__name__}]
    missingGlyphs = []

    for eachAccentedName, eachParentName, eachAccentName, eachAnchor in ACCENTED_LETTERS:
        if eachAccentedName in sourceFont:
            accentedGlyph = sourceFont[eachAccentedName]
            parentGlyph = sourceFont[eachParentName]

            # check set width
            if isWidthEqual(accentedGlyph, parentGlyph) is False:
                errorLines.append(WIDTH_DIFFER_ERROR % {'glyphOne': parentGlyph.name,
                                                  'glyphTwo': accentedGlyph.name,
                                                  'widthOne': parentGlyph.width,
                                                  'widthTwo': accentedGlyph.width})

            # check left
            if isSidebearingEqual(accentedGlyph, parentGlyph, '*left', int(sourceFont.info.xHeight/2)) is False:
                errorLines.append(LEFT_DIFFER_ERROR % {'glyphOne': parentGlyph.name, 'glyphTwo': accentedGlyph.name})

            # check right
            if isSidebearingEqual(accentedGlyph, parentGlyph, '*right', int(sourceFont.info.xHeight/2)) is False:
                errorLines.append(RIGHT_DIFFER_ERROR % {'glyphOne': parentGlyph.name, 'glyphTwo': accentedGlyph.name})

    errorLines.append(END_ERROR % {'sep': SEP})
    return errorLines, missingGlyphs

