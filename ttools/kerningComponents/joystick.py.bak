#!/usr/bin/env python
# coding: utf-8

### Modules
# custom
from ..ui import userInterfaceValues
reload(userInterfaceValues)
from ..ui.userInterfaceValues import vanillaControlsSize

import kerningMisc
reload(kerningMisc)
from kerningMisc import getCorrection, checkPairFormat, buildPairsFromString
from kerningMisc import MAJOR_STEP, MINOR_STEP

# standard
from vanilla import Group, SquareButton, CheckBox, EditText
from vanilla import Button, PopUpButton
import traceback

"""
-20: cmd+alt+leftArrow
-04: cmd+leftArrow
+04: cmd+rightArrow
+20: cmd+alt+rightArrow 
delete pair: fn+backspace

lft group switch: cmd+a
rgt group switch: cmd+s

exception: cmd+e
toggle preview: cmd+p
solved word: cmd+enter
flipped mode: cmd+f
vertical mode: cmd+v

up: upArrow
down: downArrow
left: leftArrow
right: rightArrow
"""

# Constants
MINUS_MAJOR_SHORTCUT = 'leftarrow', ['option', 'command']
MINUS_MINOR_SHORTCUT = 'leftarrow', ['command']
PLUS_MINOR_SHORTCUT = 'rightarrow', ['command']
PLUS_MAJOR_SHORTCUT = 'rightarrow', ['option', 'command']

PREVIEW_SHORTCUT = 'p', ['command']
SOLVED_SHORTCUT = unichr(13), ['command']

EXCEPTION_SHORTCUT = 'e', ['command']
LEFT_BROWSING_SHORTCUT = 'a', ['command']
RIGHT_BROWSING_SHORTCUT = 's', ['command']
DEL_PAIR_SHORTCUT = 'forwarddelete', []

SYMMETRICAL_EDITING_SHORTCUT = 'g', ['command']
VERTICAL_MODE_SHORTCUT = 'v', ['command']
FLIPPED_EDITING_SHORTCUT = 'f', ['command']

NEXT_WORD_SHORTCUT = 'downarrow', ['command', 'option']
PREVIOUS_WORD_SHORTCUT = 'uparrow', ['command', 'option']

CURSOR_UP_SHORTCUT = 'uparrow', []
CURSOR_LEFT_SHORTCUT = 'leftarrow', []
CURSOR_RIGHT_SHORTCUT = 'rightarrow', []
CURSOR_DOWN_SHORTCUT = 'downarrow', []

JUMP_TO_LINE_SHORTCUT = 'j', ['command']

UNDO_SHORTCUT = 'z', ['command']
REDO_SHORTCUT = 'z', ['command', 'shift']

AUTO_SAVE_SPAN_OPTIONS = ["1'", "5'", "10'", "15'", "20'"]
INT_2_SPAN = {"1'": 1,"5'": 5, "10'": 10, "15'": 15, "20'": 20}

# class definition!
class JoystickController(Group):

    lastEvent = None
    keyboardCorrection = 0

    def __init__(self, posSize,
                       fontObj,
                       isSymmetricalEditingOn,
                       isFlippedEditingOn,
                       isVerticalAlignedEditingOn,
                       autoSave,
                       autoSaveSpan,
                       activePair,
                       callback):

        super(JoystickController, self).__init__(posSize)
        self.fontObj = fontObj
        self.activePair = activePair

        self.isSymmetricalEditingOn = isSymmetricalEditingOn
        self.isFlippedEditingOn = isFlippedEditingOn
        self.isVerticalAlignedEditingOn = isVerticalAlignedEditingOn
        self.autoSave = autoSave
        self.autoSaveSpan = autoSaveSpan
        self.callback = callback

        buttonSide = 36
        self.ctrlWidth, self.ctrlHeight = posSize[2], posSize[3]
        self.jumping_X = buttonSide/2.
        self.jumping_Y = 0

        self.minusMajorCtrl = SquareButton((self.jumping_X, self.jumping_Y, buttonSide, buttonSide),
                                           "-%s" % MAJOR_STEP,
                                           sizeStyle='small',
                                           callback=self.minusMajorCtrlCallback)
        self.minusMajorCtrl.bind(*MINUS_MAJOR_SHORTCUT)

        self.jumping_X += buttonSide
        self.minusMinorCtrl = SquareButton((self.jumping_X, self.jumping_Y, buttonSide, buttonSide),
                                           "-%s" % MINOR_STEP,
                                           sizeStyle='small',
                                           callback=self.minusMinorCtrlCallback)
        self.minusMinorCtrl.bind(*MINUS_MINOR_SHORTCUT)

        self.jumping_X += buttonSide
        self.plusMinorCtrl = SquareButton((self.jumping_X, self.jumping_Y, buttonSide, buttonSide),
                                          "+%s" % MINOR_STEP,
                                          sizeStyle='small',
                                          callback=self.plusMinorCtrlCallback)
        self.plusMinorCtrl.bind(*PLUS_MINOR_SHORTCUT)

        self.jumping_X += buttonSide
        self.plusMajorCtrl = SquareButton((self.jumping_X, self.jumping_Y, buttonSide, buttonSide),
                                          "+%s" % MAJOR_STEP,
                                          sizeStyle='small',
                                          callback=self.plusMajorCtrlCallback)
        self.plusMajorCtrl.bind(*PLUS_MAJOR_SHORTCUT)

        self.jumping_X = buttonSide/2.
        self.jumping_Y += buttonSide
        self.lftSwitchCtrl = SquareButton((self.jumping_X, self.jumping_Y, buttonSide*2, buttonSide*.75),
                                        "lft switch",
                                        sizeStyle='small',
                                        callback=self.lftSwitchCtrlCallback)
        self.lftSwitchCtrl.bind(*LEFT_BROWSING_SHORTCUT)

        self.jumping_X += buttonSide*2
        self.rgtSwitchCtrl = SquareButton((self.jumping_X, self.jumping_Y, buttonSide*2, buttonSide*.75),
                                       "rgt switch",
                                       sizeStyle='small',
                                       callback=self.rgtSwitchCtrlCallback)
        self.rgtSwitchCtrl.bind(*RIGHT_BROWSING_SHORTCUT)

        self.jumping_X = buttonSide/2.
        self.jumping_Y += buttonSide
        self.exceptionTrigger = SquareButton((self.jumping_X, self.jumping_Y, buttonSide*2, buttonSide*.75),
                                                'exception',
                                                sizeStyle='small',
                                                callback=self.exceptionTriggerCallback)
        self.exceptionTrigger.bind(*EXCEPTION_SHORTCUT)

        self.jumping_X += buttonSide*2
        self.undoButton = SquareButton((self.jumping_X, self.jumping_Y, buttonSide, buttonSide*.75),
                                       'undo',
                                       sizeStyle='small',
                                       callback=self.undoButtonCallback)
        self.undoButton.bind(*UNDO_SHORTCUT)

        self.jumping_X += buttonSide
        self.redoButton = SquareButton((self.jumping_X, self.jumping_Y, buttonSide, buttonSide*.75),
                                       'redo',
                                       sizeStyle='small',
                                       callback=self.redoButtonCallback)
        self.redoButton.bind(*REDO_SHORTCUT)

        self.jumping_X = buttonSide/2.
        self.jumping_Y += buttonSide*.75
        self.previewCtrl = SquareButton((self.jumping_X, self.jumping_Y, buttonSide*2, buttonSide*.75),
                                        "preview",
                                        sizeStyle='small',
                                        callback=self.previewCtrlCallback)
        self.previewCtrl.bind(*PREVIEW_SHORTCUT)

        self.jumping_X += buttonSide*2
        self.solvedCtrl = SquareButton((self.jumping_X, self.jumping_Y, buttonSide*2, buttonSide*.75),
                                       "solved",
                                       sizeStyle='small',
                                       callback=self.solvedCtrlCallback)
        self.solvedCtrl.bind(*SOLVED_SHORTCUT)

        self.jumping_X = buttonSide/2.
        self.jumping_Y += buttonSide*.75+2
        self.symmetricalModeCheck = CheckBox((self.jumping_X, self.jumping_Y, self.ctrlWidth, vanillaControlsSize['CheckBoxRegularHeight']),
                                          'symmetrical editing',
                                          value=self.isFlippedEditingOn,
                                          callback=self.symmetricalModeCallback)

        self.jumping_Y += buttonSide*.6
        self.flippedModeCheck = CheckBox((self.jumping_X, self.jumping_Y, self.ctrlWidth, vanillaControlsSize['CheckBoxRegularHeight']),
                                          'flipped editing',
                                          value=self.isFlippedEditingOn,
                                          callback=self.flippedModeCallback)

        self.jumping_Y += buttonSide*.6
        self.verticalAlignedModeCheck = CheckBox((self.jumping_X, self.jumping_Y, self.ctrlWidth, vanillaControlsSize['CheckBoxRegularHeight']),
                                                 'vertically aligned editing',
                                                 value=self.isVerticalAlignedEditingOn,
                                                 callback=self.verticalAlignedModeCheckCallback)
        self.verticalAlignedModeCheck.bind(*VERTICAL_MODE_SHORTCUT)

        self.hiddenFlippedEditingButton = Button((self.jumping_X, self.ctrlHeight+40, self.ctrlWidth, vanillaControlsSize['ButtonRegularHeight']),
                                                   'hiddenSymmetriyEditingButton',
                                                   callback=self.hiddenFlippedEditingButtonCallback)
        self.hiddenFlippedEditingButton.bind(*FLIPPED_EDITING_SHORTCUT)

        self.hiddenJumpToLineButton = Button((self.jumping_X, self.ctrlHeight+40, self.ctrlWidth, vanillaControlsSize['ButtonRegularHeight']),
                                                   'hiddenJumpToLineButton',
                                                   callback=self.hiddenJumpToLineButtonCallback)
        self.hiddenJumpToLineButton.bind(*JUMP_TO_LINE_SHORTCUT)

        self.jumping_X = buttonSide
        self.jumping_Y += buttonSide
        self.previousWordCtrl = SquareButton((self.jumping_X, self.jumping_Y, buttonSide, buttonSide),
                                             u'↖',
                                             callback=self.previousWordCtrlCallback)
        self.previousWordCtrl.bind(*PREVIOUS_WORD_SHORTCUT)

        self.jumping_X += buttonSide
        self.cursorUpCtrl = SquareButton((self.jumping_X, self.jumping_Y, buttonSide, buttonSide),
                                         u'↑',
                                         callback=self.cursorUpCtrlCallback)
        self.cursorUpCtrl.bind(*CURSOR_UP_SHORTCUT)

        self.jumping_X += buttonSide*1.5
        self.activePairEditCorrection = EditText((self.jumping_X, self.jumping_Y, 50, vanillaControlsSize['EditTextRegularHeight']),
                                                 text='%s' % 0,   # init value
                                                 continuous=False,
                                                 callback=self.activePairEditCorrectionCallback)

        self.jumping_X = buttonSide
        self.jumping_Y += buttonSide
        self.cursorLeftCtrl = SquareButton((self.jumping_X, self.jumping_Y, buttonSide, buttonSide),
                                           u"←",
                                           callback=self.cursorLeftCtrlCallback)
        self.cursorLeftCtrl.bind(*CURSOR_LEFT_SHORTCUT)

        self.jumping_X += buttonSide*2
        self.cursorRightCtrl = SquareButton((self.jumping_X, self.jumping_Y, buttonSide, buttonSide),
                                            u'→',
                                            callback=self.cursorRightCtrlCallback)
        self.cursorRightCtrl.bind(*CURSOR_RIGHT_SHORTCUT)

        self.jumping_X = buttonSide
        self.jumping_Y += buttonSide

        self.delPairCtrl = SquareButton((self.jumping_X-6, self.jumping_Y+6, buttonSide, buttonSide),
                                        u'Del',
                                        callback=self.delPairCtrlCallback)
        self.delPairCtrl.bind(*DEL_PAIR_SHORTCUT)

        self.jumping_X += buttonSide
        self.cursorDownCtrl = SquareButton((self.jumping_X, self.jumping_Y, buttonSide, buttonSide),
                                           u'↓',
                                           callback=self.cursorDownCtrlCallback)
        self.cursorDownCtrl.bind(*CURSOR_DOWN_SHORTCUT)

        self.jumping_X += buttonSide
        self.nextWordCtrl = SquareButton((self.jumping_X, self.jumping_Y, buttonSide, buttonSide),
                                         u'↘',
                                         callback=self.nextWordCtrlCallback)
        self.nextWordCtrl.bind(*NEXT_WORD_SHORTCUT)

        self.jumping_Y += buttonSide*1.3
        self.jumping_X = buttonSide*.5
        self.autoSaveCheck = CheckBox((self.jumping_X, self.jumping_Y, buttonSide*2.5, vanillaControlsSize['CheckBoxRegularHeight']),
                                      'auto save',
                                      callback=self.autoSaveCheckCallback)

        self.jumping_X += buttonSide*2.5
        self.autoSaveSpanPopUp = PopUpButton((self.jumping_X, self.jumping_Y, buttonSide*1.5, vanillaControlsSize['PopUpButtonRegularHeight']),
                                             AUTO_SAVE_SPAN_OPTIONS,
                                             callback=self.autoSaveSpanPopUpCallback)
        self.autoSaveSpanPopUp.set(AUTO_SAVE_SPAN_OPTIONS.index("%d'" % self.autoSaveSpan))

    # goes out
    def getLastEvent(self):
        return self.lastEvent

    def getKeyboardCorrection(self):
        return self.keyboardCorrection

    def getAutoSaveState(self):
        return self.autoSave, self.autoSaveSpan

    # comes in
    def setActivePair(self, activePair):
        self.activePair = activePair
        self.updateCorrectionValue()

    def setFlippedEditing(self, value):
        self.isFlippedEditingOn = value
        self.flippedModeCheck.set(self.isFlippedEditingOn)

    def setSymmetricalEditing(self, value):
        self.isSymmetricalEditingOn = value
        self.symmetricalModeCheck.set(self.isSymmetricalEditingOn)

    def setFontObj(self, value):
        self.fontObj = value
        self.updateCorrectionValue()

    def updateCorrectionValue(self):
        correction, kerningReference, pairKind = getCorrection(self.activePair, self.fontObj)
        self.activePairEditCorrection.set('%s' % correction)

    # callbacks
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

    def delPairCtrlCallback(self, sender):
        self.lastEvent = 'deletePair'
        self.callback(self)

    def exceptionTriggerCallback(self, sender):
        self.lastEvent = 'exceptionTrigger'
        self.callback(self)

    def undoButtonCallback(self, sender):
        self.lastEvent = 'undo'
        self.callback(self)

    def redoButtonCallback(self, sender):
        self.lastEvent = 'redo'
        self.callback(self)

    def previewCtrlCallback(self, sender):
        self.lastEvent = 'preview'
        self.callback(self)

    def solvedCtrlCallback(self, sender):
        self.lastEvent = 'solved'
        self.callback(self)

    def flippedModeCallback(self, sender):
        self.lastEvent = 'flippedEditing'
        self.isFlippedEditingOn = bool(sender.get())
        self.callback(self)

    def symmetricalModeCallback(self, sender):
        self.lastEvent = 'symmetricalEditing'
        self.isSymmetricalEditingOn = bool(sender.get())
        self.callback(self)

    def verticalAlignedModeCheckCallback(self, sender):
        self.lastEvent = 'verticalAlignedEditing'
        self.isVerticalAlignedEditingOn = bool(sender.get())
        self.callback(self)

    def hiddenFlippedEditingButtonCallback(self, sender):
        self.lastEvent = 'flippedEditing'
        self.isFlippedEditingOn = not self.isFlippedEditingOn
        self.flippedModeCheck.set(self.isFlippedEditingOn)
        self.callback(self)

    def hiddenJumpToLineButtonCallback(self, sender):
        self.lastEvent = 'jumpToLineTrigger'
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

    def lftSwitchCtrlCallback(self, sender):
        self.lastEvent = 'switchLftGlyph'
        self.callback(self)

    def rgtSwitchCtrlCallback(self, sender):
        self.lastEvent = 'switchRgtGlyph'
        self.callback(self)

    def activePairEditCorrectionCallback(self, sender):
        try:
            self.lastEvent = 'keyboardEdit'
            self.keyboardCorrection = int(sender.get())
            self.callback(self)
        except ValueError:
            if sender.get() != '-' or sender.get() != '':
                self.activePairEditCorrection.set('%s' % self.keyboardCorrection)
                print traceback.format_exc()

    def autoSaveCheckCallback(self, sender):
        self.lastEvent = 'autoSave'
        self.autoSave = bool(sender.get())
        self.callback(self)

    def autoSaveSpanPopUpCallback(self, sender):
        self.lastEvent = 'autoSave'
        self.autoSaveSpan = INT_2_SPAN[AUTO_SAVE_SPAN_OPTIONS[sender.get()]]
        self.callback(self)

