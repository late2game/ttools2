#!/usr/bin/env python
# -*- coding: utf-8 -*-

################
# Test Metrics #
################

### Modules
# standard
import os
import types
import csv
from datetime import datetime
from robofab.interface.all.dialogs import PutFile
from mojo.events import addObserver, removeObserver
from vanilla import Window, PopUpButton, HorizontalLine
from vanilla import RadioGroup, TextBox, CheckBox, Button
from defconAppKit.windows.baseWindow import BaseWindowController

# custom
import testFunctions
reload(testFunctions)
from testFunctions import checkVerticalExtremes, checkAccented
from testFunctions import checkInterpunction, checkFigures
from testFunctions import checkDnomInfNumSup, checkFractions
from testFunctions import checkLCligatures, checkUCligatures
from testFunctions import checkLCextra, checkUCextra

import userInterfaceValues
reload(userInterfaceValues)
from userInterfaceValues import vanillaControlsSize

### Constants
RADIO_GROUP_HEIGHT = 40
NAMES_TABLE_PATH = 'resources/old_vs_new_names.csv'

PLUGIN_WIDTH = 300
PLUGIN_HEIGHT = 600

MARGIN_LFT = 15
MARGIN_TOP = 15
MARGIN_ROW = 15
MARGIN_BTM = 20
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
class MetricsTester(BaseWindowController):

    testOptions = ['Complete report', 'Vertical alignments', 'Accented letters',
                   'Interpunction', 'Figures', 'Dnom Inf Num Sup', 'Fractions',
                   'LC ligatures', 'UC ligatures', 'LC extra', 'UC extra']

    testOptionsAbbr = ['completeReport', 'verticalAlignments', 'accented',
                       'interpunction', 'figures', 'dnomInfNumSup', 'fractions',
                       'LCliga', 'UCliga', 'LCextra', 'UCextra']

    testFunctions = {'Complete report': [checkVerticalExtremes, checkAccented, checkInterpunction, checkFigures, checkDnomInfNumSup, checkFractions, checkLCligatures, checkUCligatures, checkLCextra, checkUCextra],
                     'Vertical alignments': [checkVerticalExtremes],
                     'Accented letters': [checkAccented],
                     'Interpunction': [checkInterpunction],
                     'Figures': [checkFigures],
                     'Dnom Inf Num Sup': [checkDnomInfNumSup],
                     'Fractions': [checkFractions],
                     'LC ligatures': [checkLCligatures],
                     'UC ligatures': [checkUCligatures],
                     'LC extra': [checkLCextra],
                     'UC extra': [checkUCextra]}

    chosenTest = testOptions[0]

    nameSchemeOptions = ['new', 'old']
    nameScheme = nameSchemeOptions[0]

    showMissingGlyph = False

    fontOptions = None
    chosenFont = None

    def __init__(self):

        # load data
        self.readNameTable()
        self.fontOptions = AllFonts()
        if self.fontOptions:
            self.chosenFont = self.fontOptions[0]

        # init win
        self.w = Window((0,0, PLUGIN_WIDTH, PLUGIN_HEIGHT),
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
        self.w.separationLine = HorizontalLine((MARGIN_LFT, jumpingY, NET_WIDTH, 1))

        # which name scheme
        jumpingY += 1 + MARGIN_ROW
        self.w.nameRadio = RadioGroup((MARGIN_LFT, jumpingY, NET_WIDTH, RADIO_GROUP_HEIGHT),
                                        ['%s names' % name for name in self.nameSchemeOptions],
                                        callback=self.nameRadioCallback)
        self.w.nameRadio.set(0)

        jumpingY += RADIO_GROUP_HEIGHT + MARGIN_ROW
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
        self.w.bind("close", self.closing)

        # open win
        self.w.open()


    def closing(self, sender):
        removeObserver(self, "fontWillClose")
        removeObserver(self, "fontDidOpen")
        removeObserver(self, "newFontDidOpen")

    def updateFontList(self, sender):
        self.fontOptions = AllFonts()
        self.w.targetPopUp.setItems(['%s %s' % (font.info.familyName, font.info.styleName) for font in self.fontOptions])

        if self.fontOptions:
            self.chosenFont = self.fontOptions
        else:
            self.chosenFont = None

    def readNameTable(self):
        namesTableFile = open(NAMES_TABLE_PATH, 'rb')
        namesTableReader = csv.reader(namesTableFile, delimiter='\t', quotechar='|')
        self.namesDict = {old: new for (new, old) in namesTableReader}

    def targetPopUpCallback(self, sender):
        self.chosenFont = self.fontOptions[sender.get()]
        assert isinstance(self.chosenFont, RFont), '%r is not a RFont instance' % self.chosenFont

    def testChoiceCallback(self, sender):
        self.chosenTest = self.testOptions[sender.get()]

    def nameRadioCallback(self, sender):
        self.nameScheme = self.nameSchemeOptions[sender.get()]

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
            errorLines, missingGlyphs = eachFunc(self.chosenFont, self.nameScheme)
            report = convertLinesToString(errorLines, missingGlyphs, self.showMissingGlyph)
            reportFile.write(report)
        reportFile.close()
        # progressWindow.close()

### Instructions
if __name__ == '__main__':
    mt = MetricsTester()