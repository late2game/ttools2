#!/usr/bin/env python
# coding: utf-8

################
# Test Metrics #
################

### Modules
# standard
import os, sys
import types
import traceback
from datetime import datetime
from robofab.interface.all.dialogs import PutFile
from mojo.events import addObserver, removeObserver
from mojo.roboFont import AllFonts, RFont
from vanilla import FloatingWindow, PopUpButton, HorizontalLine
from vanilla import RadioGroup, TextBox, CheckBox, Button
from defconAppKit.windows.baseWindow import BaseWindowController

# custom
import extraTools.testFunctions
reload(extraTools.testFunctions)
from extraTools.testFunctions import checkVerticalExtremes, checkAccented
from extraTools.testFunctions import checkInterpunction, checkFigures
from extraTools.testFunctions import checkDnomNumrSubsSups, checkFractions
from extraTools.testFunctions import checkLCligatures, checkUCligatures
from extraTools.testFunctions import checkLCextra, checkUCextra, checkFlippedMargins

import ui.userInterfaceValues
reload(ui.userInterfaceValues)
from ui.userInterfaceValues import vanillaControlsSize

### Constants
RADIO_GROUP_HEIGHT = 40
NAMES_TABLE_PATH = os.path.join(os.path.dirname(__file__), 'resources', 'tables', 'old_vs_new_names.csv')

PLUGIN_WIDTH = 240
PLUGIN_HEIGHT = 600

MARGIN_LFT = 15
MARGIN_TOP = 15
MARGIN_ROW = 8
MARGIN_BTM = 15
MARGIN_HALFROW = 7

NET_WIDTH = PLUGIN_WIDTH - MARGIN_LFT*2

### Functions
def convertLinesToString(errorLines, missingGlyphs, missingGlyphsMode):
    report = ''
    for indexErrorLine, eachErrorLine in enumerate(errorLines[:-1]):
        if isinstance(eachErrorLine, types.StringType) is True:
            report += eachErrorLine + '\n'

        else:   # list
            if indexErrorLine != 1:
                report += '\n'

            for eachSubErrorLine in eachErrorLine:
                report += eachSubErrorLine + '\n'

    if missingGlyphsMode is True and missingGlyphs:
        report += '\nThe following glyphs are missing: %s\n' % ', '.join(missingGlyphs)

    report += errorLines[-1]
    report += '\n\n'
    return report


### Classes
class TestMetrics(BaseWindowController):

    testOptions = ['Complete report', 'Vertical alignments', 'Accented letters',
                   'Interpunction', 'Figures', 'Dnom Inf Num Sup', 'Fractions',
                   'Flipped Margins', 'LC ligatures', 'UC ligatures',
                   'LC extra', 'UC extra']

    testOptionsAbbr = ['completeReport', 'verticalAlignments', 'accented',
                       'interpunction', 'figures', 'dnomInfNumSup', 'fractions',
                       'flippedMargins', 'LCliga', 'UCliga', 'LCextra', 'UCextra']

    testFunctions = {'Complete report': [checkVerticalExtremes, checkAccented, checkInterpunction, checkFigures, checkDnomNumrSubsSups, checkFractions, checkLCligatures, checkUCligatures, checkLCextra, checkUCextra, checkFlippedMargins],
                     'Vertical alignments': [checkVerticalExtremes],
                     'Accented letters': [checkAccented],
                     'Interpunction': [checkInterpunction],
                     'Figures': [checkFigures],
                     'Dnom Inf Num Sup': [checkDnomNumrSubsSups],
                     'Fractions': [checkFractions],
                     'Flipped Margins': [checkFlippedMargins],
                     'LC ligatures': [checkLCligatures],
                     'UC ligatures': [checkUCligatures],
                     'LC extra': [checkLCextra],
                     'UC extra': [checkUCextra]}

    chosenTest = testOptions[0]

    showMissingGlyph = False
    fontOptions = None
    chosenFont = None

    def __init__(self):

        # load data
        self.fontOptions = AllFonts()
        if self.fontOptions:
            self.chosenFont = self.fontOptions[0]

        # init win
        self.w = FloatingWindow((0,0, PLUGIN_WIDTH, PLUGIN_HEIGHT),
                                "Metrics Tester")

        # target pop up
        jumpingY = MARGIN_TOP
        self.w.targetPopUp = PopUpButton((MARGIN_LFT, jumpingY, NET_WIDTH, vanillaControlsSize['PopUpButtonRegularHeight']),
                                           ['%s %s' % (font.info.familyName, font.info.styleName) for font in self.fontOptions],
                                           callback=self.targetPopUpCallback)

        # test choice
        jumpingY += MARGIN_HALFROW + vanillaControlsSize['PopUpButtonRegularHeight']
        self.w.testChoice = PopUpButton((MARGIN_LFT, jumpingY, NET_WIDTH, vanillaControlsSize['PopUpButtonRegularHeight']),
                                          self.testOptions,
                                          callback=self.testChoiceCallback)

        # separation line
        jumpingY += vanillaControlsSize['PopUpButtonRegularHeight'] + MARGIN_HALFROW
        # self.w.separationLine = HorizontalLine((MARGIN_LFT, jumpingY, NET_WIDTH, 1))

        # jumpingY += RADIO_GROUP_HEIGHT + MARGIN_ROW
        self.w.missingGlyphCheck = CheckBox((MARGIN_LFT, jumpingY, NET_WIDTH, vanillaControlsSize['CheckBoxRegularHeight']),
                                              'Show missing glyphs',
                                              callback=self.missingGlyphCheckCallback)

        jumpingY += vanillaControlsSize['CheckBoxRegularHeight'] + MARGIN_ROW
        self.w.runButton = Button((MARGIN_LFT, jumpingY, NET_WIDTH, vanillaControlsSize['ButtonRegularHeight']),
                                    "Run Tests",
                                    callback=self.runButtonCallback)

        # adjust height
        jumpingY += vanillaControlsSize['ButtonRegularHeight'] + MARGIN_BTM
        self.w.setPosSize((0,0, PLUGIN_WIDTH, jumpingY))

        # observers
        addObserver(self, "updateFontList", "fontWillClose")
        addObserver(self, "updateFontList", "fontDidOpen")
        addObserver(self, "updateFontList", "newFontDidOpen")
        self.setUpBaseWindowBehavior()

        # open win
        self.w.open()

    def windowCloseCallback(self, sender):
        removeObserver(self, "fontWillClose")
        removeObserver(self, "fontDidOpen")
        removeObserver(self, "newFontDidOpen")
        super(TestMetrics, self).windowCloseCallback(sender)

    def updateFontList(self, sender):
        self.fontOptions = AllFonts()
        self.w.targetPopUp.setItems(['%s %s' % (font.info.familyName, font.info.styleName) for font in self.fontOptions])

        if self.fontOptions:
            self.chosenFont = self.fontOptions
        else:
            self.chosenFont = None

    def targetPopUpCallback(self, sender):
        self.chosenFont = self.fontOptions[sender.get()]
        assert isinstance(self.chosenFont, RFont), '%r is not a RFont instance' % self.chosenFont

    def testChoiceCallback(self, sender):
        self.chosenTest = self.testOptions[sender.get()]

    def missingGlyphCheckCallback(self, sender):
        self.showMissingGlyph = bool(sender.get())

    def runButtonCallback(self, sender):

        testsToRun = self.testFunctions[self.chosenTest]
        rightNow = datetime.now()
        reportFile = open(PutFile('Choose where to save the report',
                          '%s%s%s_%s_%s.txt' % (rightNow.year, rightNow.month, rightNow.day,
                          os.path.basename(self.chosenFont.path)[:-4],
                          self.testOptionsAbbr[self.testOptions.index(self.chosenTest)])),
                          'w')

        # progressWindow = self.startProgress('Running Tests')
        for eachFunc in testsToRun:
            errorLines, missingGlyphs = eachFunc(self.chosenFont)
            report = convertLinesToString(errorLines, missingGlyphs, self.showMissingGlyph)
            reportFile.write(report)
        reportFile.close()
        # progressWindow.close()

### Instructions
if __name__ == '__main__':
    mt = TestMetrics()