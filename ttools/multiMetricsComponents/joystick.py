#!/usr/bin/env python
# coding: utf-8

"""a little joystick for shortcuts"""

### Modules
# custom
from ..ui import userInterfaceValues
reload(userInterfaceValues)
from ..ui.userInterfaceValues import vanillaControlsSize

# standard
from vanilla import Group, TextBox, CheckBox, SquareButton

### Constants
MARGIN_ROW = 8
MARGIN_COL = 12
SQUARE_SIDE = 36

AMOUNT_OPTIONS = {
    'plusFour':      4,
    'minusFour':    -4,
    'plusTwenty':   20,
    'minusTwenty': -20
    }

### Objects
class SpacingJoystick(Group):

    lastMargin = None
    howMuch = None


    def __init__(self, posSize, verticalMode, marginCallback, verticalCallback):
        super(SpacingJoystick, self).__init__(posSize)
        self.marginCallback = marginCallback
        self.verticalCallback = verticalCallback
        self.verticalMode = verticalMode
        xx, yy, width, height = posSize

        singleMarginCtrlHeight = SQUARE_SIDE*2 + vanillaControlsSize['TextBoxRegularHeight'] + MARGIN_ROW
        jumpingX = 0
        self.leftMarginCtrl = SingleMargin((jumpingX, 0, SQUARE_SIDE*2, singleMarginCtrlHeight),
                                            whichMargin='LEFT',
                                            callback=self.leftMarginCtrlCallback)

        jumpingX += SQUARE_SIDE*2 + MARGIN_COL*2
        self.rightMarginCtrl = SingleMargin((jumpingX, 0, SQUARE_SIDE*2, singleMarginCtrlHeight),
                                            whichMargin='RIGHT',
                                            callback=self.rightMarginCtrlCallback)

        self.verticalModeCheck = CheckBox((0, singleMarginCtrlHeight+4, width, vanillaControlsSize['CheckBoxRegularHeight']),
                                          'vertical mode',
                                          callback=self.verticalModeCheckCallback)

    def get(self):
        return self.lastMargin, self.howMuch

    def getVerticalMode(self):
        return self.verticalMode

    def leftMarginCtrlCallback(self, sender):
        self.lastMargin = 'LEFT'
        self.howMuch = AMOUNT_OPTIONS[sender.get()]
        self.marginCallback(self)

    def rightMarginCtrlCallback(self, sender):
        self.lastMargin = 'RIGHT'
        self.howMuch = AMOUNT_OPTIONS[sender.get()]
        self.marginCallback(self)

    def verticalModeCheckCallback(self, sender):
        self.verticalMode = bool(sender.get())
        self.verticalCallback(self)


class SingleMargin(Group):

    lastAction = None

    def __init__(self, posSize, whichMargin, callback):
        super(SingleMargin, self).__init__(posSize)
        self.callback = callback
        x, y, width, height = posSize

        if whichMargin == 'LEFT':
            whichArrow = 'leftarrow'
        else:
            whichArrow = 'rightarrow'

        jumpingY = 0
        self.caption = TextBox((0, jumpingY, width, vanillaControlsSize['TextBoxRegularHeight']),
                               whichMargin)

        jumpingY += vanillaControlsSize['TextBoxRegularHeight'] + MARGIN_ROW
        self.plusFourButton = SquareButton((0, jumpingY, SQUARE_SIDE, SQUARE_SIDE),
                                           '+4',
                                           sizeStyle='small',
                                           callback=self.plusFourButtonCallback)
        self.plusFourButton.bind(whichArrow, [])

        self.minusFourButton = SquareButton((SQUARE_SIDE, jumpingY, SQUARE_SIDE, SQUARE_SIDE),
                                            '-4',
                                            sizeStyle='small',
                                            callback=self.minusFourButtonCallback)
        self.minusFourButton.bind(whichArrow, ['option'])

        jumpingY += SQUARE_SIDE
        self.plusTwentyButton = SquareButton((0, jumpingY, SQUARE_SIDE, SQUARE_SIDE),
                                             '+20',
                                             sizeStyle='small',
                                             callback=self.plusTwentyButtonCallback)
        self.plusTwentyButton.bind(whichArrow, ['command'])

        self.minusTwentyButton = SquareButton((SQUARE_SIDE, jumpingY, SQUARE_SIDE, SQUARE_SIDE),
                                              '-20',
                                              sizeStyle='small',
                                              callback=self.minusTwentyButtonCallback)
        self.minusTwentyButton.bind(whichArrow, ['option', 'command'])

    def get(self):
        return self.lastAction

    def plusFourButtonCallback(self, sender):
        self.lastAction = 'plusFour'
        self.callback(self)

    def minusFourButtonCallback(self, sender):
        self.lastAction = 'minusFour'
        self.callback(self)

    def plusTwentyButtonCallback(self, sender):
        self.lastAction = 'plusTwenty'
        self.callback(self)

    def minusTwentyButtonCallback(self, sender):
        self.lastAction = 'minusTwenty'
        self.callback(self)




