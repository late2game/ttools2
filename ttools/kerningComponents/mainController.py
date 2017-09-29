#!/usr/bin/env python
# coding: utf-8

###############################
# This is the main controller #
###############################

### Modules
# components
import factor
reload(factor)
from factor import FactorController

import graphicsManager
reload(graphicsManager)
from graphicsManager import GraphicsManager

import joystick
reload(joystick)
from joystick import JoystickController

import wordDisplay
reload(wordDisplay)
from wordDisplay import WordDisplay

import wordList
reload(wordList)
from wordList import WordListController

import chooseException
reload(chooseException)
from chooseException import ChooseExceptionWindow

import jumpToLine
reload(jumpToLine)
from jumpToLine import JumpToLineWindow

# custom
from ..ui import userInterfaceValues
reload(userInterfaceValues)
from ..ui.userInterfaceValues import vanillaControlsSize

from ..ui import uiControllers
reload(uiControllers)
from ..ui.uiControllers import FontsOrderController, FONT_ROW_HEIGHT

import kerningMisc
reload(kerningMisc)
from kerningMisc import checkPairFormat, getCorrection, findSymmetricalPair
from kerningMisc import buildPairsFromString, setCorrection, setRawCorrection
from kerningMisc import MAJOR_STEP, MINOR_STEP
from kerningMisc import MARGIN_VER, MARGIN_HOR, MARGIN_COL
from kerningMisc import CANVAS_SCALING_FACTOR_INIT

import exceptionTools
reload(exceptionTools)
from exceptionTools import checkGroupConflicts, possibleExceptions

# standard
import os
import traceback
import types
import logging
from datetime import datetime
from mojo.roboFont import AllFonts
from mojo.events import addObserver, removeObserver
from defconAppKit.windows.baseWindow import BaseWindowController
from defconAppKit.tools.textSplitter import splitText
from vanilla import Window, TextBox, HorizontalLine
from vanilla.dialogs import message

### Constants
PLUGIN_TITLE = 'TT Kerning editor'

# func
JOYSTICK_EVENTS = ['exceptionTrigger', 'verticalAlignedEditing', 'minusMajor', 'minusMinor',
                   'plusMinor', 'plusMajor', 'preview', 'solved', 'symmetricalEditing',
                   'flippedEditing', 'keyboardEdit', 'previousWord', 'cursorUp', 'cursorLeft',
                   'cursorRight', 'cursorDown', 'nextWord', 'deletePair', 'switchLftGlyph',
                   'switchRgtGlyph', 'undo', 'redo', 'autoSave', 'jumpToLineTrigger']

KERNING_NOT_DISPLAYED_ERROR = 'Why are you editing kerning if it is not displayed?'

# log messages
SET_CORRECTION_LOG = '%(leftGlyphName)s%(rightGlyphName)s from %(familyName)s %(styleName)s set to %(amount)s'

# ui
LEFT_COLUMN = 200
PLUGIN_WIDTH = 1000
PLUGIN_HEIGHT = 960


### Controllers
class KerningController(BaseWindowController):
    """this is the main controller of TT kerning editor, it handles different controllers and dialogues with font data"""

    # these attributes take good care of undo/redo stack
    archive = []
    recordIndex = 0

    displayedWord = ''
    displayedPairs = []
    activePair = None

    canvasScalingFactor = CANVAS_SCALING_FACTOR_INIT

    fontsOrder = None
    navCursor_X = 0    # related to pairs
    navCursor_Y = 0    # related to active fonts

    isPreviewOn = False
    areVerticalLettersDrawn = True
    areGroupsShown = True
    areCollisionsShown = False
    isKerningDisplayActive = True
    isSidebearingsActive = True
    isMetricsActive = True
    isColorsActive = True

    isSymmetricalEditingOn = False
    isFlippedEditingOn = False
    isVerticalAlignedEditingOn = False

    autoSave = True
    autoSaveSpan = 5  # mins

    kerningLogger = None

    def __init__(self):
        super(KerningController, self).__init__()
        # init time for the autosave
        self.initTime = datetime.now()
        # init logging
        self.initLogger()
        # init fonts
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
        self.exceptionWindow = ChooseExceptionWindow(['group2glyph', 'glyph2group', 'glyph2glyph'],
                                               callback=self.exceptionWindowCallback)
        self.exceptionWindow.enable(False)

        # jump to line window (will appear only if invoked)
        self.jumpToLineWindow = JumpToLineWindow(callback=self.jumpToLineWindowCallback)
        self.jumpToLineWindow.enable(False)

        self.jumping_Y = MARGIN_VER
        self.jumping_X = MARGIN_HOR
        self.w.wordListController = WordListController((self.jumping_X, self.jumping_Y, LEFT_COLUMN, 260),
                                                       callback=self.wordListControllerCallback)
        self.displayedWord = self.w.wordListController.get()

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
        self.w.joystick = JoystickController((self.jumping_X, self.jumping_Y, LEFT_COLUMN, 348),
                                             fontObj=self.fontsOrder[self.navCursor_Y],
                                             isSymmetricalEditingOn=self.isSymmetricalEditingOn,
                                             isFlippedEditingOn=self.isFlippedEditingOn,
                                             isVerticalAlignedEditingOn=self.isVerticalAlignedEditingOn,
                                             autoSave=self.autoSave,
                                             autoSaveSpan=self.autoSaveSpan,
                                             activePair=None,
                                             callback=self.joystickCallback)

        self.jumping_Y += self.w.joystick.getPosSize()[3] + MARGIN_VER
        self.w.graphicsManager = GraphicsManager((self.jumping_X, -184, LEFT_COLUMN, 184),
                                                 isKerningDisplayActive=self.isKerningDisplayActive,
                                                 areVerticalLettersDrawn=self.areVerticalLettersDrawn,
                                                 areGroupsShown=self.areGroupsShown,
                                                 areCollisionsShown=self.areCollisionsShown,
                                                 isSidebearingsActive=self.isSidebearingsActive,
                                                 isMetricsActive=self.isMetricsActive,
                                                 isColorsActive=self.isColorsActive,
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
        self.w.joystick.setActivePair(self.getActiveWordDisplay().getActivePair())

        # observers!
        addObserver(self, 'openCloseFontCallback', "fontDidOpen")
        addObserver(self, 'openCloseFontCallback', "fontDidClose")
        self.setUpBaseWindowBehavior()
        self.w.open()

    def initLogger(self):
        # create a logger
        self.kerningLogger = logging.getLogger('kerningLogger')
        self.kerningLogger.setLevel(logging.INFO)
        # create file handler which logs info messages
        fileHandle = logging.FileHandler('kerningLogger.log')
        fileHandle.setLevel(logging.INFO)
        # create console handler with a higher log level, only errors
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(logging.ERROR)
        # create formatter and add it to the handlers
        formatter = logging.Formatter(u'%(asctime)s – %(message)s')
        fileHandle.setFormatter(formatter)
        consoleHandler.setFormatter(formatter)
        # add the handlers to the logger
        self.kerningLogger.addHandler(fileHandle)
        self.kerningLogger.addHandler(consoleHandler)

    def windowCloseCallback(self, sender):
        removeObserver(self, "fontDidOpen")
        removeObserver(self, "fontWillClose")
        self.exceptionWindow.close()
        super(KerningController, self).windowCloseCallback(sender)
        self.w.close()

    def openCloseFontCallback(self, sender):
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

        for eachFont in self.fontsOrder:
            status, report = checkGroupConflicts(eachFont)
            if status is False:
                self.kerningLogger.error('groups conflict in %s' % eachFont.path)
                self.kerningLogger.error(report)

    def deleteWordDisplays(self):
        for eachI in xrange(len(self.fontsOrder)):
            try:
                delattr(self.w, 'wordCtrl_%#02d' % (eachI+1))
                self.jumping_Y = MARGIN_VER+vanillaControlsSize['TextBoxRegularHeight']
            except Exception as e:
                self.kerningLogger.error(traceback.format_exc())

    def initWordDisplays(self):
        windowWidth, windowHeight = self.w.getPosSize()[2], self.w.getPosSize()[3]
        netTotalWindowHeight = windowHeight-MARGIN_COL-MARGIN_VER*2-vanillaControlsSize['TextBoxRegularHeight']-MARGIN_HOR*(len(self.fontsOrder)-1)
        
        try:
            singleWindowHeight = netTotalWindowHeight/len(self.fontsOrder)
        except ZeroDivisionError:
            singleWindowHeight = 0

        rightColumnWidth = windowWidth-LEFT_COLUMN-MARGIN_COL

        self.jumping_Y = MARGIN_VER+vanillaControlsSize['TextBoxRegularHeight']+MARGIN_COL
        for eachI in xrange(len(self.fontsOrder)):

            if eachI == self.navCursor_Y:
                initPairIndex = self.navCursor_X
            else:
                initPairIndex = None

            try:
                wordCtrl = WordDisplay((self.jumping_X, self.jumping_Y, rightColumnWidth, singleWindowHeight),
                                       displayedWord=self.displayedWord,
                                       canvasScalingFactor=self.canvasScalingFactor,
                                       fontObj=self.fontsOrder[eachI],
                                       isKerningDisplayActive=self.isKerningDisplayActive,
                                       areVerticalLettersDrawn=self.areVerticalLettersDrawn,
                                       areGroupsShown=self.areGroupsShown,
                                       areCollisionsShown=self.areCollisionsShown,
                                       isSidebearingsActive=self.isSidebearingsActive,
                                       isMetricsActive=self.isMetricsActive,
                                       isColorsActive=self.isColorsActive,
                                       isPreviewOn=self.isPreviewOn,
                                       isSymmetricalEditingOn=self.isSymmetricalEditingOn,
                                       isFlippedEditingOn=self.isFlippedEditingOn,
                                       indexPair=initPairIndex)

            except Exception:
                self.kerningLogger.error(traceback.format_exc())

            self.jumping_Y += singleWindowHeight + MARGIN_HOR
            setattr(self.w, 'wordCtrl_%#02d' % (eachI+1), wordCtrl)

    def updateWordDisplays(self):
        for eachI in xrange(len(self.fontsOrder)):
            eachDisplay = getattr(self.w, 'wordCtrl_%#02d' % (eachI+1))
            eachDisplay.setSymmetricalEditingMode(self.isSymmetricalEditingOn)
            eachDisplay.setFlippedEditingMode(self.isFlippedEditingOn)
            eachDisplay.setScalingFactor(self.canvasScalingFactor)
            eachDisplay.setGraphicsBooleans(self.isKerningDisplayActive, self.areVerticalLettersDrawn, self.areGroupsShown, self.areCollisionsShown, self.isSidebearingsActive, self.isMetricsActive, self.isColorsActive)
            eachDisplay.setPreviewMode(self.isPreviewOn)
            eachDisplay.wordCanvasGroup.update()

    def nextWord(self, isRecording=True):
        self.w.wordListController.nextWord()
        self.displayedWord = self.w.wordListController.get()
        self.isFlippedEditingOn = False
        self.w.joystick.setFlippedEditing(self.isFlippedEditingOn)
        self.updateEditorAccordingToDiplayedWord()
        if isRecording is True:
            self.appendRecord('nextWord')

    def previousWord(self, isRecording=True):
        self.w.wordListController.previousWord()
        self.displayedWord = self.w.wordListController.get()
        self.isFlippedEditingOn = False
        self.w.joystick.setFlippedEditing(self.isFlippedEditingOn)
        self.updateEditorAccordingToDiplayedWord()
        if isRecording is True:
            self.appendRecord('previousWord')

    def jumpToLine(self, lineIndex, isRecording=True):
        if isRecording is True:
            self.appendRecord('jumpToLine', (self.w.wordListController.getActiveIndex(), lineIndex))

        self.w.wordListController.jumpToLine(lineIndex)
        self.displayedWord = self.w.wordListController.get()
        self.isFlippedEditingOn = False
        self.w.joystick.setFlippedEditing(self.isFlippedEditingOn)
        self.updateEditorAccordingToDiplayedWord()

    def oneStepGroupSwitch(self, location):
        if self.isVerticalAlignedEditingOn is True:
            for eachI in xrange(len(self.fontsOrder)):
                eachDisplay = getattr(self.w, 'wordCtrl_%#02d' % (eachI+1))
                eachDisplay.switchGlyphFromGroup(location, self.navCursor_X)
        else:
            self.getActiveWordDisplay().switchGlyphFromGroup(location, self.navCursor_X)
        self.w.joystick.setActivePair(self.getActiveWordDisplay().getActivePair())

    def updateEditorAccordingToDiplayedWord(self):
        self.w.displayedWordCaption.set(self.displayedWord)
        if len(self.displayedWord)-1 < (self.navCursor_X+1):
            self.navCursor_X = len(self.displayedWord)-2
        for eachI in xrange(len(self.fontsOrder)):
            eachDisplay = getattr(self.w, 'wordCtrl_%#02d' % (eachI+1))

            if self.isVerticalAlignedEditingOn is False:
                if eachI == self.navCursor_Y:
                    eachDisplay.setActivePairIndex(self.navCursor_X)
            else:
                eachDisplay.setActivePairIndex(self.navCursor_X)

            eachDisplay.setDisplayedWord(self.displayedWord)
        self.updateWordDisplays()

        self.getActiveWordDisplay().setActivePairIndex(self.navCursor_X)
        self.w.joystick.setActivePair(self.getActiveWordDisplay().getActivePair())

    def getActiveWordDisplay(self):
        return getattr(self.w, 'wordCtrl_%#02d' % (self.navCursor_Y+1))

    def switchPreviewAttribute(self, isRecording=True):
        if self.isPreviewOn is True:
            self.isPreviewOn = False
            self.w.graphicsManager.switchControls(True)
        else:
            self.isPreviewOn = True
            self.w.graphicsManager.switchControls(False)
        self.updateWordDisplays()
        if isRecording is True:
            self.appendRecord('preview')

    def switchSolvedAttribute(self, isRecording=True):
        self.w.wordListController.switchActiveWordSolvedAttribute()
        if isRecording is True:
            self.appendRecord('solved')

    def switchFlippedEditing(self, isRecording=True):
        self.isFlippedEditingOn = not self.isFlippedEditingOn
        if self.isFlippedEditingOn is True and self.isSymmetricalEditingOn is True:
            self.isSymmetricalEditingOn = False
            self.w.joystick.setSymmetricalEditing(self.isSymmetricalEditingOn)
        self.updateWordDisplays()
        if isRecording is True:
            self.appendRecord('flippedEditing')

    def switchSymmetricalEditing(self, isRecording=True):
        self.isSymmetricalEditingOn = not self.isSymmetricalEditingOn
        if self.isFlippedEditingOn is True and self.isSymmetricalEditingOn is True:
            self.isFlippedEditingOn = False
            self.w.joystick.setFlippedEditing(self.isFlippedEditingOn)
        self.updateWordDisplays()
        if isRecording is True:
            self.appendRecord('symmetricalEditing')

    def switchVerticalAlignedEditing(self, isRecording=True):
        self.isVerticalAlignedEditingOn = not self.isVerticalAlignedEditingOn
        for eachI in xrange(len(self.fontsOrder)):
            eachDisplay = getattr(self.w, 'wordCtrl_%#02d' % (eachI+1))
            if self.isVerticalAlignedEditingOn is True:
                eachDisplay.setActivePairIndex(self.navCursor_X)
            else:
                if eachI != self.navCursor_Y:
                    eachDisplay.setActivePairIndex(None)
        self.updateWordDisplays()
        if isRecording is True:
            self.appendRecord('verticalAlignedEditing')

    def exceptionTrigger(self):
        selectedFont = self.fontsOrder[self.navCursor_Y]
        selectedPair = self.getActiveWordDisplay().getActivePair()
        correction, kerningReference, pairKind = getCorrection(selectedPair, selectedFont)

        if correction:
            exceptionOptions = possibleExceptions(selectedPair, kerningReference, selectedFont)
            if exceptionOptions:
                self.exceptionWindow.setOptions(exceptionOptions)
                self.exceptionWindow.enable(True)
            else:
                self.showMessage('no possible exceptions', 'kerning exceptions can be triggered only starting from class kerning')
        else:
            self.showMessage('no kerning pair, no exception!', 'kerning exceptions can be triggered only starting from class kerning')

    # manipulate data
    def setPairCorrection(self, amount, isRecording=True):
        if self.autoSave is True:
            self.checkAutoSave()

        selectedPair = self.getActiveWordDisplay().getActivePair()
        if self.isVerticalAlignedEditingOn is True:
            selectedFonts = self.fontsOrder
        else:
            selectedFonts = [self.fontsOrder[self.navCursor_Y]]

        for eachFont in selectedFonts:
            if isRecording is True:
                previousAmount = getCorrection(selectedPair, eachFont)[0]
                self.appendRecord('setCorrection', (selectedPair, eachFont, previousAmount))
            setCorrection(selectedPair, eachFont, amount)
            self.kerningLogger.info(SET_CORRECTION_LOG % {'leftGlyphName': selectedPair[0], 'rightGlyphName': selectedPair[1], 'familyName': eachFont.info.familyName, 'styleName': eachFont.info.styleName, 'amount': amount})

            if self.isFlippedEditingOn is True:
                flippedCorrectionKey = selectedPair[1], selectedPair[0]
                if isRecording is True:
                    previousAmount = getCorrection(flippedCorrectionKey, eachFont)[0]
                    self.appendRecord('setCorrection', (flippedCorrectionKey, eachFont, previousAmount))
                setCorrection(flippedCorrectionKey, eachFont, amount)
                self.kerningLogger.info(SET_CORRECTION_LOG % {'leftGlyphName': flippedCorrectionKey[0], 'rightGlyphName': flippedCorrectionKey[1], 'familyName': eachFont.info.familyName, 'styleName': eachFont.info.styleName, 'amount': amount})

            if self.isSymmetricalEditingOn is True:
                symmetricalCorrectionKey = findSymmetricalPair(selectedPair)
                if symmetricalCorrectionKey:
                    if isRecording is True:
                        previousAmount = getCorrection(symmetricalCorrectionKey, eachFont)[0]
                        self.appendRecord('setCorrection', (symmetricalCorrectionKey, eachFont, previousAmount))
                    setCorrection(symmetricalCorrectionKey, eachFont, amount)
                    self.kerningLogger.info(SET_CORRECTION_LOG % {'leftGlyphName': symmetricalCorrectionKey[0], 'rightGlyphName': symmetricalCorrectionKey[1], 'familyName': eachFont.info.familyName, 'styleName': eachFont.info.styleName, 'amount': amount})

        self.updateWordDisplays()

    def modifyPairCorrection(self, amount, isRecording=True):
        if self.autoSave is True:
            self.checkAutoSave()

        selectedPair = self.getActiveWordDisplay().getActivePair()
        
        if self.isVerticalAlignedEditingOn is True:
            selectedFonts = self.fontsOrder
        else:
            selectedFonts = [self.fontsOrder[self.navCursor_Y]]

        for eachFont in selectedFonts:
            correction, correctionKey, pairKind = getCorrection(selectedPair, eachFont)
            if isRecording is True:
                previousAmount = getCorrection(selectedPair, eachFont)[0]
                self.appendRecord('setCorrection', (selectedPair, eachFont, previousAmount))
            setCorrection(selectedPair, eachFont, correction+amount)
            self.kerningLogger.info(SET_CORRECTION_LOG % {'leftGlyphName': selectedPair[0], 'rightGlyphName': selectedPair[1], 'familyName': eachFont.info.familyName, 'styleName': eachFont.info.styleName, 'amount': amount})

            if self.isFlippedEditingOn is True:
                flippedPair = selectedPair[1], selectedPair[0]
                if isRecording is True:
                    previousAmount = getCorrection(selectedPair, eachFont)[0]
                    self.appendRecord('setCorrection', (flippedPair, eachFont, previousAmount))
                setCorrection(flippedPair, eachFont, correction+amount)
                self.kerningLogger.info(SET_CORRECTION_LOG % {'leftGlyphName': flippedPair[0], 'rightGlyphName': flippedPair[1], 'familyName': eachFont.info.familyName, 'styleName': eachFont.info.styleName, 'amount': amount})

            if self.isSymmetricalEditingOn is True:
                symmetricalCorrectionKey = findSymmetricalPair(selectedPair)
                if symmetricalCorrectionKey:
                    if isRecording is True:
                        previousAmount = getCorrection(symmetricalCorrectionKey, eachFont)[0]
                        self.appendRecord('setCorrection', (symmetricalCorrectionKey, eachFont, previousAmount))
                    setCorrection(symmetricalCorrectionKey, eachFont, correction+amount)
                    self.kerningLogger.info(SET_CORRECTION_LOG % {'leftGlyphName': symmetricalCorrectionKey[0], 'rightGlyphName': symmetricalCorrectionKey[1], 'familyName': eachFont.info.familyName, 'styleName': eachFont.info.styleName, 'amount': amount})

        self.w.joystick.updateCorrectionValue()
        self.updateWordDisplays()

    # cursor methods
    def cursorLeftRight(self, direction, isRecording=True):
        assert direction in ['left', 'right']

        if direction == 'left':
            step = -1
            if isRecording is True:
                self.appendRecord('cursorLeft')
        else:
            step = +1
            if isRecording is True:
                self.appendRecord('cursorRight')

        self.navCursor_X = (self.navCursor_X+step)%(len(self.displayedWord)-1)
        for eachI in xrange(len(self.fontsOrder)):
            eachDisplay = getattr(self.w, 'wordCtrl_%#02d' % (eachI+1))
            if self.isVerticalAlignedEditingOn is False:
                if eachI == self.navCursor_Y:
                    eachDisplay.setActivePairIndex(self.navCursor_X)
            else:
                eachDisplay.setActivePairIndex(self.navCursor_X)
        self.w.joystick.setActivePair(self.getActiveWordDisplay().getActivePair())
        self.updateWordDisplays()

    def cursorUpDown(self, direction, isRecording=True):
        assert direction in ['up', 'down']
        if direction == 'up':
            step = -1
            if isRecording is True:
                self.appendRecord('cursorUp')
        else:
            step = +1
            if isRecording is True:
                self.appendRecord('cursorDown')

        if self.isVerticalAlignedEditingOn is False:
            self.getActiveWordDisplay().setActivePairIndex(None)               # old
            self.navCursor_Y = (self.navCursor_Y+step)%len(self.fontsOrder)
            self.getActiveWordDisplay().setActivePairIndex(self.navCursor_X)   # new
            self.w.joystick.setFontObj(self.fontsOrder[self.navCursor_Y])
            self.updateWordDisplays()

    ### callbacks
    def exceptionWindowCallback(self, sender):
        if self.isVerticalAlignedEditingOn is False:
            selectedFonts = [self.fontsOrder[self.navCursor_Y]]
        else:
            selectedFonts = self.fontsOrder
        selectedPair = self.getActiveWordDisplay().getActivePair()
        if sender.lastEvent == 'submit':
            for indexFont, eachFont in enumerate(selectedFonts):
                exceptionKey = sender.get()
                correction, kerningReference, pairKind = getCorrection(selectedPair, eachFont)
                setRawCorrection(exceptionKey, eachFont, correction)
                if indexFont == self.navCursor_Y:
                    self.w.joystick.updateCorrectionValue()
            self.updateWordDisplays()

    def jumpToLineWindowCallback(self, sender):
        if sender.get() is not None:
            self.jumpToLine(sender.get())
        self.jumpToLineWindow.enable(False)

    def mainWindowResize(self, mainWindow):
        windowWidth, windowHeight = mainWindow.getPosSize()[2], mainWindow.getPosSize()[3]
        rightColumnWidth = windowWidth - LEFT_COLUMN

        # caption
        prevdisplayedWordCaptionSize = self.w.displayedWordCaption.getPosSize()
        self.w.displayedWordCaption.setPosSize((prevdisplayedWordCaptionSize[0], prevdisplayedWordCaptionSize[1], rightColumnWidth, prevdisplayedWordCaptionSize[3]))

        # displayers
        initY = MARGIN_VER+vanillaControlsSize['TextBoxRegularHeight']+MARGIN_COL
        netTotalWindowHeight = windowHeight-initY-MARGIN_VER-MARGIN_HOR*(len(self.fontsOrder)-1)

        try:
            singleWordDisplayHeight = netTotalWindowHeight/len(self.fontsOrder)
        except ZeroDivisionError:
            singleWordDisplayHeight = 0

        y = initY
        for eachI in xrange(len(self.fontsOrder)):
            eachDisplay = getattr(self.w, 'wordCtrl_%#02d' % (eachI+1))
            eachDisplay.adjustSize((self.jumping_X, y, rightColumnWidth, singleWordDisplayHeight))
            eachDisplay.setCtrlSize(rightColumnWidth, singleWordDisplayHeight)
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
        self.isKerningDisplayActive, self.areVerticalLettersDrawn, self.areGroupsShown, self.areCollisionsShown, self.isSidebearingsActive, self.isMetricsActive, self.isColorsActive = sender.get()
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
            self.switchPreviewAttribute()

        elif joystickEvent == 'solved':
            self.switchSolvedAttribute()
            self.nextWord()

        elif joystickEvent == 'symmetricalEditing':
            self.switchSymmetricalEditing()
            
        elif joystickEvent == 'flippedEditing':
            self.switchFlippedEditing()

        elif joystickEvent == 'verticalAlignedEditing':
            self.switchVerticalAlignedEditing()

        elif joystickEvent == 'previousWord':
            self.previousWord()

        elif joystickEvent == 'cursorUp':
            self.cursorUpDown('up')

        elif joystickEvent == 'cursorLeft':
            self.cursorLeftRight('left')
            
        elif joystickEvent == 'cursorRight':
            self.cursorLeftRight('right')

        elif joystickEvent == 'cursorDown':
            self.cursorUpDown('down')

        elif joystickEvent == 'nextWord':
            self.nextWord()

        elif joystickEvent == 'deletePair':
            if self.isKerningDisplayActive is True:
                self.setPairCorrection(0)
                self.w.joystick.setActivePair(self.getActiveWordDisplay().getActivePair())

        elif joystickEvent == 'switchLftGlyph':
            self.oneStepGroupSwitch(location='left')

        elif joystickEvent == 'switchRgtGlyph':
            self.oneStepGroupSwitch(location='right')

        elif joystickEvent == 'keyboardEdit':
            if self.isKerningDisplayActive is True:
                correctionAmount = self.w.joystick.getKeyboardCorrection()
                self.setPairCorrection(correctionAmount)
                self.updateWordDisplays()
            else:
                self.showMessage('Be aware!', KERNING_NOT_DISPLAYED_ERROR, callback=None)
                self.w.joystick.updateCorrectionValue()

        elif joystickEvent == 'jumpToLineTrigger':
            self.jumpToLineWindow.enable(True)

        # from here on events are not archived in undo/redo stack
        elif joystickEvent == 'exceptionTrigger':
            self.exceptionTrigger()

        elif joystickEvent == 'undo':
            self.undo()

        elif joystickEvent == 'redo':
            self.redo()

        elif joystickEvent == 'autoSave':
            self.autoSave, self.autoSaveSpan = self.w.joystick.getAutoSaveState()

    # autosaving fonts
    def checkAutoSave(self):
        justNow = datetime.now()
        if (justNow - self.initTime).seconds > self.autoSaveSpan*60:
            self.saveFontsOrder()
            self.initTime = datetime.now()

    def saveFontsOrder(self):
        for eachFont in self.fontsOrder:
            eachFont.save()
        self.kerningLogger.info("all fonts saved")

    # undo/redo stack
    def appendRecord(self, actionName, data=None):
        if self.recordIndex < 0:
            self.archive = self.archive[:self.recordIndex]
            self.recordIndex = 0
        if data is None:
            self.archive.append(actionName)
        else:
            self.archive.append((actionName, data))

    def undo(self):
        if abs(self.recordIndex) <= len(self.archive)-1:
            self.recordIndex -= 1
            self.pullRecordFromArchive('undo')

    def redo(self):
        if self.recordIndex < 0:
            self.recordIndex += 1
            self.pullRecordFromArchive('redo')

    def pullRecordFromArchive(self, direction):
        """we miss these methods: switchLftGlyph, switchRgtGlyph"""

        assert direction in ['redo', 'undo']
        if direction == 'redo':
            record = self.archive[self.recordIndex-1]   # othwerwise we won't get back to the initial status
        else:
            record = self.archive[self.recordIndex]

        # these records, we can simply invert (they related to events in UI)
        if isinstance(record, types.StringType) is True:
            if record == 'nextWord':
                if direction == 'undo':
                    self.previousWord(isRecording=False)
                else:
                    self.nextWord(isRecording=False)
            elif record == 'previousWord':
                if direction == 'undo':
                    self.nextWord(isRecording=False)
                else:
                    self.previousWord(isRecording=False)
            elif record == 'preview':
                self.switchPreviewAttribute(isRecording=False)
            elif record == 'solved':
                self.switchSolvedAttribute(isRecording=False)
            elif record == 'flippedEditing':
                self.switchFlippedEditing(isRecording=False)
            elif record == 'symmetricalEditing':
                self.switchSymmetricalEditing(isRecording=False)
            elif record == 'verticalAlignedEditing':
                self.switchVerticalAlignedEditing(isRecording=False)

            elif record == 'cursorLeft':
                if direction == 'undo':
                    self.cursorLeftRight('right', isRecording=False)
                else:
                    self.cursorLeftRight('left', isRecording=False)

            elif record == 'cursorRight':
                if direction == 'undo':
                    self.cursorLeftRight('left', isRecording=False)
                else:
                    self.cursorLeftRight('right', isRecording=False)

            elif record == 'cursorUp':
                if direction == 'undo':
                    self.cursorUpDown('down', isRecording=False)
                else:
                    self.cursorUpDown('up', isRecording=False)

            elif record == 'cursorDown':
                if direction == 'undo':
                    self.cursorUpDown('up', isRecording=False)
                else:
                    self.cursorUpDown('down', isRecording=False)

        # these relate to data manipulation...
        else:
            recordTitle, data = record

            if recordTitle == 'setCorrection':
                pair, font, amount = data
                setCorrection(pair, font, amount)
                self.updateWordDisplays()

            elif recordTitle == 'jumpToLine':
                previousIndex, nextIndex = data
                if direction == 'undo':
                    self.jumpToLine(previousIndex)
                else:
                    self.jumpToLine(nextIndex, isRecording=False)

