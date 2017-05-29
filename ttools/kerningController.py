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

# standard
import os
import sys
import json
import types
from mojo.drawingTools import *
from mojo.roboFont import AllFonts
from mojo.canvas import CanvasGroup
from mojo.events import addObserver, removeObserver
from defconAppKit.windows.baseWindow import BaseWindowController
from vanilla import Window, Group, PopUpButton, List, EditText
from vanilla import CheckBoxListCell, TextBox, SquareButton, HorizontalLine
from vanilla import VerticalLine, CheckBox, Button
from vanilla.dialogs import message


### Constants
PLUGIN_TITLE = 'TT Kerning editor'

# func
KERNING_TEXT_FOLDER = os.path.join(os.path.dirname(__file__), 'resources', 'kerningTexts')
KERNING_STATUS_PATH = 'lastKerningStatus.json'
JOYSTICK_EVENTS = ['minusMajor', 'minusMinor', 'plusMinor', 'plusMajor', 'preview', 'solved', 'symmetricalEditing', 'keyboardEdit', 'previousWord', 'cursorUp', 'cursorLeft', 'cursorRight', 'cursorDown', 'nextWord']

MAJOR_STEP = 20
MINOR_STEP = 4

KERNING_NOT_DISPLAYED_ERROR = 'Why are you editing kerning if it is not displayed?'

# colors
BLACK = (0, 0, 0)
LIGHT_RED = (1, 0, 0, .4)
LIGHT_GREEN = (0, 1, 0, .4)
LIGHT_BLUE = (0, 0, 1, .4)
LIGHT_GRAY = (0, 0, 0, .4)
SYMMETRICAL_BACKGROUND_COLOR = (1, 0, 1, .2)

# ui
MARGIN_VER = 8
MARGIN_HOR = 8
MARGIN_COL = 4

LEFT_COLUMN = 200
PLUGIN_WIDTH = 1000
PLUGIN_HEIGHT = 800

TEXT_MARGIN = 200 #upm
CANVAS_UPM_HEIGHT = 1600.

try:
    font('.SFNSText')
    SYSTEM_FONT_NAME = '.SFNSText'
except:
    SYSTEM_FONT_NAME = '.HelveticaNeueDeskInterface-Regular'

BODY_SIZE = 14

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
def checkPairFormat(value):
    assert isinstance(value, types.TupleType), 'wrong pair format'
    assert len(value) == 2, 'wrong pair format'
    assert isinstance(value[0], types.StringType), 'wrong pair format'
    assert isinstance(value[1], types.StringType), 'wrong pair format'

class KerningController(BaseWindowController):
    """this is the main controller of TT kerning editor, it handles different controllers and dialogues with font data"""

    displayedWord = ''
    displayedPairs = []
    activePair = None

    fontsOrder = None
    navCursor_X = 0    # related to pairs
    navCursor_Y = 0    # related to active fonts

    isPreviewOn = False
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
        self.w.graphicsManager = GraphicsManager((self.jumping_X, -120, LEFT_COLUMN, 120),
                                                 self.isKerningDisplayActive,
                                                 self.isSidebearingsActive,
                                                 self.isMetricsActive,
                                                 self.isColorsActive,
                                                 callback=self.graphicsManagerCallback)

        self.jumping_X += LEFT_COLUMN+MARGIN_COL*2
        self.jumping_Y = MARGIN_VER
        self.w.displayedWordCaption = TextBox((self.jumping_X, self.jumping_Y, -1, vanillaControlsSize['TextBoxRegularHeight']),
                                              self.displayedWord)

        self.jumping_Y += self.w.displayedWordCaption.getPosSize()[3]+MARGIN_COL
        self.initWordDisplays()

        # observers!
        addObserver(self, 'openCloseFontCallback', "fontDidOpen")
        addObserver(self, 'openCloseFontCallback', "fontDidClose")
        self.w.bind("close", self.closingPlugin)
        self.w.open()

    def closingPlugin(self, sender):
        removeObserver(self, "fontDidOpen")
        removeObserver(self, "fontWillClose")

    def openCloseFontCallback(self, sender):
        if AllFonts() == []:
            message('No fonts, no party!', 'Please, open some fonts before starting the mighty MultiFont Kerning Controller')
            self.w.close()

        self.deleteWordDisplays()
        self.initFontsOrder()
        self.w.fontsOrderController.setFontsOrder(self.fontsOrder)
        self.initWordDisplays()

        prevFontsOrderPos = self.w.fontsOrderController.getPosSize()
        fontsOrderControllerHeight = FONT_ROW_HEIGHT*len(self.fontsOrder)+MARGIN_HOR
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
            print eachI

            if hasattr(self.w, 'wordCtrl_%#02d' % (eachI+1)) is True:
                delattr(self.w, 'wordCtrl_%#02d' % (eachI+1))
            else:
                print 'wordCtrl_%#02d' % (eachI+1)

        self.jumping_Y = MARGIN_VER+vanillaControlsSize['TextBoxRegularHeight']

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

            wordCtrl = WordDisplay((self.jumping_X, self.jumping_Y, rightColumnWidth, singleWindowHeight),
                                    self.displayedWord,
                                    self.displayedPairs,
                                    self.fontsOrder[eachI],
                                    self.isKerningDisplayActive,
                                    self.isSidebearingsActive,
                                    self.isMetricsActive,
                                    self.isColorsActive,
                                    self.isPreviewOn,
                                    self.isSymmetricalEditingOn,
                                    activePair=initActivePair,
                                    pairIndex=initPairIndex)

            self.jumping_Y += singleWindowHeight + MARGIN_HOR
            setattr(self.w, 'wordCtrl_%#02d' % (eachI+1), wordCtrl)

    def updateWordDisplays(self):
        for eachI in range(len(self.fontsOrder)):
            eachDisplay = getattr(self.w, 'wordCtrl_%#02d' % (eachI+1))
            eachDisplay.setDisplayedWord(self.displayedWord)
            eachDisplay.setDisplayedPairs(self.displayedPairs)
            eachDisplay.setGraphicsBooleans(self.isKerningDisplayActive, self.isSidebearingsActive, self.isMetricsActive, self.isColorsActive)
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
        selectedFont.naked().flatKerning[selectedPair] = amount

        if self.isSymmetricalEditingOn is True:
            flippedSelectedPair = selectedPair[1], selectedPair[0]
            selectedFont.naked().flatKerning[flippedSelectedPair] = amount
        self.updateWordDisplays()

    def modifyPairCorrection(self, amount):
        selectedFont = self.fontsOrder[self.navCursor_Y]
        selectedPair = tuple(self.displayedPairs[self.navCursor_X])

        if selectedPair in selectedFont.naked().flatKerning:
            selectedFont.naked().flatKerning[selectedPair] += amount
        else:
            selectedFont.naked().flatKerning[selectedPair] = amount

        if self.isSymmetricalEditingOn is True:
            flippedSelectedPair = selectedPair[1], selectedPair[0]
            if flippedSelectedPair in selectedFont.naked().flatKerning:
                selectedFont.naked().flatKerning[flippedSelectedPair] += amount
            else:
                selectedFont.naked().flatKerning[flippedSelectedPair] = amount
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

    def wordListControllerCallback(self, sender):
        self.displayedWord = sender.get()
        self.updateEditorAccordingToDiplayedWord()

    def fontsOrderControllerCallback(self, sender):
        self.deleteWordDisplays()
        self.fontsOrder = sender.getFontsOrder()
        self.initWordDisplays()

    def graphicsManagerCallback(self, sender):
        self.isKerningDisplayActive, self.isSidebearingsActive, self.isMetricsActive, self.isColorsActive = sender.get()
        self.updateWordDisplays()

    def joystickCallback(self, sender):
        joystickEvent = sender.getLastEvent()
        assert joystickEvent in JOYSTICK_EVENTS

        if joystickEvent == 'minusMajor':
            if self.isKerningDisplayActive is True:
                self.modifyPairCorrection(-MAJOR_STEP)
            else:
                self.showMessage('Be aware!', KERNING_NOT_DISPLAYED_ERROR, callback=None)

        elif joystickEvent == 'minusMinor':
            if self.isKerningDisplayActive is True:
                self.modifyPairCorrection(-MINOR_STEP)
            else:
                self.showMessage('Be aware!', KERNING_NOT_DISPLAYED_ERROR, callback=None)

        elif joystickEvent == 'plusMinor':
            if self.isKerningDisplayActive is True:
                self.modifyPairCorrection(MINOR_STEP)
            else:
                self.showMessage('Be aware!', KERNING_NOT_DISPLAYED_ERROR, callback=None)

        elif joystickEvent == 'plusMajor':
            if self.isKerningDisplayActive is True:
                self.modifyPairCorrection(MAJOR_STEP)
            else:
                self.showMessage('Be aware!', KERNING_NOT_DISPLAYED_ERROR, callback=None)

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
                self.showMessage('Be aware!', KERNING_NOT_DISPLAYED_ERROR, callback=None)
                self.w.joystick.updateCorrectionValue()



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

        if self.activePair in self.fontObj.naked().flatKerning:
            correction = self.fontObj.naked().flatKerning[self.activePair]
        else:
            correction = 0

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
        if tuple(self.activePair) in self.fontObj.naked().flatKerning:
            correction = self.fontObj.naked().flatKerning[tuple(self.activePair)]
        else:
            correction = 0
        self.activePairEditCorrection.set(correction)

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
                if self.activePair in self.fontObj.naked().flatKerning:
                    self.activePairEditCorrection.set('%s' % self.fontObj.naked().flatKerning[self.activePair])
                else:
                    self.activePairEditCorrection.set('%s' % 0)
                print traceback.format_exc()


class GraphicsManager(Group):

    previousState = None

    def __init__(self, posSize, isSidebearingsActive, isKerningDisplayActive, isMetricsActive, isColorsActive, callback):
        super(GraphicsManager, self).__init__(posSize)
        self.isKerningDisplayActive = isKerningDisplayActive
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
        return self.isKerningDisplayActive, self.isSidebearingsActive, self.isMetricsActive, self.isColorsActive

    def switchControls(self, value):
        self.showSidebearingsCheck.enable(value)
        self.showMetricsCheck.enable(value)
        self.showColorsCheck.enable(value)

    def showKerningCheckCallback(self, sender):
        self.isKerningDisplayActive = bool(sender.get())
        self.showColorsCheck.enable(bool(sender.get()))
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

    def __init__(self, posSize, displayedWord, displayedPairs, fontObj, isKerningDisplayActive, isSidebearingsActive, isMetricsActive, isColorsActive, isPreviewOn, isSymmetricalEditingOn, activePair=None, pairIndex=None):
        super(WordDisplay, self).__init__(posSize)

        self.displayedWord = displayedWord
        self.displayedPairs = displayedPairs
        self.fontObj = fontObj
        self.activePair = activePair
        self.pairIndex = pairIndex

        self.isKerningDisplayActive = isKerningDisplayActive
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

    def setGraphicsBooleans(self, isKerningDisplayActive, isSidebearingsActive, isMetricsActive, isColorsActive):
        self.isKerningDisplayActive = isKerningDisplayActive
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

    def setActivePairIndex(self, pairIndex):
        self.pairIndex = pairIndex
        if self.pairIndex is not None:
            self.activePair = self.displayedPairs[self.pairIndex]
        else:
            self.activePair = None

    def _drawColoredCorrection(self, correction):
        save()
        if correction > 0:
            fill(*LIGHT_GREEN)
        else:
            fill(*LIGHT_RED)
        rect(0, self.fontObj.info.descender, correction, self.fontObj.info.unitsPerEm)
        restore()

    def _drawMetricsCorrection(self, correction):
        save()
        fill(*BLACK)
        stroke(None)
        translate(0, self.fontObj.info.unitsPerEm+self.fontObj.info.descender+100)
        scale(1/(self.getPosSize()[3]/CANVAS_UPM_HEIGHT))
        font(SYSTEM_FONT_NAME)
        fontSize(BODY_SIZE)
        textWidth, textHeight = textSize('%s' % correction)
        textBox('%s' % correction, (-textWidth/2., -textHeight/2., textWidth, textHeight), align='center')

        restore()

    def _drawGlyphOutlines(self, glyphToDisplay):
        save()
        fill(*BLACK)
        stroke(None)
        drawGlyph(glyphToDisplay)
        restore()

    def _drawMetricsData(self, glyphToDisplay, offset):
        save()
        translate(0, self.fontObj.info.descender)
        reverseScalingFactor = self.getPosSize()[3]/CANVAS_UPM_HEIGHT

        if self.isSidebearingsActive is True:
            fill(None)
            stroke(*LIGHT_GRAY)
            strokeWidth(1/reverseScalingFactor)
            line((0, 0), (0, -offset*1/reverseScalingFactor))
            line((glyphToDisplay.width, 0), (glyphToDisplay.width, -offset*1/reverseScalingFactor))

        scale(1/reverseScalingFactor)
        translate(0, -offset)
        fill(*BLACK)
        stroke(None)
        font(SYSTEM_FONT_NAME)
        fontSize(BODY_SIZE)
        textWidth, textHeight = textSize(u'%s' % glyphToDisplay.width)
        textBox(u'%d' % glyphToDisplay.width, (0, 11, glyphToDisplay.width*reverseScalingFactor, textHeight), align='center')
        textBox(u'%d' % glyphToDisplay.leftMargin, (0, 0, glyphToDisplay.width/2.*reverseScalingFactor, textHeight), align='center')
        textBox(u'%d' % glyphToDisplay.rightMargin, (glyphToDisplay.width/2.*reverseScalingFactor, 0, glyphToDisplay.width/2.*reverseScalingFactor, textHeight), align='center')
        restore()

    def _drawBaseline(self, glyphToDisplay):
        save()
        stroke(*LIGHT_GRAY)
        fill(None)
        strokeWidth(1/(self.getPosSize()[3]/CANVAS_UPM_HEIGHT))
        line((0, 0), (glyphToDisplay.width, 0))
        restore()

    def _drawSidebearings(self, glyphToDisplay):
        save()
        stroke(*LIGHT_GRAY)
        fill(None)
        strokeWidth(1/(self.getPosSize()[3]/CANVAS_UPM_HEIGHT))

        line((0, self.fontObj.info.descender), (0, self.fontObj.info.descender+self.fontObj.info.unitsPerEm))
        line((glyphToDisplay.width, self.fontObj.info.descender), (glyphToDisplay.width, self.fontObj.info.descender+self.fontObj.info.unitsPerEm))

        restore()

    def _drawCursor(self, correction):
        save()
        lftGlyphName, rgtGlyphName = self.activePair
        fill(*LIGHT_BLUE)
        lftGlyph = self.fontObj[lftGlyphName]
        rgtGlyph = self.fontObj[rgtGlyphName]
        cursorWidth = lftGlyph.width/2. + rgtGlyph.width/2. + correction
        cursorHeight = 50   # upm
        rect(-lftGlyph.width/2.-correction, self.fontObj.info.descender-cursorHeight+cursorHeight/2., cursorWidth, cursorHeight)
        restore()

    def draw(self):
        try:
            save()

            # this is for safety reason, user should be notified about possible unwanted kerning corrections
            if self.isSymmetricalEditingOn is True:
                save()
                fill(*SYMMETRICAL_BACKGROUND_COLOR)
                rect(0, 0, self.getPosSize()[2], self.getPosSize()[3])
                restore()

            scale(self.getPosSize()[3]/CANVAS_UPM_HEIGHT)   # the canvas is virtually scaled according to CANVAS_UPM_HEIGHT value and canvasSize
            translate(TEXT_MARGIN, 0)

            flatKerning = self.fontObj.naked().flatKerning

            # background loop
            translate(0, 600)
            save()
            prevGlyphName = None
            for indexChar, eachGlyphName in enumerate(self.displayedWord):
                glyphToDisplay = self.fontObj[eachGlyphName]

                # this is for kerning
                if indexChar > 0:
                    if (prevGlyphName, eachGlyphName) in flatKerning and self.isKerningDisplayActive is True:
                        correction = flatKerning[(prevGlyphName, eachGlyphName)]
                        if correction != 0:

                            if self.isColorsActive is True and self.isPreviewOn is False:
                                self._drawColoredCorrection(correction)
                            if self.isMetricsActive is True and self.isPreviewOn is False:
                                self._drawMetricsCorrection(correction)

                            translate(correction, 0)
                    else:
                        correction = 0

                    if (indexChar-1) == self.pairIndex:
                        self._drawCursor(correction)

                # # draw metrics info
                if self.isMetricsActive is True and self.isPreviewOn is False:
                    self._drawMetricsData(glyphToDisplay, 33)

                if self.isSidebearingsActive is True and self.isPreviewOn is False:
                    self._drawBaseline(glyphToDisplay)
                    self._drawSidebearings(glyphToDisplay)

                translate(glyphToDisplay.width, 0)
                prevGlyphName = eachGlyphName
            restore()

            # foreground loop
            save()
            prevGlyphName = None
            for indexChar, eachGlyphName in enumerate(self.displayedWord):
                glyphToDisplay = self.fontObj[eachGlyphName]

                # this is for kerning
                if indexChar > 0:
                    if (prevGlyphName, eachGlyphName) in flatKerning and self.isKerningDisplayActive is True:
                        correction = flatKerning[(prevGlyphName, eachGlyphName)]
                        if correction != 0:
                            translate(correction, 0)

                self._drawGlyphOutlines(glyphToDisplay)
                translate(glyphToDisplay.width, 0)
                prevGlyphName = eachGlyphName
            restore()

            restore()

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
        if os.path.exists(KERNING_STATUS_PATH) is True:
            jsonFile = open(KERNING_STATUS_PATH, 'r')
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

            # print 
            self.kerningVocabularyPopUp.set(self.kerningTextBaseNames.index(self.activeKerningTextBaseName))
            self.wordsListCtrl.set(self.wordsDisplayList)
            self.wordsListCtrl.setSelection([self.wordsDisplayList.index(self.activeWord)])
            self.updateInfoCaption()

        else:
            print 'there is no previous status to load'

    def saveButtonCallback(self, sender):
        statusDict = {
            'kerningWordsDB': self.kerningWordsDB,
            'kerningTextBaseNames': self.kerningTextBaseNames,
            'activeKerningTextBaseName': self.activeKerningTextBaseName,
            'wordsWorkingList': self.wordsWorkingList,
            'wordsDisplayList': self.wordsDisplayList,
            'activeWord': self.activeWord,
            'wordFilter': self.wordFilter}
        jsonFile = open(KERNING_STATUS_PATH, 'w')
        json.dump(statusDict, jsonFile, indent=4)
        jsonFile.write('\n')
        jsonFile.close()

if __name__ == '__main__':
    kc = KerningController()
