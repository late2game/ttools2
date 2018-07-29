#!/usr/bin/env python
# coding: utf-8

################################
# Bcp vanilla group controller #
################################

### Modules
from sharedValues import NET_WIDTH

# custom
from ..ui.userInterfaceValues import vanillaControlsSize

# standard
from vanilla import Group, CheckBox

### Constants

### Ctrl
class BcpController(Group):

    def __init__(self, posSize, sqrActive, bcpLengthActive, callback):
        Group.__init__(self, posSize)

        self.ctrlHeight = posSize[3]
        self.sqrActive = sqrActive
        self.bcpLengthActive = bcpLengthActive
        self.callback = callback

        jumpin_Y = 2
        self.sqrCheck = CheckBox((0, jumpin_Y, NET_WIDTH, vanillaControlsSize['CheckBoxRegularHeight']),
                                 "Show squarings",
                                 value=self.sqrActive,
                                 callback=self.sqrCheckCallback)

        jumpin_Y += vanillaControlsSize['CheckBoxRegularHeight']
        self.bcpLengthCheck = CheckBox((0, jumpin_Y, NET_WIDTH, vanillaControlsSize['CheckBoxRegularHeight']),
                                       "Show bcp length",
                                       value=self.bcpLengthActive,
                                       callback=self.bcpLengthCheckCallback)

    def getSqr(self):
        return self.sqrActive

    def getBcpLength(self):
        return self.bcpLengthActive

    def sqrCheckCallback(self, sender):
        self.sqrActive = bool(sender.get())
        self.callback(self)

    def bcpLengthCheckCallback(self, sender):
        self.bcpLengthActive = bool(sender.get())
        self.callback(self)
