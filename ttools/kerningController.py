#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################
# TT Kerning controller #
#########################

### Modules
# custom
import miscFunctions
reload(miscFunctions)
from miscFunctions import loadKerningTexts, buildPairsFromString

import userInterfaceValues
reload(userInterfaceValues)
from userInterfaceValues import vanillaControlsSize

import uiControllers
reload(uiControllers)
from uiControllers import FontsOrderController, FONT_ROW_HEIGHT

import kerningMisc
reload(kerningMisc)
from kerningMisc import checkPairFormat, whichGroup, getCorrection
from kerningMisc import checkIfPairOverlaps, makePairCorrection
from kerningMisc import searchCorrections, ChooseException

# standard
import os
import sys
import json
import types
import traceback
import mojo.drawingTools as dt
from mojo.roboFont import AllFonts
from mojo.canvas import CanvasGroup
from mojo.events import addObserver, removeObserver
from defconAppKit.windows.baseWindow import BaseWindowController
from defconAppKit.tools.textSplitter import splitText
from vanilla import Window, Group, PopUpButton, List, EditText
from vanilla import CheckBoxListCell, TextBox, SquareButton, HorizontalLine
from vanilla import VerticalLine, CheckBox, Button
from vanilla.dialogs import message, getFile, putFile


### Constants
PLUGIN_TITLE = 'TT Kerning editor'

# func
KERNING_TEXT_FOLDER = os.path.join(os.path.dirname(__file__), 'resources', 'kerningTexts')
JOYSTICK_EVENTS = ['exceptionTrigger', 'minusMajor', 'minusMinor', 'plusMinor', 'plusMajor', 'preview', 'solved', 'symmetricalEditing', 'keyboardEdit', 'previousWord', 'cursorUp', 'cursorLeft', 'cursorRight', 'cursorDown', 'nextWord']

MAJOR_STEP = 20
MINOR_STEP = 4

KERNING_NOT_DISPLAYED_ERROR = 'Why are you editing kerning if it is not displayed?'

# colors
EXCEPTION_COLOR = (1,0,0,.4)
GROUP_GLYPHS_COLOR = (0, 0, 1, .1)
SYMMETRICAL_BACKGROUND_COLOR = (1, 0, 1, .2)

BLACK = (0, 0, 0)
WHITE = (1,1,1)
LIGHT_RED = (1, 0, 0, .4)
LIGHT_GREEN = (0, 1, 0, .4)
LIGHT_BLUE = (0, 0, 1, .4)
LIGHT_GRAY = (0, 0, 0, .4)

# ui
MARGIN_VER = 8
MARGIN_HOR = 8
MARGIN_COL = 4

LEFT_COLUMN = 200
PLUGIN_WIDTH = 1000
PLUGIN_HEIGHT = 850

TEXT_MARGIN = 200 #upm
CANVAS_SCALING_FACTOR_INIT = 1.6

if '.SFNSText' in dt.installedFonts():
    SYSTEM_FONT_NAME = '.SFNSText'
else:
    SYSTEM_FONT_NAME = '.HelveticaNeueDeskInterface-Regular'

BODY_SIZE = 14
GROUP_NAME_BODY_SIZE = 12

"""
Desired keys

A: -4
D: +4
W: previous word
S: following word

return: mark the word as "done"

←: move cursor
→: move cursor
↑: move cursor
↓: move cursor

<: preview mode

"""

### Controllers
class KerningController(BaseWindowController):
    """this is the main controller of TT kerning editor, it handles different controllers and dialogues with font data"""

    displayedWord = ''
    displayedPairs = []
    activePair = None

    canvasScalingFactor = CANVAS_SCALING_FACTOR_INIT

    fontsOrder = None
    navCursor_X = 0    # related to pairs
    navCursor_Y = 0    # related to active fonts

    isPreviewOn = False
    areGroupsShown = True
    areCollisionsShown = False
    isKerningDisplayActive = True
    isSidebearingsActive = True
    isMetricsActive = True
    isColorsActive = True
    isSymmetricalEditingOn = False

    def __init__(self):
        super(KerningController, self).__init__()

        if AllFonts() == []:
            message('No fonts, no party!', 'Please, open some fonts before starting the mighty MultiFont Kerning Controller')
            return None

        self.w = Window((0, 0, PLUGIN_WIDTH, PLUGIN_HEIGHT),
                        PLUGIN_TITLE,
                        minSize=(PLUGIN_WIDTH, PLUGIN_HEIGHT))
        self.w.bind('resize', self.mainWindowResize)


        # load opened fonts
        self.initFontsOrder()

        # exception window (will appear only if needed)
        self.exceptionWindow = ChooseException(['group2glyph', 'glyph2group', 'glyph2glyph'],
                                               callback=self.exceptionWindowCallback)
        self.exceptionWindow.enable(False)

        self.jumping_Y = MARGIN_VER
        self.jumping_X = MARGIN_HOR
        self.w.wordListController = WordListController((self.jumping_X, self.jumping_Y, LEFT_COLUMN, 290),
                                                       callback=self.wordListControllerCallback)
        self.displayedWord = self.w.wordListController.get()
        self.displayedPairs = buildPairsFromString(self.displayedWord)
        self.activePair = self.displayedPairs[0]
        checkPairFormat(self.activePair)

        self.jumping_Y += self.w.wordListController.getPosSize()[3]+4
        self.w.word_font_separationLine = HorizontalLine((self.jumping_X, self.jumping_Y, LEFT_COLUMN, vanillaControlsSize['HorizontalLineThickness']))

        self.jumping_Y += MARGIN_VER
        fontsOrderControllerHeight = FONT_ROW_HEIGHT*len(self.fontsOrder)+MARGIN_HOR
        self.w.fontsOrderController = FontsOrderController((self.jumping_X, self.jumping_Y, LEFT_COLUMN, fontsOrderControllerHeight),
                                                           self.fontsOrder,
                                                           callback=self.fontsOrderControllerCallback)
        self.jumping_Y += fontsOrderControllerHeight
        self.w.fonts_controller_separationLine = HorizontalLine((self.jumping_X, self.jumping_Y, LEFT_COLUMN, vanillaControlsSize['HorizontalLineThickness']))
        
        self.jumping_Y += MARGIN_VER
        self.w.joystick = JoystickGroup((self.jumping_X, self.jumping_Y, LEFT_COLUMN, 240),
                                        self.fontsOrder[self.navCursor_Y],
                                        self.activePair,
                                        self.isSymmetricalEditingOn,
                                        callback=self.joystickCallback)

        self.jumping_Y += self.w.joystick.getPosSize()[3] + MARGIN_VER
        self.w.graphicsManager = GraphicsManager((self.jumping_X, -160, LEFT_COLUMN, 160),
                                                 self.isKerningDisplayActive,
                                                 self.areGroupsShown,
                                                 self.areCollisionsShown,
                                                 self.isSidebearingsActive,
                                                 self.isMetricsActive,
                                                 self.isColorsActive,
                                                 callback=self.graphicsManagerCallback)

        self.jumping_X += LEFT_COLUMN+MARGIN_COL*2
        self.jumping_Y = MARGIN_VER

        self.w.displayedWordCaption = TextBox((self.jumping_X, self.jumping_Y, 200, vanillaControlsSize['TextBoxRegularHeight']),
                                              self.displayedWord)

        self.w.scalingFactorController = FactorController((-MARGIN_HOR-72, self.jumping_Y, 72, vanillaControlsSize['TextBoxRegularHeight']),
                                                          self.canvasScalingFactor,
                                                          callback=self.scalingFactorControllerCallback)

        self.jumping_Y += self.w.displayedWordCaption.getPosSize()[3]+MARGIN_COL
        self.initWordDisplays()

        # observers!
        addObserver(self, 'openCloseFontCallback', "fontDidOpen")
        addObserver(self, 'openCloseFontCallback', "fontDidClose")
        self.setUpBaseWindowBehavior()
        self.w.open()

    def windowCloseCallback(self, sender):
        removeObserver(self, "fontDidOpen")
        removeObserver(self, "fontWillClose")
        super(KerningController, self).windowCloseCallback(sender)

    def openCloseFontCallback(self, sender):
        if AllFonts() == []:
            message('No fonts, no party!', 'Please, open some fonts before starting the mighty MultiFont Kerning Controller')
            self.w.close()


        self.deleteWordDisplays()
        self.initFontsOrder()
        self.w.fontsOrderController.setFontsOrder(self.fontsOrder)
        self.initWordDisplays()

        fontsOrderControllerHeight = FONT_ROW_HEIGHT*len(self.fontsOrder)+MARGIN_HOR
        prevFontsOrderPos = self.w.fontsOrderController.getPosSize()
        self.w.fontsOrderController.setPosSize((prevFontsOrderPos[0], prevFontsOrderPos[1], prevFontsOrderPos[2], fontsOrderControllerHeight))

        prevSepLinePos = self.w.fonts_controller_separationLine.getPosSize()
        self.w.fonts_controller_separationLine.setPosSize((prevSepLinePos[0], prevFontsOrderPos[1] + fontsOrderControllerHeight, prevSepLinePos[2], prevSepLinePos[3]))

        prevJoystickPos = self.w.joystick.getPosSize()
        self.w.joystick.setPosSize((prevJoystickPos[0], prevFontsOrderPos[1] + fontsOrderControllerHeight + MARGIN_VER, prevJoystickPos[2], prevJoystickPos[3]))

    def initFontsOrder(self):
        if self.fontsOrder is None:
            fontsOrder = [f for f in AllFonts() if f.path is not None]
            self.fontsOrder = sorted(fontsOrder, key=lambda f:os.path.basename(f.path))
        else:
            newFontsOrder = [f for f in AllFonts() if f in self.fontsOrder] + [f for f in AllFonts() if f not in self.fontsOrder]
            self.fontsOrder = newFontsOrder

    def deleteWordDisplays(self):
        for eachI in range(len(self.fontsOrder)):
            try:
                delattr(self.w, 'wordCtrl_%#02d' % (eachI+1))
                self.jumping_Y = MARGIN_VER+vanillaControlsSize['TextBoxRegularHeight']
            except Exception as e:
                print traceback.format_exc()

    def initWordDisplays(self):
        windowWidth, windowHeight = self.w.getPosSize()[2], self.w.getPosSize()[3]
        netTotalWindowHeight = windowHeight-MARGIN_COL-MARGIN_VER*2-vanillaControlsSize['TextBoxRegularHeight']-MARGIN_HOR*(len(self.fontsOrder)-1)
        singleWindowHeight = netTotalWindowHeight/len(self.fontsOrder)
        rightColumnWidth = windowWidth-LEFT_COLUMN-MARGIN_COL

        self.jumping_Y = MARGIN_VER+vanillaControlsSize['TextBoxRegularHeight']+MARGIN_COL
        for eachI in range(len(self.fontsOrder)):

            if eachI == self.navCursor_Y:
                initActivePair = self.displayedPairs[self.navCursor_X]
                initPairIndex = self.navCursor_X
            else:
                initActivePair = None
                initPairIndex = None

            try:
                wordCtrl = WordDisplay((self.jumping_X, self.jumping_Y, rightColumnWidth, singleWindowHeight),
                                        self.displayedWord,
                                        self.canvasScalingFactor,
                                        self.displayedPairs,
                                        self.fontsOrder[eachI],
                                        self.isKerningDisplayActive,
                                        self.areGroupsShown,
                                        self.areCollisionsShown,
                                        self.isSidebearingsActive,
                                        self.isMetricsActive,
                                        self.isColorsActive,
                                        self.isPreviewOn,
                                        self.isSymmetricalEditingOn,
                                        activePair=initActivePair,
                                        pairIndex=initPairIndex)
            except Exception:
                print traceback.format_exc()

            self.jumping_Y += singleWindowHeight + MARGIN_HOR
            setattr(self.w, 'wordCtrl_%#02d' % (eachI+1), wordCtrl)

    def updateWordDisplays(self):
        for eachI in range(len(self.fontsOrder)):
            eachDisplay = getattr(self.w, 'wordCtrl_%#02d' % (eachI+1))
            eachDisplay.setDisplayedWord(self.displayedWord)
            eachDisplay.setScalingFactor(self.canvasScalingFactor)
            eachDisplay.setDisplayedPairs(self.displayedPairs)
            eachDisplay.setGraphicsBooleans(self.isKerningDisplayActive, self.areGroupsShown, self.areCollisionsShown, self.isSidebearingsActive, self.isMetricsActive, self.isColorsActive)
            eachDisplay.setPreviewMode(self.isPreviewOn)
            eachDisplay.setSymmetricalEditingMode(self.isSymmetricalEditingOn)
            eachDisplay.wordCanvasGroup.update()

    def nextWord(self):
        self.w.wordListController.nextWord()
        self.displayedWord = self.w.wordListController.get()
        self.updateEditorAccordingToDiplayedWord()

    def previousWord(self):
        self.w.wordListController.previousWord()
        self.displayedWord = self.w.wordListController.get()
        self.updateEditorAccordingToDiplayedWord()

    def updateEditorAccordingToDiplayedWord(self):
        self.w.displayedWordCaption.set(self.displayedWord)
        self.w.displayedWordCaption.set(self.displayedWord)
        self.displayedPairs = buildPairsFromString(self.displayedWord)
        if len(self.displayedPairs) < (self.navCursor_X+1):
            self.navCursor_X = len(self.displayedPairs)-1
        self.activePair = self.displayedPairs[self.navCursor_X]
        checkPairFormat(self.activePair)
        self.w.joystick.setActivePair(self.activePair)
        self.updateWordDisplays()
        getattr(self.w, 'wordCtrl_%#02d' % (self.navCursor_Y+1)).setActivePairIndex(self.navCursor_X)

    def switchSolvedAttribute(self):
        self.w.wordListController.switchActiveWordSolvedAttribute()

    def switchSymmetricalEditing(self):
        self.isSymmetricalEditingOn = not self.isSymmetricalEditingOn
        self.updateWordDisplays()

    # manipulate data
    def setPairCorrection(self, amount):
        selectedFont = self.fontsOrder[self.navCursor_Y]
        selectedPair = tuple(self.displayedPairs[self.navCursor_X])

        correction, correctionKey = getCorrection(selectedPair, selectedFont, getKey=True)
        selectedFont.kerning[correctionKey] = amount

        if self.isSymmetricalEditingOn is True:
            flippedCorrectionKey = correctionKey[1], correctionKey[0]
            selectedFont.kerning[flippedCorrectionKey] = amount
        self.updateWordDisplays()

    def modifyPairCorrection(self, amount):
        selectedFont = self.fontsOrder[self.navCursor_Y]
        selectedPair = tuple(splitText(''.join(self.displayedPairs[self.navCursor_X]), selectedFont.naked().unicodeData))

        makePairCorrection(selectedPair, selectedFont, amount)
        if self.isSymmetricalEditingOn is True:
            flippedPair = selectedPair[1], selectedPair[0]
            makePairCorrection(flippedPair, selectedFont, amount)

        self.w.joystick.updateCorrectionValue()
        self.updateWordDisplays()

    # cursor methods
    def cursorLeft(self):
        self.navCursor_X = (self.navCursor_X-1)%len(self.displayedPairs)
        getattr(self.w, 'wordCtrl_%#02d' % (self.navCursor_Y+1)).setActivePairIndex(self.navCursor_X)
        self.w.joystick.setActivePair(self.displayedPairs[self.navCursor_X])
        self.updateWordDisplays()

    def cursorRight(self):
        self.navCursor_X = (self.navCursor_X+1)%len(self.displayedPairs)
        getattr(self.w, 'wordCtrl_%#02d' % (self.navCursor_Y+1)).setActivePairIndex(self.navCursor_X)
        self.w.joystick.setActivePair(self.displayedPairs[self.navCursor_X])
        self.updateWordDisplays()

    def cursorUp(self):
        getattr(self.w, 'wordCtrl_%#02d' % (self.navCursor_Y+1)).setActivePairIndex(None)   # old
        self.navCursor_Y = (self.navCursor_Y-1)%len(self.fontsOrder)
        getattr(self.w, 'wordCtrl_%#02d' % (self.navCursor_Y+1)).setActivePairIndex(self.navCursor_X)   # new
        self.w.joystick.setFontObj(self.fontsOrder[self.navCursor_Y])
        self.updateWordDisplays()

    def cursorDown(self):
        getattr(self.w, 'wordCtrl_%#02d' % (self.navCursor_Y+1)).setActivePairIndex(None)   # old
        self.navCursor_Y = (self.navCursor_Y+1)%len(self.fontsOrder)
        getattr(self.w, 'wordCtrl_%#02d' % (self.navCursor_Y+1)).setActivePairIndex(self.navCursor_X)   # new
        self.w.joystick.setFontObj(self.fontsOrder[self.navCursor_Y])
        self.updateWordDisplays()

    ### callbacks
    def exceptionWindowCallback(self, sender):
        self.whichException = sender.get()

    def mainWindowResize(self, mainWindow):
        windowWidth, windowHeight = mainWindow.getPosSize()[2], mainWindow.getPosSize()[3]
        rightColumnWidth = windowWidth - LEFT_COLUMN

        # caption
        prevdisplayedWordCaptionSize = self.w.displayedWordCaption.getPosSize()
        self.w.displayedWordCaption.setPosSize((prevdisplayedWordCaptionSize[0], prevdisplayedWordCaptionSize[1], rightColumnWidth, prevdisplayedWordCaptionSize[3]))

        # displayers
        initY = MARGIN_VER+vanillaControlsSize['TextBoxRegularHeight']+MARGIN_COL
        netTotalWindowHeight = windowHeight-initY-MARGIN_VER-MARGIN_HOR*(len(self.fontsOrder)-1)
        singleWordDisplayHeight = netTotalWindowHeight/len(self.fontsOrder)

        y = initY
        for eachI in range(len(self.fontsOrder)):
            getattr(self.w, 'wordCtrl_%#02d' % (eachI+1)).adjustSize((self.jumping_X, y, rightColumnWidth, singleWordDisplayHeight))
            y += singleWordDisplayHeight+MARGIN_HOR

    def scalingFactorControllerCallback(self, sender):
        self.canvasScalingFactor = sender.getScalingFactor()
        self.updateWordDisplays()

    def wordListControllerCallback(self, sender):
        self.displayedWord = sender.get()
        self.updateEditorAccordingToDiplayedWord()

    def fontsOrderControllerCallback(self, sender):
        self.deleteWordDisplays()
        self.fontsOrder = sender.getFontsOrder()
        self.initWordDisplays()

    def graphicsManagerCallback(self, sender):
        self.isKerningDisplayActive, self.areGroupsShown, self.areCollisionsShown, self.isSidebearingsActive, self.isMetricsActive, self.isColorsActive = sender.get()
        self.updateWordDisplays()

    def joystickCallback(self, sender):
        joystickEvent = sender.getLastEvent()
        assert joystickEvent in JOYSTICK_EVENTS

        if joystickEvent == 'minusMajor':
            if self.isKerningDisplayActive is True:
                self.modifyPairCorrection(-MAJOR_STEP)
            else:
                message('Be aware!', KERNING_NOT_DISPLAYED_ERROR, callback=None)

        elif joystickEvent == 'minusMinor':
            if self.isKerningDisplayActive is True:
                self.modifyPairCorrection(-MINOR_STEP)
            else:
                message('Be aware!', KERNING_NOT_DISPLAYED_ERROR, callback=None)

        elif joystickEvent == 'plusMinor':
            if self.isKerningDisplayActive is True:
                self.modifyPairCorrection(MINOR_STEP)
            else:
                message('Be aware!', KERNING_NOT_DISPLAYED_ERROR, callback=None)

        elif joystickEvent == 'plusMajor':
            if self.isKerningDisplayActive is True:
                self.modifyPairCorrection(MAJOR_STEP)
            else:
                message('Be aware!', KERNING_NOT_DISPLAYED_ERROR, callback=None)

        elif joystickEvent == 'preview':
            if self.isPreviewOn is True:
                self.isPreviewOn = False
                self.w.graphicsManager.switchControls(True)
            else:
                self.isPreviewOn = True
                self.w.graphicsManager.switchControls(False)
            self.updateWordDisplays()

        elif joystickEvent == 'solved':
            self.switchSolvedAttribute()
            self.nextWord()

        elif joystickEvent == 'symmetricalEditing':
            self.switchSymmetricalEditing()

        elif joystickEvent == 'previousWord':
            self.previousWord()

        elif joystickEvent == 'cursorUp':
            self.cursorUp()

        elif joystickEvent == 'cursorLeft':
            self.cursorLeft()

        elif joystickEvent == 'cursorRight':
            self.cursorRight()

        elif joystickEvent == 'cursorDown':
            self.cursorDown()

        elif joystickEvent == 'nextWord':
            self.nextWord()

        elif joystickEvent == 'keyboardEdit':
            if self.isKerningDisplayActive is True:
                self.setPairCorrection(self.w.joystick.getKeyboardCorrection())
                self.updateWordDisplays()
            else:
                message('Be aware!', KERNING_NOT_DISPLAYED_ERROR, callback=None)
                self.w.joystick.updateCorrectionValue()

        elif joystickEvent == 'exceptionTrigger':
            self.exceptionWindow.enable(True)


class FactorController(Group):

    def __init__(self, posSize, canvasScalingFactor, callback):
        super(FactorController, self).__init__(posSize)
        self.canvasScalingFactor = canvasScalingFactor
        self.callback = callback

        jumpingX = 0
        self.caption = TextBox((jumpingX, 0, 30, vanillaControlsSize['TextBoxRegularHeight']),
                               '%.1f' % self.canvasScalingFactor)

        jumpingX += 30+MARGIN_COL
        self.upButton = SquareButton((jumpingX, 0, 16, 16),
                                     '+',
                                     sizeStyle='small',
                                     callback=self.upButtonCallback)

        jumpingX += 16+MARGIN_COL
        self.dwButton = SquareButton((jumpingX, 0, 16, 16),
                                     '-',
                                     sizeStyle='small',
                                     callback=self.dwButtonCallback)

    def getScalingFactor(self):
        return self.canvasScalingFactor

    def upButtonCallback(self, sender):
        self.canvasScalingFactor += .1
        self.caption.set('%.1f' % self.canvasScalingFactor)
        self.callback(self)

    def dwButtonCallback(self, sender):
        self.canvasScalingFactor -= .1
        self.caption.set('%.1f' % self.canvasScalingFactor)
        self.callback(self)


class JoystickGroup(Group):

    lastEvent = None
    keyboardCorrection = 0

    def __init__(self, posSize, fontObj, activePair, isSymmetricalEditingOn, callback):
        super(JoystickGroup, self).__init__(posSize)
        self.activePair = activePair
        self.fontObj = fontObj
        self.isSymmetricalEditingOn = isSymmetricalEditingOn
        self.callback = callback

        buttonSide = 36
        self.ctrlWidth, self.ctrlHeight = posSize[2], posSize[3]
        self.jumping_X = buttonSide/2.
        self.jumping_Y = 0

        correction = getCorrection(self.activePair, self.fontObj, checkWithFlatKerning=True)

        self.minusMajorCtrl = SquareButton((self.jumping_X, self.jumping_Y, buttonSide, buttonSide),
                                           "-%s" % MAJOR_STEP,
                                           sizeStyle='small',
                                           callback=self.minusMajorCtrlCallback)
        self.minusMajorCtrl.bind('leftarrow', ['option', 'command'])

        self.jumping_X += buttonSide
        self.minusMinorCtrl = SquareButton((self.jumping_X, self.jumping_Y, buttonSide, buttonSide),
                                           "-%s" % MINOR_STEP,
                                           sizeStyle='small',
                                           callback=self.minusMinorCtrlCallback)
        self.minusMinorCtrl.bind('leftarrow', ['command'])

        self.jumping_X += buttonSide
        self.plusMinorCtrl = SquareButton((self.jumping_X, self.jumping_Y, buttonSide, buttonSide),
                                          "+%s" % MINOR_STEP,
                                          sizeStyle='small',
                                          callback=self.plusMinorCtrlCallback)
        self.plusMinorCtrl.bind('rightarrow', ["command"])

        self.jumping_X += buttonSide
        self.plusMajorCtrl = SquareButton((self.jumping_X, self.jumping_Y, buttonSide, buttonSide),
                                          "+%s" % MAJOR_STEP,
                                          sizeStyle='small',
                                          callback=self.plusMajorCtrlCallback)
        self.plusMajorCtrl.bind('rightarrow', ['option', 'command'])

        self.jumping_X = buttonSide/2.
        self.jumping_Y += buttonSide
        self.exceptionController = SquareButton((self.jumping_X, self.jumping_Y, buttonSide*4, buttonSide*.75),
                                                'exception',
                                                sizeStyle='small',
                                                callback=self.exceptionControllerCallback)
        self.exceptionController.bind('e', ['command'])

        self.jumping_X = buttonSide/2.
        self.jumping_Y += buttonSide*.75
        self.previewCtrl = SquareButton((self.jumping_X, self.jumping_Y, buttonSide*2, buttonSide*.75),
                                        "preview",
                                        sizeStyle='small',
                                        callback=self.previewCtrlCallback)
        self.previewCtrl.bind(unichr(112), ['command'])

        self.jumping_X += buttonSide*2
        self.solvedCtrl = SquareButton((self.jumping_X, self.jumping_Y, buttonSide*2, buttonSide*.75),
                                       "solved",
                                       sizeStyle='small',
                                       callback=self.solvedCtrlCallback)
        self.solvedCtrl.bind(unichr(13), ['command'])

        self.jumping_X = buttonSide/2.
        self.jumping_Y += buttonSide*.75+2
        self.symmetryModeCheck = CheckBox((self.jumping_X, self.jumping_Y, self.ctrlWidth, vanillaControlsSize['CheckBoxRegularHeight']),
                                          'symmetrical editing',
                                          value=self.isSymmetricalEditingOn,
                                          callback=self.symmetryModeCheckCallback)

        self.hiddenSymmetryEditingButton = Button((self.jumping_X, self.ctrlHeight+40, self.ctrlWidth, vanillaControlsSize['ButtonRegularHeight']),
                                                   'hiddenSymmetriyEditingButton',
                                                   callback=self.hiddenSymmetryEditingButtonCallback)
        self.hiddenSymmetryEditingButton.bind('s', ['command'])

        self.jumping_X = buttonSide
        self.jumping_Y += buttonSide
        self.previousWordCtrl = SquareButton((self.jumping_X, self.jumping_Y, buttonSide, buttonSide),
                                             u'↖',
                                             sizeStyle='small',
                                             callback=self.previousWordCtrlCallback)
        self.previousWordCtrl.bind('uparrow', ['command', 'option'])

        self.jumping_X += buttonSide
        self.cursorUpCtrl = SquareButton((self.jumping_X, self.jumping_Y, buttonSide, buttonSide),
                                         u'↑',
                                         sizeStyle='small',
                                         callback=self.cursorUpCtrlCallback)
        self.cursorUpCtrl.bind("uparrow", [])

        self.jumping_X += buttonSide*1.5
        self.activePairEditCorrection = EditText((self.jumping_X, self.jumping_Y, 50, vanillaControlsSize['EditTextRegularHeight']),
                                                 text='%s' % correction,
                                                 continuous=False,
                                                 callback=self.activePairEditCorrectionCallback)

        self.jumping_X = buttonSide
        self.jumping_Y += buttonSide
        self.cursorLeftCtrl = SquareButton((self.jumping_X, self.jumping_Y, buttonSide, buttonSide),
                                           u"←",
                                           sizeStyle='small',
                                           callback=self.cursorLeftCtrlCallback)
        self.cursorLeftCtrl.bind("leftarrow", [])

        self.jumping_X += buttonSide*2
        self.cursorRightCtrl = SquareButton((self.jumping_X, self.jumping_Y, buttonSide, buttonSide),
                                            u'→',
                                            sizeStyle='small',
                                            callback=self.cursorRightCtrlCallback)
        self.cursorRightCtrl.bind("rightarrow", [])

        self.jumping_X = buttonSide*2
        self.jumping_Y += buttonSide
        self.cursorDownCtrl = SquareButton((self.jumping_X, self.jumping_Y, buttonSide, buttonSide),
                                           u'↓',
                                           sizeStyle='small',
                                           callback=self.cursorDownCtrlCallback)
        self.cursorDownCtrl.bind("downarrow", [])

        self.jumping_X += buttonSide
        self.nextWordCtrl = SquareButton((self.jumping_X, self.jumping_Y, buttonSide, buttonSide),
                                         u'↘',
                                         sizeStyle='small',
                                         callback=self.nextWordCtrlCallback)
        self.nextWordCtrl.bind('downarrow', ['command', 'option'])

    def getLastEvent(self):
        return self.lastEvent

    def getKeyboardCorrection(self):
        return self.keyboardCorrection

    def setActivePair(self, value):
        checkPairFormat(value)
        self.activePair = value
        self.updateCorrectionValue()

    def setFontObj(self, value):
        self.fontObj = value
        self.updateCorrectionValue()

    def updateCorrectionValue(self):
        correctionsMap = searchCorrections(self.activePair, self.fontObj)
        if 'exception' in correctionsMap:
            correctionKey, correction = correctionsMap['exception']
        elif 'standard' in correctionsMap:
            correctionKey, correction = correctionsMap['standard']
        else:
            correctionKey, correction = None, 0
        self.activePairEditCorrection.set('%s' % correction)

    def minusMajorCtrlCallback(self, sender):
        self.lastEvent = 'minusMajor'
        self.callback(self)

    def minusMinorCtrlCallback(self, sender):
        self.lastEvent = 'minusMinor'
        self.callback(self)

    def plusMinorCtrlCallback(self, sender):
        self.lastEvent = 'plusMinor'
        self.callback(self)

    def plusMajorCtrlCallback(self, sender):
        self.lastEvent = 'plusMajor'
        self.callback(self)

    def exceptionControllerCallback(self, sender):
        self.lastEvent = 'exceptionTrigger'
        self.callback(self)

    def previewCtrlCallback(self, sender):
        self.lastEvent = 'preview'
        self.callback(self)

    def solvedCtrlCallback(self, sender):
        self.lastEvent = 'solved'
        self.callback(self)

    def symmetryModeCheckCallback(self, sender):
        self.lastEvent = 'symmetricalEditing'
        self.isSymmetricalEditingOn = bool(sender.get())
        self.callback(self)

    def hiddenSymmetryEditingButtonCallback(self, sender):
        self.lastEvent = 'symmetricalEditing'
        self.isSymmetricalEditingOn = not self.isSymmetricalEditingOn
        self.symmetryModeCheck.set(self.isSymmetricalEditingOn)
        self.callback(self)

    def previousWordCtrlCallback(self, sender):
        self.lastEvent = 'previousWord'
        self.callback(self)

    def cursorUpCtrlCallback(self, sender):
        self.lastEvent = 'cursorUp'
        self.callback(self)

    def cursorLeftCtrlCallback(self, sender):
        self.lastEvent = 'cursorLeft'
        self.callback(self)

    def cursorRightCtrlCallback(self, sender):
        self.lastEvent = 'cursorRight'
        self.callback(self)

    def cursorDownCtrlCallback(self, sender):
        self.lastEvent = 'cursorDown'
        self.callback(self)

    def nextWordCtrlCallback(self, sender):
        self.lastEvent = 'nextWord'
        self.callback(self)

    def activePairEditCorrectionCallback(self, sender):
        try:
            self.lastEvent = 'keyboardEdit'
            self.keyboardCorrection = int(sender.get())
            self.callback(self)

        except ValueError:
            if sender.get() != '-' or sender.get() != '':
                correctionsMap = searchCorrections(self.activePair, self.fontObj)
                if 'exception' in correctionsMap:
                    correctionKey, correction = correctionsMap['exception']
                elif 'standard' in correctionsMap:
                    correctionKey, correction = correctionsMap['standard']
                else:
                    correctionKey, correction = 0
                self.activePairEditCorrection.set('%s' % correction)
                print traceback.format_exc()


class GraphicsManager(Group):

    previousState = None

    def __init__(self, posSize, isSidebearingsActive, areGroupsShown, areCollisionsShown, isKerningDisplayActive, isMetricsActive, isColorsActive, callback):
        super(GraphicsManager, self).__init__(posSize)
        self.isKerningDisplayActive = isKerningDisplayActive
        self.areGroupsShown = areGroupsShown
        self.areCollisionsShown = areCollisionsShown
        self.isSidebearingsActive = isSidebearingsActive
        self.isMetricsActive = isMetricsActive
        self.isColorsActive = isColorsActive
        self.callback = callback

        self.ctrlWidth, self.ctrlHeight = posSize[2], posSize[3]

        jumping_Y = 0
        self.ctrlCaption = TextBox((0, jumping_Y, self.ctrlWidth, vanillaControlsSize['TextBoxRegularHeight']),
                                   'Display options:')

        jumping_Y = vanillaControlsSize['TextBoxRegularHeight'] + MARGIN_VER/2.
        indent = 16
        self.showKerningCheck = CheckBox((indent, jumping_Y, self.ctrlWidth-indent, vanillaControlsSize['CheckBoxRegularHeight']),
                                          'show kerning',
                                          value=self.isKerningDisplayActive,
                                          callback=self.showKerningCheckCallback)

        self.showKerningHiddenButton = Button((0,self.ctrlHeight+40,0,0),
                                              'hidden kerning button',
                                              callback=self.showKerningHiddenButtonCallback)
        # self.showKerningHiddenButton.show(False)
        self.showKerningHiddenButton.bind('k', ['command'])

        jumping_Y += vanillaControlsSize['CheckBoxRegularHeight']
        self.showGroupsCheck = CheckBox((indent, jumping_Y, self.ctrlWidth-indent, vanillaControlsSize['CheckBoxRegularHeight']),
                                        'show groups',
                                        value=self.areGroupsShown,
                                        callback=self.showGroupsCheckCallback)

        jumping_Y += vanillaControlsSize['CheckBoxRegularHeight']
        self.showCollisionsCheck = CheckBox((indent, jumping_Y, self.ctrlWidth-indent, vanillaControlsSize['CheckBoxRegularHeight']),
                                        'show collisions',
                                        value=self.areCollisionsShown,
                                        callback=self.showCollisionsCheckCallback)

        jumping_Y += vanillaControlsSize['CheckBoxRegularHeight']
        self.showSidebearingsCheck = CheckBox((indent, jumping_Y, self.ctrlWidth-indent, vanillaControlsSize['CheckBoxRegularHeight']),
                                          'show sidebearings',
                                          value=self.isSidebearingsActive,
                                          callback=self.showSidebearingsCheckCallback)

        jumping_Y += vanillaControlsSize['CheckBoxRegularHeight']
        self.showMetricsCheck = CheckBox((indent, jumping_Y, self.ctrlWidth-indent, vanillaControlsSize['CheckBoxRegularHeight']),
                                     'show metrics',
                                     value=self.isMetricsActive,
                                     callback=self.showMetricsCheckCallback)

        jumping_Y += vanillaControlsSize['CheckBoxRegularHeight']
        self.showColorsCheck = CheckBox((indent, jumping_Y, self.ctrlWidth-indent, vanillaControlsSize['CheckBoxRegularHeight']),
                                    'show corrections',
                                    value=self.isColorsActive,
                                    callback=self.showColorsCheckCallback)

    def get(self):
        return self.isKerningDisplayActive, self.areGroupsShown, self.areCollisionsShown, self.isSidebearingsActive, self.isMetricsActive, self.isColorsActive

    def switchControls(self, value):
        self.showSidebearingsCheck.enable(value)
        self.showMetricsCheck.enable(value)
        self.showColorsCheck.enable(value)
        self.showGroupsCheck.enable(value)
        self.showCollisionsCheck.enable(value)

    def showKerningCheckCallback(self, sender):
        self.isKerningDisplayActive = bool(sender.get())
        self.showColorsCheck.enable(bool(sender.get()))
        self.callback(self)

    def showGroupsCheckCallback(self, sender):
        self.areGroupsShown = bool(sender.get())
        self.callback(self)

    def showCollisionsCheckCallback(self, sender):
        self.areCollisionsShown = bool(sender.get())
        self.callback(self)

    def showKerningHiddenButtonCallback(self, sender):
        self.isKerningDisplayActive = not self.isKerningDisplayActive
        self.showKerningCheck.set(self.isKerningDisplayActive)
        self.callback(self)

    def showSidebearingsCheckCallback(self, sender):
        self.isSidebearingsActive = bool(sender.get())
        self.callback(self)

    def showMetricsCheckCallback(self, sender):
        self.isMetricsActive = bool(sender.get())
        self.callback(self)

    def showColorsCheckCallback(self, sender):
        self.isColorsActive = bool(sender.get())
        self.callback(self)


class WordDisplay(Group):

    def __init__(self, posSize, displayedWord, canvasScalingFactor, displayedPairs, fontObj, isKerningDisplayActive, areGroupsShown, areCollisionsShown, isSidebearingsActive, isMetricsActive, isColorsActive, isPreviewOn, isSymmetricalEditingOn, activePair=None, pairIndex=None):
        super(WordDisplay, self).__init__(posSize)

        self.displayedWord = displayedWord
        self.displayedPairs = displayedPairs
        self.canvasScalingFactor = canvasScalingFactor
        self.fontObj = fontObj
        self.activePair = activePair
        self.pairIndex = pairIndex

        self.isKerningDisplayActive = isKerningDisplayActive
        self.areGroupsShown = areGroupsShown
        self.areCollisionsShown = areCollisionsShown
        self.isSidebearingsActive = isSidebearingsActive
        self.isMetricsActive = isMetricsActive
        self.isColorsActive = isColorsActive
        self.isPreviewOn = isPreviewOn
        self.isSymmetricalEditingOn = isSymmetricalEditingOn

        self.ctrlWidth, self.ctrlHeight = posSize[2], posSize[3]

        self.wordCanvasGroup = CanvasGroup((0, 0, 0, 0),
                                           delegate=self)

    def setSymmetricalEditingMode(self, value):
        self.isSymmetricalEditingOn = value

    def setPreviewMode(self, value):
        self.isPreviewOn = value

    def setGraphicsBooleans(self, isKerningDisplayActive, areGroupsShown, areCollisionsShown, isSidebearingsActive, isMetricsActive, isColorsActive):
        self.isKerningDisplayActive = isKerningDisplayActive
        self.areGroupsShown = areGroupsShown
        self.areCollisionsShown = areCollisionsShown
        self.isSidebearingsActive = isSidebearingsActive
        self.isMetricsActive = isMetricsActive
        self.isColorsActive = isColorsActive

    def adjustSize(self, posSize):
        x, y, width, height = posSize
        self.setPosSize((x, y, width, height))
        self.wordCanvasGroup.setPosSize((0, 0, width, height))
        self.wordCanvasGroup.resize(width, height)
        self.wordCanvasGroup.update()

    def setDisplayedWord(self, displayedWord):
        self.displayedWord = displayedWord

    def setDisplayedPairs(self, displayedPairs):
        self.displayedPairs = displayedPairs

    def setScalingFactor(self, scalingFactor):
        self.canvasScalingFactor = scalingFactor

    def setActivePairIndex(self, pairIndex):
        self.pairIndex = pairIndex
        if self.pairIndex is not None:
            self.activePair = self.displayedPairs[self.pairIndex]
        else:
            self.activePair = None

    def _drawColoredCorrection(self, correction):
        dt.save()

        if correction > 0:
            dt.fill(*LIGHT_GREEN)
        else:
            dt.fill(*LIGHT_RED)
        dt.rect(0, self.fontObj.info.descender, correction, self.fontObj.info.unitsPerEm)
        dt.restore()

    def _drawMetricsCorrection(self, correction):
        dt.save()
        dt.fill(*BLACK)
        dt.stroke(None)
        dt.translate(0, self.fontObj.info.unitsPerEm+self.fontObj.info.descender+100)
        dt.scale(1/(self.getPosSize()[3]/(self.canvasScalingFactor*self.fontObj.info.unitsPerEm)))
        dt.font(SYSTEM_FONT_NAME)
        dt.fontSize(BODY_SIZE)
        textWidth, textHeight = dt.textSize('%s' % correction)
        dt.textBox('%s' % correction, (-textWidth/2., -textHeight/2., textWidth, textHeight), align='center')

        dt.restore()

    def _drawGlyphOutlines(self, glyphName):
        dt.save()
        dt.fill(*BLACK)
        dt.stroke(None)
        glyphToDisplay = self.fontObj[glyphName]
        dt.drawGlyph(glyphToDisplay)
        dt.restore()

    def _drawMetricsData(self, glyphName, offset):
        dt.save()
        glyphToDisplay = self.fontObj[glyphName]
        dt.translate(0, self.fontObj.info.descender)
        reverseScalingFactor = 1/(self.getPosSize()[3]/(self.canvasScalingFactor*self.fontObj.info.unitsPerEm))

        if self.isSidebearingsActive is True:
            dt.fill(None)
            dt.stroke(*BLACK)
            dt.strokeWidth(reverseScalingFactor)
            dt.line((0, 0), (0, -offset*reverseScalingFactor))
            dt.line((glyphToDisplay.width, 0), (glyphToDisplay.width, -offset*reverseScalingFactor))
        dt.restore()

        dt.save()
        dt.translate(0, self.fontObj.info.descender)
        dt.translate(0, -offset*reverseScalingFactor)
        dt.fill(*BLACK)

        dt.stroke(None)
        dt.font(SYSTEM_FONT_NAME)
        dt.fontSize(BODY_SIZE*reverseScalingFactor)

        textWidth, textHeight = dt.textSize(u'%s' % glyphToDisplay.width)
        dt.textBox(u'<%d>' % glyphToDisplay.width, (0, 0, glyphToDisplay.width, textHeight*2), align='center')
        dt.textBox(u'\nL%d' % glyphToDisplay.leftMargin, (0, 0, glyphToDisplay.width/2., textHeight*2), align='center')
        dt.textBox(u'\nR%d' % glyphToDisplay.rightMargin, (glyphToDisplay.width/2., 0, glyphToDisplay.width/2., textHeight*2), align='center')
        dt.restore()

    def _drawBaseline(self, glyphName):
        glyphToDisplay = self.fontObj[glyphName]

        dt.save()
        dt.stroke(*BLACK)
        dt.fill(None)
        # reversed scaling factor
        dt.strokeWidth(1/(self.getPosSize()[3]/(self.canvasScalingFactor*self.fontObj.info.unitsPerEm)))
        dt.line((0, 0), (glyphToDisplay.width, 0))
        dt.restore()

    def _drawSidebearings(self, glyphName):
        glyphToDisplay = self.fontObj[glyphName]

        dt.save()
        dt.stroke(*BLACK)
        dt.fill(None)

        # reversed scaling factor
        dt.strokeWidth(1/(self.getPosSize()[3]/(self.canvasScalingFactor*self.fontObj.info.unitsPerEm)))

        dt.fill(*LIGHT_GRAY)
        dt.line((0, self.fontObj.info.descender), (0, self.fontObj.info.descender+self.fontObj.info.unitsPerEm))
        dt.line((glyphToDisplay.width, self.fontObj.info.descender), (glyphToDisplay.width, self.fontObj.info.descender+self.fontObj.info.unitsPerEm))

        dt.restore()

    def _drawCursor(self, correction, isException):
        dt.save()
        if isException is True:
            dt.fill(*EXCEPTION_COLOR)
        else:
            dt.fill(*LIGHT_BLUE)

        lftGlyphName, rgtGlyphName = splitText(''.join(self.activePair), self.fontObj.naked().unicodeData)
        lftGlyph = self.fontObj[lftGlyphName]
        rgtGlyph = self.fontObj[rgtGlyphName]
        cursorWidth = lftGlyph.width/2. + rgtGlyph.width/2. + correction
        cursorHeight = 50   # upm
        dt.rect(-lftGlyph.width/2.-correction, self.fontObj.info.descender-cursorHeight+cursorHeight/2., cursorWidth, cursorHeight)
        dt.restore()

    def _drawGlyphOutlinesFromGroups(self, aPair, correctionKey, correction):
        prevGlyphName, eachGlyphName = aPair

        if correctionKey is not None:
            lftReference, rgtReference = correctionKey
        else:
            lftReference = whichGroup(prevGlyphName, 'lft', self.fontObj)
            rgtReference = whichGroup(eachGlyphName, 'rgt', self.fontObj)

        prevGlyph, eachGlyph = self.fontObj[prevGlyphName], self.fontObj[eachGlyphName]
        reverseScalingFactor = 1/(self.getPosSize()[3]/(self.canvasScalingFactor*self.fontObj.info.unitsPerEm))

        # _L__ group
        if lftReference:
            if lftReference.startswith('@MMK_L_'):
                dt.save()
                dt.fill(*GROUP_GLYPHS_COLOR)
                groupContent = self.fontObj.groups[lftReference]
                for eachGroupSibling in groupContent:
                    if eachGroupSibling != prevGlyphName:
                        glyphToDisplay = self.fontObj[eachGroupSibling]
                        dt.save()
                        dt.translate(-glyphToDisplay.width, 0) # back, according to his width, otherwise it does not coincide
                        dt.drawGlyph(glyphToDisplay)
                        dt.restore()

                dt.fill(*BLACK)    # caption
                dt.translate(-prevGlyph.width, 0) # we need a caption in the right place
                dt.font(SYSTEM_FONT_NAME)
                dt.fontSize(GROUP_NAME_BODY_SIZE*reverseScalingFactor)
                textWidth, textHeight = dt.textSize(lftReference)
                dt.text(lftReference, (glyphToDisplay.width/2.-textWidth/2., -GROUP_NAME_BODY_SIZE*reverseScalingFactor*2))
                dt.restore()

        # _R__ group
        if rgtReference:
            if rgtReference.startswith('@MMK_R_'):
                dt.save()
                dt.translate(correction, 0)
                dt.fill(*GROUP_GLYPHS_COLOR)
                groupContent = self.fontObj.groups[rgtReference]
                for eachGroupSibling in groupContent:
                    if eachGroupSibling != eachGlyphName:
                        glyphToDisplay = self.fontObj[eachGroupSibling]
                        dt.drawGlyph(glyphToDisplay)

                dt.fill(*BLACK)
                dt.font(SYSTEM_FONT_NAME)
                dt.fontSize(GROUP_NAME_BODY_SIZE*reverseScalingFactor)
                textWidth, textHeight = dt.textSize(rgtReference)
                dt.text(rgtReference, (glyphToDisplay.width/2.-textWidth/2., -GROUP_NAME_BODY_SIZE*reverseScalingFactor*2))
                dt.restore()

    def _drawCollisions(self, aPair):
        dt.save()
        correction, kerningKey = getCorrection(aPair, self.fontObj, getKey=True)

        if kerningKey is None:
            lftName, rgtName = aPair
        else:
            lftName, rgtName = kerningKey

        lftGlyphs = []
        if lftName.startswith('@MMK') is True:
            lftGlyphs = self.fontObj.groups[lftName]
        else:
            lftGlyphs = [lftName]

        rgtGlyphs = []
        if rgtName.startswith('@MMK') is True:
            rgtGlyphs = self.fontObj.groups[rgtName]
        else:
            rgtGlyphs = [rgtName]

        COLLISION_BODY_SIZE = 48
        dt.fontSize(COLLISION_BODY_SIZE)

        breakCycle = False
        for eachLftName in lftGlyphs:
            for eachRgtName in rgtGlyphs:
                isTouching = checkIfPairOverlaps(self.fontObj[eachLftName], self.fontObj[eachRgtName])
                if isTouching:
                    dt.text(u'💥', (0, 0))
                    breakCycle = True
                    break

            if breakCycle is True:
                break
        dt.restore()


    def draw(self):

        try:
            dt.save()

            # this is for safety reason, user should be notified about possible unwanted kerning corrections
            if self.isSymmetricalEditingOn is True:
                dt.save()
                dt.fill(*SYMMETRICAL_BACKGROUND_COLOR)
                dt.rect(0, 0, self.getPosSize()[2], self.getPosSize()[3])
                dt.restore()

            dt.scale(self.getPosSize()[3]/(self.canvasScalingFactor*self.fontObj.info.unitsPerEm))   # the canvas is virtually scaled according to self.canvasScalingFactor value and canvasSize
            dt.translate(TEXT_MARGIN, 0)

            # group glyphs
            dt.translate(0, 600)

            if self.areGroupsShown is True:
                dt.save()
                prevGlyphName = None
                glyphsToDisplay = splitText(self.displayedWord, self.fontObj.naked().unicodeData)
                for indexChar, eachGlyphName in enumerate(glyphsToDisplay):
                    eachGlyph = self.fontObj[eachGlyphName]

                    # this is for kerning
                    if indexChar > 0:
                        correctionsMap = searchCorrections((prevGlyphName, eachGlyphName), self.fontObj)
                        if 'exception' in correctionsMap:
                            correctionKey, correction = correctionsMap['exception']
                        elif 'standard' in correctionsMap:
                            correctionKey, correction = correctionsMap['standard']
                        else:
                            correctionKey, correction = None, 0

                        if (indexChar-1) == self.pairIndex:
                            self._drawGlyphOutlinesFromGroups((prevGlyphName, eachGlyphName), correctionKey, correction)

                        if correction and correction != 0:
                            dt.translate(correction, 0)

                    dt.translate(eachGlyph.width, 0)
                    prevGlyphName = eachGlyphName
                dt.restore()

            # background loop
            dt.save()
            prevGlyphName = None
            glyphsToDisplay = splitText(self.displayedWord, self.fontObj.naked().unicodeData)
            for indexChar, eachGlyphName in enumerate(glyphsToDisplay):
                eachGlyph = self.fontObj[eachGlyphName]

                # this is for kerning
                if indexChar > 0:
                    correctionsMap = searchCorrections((prevGlyphName, eachGlyphName), self.fontObj)
                    if 'exception' in correctionsMap:
                        correctionKey, correction = correctionsMap['exception']
                        isException = True
                    elif 'standard' in correctionsMap:
                        correctionKey, correction = correctionsMap['standard']
                        isException = False
                    else:
                        correctionKey, correction = None, 0
                        isException = False

                    if correction and correction != 0:
                        if self.isColorsActive is True and self.isPreviewOn is False:
                            self._drawColoredCorrection(correction)
                        if self.isMetricsActive is True and self.isPreviewOn is False:
                            self._drawMetricsCorrection(correction)
                        dt.translate(correction, 0)

                    if (indexChar-1) == self.pairIndex:
                        self._drawCursor(correction, isException)

                # # draw metrics info
                if self.isMetricsActive is True and self.isPreviewOn is False:
                    self._drawMetricsData(eachGlyphName, 52)

                if self.isSidebearingsActive is True and self.isPreviewOn is False:
                    self._drawBaseline(eachGlyphName)
                    self._drawSidebearings(eachGlyphName)

                dt.translate(eachGlyph.width, 0)
                prevGlyphName = eachGlyphName
            dt.restore()

            # foreground loop
            dt.save()
            prevGlyphName = None
            glyphsToDisplay = splitText(self.displayedWord, self.fontObj.naked().unicodeData)
            for indexChar, eachGlyphName in enumerate(glyphsToDisplay):
                eachGlyph = self.fontObj[eachGlyphName]

                # this is for kerning
                if indexChar > 0:
                    correctionsMap = searchCorrections((prevGlyphName, eachGlyphName), self.fontObj)
                    if 'exception' in correctionsMap:
                        correctionKey, correction = correctionsMap['exception']
                    elif 'standard' in correctionsMap:
                        correctionKey, correction = correctionsMap['standard']
                    else:
                        correctionKey, correction = None, 0

                    if correction and correction != 0:
                        dt.translate(correction, 0)

                    if (indexChar-1) == self.pairIndex and self.areCollisionsShown is True:
                        self._drawCollisions((prevGlyphName, eachGlyphName))

                self._drawGlyphOutlines(eachGlyphName)
                dt.translate(eachGlyph.width, 0)

                prevGlyphName = eachGlyphName
            dt.restore()

            # main restore, it wraps the three loops
            dt.restore()

        except Exception:
            print traceback.format_exc()


class WordListController(Group):
    """this controller takes good care of word list flow"""

    def __init__(self, posSize, callback):
        super(WordListController, self).__init__(posSize)
        x, y, self.ctrlWidth, self.ctrlHeight = posSize
        self.callback = callback

        # handling kerning words
        self.kerningWordsDB = loadKerningTexts(KERNING_TEXT_FOLDER)
        self.kerningTextBaseNames = self.kerningWordsDB.keys()
        self.activeKerningTextBaseName = self.kerningTextBaseNames[0]
        self.wordsWorkingList = self.kerningWordsDB[self.activeKerningTextBaseName]
        self.wordsDisplayList = list(self.wordsWorkingList)
        self.activeWord = self.wordsWorkingList[0]['word']
        self.wordFilter = ''

        jumping_Y = 0
        self.kerningVocabularyPopUp = PopUpButton((0, jumping_Y, self.ctrlWidth, vanillaControlsSize['PopUpButtonRegularHeight']),
                                                  self.kerningTextBaseNames,
                                                  callback=self.kerningVocabularyPopUpCallback)

        wordsColumnDescriptors = [
            {'title': 'word', 'width': self.ctrlWidth-60, 'editable': False},
            {'title': 'done?', 'width': 35, 'cell': CheckBoxListCell(), 'editable': False}]

        jumping_Y += self.kerningVocabularyPopUp.getPosSize()[3] + MARGIN_VER
        self.wordsListCtrl = List((0, jumping_Y, self.ctrlWidth, 200),
                                  self.wordsDisplayList,
                                  enableDelete=False,
                                  allowsMultipleSelection=False,
                                  columnDescriptions=wordsColumnDescriptors,
                                  selectionCallback=self.wordsListCtrlSelectionCallback,
                                  doubleClickCallback=self.wordsListCtrlDoubleClickCallback)

        jumping_Y += self.wordsListCtrl.getPosSize()[3] + MARGIN_VER
        self.wordsFilterCtrl = EditText((-70, jumping_Y-1, 70, vanillaControlsSize['EditTextRegularHeight']),
                                        placeholder='filter...',
                                        callback=self.wordsFilterCtrlCallback)

        self.wordsDone = len([row['done?'] for row in self.wordsWorkingList if row['done?'] != 0])
        self.infoCaption = TextBox((0, jumping_Y+2, self.ctrlWidth-self.wordsFilterCtrl.getPosSize()[2], vanillaControlsSize['TextBoxRegularHeight']),
                                   'done: %d/%d' % (self.wordsDone, len(self.wordsWorkingList)))

        jumping_Y += self.wordsFilterCtrl.getPosSize()[3] + MARGIN_VER
        self.loadStatus = SquareButton((0, jumping_Y, 90, vanillaControlsSize['ButtonRegularHeight']+2),
                                       'Load status',
                                       callback=self.loadStatusCallback)

        self.saveButton = SquareButton((-90, jumping_Y, 90, vanillaControlsSize['ButtonRegularHeight']+2),
                                       'Save status',
                                       callback=self.saveButtonCallback)

    def get(self):
        return self.activeWord

    def nextWord(self):
        activeWordData = [wordData for wordData in self.wordsDisplayList if wordData['word'] == self.activeWord][0]
        activeWordIndex = self.wordsDisplayList.index(activeWordData)
        nextWordIndex = (activeWordIndex+1)%len(self.wordsDisplayList)
        self.activeWord = self.wordsDisplayList[nextWordIndex]['word']
        self.wordsListCtrl.setSelection([nextWordIndex])

    def previousWord(self):
        activeWordData = [wordData for wordData in self.wordsDisplayList if wordData['word'] == self.activeWord][0]
        activeWordIndex = self.wordsDisplayList.index(activeWordData)
        previousWordIndex = (activeWordIndex-1)%len(self.wordsDisplayList)
        self.activeWord = self.wordsDisplayList[previousWordIndex]['word']
        self.wordsListCtrl.setSelection([previousWordIndex])

    def switchActiveWordSolvedAttribute(self):
        activeWordData = [wordData for wordData in self.wordsDisplayList if wordData['word'] == self.activeWord][0]
        activeWordIndex = self.wordsDisplayList.index(activeWordData)
        if activeWordData['done?'] == 0:
            self.wordsDisplayList[activeWordIndex] = {'done?': 1, 'word': self.activeWord}
        else:
            self.wordsDisplayList[activeWordIndex] = {'done?': 0, 'word': self.activeWord}
        self.wordsListCtrl.set(self.wordsDisplayList)
        self.wordsListCtrl.setSelection([activeWordIndex])

    def updateInfoCaption(self):
        self.infoCaption.set('done: %d/%d' % (self.wordsDone, len(self.wordsWorkingList)))

    # ctrls callbacks
    def kerningVocabularyPopUpCallback(self, sender):
        self.activeKerningTextBaseName = self.kerningTextBaseNames[sender.get()]
        self.wordsWorkingList = self.kerningWordsDB[self.activeKerningTextBaseName]
        self.activeWord = self.wordsWorkingList[0]['word']
        self.wordsListCtrl.set(self.wordsWorkingList)
        self.callback(self)

    def wordsListCtrlSelectionCallback(self, sender):
        """this takes care of word count"""
        self.wordsDisplayList = [{'word': row['word'], 'done?': row['done?']} for row in sender.get()]
        for eachDisplayedRow in self.wordsDisplayList:
            for indexWorkingRow, eachWorkingRow in enumerate(self.wordsWorkingList):
                if eachWorkingRow['word'] == eachDisplayedRow['word']:
                    self.wordsWorkingList[indexWorkingRow] = eachDisplayedRow
        self.wordsDone = len([row['done?'] for row in self.wordsWorkingList if row['done?'] != 0])
        self.updateInfoCaption()

    def wordsListCtrlDoubleClickCallback(self, sender):
        self.activeWord = self.wordsDisplayList[sender.getSelection()[0]]['word']
        self.callback(self)

    def wordsFilterCtrlCallback(self, sender):
        self.wordFilter = sender.get()
        self.wordsDisplayList = [row for row in self.wordsWorkingList if self.wordFilter in row['word']]
        self.wordsListCtrl.set(self.wordsDisplayList)
        if len(self.wordsDisplayList) == 0:
            self.activeWord = None
        else:
            if self.activeWord not in [row['word'] for row in self.wordsDisplayList]:
                self.activeWord = self.wordsDisplayList[0]['word']
        self.callback(self)

    def loadStatusCallback(self, sender):
        kerningStatusPath = getFile(title='Load Kerning Status JSON file',
                                    allowsMultipleSelection=False)[0]

        if os.path.splitext(os.path.basename(kerningStatusPath))[1] == '.json':
            jsonFile = open(kerningStatusPath, 'r')
            statusDictionary = json.load(jsonFile)
            jsonFile.close()

            # unwrap dictionaries
            self.kerningWordsDB = statusDictionary['kerningWordsDB']
            self.kerningTextBaseNames = statusDictionary['kerningTextBaseNames']
            self.activeKerningTextBaseName = statusDictionary['activeKerningTextBaseName']
            self.wordsWorkingList = statusDictionary['wordsWorkingList']
            self.wordsDisplayList = statusDictionary['wordsDisplayList']
            self.activeWord = statusDictionary['activeWord']
            self.wordFilter = statusDictionary['wordFilter']

            # adjust controllers
            self.kerningVocabularyPopUp.setItems(self.kerningTextBaseNames)
            self.kerningVocabularyPopUp.set(self.kerningTextBaseNames.index(self.activeKerningTextBaseName))
            self.wordsListCtrl.set(self.wordsDisplayList)

            for indexRow, eachRow in enumerate(self.wordsDisplayList):
                if eachRow['word'] == self.activeWord:
                    self.wordsListCtrl.setSelection([indexRow])
                    break

            self.updateInfoCaption()
            self.callback(self)

        else:
            message('No JSON, no party!', 'Chosen file is not in the right format')

    def saveButtonCallback(self, sender):
        statusDict = {
            'kerningWordsDB': self.kerningWordsDB,
            'kerningTextBaseNames': self.kerningTextBaseNames,
            'activeKerningTextBaseName': self.activeKerningTextBaseName,
            'wordsWorkingList': self.wordsWorkingList,
            'wordsDisplayList': self.wordsDisplayList,
            'activeWord': self.activeWord,
            'wordFilter': self.wordFilter}

        kerningStatusPath = putFile(title='Save Kerning Status JSON file',
                                    fileName='kerningStatus.json',
                                    canCreateDirectories=True)

        jsonFile = open(kerningStatusPath, 'w')
        json.dump(statusDict, jsonFile, indent=4)
        jsonFile.write('\n')
        jsonFile.close()

if __name__ == '__main__':
    kc = KerningController()
