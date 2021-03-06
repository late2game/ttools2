#!/usr/bin/env python
# coding: utf-8

"""one main controller, to rule them all"""

### Modules
# other components

# custom
from ..extraTools import miscFunctions
reload(miscFunctions)
from ..extraTools.miscFunctions import catchFilesAndFolders

from ..ui import userInterfaceValues, uiControllers
reload(userInterfaceValues)
from ..ui.userInterfaceValues import vanillaControlsSize
reload(uiControllers)
from ..ui.uiControllers import FontsOrderController, FONT_ROW_HEIGHT

import topCtrls, sidebar, spacingMatrix, joystick
reload(topCtrls)
from topCtrls import Typewriter, TextStringsControls
reload(sidebar)
from sidebar import ComboBoxWithCaption
reload(spacingMatrix)
from spacingMatrix import SpacingMatrix
reload(joystick)
from joystick import SpacingJoystick


# standard
import os
import codecs
from math import floor, ceil
import traceback
from AppKit import NSColor, NSFont, NSCenterTextAlignment
from mojo.UI import MultiLineView, OpenGlyphWindow
from mojo.events import addObserver, removeObserver
from mojo.roboFont import AllFonts, OpenFont, RFont, version
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
MARGIN_BTM = 10
MARGIN_HALFROW = 7
RIGHT_COLUMN = 180

RED = (1,0,0)
BLACK = (0,0,0)

RESOURCES_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'resources')

if version[0] == '2':
    NOT_DEF_GLYPH = OpenFont(os.path.join(RESOURCES_FOLDER, 'notdef.ufo'), showInterface=False)['.notdef']
else:
    NOT_DEF_GLYPH = OpenFont(os.path.join(RESOURCES_FOLDER, 'notdef.ufo'), showUI=False)['.notdef']


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
    leftToRight = True
    verticalMode = False

    multiLineOptions = {}

    bodySizeOptions = [10, 11, 12, 13, 18, 24, 30, 36, 48, 60, 72,
                       144, 216, 360]
    lineHeightOptions = range(0, 301, 10)

    bodySize = bodySizeOptions[10]
    lineHeight = lineHeightOptions[0]

    fontsAmountOptions = range(1, 9)

    def __init__(self):
        super(MultiFontMetricsWindow, self).__init__()

        # ui vars
        originLeft = 0
        originRight = 0
        width = 956
        height = 640

        netWidth = width - MARGIN_LFT - MARGIN_RGT
        jumpingY = MARGIN_TOP

        # let's see if there are opened fonts (fontDB, ctrlFontsList, fontsOrder)
        self.loadFontsOrder()
        self.updateUnicodeMinimum()

        # defining plugin windows
        self.w = Window((originLeft, originRight, width, height),
                        "Multi Font Metrics Window",
                        minSize=(800, 400))
        self.w.bind('resize', self.mainWindowResize)

        switchButtonWdt = 140
        self.w.switchButton = PopUpButton((MARGIN_LFT, jumpingY, switchButtonWdt, vanillaControlsSize['PopUpButtonRegularHeight']),
                                            self.textModeOptions,
                                            sizeStyle='regular',
                                            callback=self.switchButtonCallback)

        # free text
        textCtrlX = MARGIN_LFT+MARGIN_COL+switchButtonWdt
        self.w.typewriterCtrl = Typewriter((textCtrlX, jumpingY, -(RIGHT_COLUMN+MARGIN_COL+MARGIN_RGT), vanillaControlsSize['EditTextRegularHeight']),
                                             self.unicodeMinimum,
                                             callback=self.typewriterCtrlCallback)
        self.w.typewriterCtrl.show(False)

        # strings ctrls
        self.w.textStringsControls = TextStringsControls((textCtrlX, jumpingY, -(RIGHT_COLUMN+MARGIN_COL+MARGIN_RGT), vanillaControlsSize['PopUpButtonRegularHeight']+1),
                                                         self.unicodeMinimum,
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
            'Left to Right': self.leftToRight}
        self.w.lineView = MultiLineView((MARGIN_LFT, jumpingY, -(RIGHT_COLUMN+MARGIN_COL+MARGIN_RGT), -MARGIN_BTM-MARGIN_HALFROW-self.spacingMatrixHeight),
                                        pointSize=self.bodySize,
                                        lineHeight=self.lineHeight,
                                        doubleClickCallback=self.lineViewDoubleClickCallback,
                                        selectionCallback=self.lineViewSelectionCallback,
                                        bordered=True,
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
                                                '{}'.format(self.bodySize),
                                                sizeStyle='small',
                                                callback=self.bodyCtrlCallback)

            # line height
        jumpingY += vanillaControlsSize['ComboBoxSmallHeight'] + int(MARGIN_HALFROW)
        self.w.lineHgtCtrl = ComboBoxWithCaption((-(RIGHT_COLUMN+MARGIN_RGT), jumpingY, RIGHT_COLUMN, vanillaControlsSize['ComboBoxSmallHeight']+1),
                                                   'Line Height:',
                                                   self.lineHeightOptions,
                                                   '{}'.format(self.lineHeight),
                                                   sizeStyle='small',
                                                   callback=self.lineHgtCtrlCallback)

            # show metrics
        jumpingY += vanillaControlsSize['ComboBoxSmallHeight'] + MARGIN_ROW
        self.w.showMetricsCheck = CheckBox((-(RIGHT_COLUMN+MARGIN_RGT), jumpingY, RIGHT_COLUMN, vanillaControlsSize['CheckBoxSmallHeight']),
                                             "Show Metrics",
                                             value=self.showMetrics,
                                             sizeStyle='small',
                                             callback=self.showMetricsCheckCallback)

            # show kerning checkbox
        jumpingY += vanillaControlsSize['CheckBoxSmallHeight'] + MARGIN_ROW*.3
        self.w.applyKerningCheck = CheckBox((-(RIGHT_COLUMN+MARGIN_RGT), jumpingY, RIGHT_COLUMN, vanillaControlsSize['CheckBoxSmallHeight']),
                                         "Show Kerning",
                                         value=self.applyKerning,
                                         sizeStyle='small',
                                         callback=self.applyKerningCheckCallback)

        jumpingY += vanillaControlsSize['CheckBoxSmallHeight'] + MARGIN_ROW*.3
        self.w.leftToRightCheck = CheckBox((-(RIGHT_COLUMN+MARGIN_RGT), jumpingY, RIGHT_COLUMN, vanillaControlsSize['CheckBoxSmallHeight']),
                                           "Left to right",
                                           value=self.leftToRight,
                                           sizeStyle='small',
                                           callback=self.leftToRightCheckCallback)

        # separationLine
        jumpingY += vanillaControlsSize['CheckBoxSmallHeight'] + int(MARGIN_HALFROW)
        self.w.separationLineOne = HorizontalLine((-(RIGHT_COLUMN+MARGIN_RGT), jumpingY, RIGHT_COLUMN, 1))

        jumpingY += int(MARGIN_HALFROW)
        fontsOrderControllerHeight = FONT_ROW_HEIGHT*len(self.fontsOrder)+2
        self.w.fontsOrderController = FontsOrderController((-(RIGHT_COLUMN+MARGIN_RGT), jumpingY, RIGHT_COLUMN, fontsOrderControllerHeight),
                                                           self.fontsOrder,
                                                           callback=self.fontsOrderControllerCallback)

        jumpingY += fontsOrderControllerHeight
        self.w.separationLineTwo = HorizontalLine((-(RIGHT_COLUMN+MARGIN_RGT), jumpingY, RIGHT_COLUMN, 1))

        # joystick
        jumpingY += MARGIN_HALFROW
        self.w.joystick = SpacingJoystick((-(RIGHT_COLUMN+MARGIN_RGT), jumpingY, RIGHT_COLUMN, 0),
                                          verticalMode=self.verticalMode,
                                          marginCallback=self.joystickMarginCallback,
                                          verticalCallback=self.joystickVerticalCallback)

        # edit metrics
        self.w.spacingMatrix = SpacingMatrix((MARGIN_LFT, -(MARGIN_BTM+self.spacingMatrixHeight), self.w.getPosSize()[2]-MARGIN_LFT-MARGIN_RGT, self.spacingMatrixHeight),
                                             glyphNamesToDisplay=self.glyphNamesToDisplay,
                                             verticalMode=self.verticalMode,
                                             fontsOrder=self.fontsOrder,
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
        self.w.lineView.update()

    # observers funcs
    def mainWindowResize(self, mainWindow):
        windowWidth = mainWindow.getPosSize()[2]
        self.w.spacingMatrix.adjustSize((windowWidth-MARGIN_LFT-MARGIN_RGT, self.spacingMatrixHeight))

    def openCloseFontCallback(self, sender):
        self.loadFontsOrder()
        self.w.fontsOrderController.setFontsOrder(self.fontsOrder)
        self.w.spacingMatrix.setFontsOrder(self.fontsOrder)
        self.updateUnicodeMinimum()
        self.updateSubscriptions()
        self.adjustSpacingMatrixHeight()
        self.w.spacingMatrix.update()
        self.adjustFontsOrderControllerHeight()
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

    def calcSpacingMatrixHeight(self):
        self.spacingMatrixHeight = vanillaControlsSize['EditTextSmallHeight']+len(self.fontsOrder)*vanillaControlsSize['EditTextSmallHeight']*2

    def spacingMatrixCallback(self, sender):
        self.w.lineView.update()

    # other funcs
    def adjustSpacingMatrixHeight(self):
        self.calcSpacingMatrixHeight()
        lineViewPosSize = self.w.lineView.getPosSize()
        self.w.lineView.setPosSize((lineViewPosSize[0], lineViewPosSize[1], lineViewPosSize[2], -MARGIN_BTM-MARGIN_HALFROW-self.spacingMatrixHeight))
        spacingMatrixPosSize = self.w.spacingMatrix.getPosSize()
        self.w.spacingMatrix.setPosSize((spacingMatrixPosSize[0], -MARGIN_BTM-self.spacingMatrixHeight, spacingMatrixPosSize[2], self.spacingMatrixHeight))

    def adjustFontsOrderControllerHeight(self):
        fontsOrderControllerHeight = FONT_ROW_HEIGHT*len(self.fontsOrder)+MARGIN_COL
        fontsOrderControllerPosSize = self.w.fontsOrderController.getPosSize()
        self.w.fontsOrderController.setPosSize((fontsOrderControllerPosSize[0], fontsOrderControllerPosSize[1], fontsOrderControllerPosSize[2], fontsOrderControllerHeight))

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
                    break
            if eachValue:
                self.unicodeMinimum[eachKey] = eachValue

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
                        elif eachGlyphName == '.newLine':
                            newLineGlyph = self.w.lineView.createNewLineGlyph()
                            displayedGlyphs.append(newLineGlyph)
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
        self.updateSubscriptions()
        self.w.spacingMatrix.setGlyphNamesToDisplay(self.glyphNamesToDisplay)
        self.w.spacingMatrix.refreshActiveElements()
        self.updateLineView()

    def textStringsControlsCallback(self, sender):
        self.stringDisplayMode, self.glyphNamesToDisplay = sender.get()
        self.updateSubscriptions()
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
        if sender.getSelectedGlyph() is not None:
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
        self.w.lineView.setDisplayStates(self.multiLineOptions)

    def applyKerningCheckCallback(self, sender):
        self.applyKerning = bool(sender.get())
        self.multiLineOptions['Show Kerning'] = self.applyKerning
        self.w.lineView.setDisplayStates(self.multiLineOptions)
        self.updateLineView()

    def leftToRightCheckCallback(self, sender):
        self.leftToRight = bool(sender.get())
        self.multiLineOptions['Left to Right'] = self.leftToRight
        self.w.lineView.setDisplayStates(self.multiLineOptions)
        self.w.lineView.setLeftToRight(self.leftToRight)
        self.updateLineView()

    def fontsOrderControllerCallback(self, sender):
        self.fontsOrder = []
        for indexFont, eachFont in enumerate(sender.getFontsOrder()):
            if sender.getIsDisplayedOrder()[indexFont] is True:
                self.fontsOrder.append(eachFont)

        self.w.spacingMatrix.setFontsOrder(self.fontsOrder)
        self.adjustSpacingMatrixHeight()
        self.updateLineView()

    def joystickMarginCallback(self, sender):
        selectedGlyph = self.w.lineView.getSelectedGlyph()
        whichMargin, amount = sender.get()
        assert whichMargin in ['LEFT', 'RIGHT']

        if selectedGlyph is not None:
            if self.verticalMode is False:
                glyphsToModify = [selectedGlyph]
            else:
                glyphsToModify = [ff[selectedGlyph.name] for ff in self.fontsOrder if ff[selectedGlyph.name].name == selectedGlyph.name]

            for eachGlyph in glyphsToModify:
                if whichMargin == 'LEFT':
                    eachGlyph.leftMargin += amount
                else:
                    eachGlyph.rightMargin += amount

        self.w.lineView.update()
        self.w.spacingMatrix.update()

    def joystickVerticalCallback(self, sender):
        self.verticalMode = sender.getVerticalMode()
        self.w.spacingMatrix.setVerticalMode(self.verticalMode)

