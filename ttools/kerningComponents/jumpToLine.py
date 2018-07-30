#!/usr/bin/env python
# coding: utf-8

#######################
# Jump To Line Window #
#######################

### Modules
# standard
import importlib
from vanilla import FloatingWindow, TextBox, EditText, Button
from defconAppKit.windows.baseWindow import BaseWindowController

# custom
from ..ui import userInterfaceValues
importlib.reload(userInterfaceValues)
from ..ui.userInterfaceValues import vanillaControlsSize

### Constants
vanillaControlsSize = {
    'HorizontalLineThickness': 1,
    'VerticalLineThickness': 1,

    'ButtonRegularHeight': 20,
    'ButtonSmallHeight': 17,
    'ButtonMiniHeight': 14,

    'TextBoxRegularHeight': 17,
    'TextBoxSmallHeight': 14,
    'TextBoxMiniHeight': 12,

    'EditTextRegularHeight': 22,
    'EditTextSmallHeight': 19,
    'EditTextMiniHeight': 16,

    'CheckBoxRegularHeight': 22,
    'CheckBoxSmallHeight': 18,
    'CheckBoxMiniHeight': 10,

    'ComboBoxRegularHeight': 21,
    'ComboBoxSmallHeight': 17,
    'ComboBoxMiniHeight': 14,

    'PopUpButtonRegularHeight': 20,
    'PopUpButtonSmallHeight': 17,
    'PopUpButtonMiniHeight': 15,

    'SliderWithoutTicksRegularHeight': 15,
    'SliderWithoutTicksSmallHeight': 11,
    'SliderWithoutTicksMiniHeight': 10,

    'SliderWithTicksRegularHeight': 23,
    'SliderWithTicksSmallHeight': 17,
    'SliderWithTicksMiniHeight': 16,
    }

WINDOW_WIDTH = 180

MARGIN_INT = 8
MARGIN_TOP = 15
MARGIN_BTM = 15
MARGIN_LFT = 15
MARGIN_RGT = 15

NET_WIDTH = WINDOW_WIDTH-MARGIN_LFT-MARGIN_RGT

BUTTON_WIDTH = 70

### Object
class JumpToLineWindow(BaseWindowController):

    lineNumber = None

    def __init__(self, callback):
        self.callback = callback
        
        # init the window
        self.w = FloatingWindow((WINDOW_WIDTH, 0), 'Jump to line')

        # edit text caption
        jumpingY = MARGIN_TOP
        self.w.caption = TextBox((MARGIN_LFT, jumpingY+3, NET_WIDTH*.6, vanillaControlsSize['TextBoxRegularHeight']),
                               'Jump to line:')

        self.w.lineEdit = EditText((MARGIN_LFT+NET_WIDTH*.6, jumpingY, -MARGIN_RGT, vanillaControlsSize['EditTextRegularHeight']),
                                   continuous=False) #,
                                   # callback=self.lineEditCallback)
        
        jumpingY += vanillaControlsSize['EditTextRegularHeight'] + MARGIN_INT
        self.w.cancelButton = Button((-(BUTTON_WIDTH*2+MARGIN_INT+MARGIN_RGT), jumpingY, BUTTON_WIDTH, vanillaControlsSize['ButtonRegularHeight']),
                                   'Cancel',
                                   callback=self.cancelButtonCallback)

        self.w.okButton = Button((-(BUTTON_WIDTH+MARGIN_RGT), jumpingY, BUTTON_WIDTH, vanillaControlsSize['ButtonRegularHeight']),
                               'Ok',
                               callback=self.okButtonCallback)

        jumpingY += vanillaControlsSize['ButtonRegularHeight'] + MARGIN_BTM
        self.w.resize(WINDOW_WIDTH, jumpingY)

        # open the window
        self.w.open()

    def get(self):
        try:
            self.lineNumber = int(self.w.lineEdit.get())
        except ValueError:
            self.w.lineEdit.set('')
            self.lineNumber = None
        return self.lineNumber

    def enable(self, value):
        if value is True:
            self.w.center()
            self.w.show()
        else:
            self.w.hide()

    def cancelButtonCallback(self, sender):
        self.w.show(False)

    def okButtonCallback(self, sender):
        self.callback(self)


if __name__ == '__main__':
    jl = JumpToLineWindow()
