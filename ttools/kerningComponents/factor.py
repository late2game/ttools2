#!/usr/bin/env python
# coding: utf-8

### Modules
# standard
from __future__ import absolute_import
import importlib
from vanilla import Group, TextBox, SquareButton, SquareButton

# custom
from . import kerningMisc
importlib.reload(kerningMisc)
from .kerningMisc import MARGIN_VER, MARGIN_COL

from ..ui import userInterfaceValues
importlib.reload(userInterfaceValues)
from ..ui.userInterfaceValues import vanillaControlsSize

### Classes
class FactorController(Group):

    def __init__(self, posSize, canvasScalingFactor, callback):
        super(FactorController, self).__init__(posSize)
        self.canvasScalingFactor = canvasScalingFactor
        self.callback = callback

        jumpingX = 0
        self.caption = TextBox((jumpingX, 0, 30, vanillaControlsSize['TextBoxRegularHeight']),
                               '{:.1f}'.format(self.canvasScalingFactor))

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
        self.caption.set('{:.1f}'.format(self.canvasScalingFactor))
        self.callback(self)

    def dwButtonCallback(self, sender):
        self.canvasScalingFactor -= .1
        self.caption.set('{:.1f}'.format(self.canvasScalingFactor))
        self.callback(self)
