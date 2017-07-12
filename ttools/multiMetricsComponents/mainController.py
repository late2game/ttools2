#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""here goes the main controller, which controls them all"""

### Modules
# other components

# custom
from ..miscFunctions import catchFilesAndFolders
from ..userInterfaceValues import vanillaControlsSize
from ..uiControllers import FontsOrderController, FONT_ROW_HEIGHT

import topCtrls
reload(topCtrls)
from topCtrls import Typewriter, TextStringsControls

import sidebar
reload(sidebar)
from sidebar import ComboBoxWithCaption

import spacingMatrix
reload(spacingMatrix)
from spacingMatrix import SpacingMatrix

# standard
import os
from math import floor, ceil
import traceback
from AppKit import NSColor, NSFont, NSCenterTextAlignment
from mojo.UI import MultiLineView, OpenGlyphWindow
from mojo.events import addObserver, removeObserver
from mojo.roboFont import AllFonts, OpenFont, RFont
from vanilla import Window, EditText, CheckBox
from vanilla import PopUpButton, HorizontalLine
from vanilla.dialogs import message
from defconAppKit.windows.baseWindow import BaseWindowController

### Constants
LIGHT_YELLOW = (255./255, 248./255, 216./255, 1)

MARGIN_LFT = 15
MARGIN_RGT = 15
MARGIN_TOP = 15
MARGIN_COL = 10
MARGIN_ROW = 15
MARGIN_BTM = 20
MARGIN_HALFROW = 7
RIGHT_COLUMN = 180

RED = (1,0,0)
BLACK = (0,0,0)

TTOOLS_FOLDER = os.path.dirname(os.path.dirname(__file__))
NOT_DEF_GLYPH = OpenFont(os.path.join(TTOOLS_FOLDER, 'resources', 'notdef.ufo'), showUI=False)['.notdef']

# the control factory
class MultiFontMetricsWindow(BaseWindowController):

    # attrs
    textModeOptions = ['Loaded Strings', 'Typewriter']
    textMode = textModeOptions[0]

    selectedGlyph = None
    subscribedGlyph = None

    fontsDB = None
    unicodeMinimum = {}

    fontsOrder = None
    glyphNamesToDisplay = []

    showMetrics = False
    applyKerning = False
    multiLineOptions = {}

    bodySizeOptions = [10, 11, 12, 13, 18, 24, 30, 36, 48, 60, 72,
                       144, 216, 360]
    lineHeightOptions = range(0, 301, 10)

    bodySize = bodySizeOptions[10]
    lineHeight = lineHeightOptions[0]

    folderPath = os.path.join(TTOOLS_FOLDER, 'resources', 'spacingTexts')
    fontsAmountOptions = range(1, 9)

    def __init__(self):
        super(MultiFontMetricsWindow, self).__init__()

        # ui vars
        originLeft = 0
        originRight = 0
        width = 956
        height = 600

        netWidth = width - MARGIN_LFT - MARGIN_RGT
        jumpingY = MARGIN_TOP

        # load edit text
        self.editTexts = {}
        self.collectEditTexts()
        self.editTextSortedKeys = self.editTexts.keys().sort()

        # let's see if there are opened fonts (fontDB, ctrlFontsList, fontsOrder)
        self.loadFontsOrder()
        self.updateUnicodeMinimum()

        # defining plugin windows
        self.w = Window((originLeft, originRight, width, height),
                        "Multi Font Metrics Window",
                        minSize=(800, 400))
        self.w.bind('resize', self.mainWindowResize)

        if not self.fontsOrder:
            # no fonts, no party
            return None

        self.w.switchButton = PopUpButton((MARGIN_LFT, jumpingY, netWidth*.2, vanillaControlsSize['PopUpButtonRegularHeight']),
                                            self.textModeOptions,
                                            sizeStyle='regular',
                                            callback=self.switchButtonCallback)

        # free text
        textCtrlX = MARGIN_LFT+MARGIN_COL+netWidth*.2
        self.w.typewriterCtrl = Typewriter((textCtrlX, jumpingY, -(RIGHT_COLUMN+MARGIN_COL+MARGIN_RGT), vanillaControlsSize['EditTextRegularHeight']),
                                             self.unicodeMinimum,
                                             callback=self.typewriterCtrlCallback)
        self.w.typewriterCtrl.show(False)
        
        # strings ctrls
        self.w.textStringsControls = TextStringsControls((textCtrlX, jumpingY, -(RIGHT_COLUMN+MARGIN_COL+MARGIN_RGT), vanillaControlsSize['PopUpButtonRegularHeight']+1),
                                                           self.editTexts,
                                                           callback=self.textStringsControlsCallback)
        self.stringDisplayMode, self.glyphNamesToDisplay = self.w.textStringsControls.get()

        # multi line
        jumpingY += vanillaControlsSize['ButtonRegularHeight'] + MARGIN_ROW
        
        self.calcSpacingMatrixHeight()
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
        self.w.lineView = MultiLineView((MARGIN_LFT, jumpingY, -(RIGHT_COLUMN+MARGIN_COL+MARGIN_RGT), -MARGIN_BTM-MARGIN_HALFROW-self.spacingMatrixHeight),
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
        self.w.bodyCtrl = ComboBoxWithCaption((-(RIGHT_COLUMN+MARGIN_RGT), jumpingY, RIGHT_COLUMN, vanillaControlsSize['ComboBoxSmallHeight']+1),
                                                'Body Size:',
                                                self.bodySizeOptions,
                                                '%s' % self.bodySize,
                                                sizeStyle='small',
                                                callback=self.bodyCtrlCallback)

            # line height
        jumpingY += vanillaControlsSize['ComboBoxSmallHeight'] + int(MARGIN_HALFROW)
        self.w.lineHgtCtrl = ComboBoxWithCaption((-(RIGHT_COLUMN+MARGIN_RGT), jumpingY, RIGHT_COLUMN, vanillaControlsSize['ComboBoxSmallHeight']+1),
                                                   'Line Height:',
                                                   self.lineHeightOptions,
                                                   '%s' % self.lineHeight,
                                                   sizeStyle='small',
                                                   callback=self.lineHgtCtrlCallback)

            # show metrics
        jumpingY += vanillaControlsSize['ComboBoxSmallHeight'] + MARGIN_ROW
        self.w.showMetricsCheck = CheckBox((-(RIGHT_COLUMN+MARGIN_RGT), jumpingY, RIGHT_COLUMN, vanillaControlsSize['ComboBoxSmallHeight']),
                                             "Show Metrics",
                                             value=self.showMetrics,
                                             sizeStyle='small',
                                             callback=self.showMetricsCheckCallback)

            # show kerning checkbox
        jumpingY += vanillaControlsSize['ComboBoxSmallHeight'] + MARGIN_ROW*.3
        self.w.applyKerningCheck = CheckBox((-(RIGHT_COLUMN+MARGIN_RGT), jumpingY, RIGHT_COLUMN, vanillaControlsSize['ComboBoxSmallHeight']),
                                         "Show Kerning",
                                         value=self.applyKerning,
                                         sizeStyle='small',
                                         callback=self.applyKerningCheckCallback)

        # separationLine
        jumpingY += vanillaControlsSize['ComboBoxSmallHeight'] + int(MARGIN_HALFROW)
        self.w.separationLine = HorizontalLine((-(RIGHT_COLUMN+MARGIN_RGT), jumpingY, RIGHT_COLUMN, 1))

        jumpingY += int(MARGIN_HALFROW)
        fontsOrderControllerHeight = FONT_ROW_HEIGHT*len(self.fontsOrder)+MARGIN_COL
        self.w.fontsOrderController = FontsOrderController((-(RIGHT_COLUMN+MARGIN_RGT), jumpingY, RIGHT_COLUMN, fontsOrderControllerHeight),
                                                           self.fontsOrder,
                                                           callback=self.fontsOrderControllerCallback)

        # edit metrics
        self.w.spacingMatrix = SpacingMatrix((MARGIN_LFT, -(MARGIN_HALFROW+self.spacingMatrixHeight), self.w.getPosSize()[2]-MARGIN_LFT-MARGIN_RGT, self.spacingMatrixHeight),
                                             self.glyphNamesToDisplay,
                                             self.fontsOrder,
                                             callback=self.spacingMatrixCallback)

        # add observer
        addObserver(self, 'newFontOpened', "newFontDidOpen")
        addObserver(self, 'openCloseFontCallback', "fontDidOpen")
        addObserver(self, 'openCloseFontCallback', "fontDidClose")

        # lit up!
        self.updateSubscriptions()
        self.updateLineView()
        self.setUpBaseWindowBehavior()
        self.w.open()

    # defcon observers (glyph obj)
    def updateSubscriptions(self):
        self.unsubscribeGlyphs()

        # subscribe
        self.subscribedGlyph = []
        for eachFont in self.fontsOrder:
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
    def mainWindowResize(self, mainWindow):
        windowWidth = mainWindow.getPosSize()[2]
        self.w.spacingMatrix.adjustSize((windowWidth-MARGIN_LFT-MARGIN_RGT, self.spacingMatrixHeight))

    def openCloseFontCallback(self, sender):
        if AllFonts() == []:
            message('No fonts, no party!', 'Please, open some fonts before starting the mighty MultiFont Kerning Controller')
            self.w.close()
        self.loadFontsOrder()
        self.w.fontsOrderController.setFontsOrder(self.fontsOrder)
        self.updateUnicodeMinimum()
        self.adjustSpacingMatrixHeight()
        self.updateSubscriptions()
        self.updateLineView()

    def loadFontsOrder(self):
        if self.fontsOrder is None:
            fontsOrder = [f for f in AllFonts() if f.path is not None]
            self.fontsOrder = sorted(fontsOrder, key=lambda f:os.path.basename(f.path))
        else:
            newFontsOrder = [f for f in AllFonts() if f in self.fontsOrder] + [f for f in AllFonts() if f not in self.fontsOrder]
            self.fontsOrder = newFontsOrder

    def newFontOpened(self, notification):
        message('The MultiFont Metrics Window works only with saved font, please save the new font and re-open the plugin')
        self.w.close()

    def calcSpacingMatrixHeight(self):
        self.spacingMatrixHeight = vanillaControlsSize['EditTextSmallHeight']+len(self.fontsOrder)*vanillaControlsSize['EditTextSmallHeight']*2

    def spacingMatrixCallback(self, sender):
        self.w.lineView.update()

    # other funcs
    def adjustSpacingMatrixHeight(self):
        lineViewPosSize = self.w.lineView.getPosSize()
        self.w.lineView.setPosSize((lineViewPosSize[0], lineViewPosSize[1], lineViewPosSize[2], -MARGIN_BTM-MARGIN_HALFROW-self.spacingMatrixHeight))
        self.calcSpacingMatrixHeight()

    def windowCloseCallback(self, sender):
        self.unsubscribeGlyphs()
        removeObserver(self, "newFontDidOpen")
        removeObserver(self, "fontDidOpen")
        removeObserver(self, "fontDidClose")
        super(MultiFontMetricsWindow, self).windowCloseCallback(sender)

    def updateUnicodeMinimum(self):
        # collect everything
        allUnicodeData = {}
        for eachFont in self.fontsOrder:
            for eachKey, eachValue in eachFont.naked().unicodeData.items():
                if eachKey not in allUnicodeData:
                    allUnicodeData[eachKey] = eachValue

        # filter
        self.unicodeMinimum = {}
        for eachKey, eachValue in allUnicodeData.items():
            for eachFont in self.fontsOrder:
                if eachKey not in eachFont.naked().unicodeData:
                    # print '[WARNING] %s unicode value is not shared across the fonts' % eachKey
                    break
            self.unicodeMinimum[eachKey] = eachValue

    def collectEditTexts(self):
        editTextsPaths = catchFilesAndFolders(self.folderPath, '.txt')
        for eachPath in editTextsPaths:
            editTextRows = [item.replace('\n', '') for item in open(eachPath, 'r').readlines()]
            self.editTexts[os.path.basename(eachPath)[:-4]] = editTextRows

    def updateLineView(self):
        try:
            displayedGlyphs = []
            if self.stringDisplayMode == 'Waterfall':
                for indexFont, eachFont in enumerate(self.fontsOrder):
                    assert isinstance(eachFont, RFont), 'object in self.fontsOrder not a RFont'
                    if indexFont != 0:
                        newLineGlyph = self.w.lineView.createNewLineGlyph()
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
                    for indexFont, eachFont in enumerate(self.fontsOrder):
                        assert isinstance(eachFont, RFont), 'object in self.fontsOrder not a RFont'
                        if eachFont.has_key(eachGlyphName):
                            displayedGlyphs.append(eachFont[eachGlyphName])
                        else:
                            if eachFont.has_key('.notdef'):
                                displayedGlyphs.append(eachFont['.notdef'])
                            else:
                                displayedGlyphs.append(NOT_DEF_GLYPH)

            self.w.lineView.set(displayedGlyphs)

            # add kerning if needed
            if self.applyKerning is True:
                glyphRecords = self.w.lineView.contentView().getGlyphRecords()

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

            # manually refresh the line view ctrl, it should help
            self.w.lineView.update()

            # update spacing matrix
            self.w.spacingMatrix.canvas.update()

        except Exception, error:
            print traceback.format_exc()

    ### callback
    def switchButtonCallback(self, sender):
        assert self.textMode in self.textModeOptions
        self.textMode = self.textModeOptions[sender.get()]

        if self.w.typewriterCtrl.title == self.textMode:
            self.w.typewriterCtrl.show(True)
            self.stringDisplayMode, self.glyphNamesToDisplay = 'Waterfall', self.w.typewriterCtrl.get()
            self.w.textStringsControls.show(False)
        else:
            self.w.textStringsControls.show(True)
            self.stringDisplayMode, self.glyphNamesToDisplay = self.w.textStringsControls.get()
            self.w.typewriterCtrl.show(False)

        self.w.spacingMatrix.setGlyphNamesToDisplay(self.glyphNamesToDisplay)
        self.updateLineView()

    def typewriterCtrlCallback(self, sender):
        self.stringDisplayMode, self.glyphNamesToDisplay = 'Waterfall', sender.get()
        self.w.spacingMatrix.setGlyphNamesToDisplay(self.glyphNamesToDisplay)
        self.w.spacingMatrix.refreshActiveElements()
        self.updateLineView()

    def textStringsControlsCallback(self, sender):
        self.stringDisplayMode, self.glyphNamesToDisplay = sender.get()
        self.w.spacingMatrix.setGlyphNamesToDisplay(self.glyphNamesToDisplay)
        self.w.spacingMatrix.refreshActiveElements()
        self.updateLineView()

    def bodyCtrlCallback(self, sender):
        assert sender.get().isdigit() is True
        self.bodySize = int(sender.get())
        self.w.lineView.setPointSize(self.bodySize)

    def lineHgtCtrlCallback(self, sender):
        assert sender.get().isdigit() is True
        self.lineHeight = int(sender.get())
        self.w.lineView.setLineHeight(self.lineHeight)

    def lineViewSelectionCallback(self, sender):
        if sender.getSelectedGlyph() is not None:
            doodleGlyph = sender.getSelectedGlyph()
            doodleFont = doodleGlyph.getParent()
            for indexFont, eachFont in enumerate(self.fontsOrder):
                if eachFont.path == doodleFont.path:
                    selectedGlyph = self.fontsOrder[indexFont][doodleGlyph.name]
                    self.w.spacingMatrix.setLineViewSelectedGlyph(selectedGlyph)
                    break
        else:
            selectedGlyph = None
            self.w.spacingMatrix.setLineViewSelectedGlyph(selectedGlyph)
        self.w.spacingMatrix.canvas.update()

    def lineViewDoubleClickCallback(self, sender):
        doodleGlyph = sender.getSelectedGlyph()
        doodleFont = doodleGlyph.getParent()
        for indexFont, eachFont in enumerate(self.fontsOrder):
            if eachFont.path == doodleFont.path:
                roboGlyph = self.fontsOrder[indexFont][doodleGlyph.name]
                break

        if roboGlyph is not None:
            OpenGlyphWindow(glyph=roboGlyph, newWindow=False)

    def showMetricsCheckCallback(self, sender):
        self.showMetrics = bool(sender.get())
        self.multiLineOptions['Show Metrics'] = self.showMetrics
        self.multiLineOptions['Show Kerning'] = self.showMetrics
        self.w.lineView.setDisplayStates(self.multiLineOptions)

    def applyKerningCheckCallback(self, sender):
        self.applyKerning = bool(sender.get())
        self.updateLineView()

    def fontsOrderControllerCallback(self, sender):
        self.fontsOrder = sender.getFontsOrder()
        self.w.spacingMatrix.setFontsOrder(self.fontsOrder)
        self.updateLineView()

    def fontCtrlCallback(self, sender):
        fontIndex, fontName = sender.get()
        self.fontsOrder[int(fontIndex)] = fontName
        self.updateLineView()

