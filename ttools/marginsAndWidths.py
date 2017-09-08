#!/usr/bin/env python
# coding: utf-8

#############################
# Set margins or set widths #
#############################

### Modules
# custom
import userInterfaceValues
reload(userInterfaceValues)
from userInterfaceValues import vanillaControlsSize

# standard
from vanilla import FloatingWindow, RadioGroup, PopUpButton, TextBox, EditText

### Constants
PLUGIN_WIDTH = 320
PLUGIN_TITLE = 'Margins and Widths'

MARGIN_HOR = 10
MARGIN_VER = 8
NET_WIDTH = PLUGIN_WIDTH - MARGIN_HOR*2

MODE_OPTIONS = ['Set Margins', 'Set Widths']
TARGET_OPTIONS = ['All Fonts', 'Current Font']

### Classes
class MarginsAndWidthsManager(object):

    def __init__(self):
        self.target = TARGET_OPTIONS[0]
        self.mode = MODE_OPTIONS[0]

        self.w = FloatingWindow((0, 0, PLUGIN_WIDTH, 400), PLUGIN_TITLE)
        jumpingY = MARGIN_VER

        self.w.modePopUp = PopUpButton((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['PopUpButtonRegularHeight']),
                                       MODE_OPTIONS,
                                       callback=self.modePopUpCallback)
        jumpingY += vanillaControlsSize['PopUpButtonRegularHeight']+MARGIN_VER

        self.w.targetOptionsPopUp = PopUpButton((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['PopUpButtonRegularHeight']),
                                               TARGET_OPTIONS,
                                               callback=self.targetOptionsPopUpCallback)
        jumpingY += vanillaControlsSize['PopUpButtonRegularHeight']+MARGIN_VER

        self.w.marginsCtrl = MarginsManager((MARGIN_HOR, jumpingY, NET_WIDTH, 200))
        self.w.marginsCtrl.show(True)

        self.w.widthsCtrl = WidthsManager((MARGIN_HOR, jumpingY, NET_WIDTH, 200))
        self.w.widthsCtrl.show(False)

        self.w.open()

    def modePopUpCallback(self, sender):
        self.mode = MODE_OPTIONS[sender.get()]
        if self.mode == 'Set Margins':
            self.w.marginsCtrl.show(True)
            self.w.widthsCtrl.show(False)
            self.w.resize(PLUGIN_WIDTH, 400)
        else:
            self.w.marginsCtrl.show(False)
            self.w.widthsCtrl.show(True)
            self.w.resize(PLUGIN_WIDTH, 400)

    def targetOptionsPopUpCallback(self, sender):
        pass


class MarginsManager(Group):

    def __init__(self, posSize):
        super(MarginsManager, self).__init__(posSize)
        jumpingY = 0

        self.operationOptions = RadioGroup((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['EditTextRegularHeight']))
        jumpingY += vanillaControlsSize['EditTextRegularHeight'] + MARGIN_VER

        self.amountCaption = TextBox((MARGIN_HOR, jumpingY+2, NET_WIDTH, vanillaControlsSize['TextBoxRegularHeight']),
                                     'amount')

        self.amountEdit = EditText((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['EditTextRegularHeight']),
                                   callback=self.amountEditCallback)
        jumpingY += vanillaControlsSize['EditTextRegularHeight'] + MARGIN_VER

    def amountEditCallback(self, sender):
        print sender.get()


class WidthsManager(Group):

    def __init__(self, posSize):
        super(WidthsManager, self).__init__(posSize)


if __name__ == '__main__':
    mw = MarginsAndWidthsManager()
