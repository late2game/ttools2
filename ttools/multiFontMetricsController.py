#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################
# Multi Font Metrics Window #
#############################

### Modules
# standard modules
import os
from math import floor, ceil
import traceback
from types import DictType
from AppKit import NSColor, NSFont, NSCenterTextAlignment
from mojo.UI import MultiLineView, OpenGlyphWindow
from mojo.events import addObserver, removeObserver
from mojo.roboFont import AllFonts, OpenFont
from fontTools.agl import AGL2UV, UV2AGL
from vanilla import Window, Group, EditText, CheckBox
from vanilla import PopUpButton, ComboBox, TextBox
from vanilla import HorizontalLine, SquareButton
from vanilla.dialogs import message
from defconAppKit.tools.textSplitter import splitText
from robofab.world import RFont

# custom modules
import miscFunctions
reload(miscFunctions)
from miscFunctions import catchFilesAndFolders

import userInterfaceValues
reload(userInterfaceValues)
from userInterfaceValues import vanillaControlsSize

### Constants
LIGHT_YELLOW = (255./255, 248./255, 216./255, 1)

SPACING_COL_WIDTH = 74
SPACING_COL_MARGIN = 2
MARGIN_LFT = 15
MARGIN_RGT = 15
MARGIN_TOP = 15
MARGIN_COL = 10
MARGIN_ROW = 15
MARGIN_BTM = 20
MARGIN_HALFROW = 7

NOT_DEF_GLYPH = OpenFont(os.path.join(os.path.dirname(__file__), 'resources', 'notdef.ufo'), showUI=False)['.notdef']

### Functions and classes
def convertLineToPseudoUnicode(glyphNamesLine):
    pseudoUniString = u''
    for eachGlyphName in glyphNamesLine:
        if eachGlyphName in AGL2UV:
            pseudoUniString += unichr(AGL2UV[eachGlyphName])
        else:
            pseudoUniString += '\\%s ' % eachGlyphName
    return pseudoUniString


class MultiFontMetricsWindow(object):

    # attrs
    textModeOptions = ['Loaded Strings', 'Typewriter']
    textMode = textModeOptions[0]

    selectedGlyph = None
    subscribedGlyph = None

    fontsDB = None
    unicodeMinimum = {}

    fontOrder = None
    glyphNamesToDisplay = []

    showMetrics = False
    applyKerning = False
    multiLineOptions = {}

    bodySizeOptions = [10, 11, 12, 13, 18, 24, 30, 36, 48, 60, 72,
                       144, 216, 360]
    lineHeightOptions = range(0, 301, 10)

    bodySize = bodySizeOptions[10]
    lineHeight = lineHeightOptions[0]

    folderPath = os.path.join(os.path.dirname(__file__), 'resources', 'spacingTexts')
    fontsAmountOptions = range(1, 9)

    def __init__(self):

        # ui vars
        originLeft = 0
        originRight = 0
        width = 800
        height = 600

        netWidth = width - MARGIN_LFT - MARGIN_RGT
        self.optionsColWidth = 150

        jumpingY = MARGIN_TOP

        # load edit text
        self.editTexts = {}
        self.collectEditTexts()
        self.editTextSortedKeys = self.editTexts.keys().sort()

        # let's see if there are opened fonts (fontDB, ctrlFontsList, fontOrder)
        self.buildFontsData()

        # defining plugin window
        self.win = Window((originLeft, originRight, width, height),
                          "Multi Font Metrics Window",
                          minSize=(800, 400))

        self.win.switchButton = PopUpButton((MARGIN_LFT, jumpingY, netWidth*.2, vanillaControlsSize['PopUpButtonRegularHeight']),
                                            self.textModeOptions,
                                            sizeStyle='regular',
                                            callback=self.switchButtonCallback)

        # free text
        textCtrlX = MARGIN_LFT+MARGIN_COL+netWidth*.2
        self.win.typewriterCtrl = Typewriter((textCtrlX, jumpingY, -(self.optionsColWidth+MARGIN_COL+MARGIN_RGT), vanillaControlsSize['EditTextRegularHeight']),
                                             self.unicodeMinimum,
                                             callback=self.typewriterCtrlCallback)
        self.win.typewriterCtrl.show(False)
        
        # strings ctrls
        self.win.textStringsControls = TextStringsControls((textCtrlX, jumpingY, -(self.optionsColWidth+MARGIN_COL+MARGIN_RGT), vanillaControlsSize['PopUpButtonRegularHeight']+1),
                                                           self.editTexts,
                                                           callback=self.textStringsControlsCallback)
        self.stringDisplayMode, self.glyphNamesToDisplay = self.win.textStringsControls.get()

        # multi line
        jumpingY += vanillaControlsSize['ButtonRegularHeight'] + MARGIN_ROW
        self.spacingMatrixHeight = vanillaControlsSize['EditTextSmallHeight']+len(self.fontOrder)*vanillaControlsSize['EditTextSmallHeight']*2

        self.multiLineOptions = {
            'Show Kerning': self.applyKerning,
            'Center': False,
            'Show Space Matrix': False,
            'Single Line': False,
            'displayMode': u'Multi Line',
            'Stroke': False,
            'xHeight Cut': False,
            'Upside Down': False,
            'Beam': False,
            'Water Fall': False,
            'Inverse': False,
            'Show Template Glyphs': True,
            'Multi Line': True,
            'Right to Left': False,
            'Show Metrics': self.showMetrics,
            'Show Control glyphs': True,
            'Fill': True,
            'Left to Right': True}
        self.win.lineView = MultiLineView((MARGIN_LFT, jumpingY, -(self.optionsColWidth+MARGIN_COL+MARGIN_RGT), -MARGIN_BTM-MARGIN_HALFROW-self.spacingMatrixHeight),
                                          pointSize=self.bodySize,
                                          lineHeight=self.lineHeight,
                                          doubleClickCallback=self.lineViewDoubleClickCallback,
                                          selectionCallback=self.lineViewSelectionCallback,
                                          bordered=True,
                                          # applyKerning=True,
                                          applyKerning=self.applyKerning,
                                          hasHorizontalScroller=False,
                                          hasVerticalScroller=True,
                                          displayOptions=self.multiLineOptions,
                                          updateUserDefaults=False,
                                          menuForEventCallback=None)

        # static options
            # body
        # jumpingY += size.ComboBoxHeight
        self.win.bodyCtrl = ComboBoxWithCaption((-(self.optionsColWidth+MARGIN_RGT), jumpingY, self.optionsColWidth, vanillaControlsSize['ComboBoxSmallHeight']),
                                                'Body Size:',
                                                self.bodySizeOptions,
                                                '%s' % self.bodySize,
                                                sizeStyle='small',
                                                callback=self.bodyCtrlCallback)

            # line height
        jumpingY += vanillaControlsSize['ComboBoxSmallHeight'] + int(MARGIN_HALFROW)
        self.win.lineHgtCtrl = ComboBoxWithCaption((-(self.optionsColWidth+MARGIN_RGT), jumpingY, self.optionsColWidth, vanillaControlsSize['ComboBoxSmallHeight']),
                                                   'Line Height:',
                                                   self.lineHeightOptions,
                                                   '%s' % self.lineHeight,
                                                   sizeStyle='small',
                                                   callback=self.lineHgtCtrlCallback)

            # show metrics
        jumpingY += vanillaControlsSize['ComboBoxSmallHeight'] + MARGIN_ROW
        self.win.showMetricsCheck = CheckBox((-(self.optionsColWidth*.9+MARGIN_RGT), jumpingY, self.optionsColWidth, vanillaControlsSize['ComboBoxSmallHeight']),
                                             "Show Metrics",
                                             value=self.showMetrics,
                                             sizeStyle='small',
                                             callback=self.showMetricsCheckCallback)

            # show kerning checkbox
        jumpingY += vanillaControlsSize['ComboBoxSmallHeight'] + MARGIN_ROW*.3
        self.win.applyKerningCheck = CheckBox((-(self.optionsColWidth*.9+MARGIN_RGT), jumpingY, self.optionsColWidth, vanillaControlsSize['ComboBoxSmallHeight']),
                                         "Show Kerning",
                                         value=self.applyKerning,
                                         sizeStyle='small',
                                         callback=self.applyKerningCheckCallback)

        # separationLine
        jumpingY += vanillaControlsSize['ComboBoxSmallHeight'] + int(MARGIN_HALFROW)
        self.win.separationLine = HorizontalLine((-(self.optionsColWidth+MARGIN_RGT), jumpingY, self.optionsColWidth, 1))

        # dynamic options
            # fonts amount caption
        jumpingY += int(MARGIN_HALFROW)
        self.win.fontsAmountCaption = TextBox((-(self.optionsColWidth+MARGIN_RGT), jumpingY+2, self.optionsColWidth*.35, vanillaControlsSize['TextBoxRegularHeight']),
                                              "Fonts:",
                                              sizeStyle='regular')

            # fonts amount popUp
        self.fontsAmount = len(self.fontsDB)
        self.win.fontsAmountPopUp = PopUpButton((-(self.optionsColWidth+MARGIN_RGT)+self.optionsColWidth*.35, jumpingY, self.optionsColWidth*.4, vanillaControlsSize['PopUpButtonRegularHeight']),
                                                ['%s' % item for item in self.fontsAmountOptions],
                                                sizeStyle='regular',
                                                callback=self.fontsAmountPopUpCallback)
        if self.fontsAmountOptions[-1] >= self.fontsAmount > 0: # if between
            self.win.fontsAmountPopUp.set(self.fontsAmountOptions.index(self.fontsAmount))
            ctrlsToInit = self.fontsAmount

        elif self.fontsAmountOptions[-1] < self.fontsAmount: # if higher
            self.win.fontsAmountPopUp.set(self.fontsAmountOptions.index(self.fontsAmountOptions[-1]))
            ctrlsToInit = self.fontsAmountOptions[-1]
    
        else: # if none
            self.win.fontsAmountPopUp.set(self.fontsAmountOptions.index(1))
            ctrlsToInit = 1

        for eachI in range(ctrlsToInit):
            jumpingY += vanillaControlsSize['PopUpButtonRegularHeight'] + int(MARGIN_HALFROW)
            fontCtrl = PopUpWithCaption((-(self.optionsColWidth+MARGIN_RGT), jumpingY+2, self.optionsColWidth, vanillaControlsSize['PopUpButtonRegularHeight']+1),
                                                    eachI,
                                                    self.fontsDB,
                                                    self.ctrlFontsList,
                                                    callback=self.fontCtrlCallback)
            fontCtrl.set(eachI)
            setattr(self.win, '%#02d' % eachI, fontCtrl)

        self.PopUpWithCaptionY = jumpingY

        # edit metrics
        spacingMatrixWidth = SPACING_COL_WIDTH*len(self.glyphNamesToDisplay)
        self.win.spacingMatrix = SpacingMatrix((MARGIN_RGT, -(MARGIN_HALFROW+self.spacingMatrixHeight), -(self.optionsColWidth+MARGIN_COL+MARGIN_RGT), self.spacingMatrixHeight),
                                               self.glyphNamesToDisplay,
                                               self.fontOrder,
                                               callback=self.spacingMatrixCallback)

        # add observer
        addObserver(self, 'newFontOpened', "newFontDidOpen")
        addObserver(self, 'addFont', "fontDidOpen")
        addObserver(self, 'removeFont', "fontWillClose")
        self.win.bind("close", self.closingPlugin)

        # lit up!
        self.updateSubscriptions()
        self.updateLineView()
        self.win.open()

    # defcon observers (glyph obj)
    def updateSubscriptions(self):
        self.unsubscribeGlyphs()

        # subscribe
        self.subscribedGlyph = []
        for eachFont in self.fontOrder:
            for eachGlyphName in self.glyphNamesToDisplay:
                if eachFont.has_key(eachGlyphName):
                    eachGlyph = eachFont[eachGlyphName]
                    if eachGlyph not in self.subscribedGlyph: # you can't subscribe a glyph twice
                        eachGlyph.addObserver(self, "glyphChangedCallback", "Glyph.Changed")
                        self.subscribedGlyph.append(eachGlyph)

    def unsubscribeGlyphs(self):
        if self.subscribedGlyph:
            for eachGlyph in self.subscribedGlyph:
                eachGlyph.removeObserver(self, "Glyph.Changed")

    def glyphChangedCallback(self, notification):
        self.updateLineView()

    # observers funcs
    def newFontOpened(self, notification):
        message('The MultiFont Metrics Window works only with saved font, please save the new font and re-open the plugin')
        self.win.close()

    def addFont(self, notification):
        fontToAdd = notification['font']
        self.fontsDB[fontToAdd.path] = fontToAdd
        self.ctrlFontsList = ['%s %s' % (keyValue[1].info.familyName, keyValue[1].info.styleName) for keyValue in self.fontsDB.items()]
        self.updateFontsCtrl()

    def spacingMatrixCallback(self, sender):
        self.win.lineView.update()
        self.win.spacingMatrix.update(self.glyphNamesToDisplay, self.fontOrder) # text, fontOrder

        # color the selected glyph in the spacing matrix, if any selected (same code from line view callback, they should be collected somewhere)
        if self.win.lineView.getSelectedGlyph() is not None:

            if self.win.lineView.getSelectedGlyph() != self.selectedGlyph and self.selectedGlyph is not None:
                self.colorSelectedGlyph(NSColor.blackColor())

            doodleGlyph = self.win.lineView.getSelectedGlyph()
            doodleFont = doodleGlyph.getParent()
            self.selectedGlyph = self.fontsDB['%s' % doodleFont.path][doodleGlyph.name]
            self.colorSelectedGlyph(NSColor.redColor())
        else:
            if self.selectedGlyph is not None:
                self.colorSelectedGlyph(NSColor.blackColor())
                self.selectedGlyph = None

    def removeFont(self, notification):
        fontToDelete = notification['font']
        self.fontOrder = [item for item in self.fontOrder if item != fontToDelete]
        self.updateUnicodeMinimum()
        self.adjustSpacingMatrixHeight()
        self.fontsDB.pop(fontToDelete.path)
        self.ctrlFontsList = ['%s %s' % (keyValue[1].info.familyName, keyValue[1].info.styleName) for keyValue in self.fontsDB.items()]
        self.updateSubscriptions()
        self.updateFontsCtrl()
        self.updateLineView()

    # other funcs
    def adjustSpacingMatrixHeight(self):
        self.spacingMatrixHeight = vanillaControlsSize['EditTextSmallHeight']+2+len(self.fontOrder)*vanillaControlsSize['EditTextSmallHeight']*2

        lineViewPosSize = self.win.lineView.getPosSize()
        self.win.lineView.setPosSize((lineViewPosSize[0], lineViewPosSize[1], lineViewPosSize[2], -MARGIN_BTM-MARGIN_HALFROW-self.spacingMatrixHeight))

        spacingMatrixPosSize = self.win.spacingMatrix.getPosSize()
        self.win.spacingMatrix.height = self.spacingMatrixHeight   # dirty hack
        self.win.spacingMatrix.setPosSize((spacingMatrixPosSize[0], -(MARGIN_HALFROW+self.spacingMatrixHeight), spacingMatrixPosSize[2], self.spacingMatrixHeight))

    def closingPlugin(self, sender):
        self.unsubscribeGlyphs()
        removeObserver(self, "newFontDidOpen")
        removeObserver(self, "fontDidOpen")
        removeObserver(self, "fontWillClose")

    def updateFontsCtrl(self):
        if hasattr(self, 'win') is True:
            for eachI in range(self.fontsAmount):
                if eachI >= len(self.fontOrder):
                    delattr(self.win, '%#02d' % eachI)
                    self.PopUpWithCaptionY -= vanillaControlsSize['PopUpButtonRegularHeight'] + int(MARGIN_HALFROW)
                else:
                    ctrl = getattr(self.win, '%#02d' % eachI)
                    ctrl.updateFontsNames(self.ctrlFontsList)
                    ctrl.set(self.ctrlFontsList.index('%s %s' % (self.fontOrder[eachI].info.familyName, self.fontOrder[eachI].info.styleName)))
        self.fontsAmount = len(self.fontOrder)
        self.win.fontsAmountPopUp.set(self.fontsAmountOptions.index(self.fontsAmount))

    def updateUnicodeMinimum(self):
        # collect everything
        allUnicodeData = {}
        for eachFont in self.fontOrder:
            for eachKey, eachValue in eachFont.naked().unicodeData.items():
                if eachKey not in allUnicodeData:
                    allUnicodeData[eachKey] = eachValue

        # filter
        self.unicodeMinimum = {}
        for eachKey, eachValue in allUnicodeData.items():
            for eachFont in self.fontOrder:
                if eachKey not in eachFont.naked().unicodeData:
                    # print '[WARNING] %s unicode value is not shared across the fonts' % eachKey
                    break
            self.unicodeMinimum[eachKey] = eachValue

    def buildFontsData(self):
        self.fontsDB = {}
        openedFonts = AllFonts()
        if openedFonts:
            for eachFont in openedFonts:
                self.fontsDB['%s' % eachFont.path] = eachFont
        self.fontOrder = [keyValue[1] for keyValue in self.fontsDB.items()]
        self.updateUnicodeMinimum()
        self.updateSubscriptions()

        # update fonts list
        self.ctrlFontsList = ['%s %s' % (keyValue[1].info.familyName, keyValue[1].info.styleName) for keyValue in self.fontsDB.items()]

    def collectEditTexts(self):
        editTextsPaths = catchFilesAndFolders(self.folderPath, '.txt')
        for eachPath in editTextsPaths:
            editTextRows = [item.replace('\n', '') for item in open(eachPath, 'r').readlines()]
            self.editTexts[os.path.basename(eachPath)[:-4]] = editTextRows

    def updateLineView(self):
        try:
            displayedGlyphs = []
            if self.stringDisplayMode == 'Waterfall':
                for indexFont, eachFont in enumerate(self.fontOrder):
                    assert isinstance(eachFont, RFont), 'object in self.fontOrder not a RFont'
                    if indexFont != 0:
                        newLineGlyph = self.win.lineView.createNewLineGlyph()
                        displayedGlyphs.append(newLineGlyph)

                    for eachGlyphName in self.glyphNamesToDisplay:
                        if eachFont.has_key(eachGlyphName):
                            displayedGlyphs.append(eachFont[eachGlyphName])
                        else:
                            if eachFont.has_key('.notdef'):
                                displayedGlyphs.append(eachFont['.notdef'])
                            else:
                                displayedGlyphs.append(NOT_DEF_GLYPH)

            else:
                for eachGlyphName in self.glyphNamesToDisplay:
                    for indexFont, eachFont in enumerate(self.fontOrder):
                        assert isinstance(eachFont, RFont), 'object in self.fontOrder not a RFont'
                        if eachFont.has_key(eachGlyphName):
                            displayedGlyphs.append(eachFont[eachGlyphName])
                        else:
                            if eachFont.has_key('.notdef'):
                                displayedGlyphs.append(eachFont['.notdef'])
                            else:
                                displayedGlyphs.append(NOT_DEF_GLYPH)

            self.win.lineView.set(displayedGlyphs)

            # add kerning if needed
            if self.applyKerning is True:
                glyphRecords = self.win.lineView.contentView().getGlyphRecords()

                leftRecord = glyphRecords[0]
                rightRecord = glyphRecords[1]

                for indexRecords, eachGlyphRecord in enumerate(glyphRecords):
                    if indexRecords == len(glyphRecords) and indexRecords == len(0): # avoid first and last
                        continue

                    leftRecord = glyphRecords[indexRecords-1]
                    rightRecord = glyphRecords[indexRecords]
                    leftGlyph = leftRecord.glyph
                    rightGlyph = rightRecord.glyph

                    # if they come from the same font...
                    leftFont = leftGlyph.getParent()
                    rightFont = rightGlyph.getParent()
                    if leftFont is rightFont:
                        if (leftGlyph.name, rightGlyph.name) in leftFont.flatKerning:
                            leftRecord.xAdvance += leftFont.flatKerning[(leftGlyph.name, rightGlyph.name)]

            # update spacing matrix
            self.win.spacingMatrix.update(self.glyphNamesToDisplay, self.fontOrder)

        except Exception, error:
            print traceback.format_exc()

    ### callback
    def switchButtonCallback(self, sender):
        assert self.textMode in self.textModeOptions
        self.textMode = self.textModeOptions[sender.get()]

        if self.win.typewriterCtrl.title == self.textMode:
            self.win.typewriterCtrl.show(True)
            self.stringDisplayMode, self.glyphNamesToDisplay = 'Waterfall', self.win.typewriterCtrl.get()
            self.win.textStringsControls.show(False)
        else:
            self.win.textStringsControls.show(True)
            self.stringDisplayMode, self.glyphNamesToDisplay = self.win.textStringsControls.get()
            print self.stringDisplayMode, self.glyphNamesToDisplay
            self.win.typewriterCtrl.show(False)

        self.updateLineView()

    def typewriterCtrlCallback(self, sender):
        self.stringDisplayMode, self.glyphNamesToDisplay = 'Waterfall', sender.get()
        self.updateLineView()

    def textStringsControlsCallback(self, sender):
        self.stringDisplayMode, self.glyphNamesToDisplay = sender.get()
        self.updateLineView()

    def bodyCtrlCallback(self, sender):
        assert sender.get().isdigit() is True
        self.bodySize = int(sender.get())
        self.win.lineView.setPointSize(self.bodySize)

    def lineHgtCtrlCallback(self, sender):
        assert sender.get().isdigit() is True
        self.lineHeight = int(sender.get())
        self.win.lineView.setLineHeight(self.lineHeight)

    def lineViewSelectionCallback(self, sender):
        if sender.getSelectedGlyph() is not None:

            if sender.getSelectedGlyph() != self.selectedGlyph and self.selectedGlyph is not None:
                self.colorSelectedGlyph(NSColor.blackColor())

            doodleGlyph = sender.getSelectedGlyph()
            doodleFont = doodleGlyph.getParent()
            self.selectedGlyph = self.fontsDB['%s' % doodleFont.path][doodleGlyph.name]
            self.colorSelectedGlyph(NSColor.redColor())
        else:
            if self.selectedGlyph is not None:
                self.colorSelectedGlyph(NSColor.blackColor())
                self.selectedGlyph = None

    def colorSelectedGlyph(self, whichColor):
        selectedFont = self.selectedGlyph.getParent()
        rowIndexes = [indexItem[0] for indexItem in enumerate(self.fontOrder) if indexItem[1] == selectedFont]
        colIndexes = [indexItem[0] for indexItem in enumerate(self.glyphNamesToDisplay) if indexItem[1] == self.selectedGlyph.name]

        for eachColIndex in colIndexes:
            multiGlyphCtrl = getattr(self.win.spacingMatrix, '%#02d' % eachColIndex)
            for eachRowIndex in rowIndexes:
                singleGlyphCtrl = getattr(multiGlyphCtrl, '%#02d' % eachRowIndex)
                singleGlyphCtrl.colorText(whichColor)

    def lineViewDoubleClickCallback(self, sender):
        doodleGlyph = sender.getSelectedGlyph()
        doodleFont = doodleGlyph.getParent()
        roboGlyph = self.fontsDB['%s' % doodleFont.path][doodleGlyph.name]
        if roboGlyph is not None:
            OpenGlyphWindow(glyph=roboGlyph, newWindow=False)

    def showMetricsCheckCallback(self, sender):
        self.showMetrics = bool(sender.get())
        self.multiLineOptions['Show Metrics'] = self.showMetrics
        self.multiLineOptions['Show Kerning'] = self.showMetrics
        self.win.lineView.setDisplayStates(self.multiLineOptions)

    def applyKerningCheckCallback(self, sender):
        self.applyKerning = bool(sender.get())
        self.updateLineView()

    def fontsAmountPopUpCallback(self, sender):
        # do nothing
        if self.fontsAmountOptions[sender.get()] == self.fontsAmount:
            pass

        # delete extra objects
        elif self.fontsAmountOptions[sender.get()] < self.fontsAmount:
            self.fontOrder = self.fontOrder[0:self.fontsAmountOptions[sender.get()]]
            self.updateUnicodeMinimum()
            self.adjustSpacingMatrixHeight()
            self.updateSubscriptions()
            for eachI in reversed(range(self.fontsAmountOptions[sender.get()], self.fontsAmount)):
                self.PopUpWithCaptionY -= vanillaControlsSize['PopUpButtonRegularHeight'] + int(MARGIN_HALFROW)
                delattr(self.win, '%#02d' % eachI)
        
        # add what's needed
        else:
            for eachI in range(self.fontsAmount, self.fontsAmountOptions[sender.get()]):
                self.PopUpWithCaptionY += vanillaControlsSize['PopUpButtonRegularHeight'] + int(MARGIN_HALFROW)
                fontCtrl = PopUpWithCaption((-(self.optionsColWidth+MARGIN_RGT), self.PopUpWithCaptionY, self.optionsColWidth, vanillaControlsSize['PopUpButtonRegularHeight']+1),
                                                        eachI,
                                                        self.fontsDB,
                                                        self.ctrlFontsList,
                                                        callback=self.fontCtrlCallback)
                setattr(self.win, '%#02d' % eachI, fontCtrl)

                if len(self.fontOrder) > 0:
                    self.fontOrder.append(self.fontOrder[0])
                    self.adjustSpacingMatrixHeight()

        self.fontsAmount = self.fontsAmountOptions[sender.get()]
        self.updateLineView()

    def fontCtrlCallback(self, sender):
        fontIndex, fontName = sender.get()
        self.fontOrder[int(fontIndex)] = fontName
        self.updateLineView()


class ComboBoxWithCaption(Group):

    # attrs
    choice = None

    def __init__(self, posSize, title, options, chosenOption, sizeStyle, callback):
        Group.__init__(self, posSize)
        self.callback = callback
        self.options = options
        width = posSize[2]
        height = posSize[3]

        self.caption = TextBox((0, 2, width*.5, height),
                               title,
                               sizeStyle=sizeStyle,
                               alignment='right')

        self.combo = ComboBox((width*.5, 0, width*.5, height),
                              options,
                              continuous=False,
                              sizeStyle=sizeStyle,
                              callback=self.comboCallback)
        self.combo.set(chosenOption)

    def get(self):
        return self.choice

    def comboCallback(self, sender):
        self.choice = str(sender.get())
        self.callback(self)


class PopUpWithCaption(Group):

    def __init__(self, posSize, index, fontsDB, ctrlFontsList, callback):
        Group.__init__(self, posSize)
        width = posSize[2]
        height = posSize[3]
        self.callback = callback
        self.fontsDB = fontsDB
        self.ctrlFontsList = ctrlFontsList
        self.chosenFont = self.fontsDB[self.fontsDB.keys()[0]]

        self.caption = TextBox((0, 1, width*.15, height),
                               '%s:' % (index+1))

        jumpingX = width*.15
        self.popUp = PopUpButton((jumpingX, 0, width*.85, height),
                                 self.ctrlFontsList,
                                 callback=self.popUpButtonCallback)


    def get(self):
        index = int(self.caption.get().replace(':', ''))-1
        return index, self.chosenFont

    def set(self, index):
        self.popUp.set(index)
        self.chosenFont = self.fontsDB[self.fontsDB.keys()[index]]

    def updateFontsNames(self, ctrlFontsList):
        self.ctrlFontsList = ctrlFontsList
        self.popUp.setItems(self.ctrlFontsList)

    def popUpButtonCallback(self, sender):
        self.chosenFont = self.fontsDB[self.fontsDB.keys()[sender.get()]]
        self.callback(self)


class Typewriter(Group):

    # attrs
    glyphNamesToDisplay = []
    title = 'Typewriter'

    leftGlyphNames = []
    centerGlyphNames = []
    rightGlyphNames = []
    typewriterGlyphNames = []

    siblingsWidth = 40

    def __init__(self, posSize, unicodeMinimum, callback):
        Group.__init__(self, posSize)
        self.callback = callback
        self.unicodeMinimum = unicodeMinimum
        ctrlWidth = posSize[2]

        self.leftSiblingEdit = EditText((0, 0, self.siblingsWidth, vanillaControlsSize['EditTextRegularHeight']),
                                        callback=self.leftSiblingEditCallback)

        self.typewriterEdit = EditText((self.siblingsWidth+MARGIN_COL, 0, -(self.siblingsWidth+MARGIN_COL), vanillaControlsSize['EditTextRegularHeight']),
                                       callback=self.typewriterEditCallback)

        self.rightSiblingEdit = EditText((-self.siblingsWidth, 0, self.siblingsWidth, vanillaControlsSize['EditTextRegularHeight']),
                                         callback=self.rightSiblingEditCallback)

    def leftSiblingEditCallback(self, sender):
        if sender.get() is not None:
            self.leftGlyphNames = splitText(sender.get(), self.unicodeMinimum)
        else:
            self.leftGlyphNames = []
        self.callback(self)

    def typewriterEditCallback(self, sender):
        if sender.get() is not None:
            self.centerGlyphNames = splitText(sender.get(), self.unicodeMinimum)
        else:
            self.centerGlyphNames = []
        self.callback(self)

    def rightSiblingEditCallback(self, sender):
        if sender.get() is not None:
            self.rightGlyphNames = splitText(sender.get(), self.unicodeMinimum)
        else:
            self.rightGlyphNames = []
        self.callback(self)

    def setUnicodeMinimum(self, unicodeMinimum):
        assert isinstance(unicodeMinimum, DictType), 'unicode minimum is not a dict'
        self.unicodeMinimum = unicodeMinimum

    def get(self):
        self.typewriterGlyphNames = []
        for eachGlyphName in self.centerGlyphNames:
            self.typewriterGlyphNames += self.leftGlyphNames
            self.typewriterGlyphNames += [eachGlyphName]
            self.typewriterGlyphNames += self.rightGlyphNames
        return self.typewriterGlyphNames

    def show(self, onOff):
        assert onOff in [True, False]
        self.leftSiblingEdit.show(onOff)
        self.typewriterEdit.show(onOff)
        self.rightSiblingEdit.show(onOff)


class TextStringsControls(Group):

    # attrs
    stringOptions = ('Waterfall', 'Shuffled')
    title = 'Loaded Strings'

    def __init__(self, posSize, editTexts, callback):
        Group.__init__(self, posSize)
        self.callback = callback

        self.editTexts = editTexts
        self.editTextSortedKeys = self.editTexts.keys()
        self.editTextSortedKeys.sort()

        self.chosenStringOption = self.stringOptions[0]

        self.chosenTxt = self.editTexts[self.editTextSortedKeys[0]]
        self.stringIndex = 0
        self.chosenLine = self.chosenTxt[self.stringIndex].split(' ')

        textModePopUpWidth = 120
        self.textModePopUp = PopUpButton((1, 0, textModePopUpWidth, vanillaControlsSize['PopUpButtonRegularHeight']),
                                         self.stringOptions,
                                         callback=self.textModePopUpCallback)

        jumpingX = textModePopUpWidth + MARGIN_COL
        textFilePopUpWidth = 180
        self.textFilePopUp = PopUpButton((jumpingX, 0, textFilePopUpWidth, vanillaControlsSize['PopUpButtonRegularHeight']),
                                         self.editTextSortedKeys,
                                         callback=self.textFilePopUpCallback)

        jumpingX += textFilePopUpWidth + MARGIN_COL
        textLinePopUpWidth = 60
        self.textLinePopUp = PopUpButton((jumpingX, 0, textLinePopUpWidth, vanillaControlsSize['PopUpButtonRegularHeight']),
                                         ['%#02d' % item for item in range(1, len(self.chosenTxt)+1)],
                                         callback=self.textLinePopUpCallback)

        jumpingX += textLinePopUpWidth + MARGIN_COL
        arrowWidth = 30
        self.arrowUp = SquareButton((jumpingX, 0, arrowWidth, vanillaControlsSize['PopUpButtonRegularHeight']),
                                    u'↑',
                                    callback=self.arrowUpCallback)
        self.arrowUp.bind(key='uparrow', modifiers=[])

        jumpingX += arrowWidth + MARGIN_COL
        self.arrowDw = SquareButton((jumpingX, 0, arrowWidth, vanillaControlsSize['PopUpButtonRegularHeight']),
                                    u'↓',
                                    callback=self.arrowDwCallback)
        self.arrowDw.bind(key='downarrow', modifiers=[])

        jumpingX += arrowWidth + MARGIN_COL

        pseudoUniString = convertLineToPseudoUnicode(self.chosenLine)
        self.selectedLine = TextBox((jumpingX, 0, -MARGIN_RGT, vanillaControlsSize['TextBoxRegularHeight']),
                                    pseudoUniString)

    def get(self):
        return self.chosenStringOption, self.chosenLine

    def show(self, onOff):
        assert onOff in [True, False]
        self.textModePopUp.show(onOff)
        self.textFilePopUp.show(onOff)
        self.textLinePopUp.show(onOff)
        self.arrowUp.show(onOff)
        self.arrowDw.show(onOff)
        self.selectedLine.show(onOff)

    def textModePopUpCallback(self, sender):
        self.chosenStringOption = self.stringOptions[sender.get()]
        self.callback(self)

    def textFilePopUpCallback(self, sender):
        self.chosenTxt = self.editTexts[self.editTextSortedKeys[sender.get()]]
        self.stringIndex = 0
        self.chosenLine = self.chosenTxt[self.stringIndex].split(' ')

        self.textLinePopUp.setItems(['%#02d' % item for item in range(1, len(self.chosenTxt)+1)])
        self.selectedLine.set(convertLineToPseudoUnicode(self.chosenLine))
        self.callback(self)

    def textLinePopUpCallback(self, sender):
        self.stringIndex = sender.get()
        self.chosenLine = self.chosenTxt[self.stringIndex].split(' ')
        self.selectedLine.set(convertLineToPseudoUnicode(self.chosenLine))
        self.callback(self)

    def arrowUpCallback(self, sender):
        self.stringIndex -= 1
        if self.stringIndex < 0:
            self.stringIndex = -abs(-self.stringIndex % len(self.chosenTxt))
        else:
            self.stringIndex = self.stringIndex % len(self.chosenTxt)

        self.chosenLine = self.chosenTxt[self.stringIndex].split(' ')
        self.selectedLine.set(convertLineToPseudoUnicode(self.chosenLine))
        self.textLinePopUp.set(self.chosenTxt.index(' '.join(self.chosenLine)))
        self.callback(self)

    def arrowDwCallback(self, sender):
        self.stringIndex += 1
        if self.stringIndex < 0:
            self.stringIndex = -abs(-self.stringIndex % len(self.chosenTxt))
        else:
            self.stringIndex = self.stringIndex % len(self.chosenTxt)

        self.chosenLine = self.chosenTxt[self.stringIndex].split(' ')
        self.selectedLine.set(convertLineToPseudoUnicode(self.chosenLine))
        self.textLinePopUp.set(self.chosenTxt.index(' '.join(self.chosenLine)))
        self.callback(self)


class SpacingMatrix(Group):

    def __init__(self, posSize, glyphNamesToDisplay, fontOrder, callback):
        # Group constructor
        Group.__init__(self, posSize)
        self.glyphNamesToDisplay = glyphNamesToDisplay
        self.fontOrder = fontOrder
        self.callback = callback
        self.left, self.top, self.width, self.height = posSize
        self._addCtrls()

    def _delCtrls(self):
        for indexGlyphName, eachGlyphName in enumerate(self.glyphNamesToDisplay):
            delattr(self, '%#02d' % indexGlyphName)

    def _addCtrls(self):
        jumpingX = 0
        for indexGlyphName, eachGlyphName in enumerate(self.glyphNamesToDisplay):
            mgme = MultiGlyphMetricsEditor((jumpingX, 0, SPACING_COL_WIDTH, self.height),
                                           glyphName=eachGlyphName,
                                           fontOrder=self.fontOrder,
                                           callback=self.callback)
            setattr(self, '%#02d' % indexGlyphName, mgme)
            jumpingX += SPACING_COL_WIDTH+SPACING_COL_MARGIN

    def update(self, glyphNamesToDisplay, fontOrder):
        self._delCtrls()
        self.glyphNamesToDisplay = glyphNamesToDisplay
        self.fontOrder = fontOrder
        self._addCtrls()


class MultiGlyphMetricsEditor(Group):

    def __init__(self, posSize, glyphName, fontOrder, callback):
        # Group constructor
        Group.__init__(self, posSize)
        self.callback = callback

        # attrs
        jumpingY = 0

        # glyph name
        self.glyphNameEdit = CustomEditText((0, jumpingY, SPACING_COL_WIDTH, vanillaControlsSize['EditTextSmallHeight']),
                                      text=glyphName,
                                      callback=None,
                                      continuous=False,
                                      readOnly=True,
                                      sizeStyle='small')
        self.glyphNameEdit.centerAlignment()
        # self.glyphNameEdit.switchToBold()
        jumpingY += vanillaControlsSize['EditTextSmallHeight']

        # single glyph editors
        for indexLine, eachFont in enumerate(fontOrder):

            if eachFont.has_key(glyphName):
                singleGlyph = eachFont[glyphName]
            else:
                singleGlyph = NOT_DEF_GLYPH
            singleGlyphEditor = SingleGlyphMetricsEditor((0, jumpingY, SPACING_COL_WIDTH, vanillaControlsSize['EditTextSmallHeight']*2),
                                                         singleGlyph,
                                                         callback=self.callback)
            if indexLine % 2 == 0:
                singleGlyphEditor.colorBackground(LIGHT_YELLOW)

            jumpingY += vanillaControlsSize['EditTextSmallHeight']*2-2
            setattr(self, '%#02d' % indexLine, singleGlyphEditor)


class CustomEditText(EditText):

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.nst = self.getNSTextField()

    def centerAlignment(self):
        self.nst.setAlignment_(NSCenterTextAlignment)

    def setBackgroundColor(self, color):
        self.nst.setBackgroundColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(*color))

    def setTextColor(self, color):
        self.nst.setTextColor_(color)

    def switchToBold(self):
        self.nst.setFont_(NSFont.boldSystemFontOfSize_(NSFont.systemFontSize()))


class SingleGlyphMetricsEditor(Group):

    def __init__(self, posSize, glyph, callback):
        # Group constructor
        Group.__init__(self, posSize)
        self.callback = callback

        # attrs
        jumpingY = 0
        self.glyph = glyph

        # glyph width
        try:
            glyphWidthRepr = '%d' % self.glyph.width
        except RoboFontError as e:
            glyphWidthRepr = ''

        self.widthEdit = CustomEditText((0, jumpingY, SPACING_COL_WIDTH, vanillaControlsSize['EditTextSmallHeight']),
                                        text=glyphWidthRepr,
                                        callback=self.widthEditCallback,
                                        continuous=False,
                                        readOnly=False,
                                        sizeStyle='small',)
        self.widthEdit.centerAlignment()
        jumpingY += vanillaControlsSize['EditTextSmallHeight']-1

        # left margin
        try:
            leftMarginRepr = '%d' % self.glyph.leftMargin
        except RoboFontError as e:
            leftMarginRepr = ''

        self.leftEdit = CustomEditText((0, jumpingY, ceil(SPACING_COL_WIDTH/2), vanillaControlsSize['EditTextSmallHeight']),
                                       text=leftMarginRepr,
                                       callback=self.leftEditCallback,
                                       continuous=False,
                                       readOnly=False,
                                       sizeStyle='small')
        self.leftEdit.centerAlignment()

        # right margin
        try:
            rightMarginRepr = '%d' % self.glyph.rightMargin
        except RoboFontError as e:
            rightMarginRepr = ''

        self.rightEdit = CustomEditText((floor(SPACING_COL_WIDTH/2), jumpingY, ceil(SPACING_COL_WIDTH/2), vanillaControlsSize['EditTextSmallHeight']),
                                        text=rightMarginRepr,
                                        callback=self.rightEditCallback,
                                        continuous=False,
                                        readOnly=False,
                                        sizeStyle='small')
        self.rightEdit.centerAlignment()

    def colorText(self, color):
        self.widthEdit.setTextColor(color)
        self.leftEdit.setTextColor(color)
        self.rightEdit.setTextColor(color)

    def colorBackground(self, color):
        self.widthEdit.setBackgroundColor((LIGHT_YELLOW))
        self.leftEdit.setBackgroundColor((LIGHT_YELLOW))
        self.rightEdit.setBackgroundColor((LIGHT_YELLOW))

    def widthEditCallback(self, sender):
        try:
            self.glyph.width = int(sender.get())
            self.callback(self)
        except ValueError, error:
            print error
            sender.set('%s' % self.glyph.width)

    def leftEditCallback(self, sender):
        try:
            self.glyph.leftMargin = int(sender.get())
            self.callback(self)
        except ValueError, error:
            print error
            sender.set('%s' % self.glyph.leftMargin)

    def rightEditCallback(self, sender):
        try:
            self.glyph.rightMargin = int(sender.get())
            self.callback(self)
        except ValueError, error:
            print error
            sender.set('%s' % self.glyph.rightMargin)

### Instructions
if __name__ == '__main__':
    mfmw = MultiFontMetricsWindow()
