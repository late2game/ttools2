#!/usr/bin/env python
# coding: utf-8

#################################
# TTools for numr, fractions... #
#################################

### Modules
# custom
import ui.userInterfaceValues
reload(ui.userInterfaceValues)
from ui.userInterfaceValues import vanillaControlsSize
import extraTools.miscFunctions
reload(extraTools.miscFunctions)
from extraTools.miscFunctions import loadGlyphNamesTable

# standard
import os
import types
from math import tan, radians
from mojo.roboFont import AllFonts, CurrentFont
from vanilla import FloatingWindow, PopUpButton, TextBox, EditText, Button

### Constants
BASIC_PATH = os.path.join(os.path.dirname(__file__), 'resources', 'tables')

DNOM_NUMR_SUBS_SUPS_PATH = os.path.join(BASIC_PATH, 'dnomNumrSubsSups.csv')
DNOM_NUMR_SUBS_SUPS = loadGlyphNamesTable(DNOM_NUMR_SUBS_SUPS_PATH)
DNOM_NUMR = [(row[2], row[1]) for row in DNOM_NUMR_SUBS_SUPS]
DNOM_SUBS = [(row[3], row[1]) for row in DNOM_NUMR_SUBS_SUPS]
DNOM_SUPS = [(row[4], row[1]) for row in DNOM_NUMR_SUBS_SUPS]

LC_LIGATURES_PATH = os.path.join(BASIC_PATH, 'lcLigatures.csv')
LC_LIGATURES = loadGlyphNamesTable(LC_LIGATURES_PATH)

FRACTIONS_PATH = os.path.join(BASIC_PATH, 'fractions.csv')
FRACTIONS = loadGlyphNamesTable(FRACTIONS_PATH)

MATH_CASE_PATH = os.path.join(BASIC_PATH, 'mathCase.csv')
MATH_CASE = loadGlyphNamesTable(MATH_CASE_PATH)

MATH_SC_PATH = os.path.join(BASIC_PATH, 'mathSC.csv')
MATH_SC = loadGlyphNamesTable(MATH_SC_PATH)

LIG_AND_EXTRA_SC_PATH = os.path.join(BASIC_PATH, 'LigAndExtraSC.csv')
LIG_AND_EXTRA_SC = loadGlyphNamesTable(LIG_AND_EXTRA_SC_PATH)

GLYPHLISTS_OPTIONS = ('Numerators', 'Subscripts', 'Superscripts', 'LC ligatures', 'Fractions', 'Math Case', 'Math SC', 'Ligatures and Extras SC')
NAME_2_GLYPHLIST = {'Numerators': DNOM_NUMR,
                    'Subscripts': DNOM_SUBS,
                    'Superscripts': DNOM_SUPS,
                    'LC ligatures': LC_LIGATURES,
                    'Fractions': FRACTIONS,
                    'Math Case': MATH_CASE,
                    'Math SC': MATH_SC,
                    'Ligatures and Extras SC': LIG_AND_EXTRA_SC}

ACTIVE_OFFSET = ['Numerators', 'Subscripts', 'Superscripts', 'Math Case', 'Math SC']
TARGET_OPTIONS = ['All Fonts', 'Current Font']

PLUGIN_TITLE = 'TT Copy and move'
PLUGIN_WIDTH = 230
MARGIN_HOR = 10
MARGIN_VER = 8
NET_WIDTH = PLUGIN_WIDTH - MARGIN_HOR*2

### Classes
class CopyAndMove(object):

    isOffsetAllowed = False
    verticalOffset = 0

    def __init__(self):
        self.transferList = NAME_2_GLYPHLIST[GLYPHLISTS_OPTIONS[0]]
        self.target = TARGET_OPTIONS[0]

        self.w = FloatingWindow((0, 0, PLUGIN_WIDTH, 400), PLUGIN_TITLE)
        jumpingY = MARGIN_VER

        # target fonts
        self.w.targetFontsPopUp = PopUpButton((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['PopUpButtonRegularHeight']),
                                        TARGET_OPTIONS,
                                        callback=self.targetFontsPopUpCallback)
        jumpingY += vanillaControlsSize['PopUpButtonRegularHeight']+MARGIN_VER

        # transfer lists pop up
        self.w.glyphListPopUp = PopUpButton((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['PopUpButtonRegularHeight']),
                                            GLYPHLISTS_OPTIONS,
                                            callback=self.glyphListPopUpCallback)
        jumpingY += vanillaControlsSize['PopUpButtonRegularHeight']+MARGIN_VER

        # offset caption
        self.w.offsetCaption = TextBox((MARGIN_HOR, jumpingY+2, NET_WIDTH*.22, vanillaControlsSize['TextBoxRegularHeight']),
                                       'Offset:')

        # offset edit text
        self.w.offsetEdit = EditText((MARGIN_HOR+NET_WIDTH*.25, jumpingY, NET_WIDTH*.35, vanillaControlsSize['EditTextRegularHeight']),
                                     callback=self.offsetEditCallback)
        self.w.offsetEdit.set('%d' % self.verticalOffset)
        jumpingY += vanillaControlsSize['EditTextRegularHeight']+MARGIN_VER

        # clean button
        self.w.cleanButton = Button((MARGIN_HOR, jumpingY, NET_WIDTH*.45, vanillaControlsSize['ButtonRegularHeight']),
                                    'Clean',
                                    callback=self.cleanButtonCallback)

        # run button
        self.w.runButton = Button((MARGIN_HOR+NET_WIDTH*.55, jumpingY, NET_WIDTH*.45, vanillaControlsSize['ButtonRegularHeight']),
                                  'Run!',
                                  callback=self.runButtonCallback)
        jumpingY += vanillaControlsSize['ButtonRegularHeight']+MARGIN_VER

        self.w.setPosSize((0, 0, PLUGIN_WIDTH, jumpingY))
        self.w.open()


    def targetFontsPopUpCallback(self, sender):
        self.target = TARGET_OPTIONS[sender.get()]

    def glyphListPopUpCallback(self, sender):
        if GLYPHLISTS_OPTIONS[sender.get()] in ACTIVE_OFFSET:
            self.w.offsetEdit.enable(True)
        else:
            self.w.offsetEdit.enable(False)

        self.transferList = NAME_2_GLYPHLIST[GLYPHLISTS_OPTIONS[sender.get()]]
        self.isOffsetAllowed = False

    def offsetEditCallback(self, sender):
        try:
            self.verticalOffset = int(sender.get())
        except ValueError:
            self.w.offsetEdit.set('%d' % self.verticalOffset)

    def cleanButtonCallback(self, sender):
        if self.target == 'All Fonts':
            fontsToProcess = AllFonts()
        else:
            fontsToProcess = [CurrentFont()]

        for eachFont in fontsToProcess:
            for _, eachTarget in self.transferList:
                eachFont[eachTarget].clear()

    def runButtonCallback(self, sender):
        if self.target == 'All Fonts':
            fontsToProcess = AllFonts()
        else:
            fontsToProcess = [CurrentFont()]

        for eachFont in fontsToProcess:
            for eachRow in self.transferList:
                
                if len(eachRow) == 2:
                    eachTarget, eachSource = eachRow
                else:
                    eachTarget, eachSource = eachRow[0], eachRow[1:]

                if eachTarget not in eachFont:
                    targetGlyph = eachFont.newGlyph(eachTarget)
                else:
                    targetGlyph = eachFont[eachTarget]
                    targetGlyph.clear()

                if isinstance(eachSource, types.ListType) is False:
                    targetGlyph.width = eachFont[eachSource].width

                    if eachFont.info.italicAngle:
                        anchorAngle = radians(-eachFont.info.italicAngle)
                    else:
                        anchorAngle = radians(0)

                    tangentOffset = tan(anchorAngle)*self.verticalOffset
                    targetGlyph.appendComponent(eachSource, (tangentOffset, self.verticalOffset))
                else:
                    offsetX = 0
                    for eachSourceGlyphName in eachSource:
                        targetGlyph.appendComponent(eachSourceGlyphName, (offsetX, 0))
                        offsetX += eachFont[eachSourceGlyphName].width
                    targetGlyph.width = offsetX


if __name__ == '__main__':
    cm = CopyAndMove()
