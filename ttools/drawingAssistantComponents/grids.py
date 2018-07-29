#!/usr/bin/env python
# coding: utf-8

##############
# Grid ctrls #
##############

### Modules
import sharedValues
reload(sharedValues)
from sharedValues import MARGIN_VER, NET_WIDTH

# custom
from ..ui import userInterfaceValues
reload(userInterfaceValues)
from ..ui.userInterfaceValues import vanillaControlsSize

# standard
from vanilla import Group, CheckBox, TextBox, EditText, ColorWell
from AppKit import NSColor

### Constants
GRID_COLOR_ONE = (1, 0.4, 0.4, 1)
GRID_COLOR_TWO = (0.4, 0.64, 1, 1)
GRID_COLOR_THREE = (0.88, 0.4, 1, 1)
GRID_COLOR_FOUR = (0.4, 1, 0.64, 1)
GRID_COLOR_FIVE = (0.88, 1, 0.4, 1)
GRID_COLOR_INIT = [GRID_COLOR_ONE, GRID_COLOR_TWO, GRID_COLOR_THREE, GRID_COLOR_FOUR, GRID_COLOR_FIVE]

### Ctrls
class MultipleGridController(Group):

    def __init__(self, posSize, gridActive, ctrlsAmount, activeCtrls, offgridActive, callback):
        Group.__init__(self, posSize)
        assert activeCtrls <= ctrlsAmount

        self.ctrlHeight = posSize[3]
        self.gridActive = gridActive
        self.ctrlsAmount = ctrlsAmount
        self.activeCtrls = activeCtrls
        self.offgridActive = offgridActive
        self.gridIndexes = ['{:d}'.format(integer) for integer in range(1, ctrlsAmount+1)]
        self.callback = callback

        self.gridsDB = [{'horizontal': False, 'vertical': False, 'step': None, 'color': color} for color in GRID_COLOR_INIT]

        jumpin_Y = 4
        self.gridActiveCheck = CheckBox((0, jumpin_Y, NET_WIDTH*.6, vanillaControlsSize['CheckBoxRegularHeight']),
                                        "Show grids",
                                        value=self.gridActive,
                                        callback=self.gridActiveCheckCallback)

        for eachI in range(1, ctrlsAmount+1):
            jumpin_Y += vanillaControlsSize['EditTextRegularHeight'] + MARGIN_VER
            gridCtrl = SingleGridController((0, jumpin_Y, NET_WIDTH, vanillaControlsSize['EditTextRegularHeight']),
                                            index=eachI,
                                            isVertical=False,
                                            isHorizontal=False,
                                            step=None,
                                            gridColor=GRID_COLOR_INIT[eachI-1],
                                            callback=self.gridCtrlCallback)
            gridCtrl.enable(self.gridActive)
            setattr(self, 'grid{:0>2}'.format(eachI), gridCtrl)

        jumpin_Y += vanillaControlsSize['EditTextRegularHeight'] + MARGIN_VER
        self.showOffgridCheck = CheckBox((0, jumpin_Y, NET_WIDTH, vanillaControlsSize['CheckBoxRegularHeight']),
                                         "Show offgrid points",
                                         value=self.offgridActive,
                                         callback=self.showOffgridCheckCallback)

    def get(self):
        return self.gridActive, self.gridsDB, self.offgridActive

    def gridCtrlCallback(self, sender):
        ctrlIndex, ctrlDB = sender.get()
        self.gridsDB[ctrlIndex] = ctrlDB
        self.callback(self)

    def gridActiveCheckCallback(self, sender):
        self.gridActive = bool(sender.get())
        for eachI in range(1, self.ctrlsAmount+1):
            gridCtrl = getattr(self, 'grid{:0>2}'.format(eachI))
            gridCtrl.enable(self.gridActive)
        self.callback(self)

    def showOffgridCheckCallback(self, sender):
        self.offgridActive = bool(sender.get())
        self.callback(self)


class SingleGridController(Group):
    """this controller takes care of canvas grid drawing"""

    def __init__(self, posSize, index, isVertical, isHorizontal, step, gridColor, callback):
        Group.__init__(self, posSize)

        # from arguments to attributes
        self.ctrlX, self.ctrlY, self.ctrlWidth, self.ctrlHeight = posSize
        self.index = index
        self.isVertical = isVertical
        self.isHorizontal = isHorizontal
        self.step = step
        self.gridColor = gridColor
        self.callback = callback

        # ctrls
        jumpin_X = 12
        self.indexText = TextBox((jumpin_X, 0, 16, vanillaControlsSize['TextBoxRegularHeight']), '{:d})'.format(index))
        jumpin_X += self.indexText.getPosSize()[2]

        self.stepCtrl = EditText((jumpin_X, 0, 38, vanillaControlsSize['EditTextRegularHeight']),
                                 callback=self.stepCtrlCallback)
        jumpin_X += self.stepCtrl.getPosSize()[2] + 16

        self.isHorizontalCheck = CheckBox((jumpin_X, 0, 32, vanillaControlsSize['CheckBoxRegularHeight']),
                                          "H",
                                          value=self.isHorizontal,
                                          callback=self.isHorizontalCheckCallback)
        jumpin_X += self.isHorizontalCheck.getPosSize()[2]+2

        self.isVerticalCheck = CheckBox((jumpin_X, 0, 32, vanillaControlsSize['CheckBoxRegularHeight']),
                                        "V",
                                        value=self.isVertical,
                                        callback=self.isVerticalCheckCallback)
        jumpin_X += self.isVerticalCheck.getPosSize()[2]+10

        self.whichColorWell = ColorWell((jumpin_X, 0, 46, self.ctrlHeight),
                                        color=NSColor.colorWithCalibratedRed_green_blue_alpha_(*gridColor),
                                        callback=self.whichColorWellCallback)

    def enable(self, onOff):
        self.indexText.enable(onOff)
        self.stepCtrl.enable(onOff)
        self.isHorizontalCheck.enable(onOff)
        self.isVerticalCheck.enable(onOff)
        self.whichColorWell.enable(onOff)

    def get(self):
        return self.index-1, {'horizontal': self.isHorizontal, 'vertical': self.isVertical, 'step': self.step, 'color': self.gridColor}

    def stepCtrlCallback(self, sender):
        try:
            self.step = int(sender.get())
            self.callback(self)
        except ValueError as error:
            self.step = None
            self.stepCtrl.set('')

    def isHorizontalCheckCallback(self, sender):
        self.isHorizontal = bool(sender.get())
        self.callback(self)

    def isVerticalCheckCallback(self, sender):
        self.isVertical = bool(sender.get())
        self.callback(self)

    def whichColorWellCallback(self, sender):
        calibratedColor = sender.get()
        self.gridColor = (calibratedColor.redComponent(),
                          calibratedColor.greenComponent(),
                          calibratedColor.blueComponent(),
                          calibratedColor.alphaComponent())
        self.callback(self)
