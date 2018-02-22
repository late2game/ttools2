#!/usr/bin/env python
# coding: utf-8

#######################
# Jump To Line Window #
#######################

### Modules
# custom
from ..ui import userInterfaceValues
reload(userInterfaceValues)
from ..ui.userInterfaceValues import vanillaControlsSize

# standard
from vanilla import FloatingWindow, TextBox, EditText, Button
from defconAppKit.windows.baseWindow import BaseWindowController

### Constants
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
        super(JumpToLineWindow, self).__init__()
        self.callback = callback
        
        # init the window
        self.w = FloatingWindow((WINDOW_WIDTH, 0), 'Jump to line')

        # edit text caption
        jumpingY = MARGIN_TOP
        self.w.caption = TextBox((MARGIN_LFT, jumpingY+3, NET_WIDTH*.6, vanillaControlsSize['TextBoxRegularHeight']),
                               'Jump to line:')

        self.w.lineEdit = EditText((MARGIN_LFT+NET_WIDTH*.6, jumpingY, -MARGIN_RGT, vanillaControlsSize['EditTextRegularHeight']),
                                   continuous=False)

        jumpingY += vanillaControlsSize['EditTextRegularHeight'] + MARGIN_INT
        self.w.cancelButton = Button((-(BUTTON_WIDTH*2+MARGIN_INT+MARGIN_RGT), jumpingY, BUTTON_WIDTH, vanillaControlsSize['ButtonRegularHeight']),
                                     'Cancel',
                                     callback=self.cancelButtonCallback)

        self.w.okButton = Button((-(BUTTON_WIDTH+MARGIN_RGT), jumpingY, BUTTON_WIDTH, vanillaControlsSize['ButtonRegularHeight']),
                                 'Ok',
                                 callback=self.okButtonCallback)

        jumpingY += vanillaControlsSize['ButtonRegularHeight'] + MARGIN_BTM
        self.setUpBaseWindowBehavior()
        self.w.resize(WINDOW_WIDTH, jumpingY)

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
