#!/usr/bin/env python
# -*- coding: utf-8 -*-

# custom modules
from ..userInterfaceValues import vanillaControlsSize
from kerningMisc import getCorrection, checkPairFormat, buildPairsFromString
from kerningMisc import MAJOR_STEP, MINOR_STEP

# standard modules
from vanilla import Group, SquareButton, CheckBox, EditText
from vanilla import Button
import traceback


class JoystickController(Group):

    lastEvent = None
    keyboardCorrection = 0

    def __init__(self, posSize, fontObj, displayedWord, indexPair, isSymmetricalEditingOn, isVerticalAlignedEditingOn, callback):
        super(JoystickController, self).__init__(posSize)
        self.indexPair = indexPair
        self.fontObj = fontObj
        self.displayedPairs = buildPairsFromString(displayedWord, self.fontObj)
        self.activePair = self.displayedPairs[self.indexPair]

        self.isSymmetricalEditingOn = isSymmetricalEditingOn
        self.isVerticalAlignedEditingOn = isVerticalAlignedEditingOn
        self.callback = callback

        buttonSide = 36
        self.ctrlWidth, self.ctrlHeight = posSize[2], posSize[3]
        self.jumping_X = buttonSide/2.
        self.jumping_Y = 0

        correction, kerningReference, pairKind = getCorrection(self.activePair, self.fontObj)

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

        self.jumping_Y += buttonSide*.6
        self.verticalAlignedModeCheck = CheckBox((self.jumping_X, self.jumping_Y, self.ctrlWidth, vanillaControlsSize['CheckBoxRegularHeight']),
                                                 'vertically aligned editing',
                                                 value=self.isVerticalAlignedEditingOn,
                                                 callback=self.verticalAlignedModeCheckCallback)
        self.verticalAlignedModeCheck.bind('v', ['command'])

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

        self.jumping_X = buttonSide
        self.jumping_Y += buttonSide

        self.delPairCtrl = SquareButton((self.jumping_X-6, self.jumping_Y+6, buttonSide, buttonSide),
                                        u'Del',
                                        sizeStyle='small',
                                        callback=self.delPairCtrlCallback)
        self.delPairCtrl.bind("forwarddelete", [])

        self.jumping_X += buttonSide
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

    def setActivePair(self, displayedWord, indexPair):
        self.indexPair = indexPair
        self.displayedPairs = buildPairsFromString(displayedWord, self.fontObj)
        self.activePair = self.displayedPairs[self.indexPair]
        self.updateCorrectionValue()

    def setSymmetricalEditing(self, symmetricalEditing):
        self.isSymmetricalEditingOn = symmetricalEditing
        self.symmetryModeCheck.set(self.isSymmetricalEditingOn)

    def setFontObj(self, value):
        self.fontObj = value
        self.updateCorrectionValue()

    def updateCorrectionValue(self):
        correction, kerningReference, pairKind = getCorrection(self.activePair, self.fontObj)
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

    def delPairCtrlCallback(self, sender):
        self.lastEvent = 'deletePair'
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

    def verticalAlignedModeCheckCallback(self, sender):
        self.lastEvent = 'verticalAlignedEditing'
        self.isVerticalAlignedEditingOn = bool(sender.get())
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
                self.activePairEditCorrection.set('%s' % self.keyboardCorrection)
                print traceback.format_exc()
