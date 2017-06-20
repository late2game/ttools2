#!/usr/bin/env python
# -*- coding: utf-8 -*-

##################################################
# Choose exception window for kerning controller #
##################################################

import userInterfaceValues
reload(userInterfaceValues)
from userInterfaceValues import vanillaControlsSize
from vanilla import Window, RadioGroup, Button

MARGIN = 12

class ChooseException(object):

    def __init__(self, options):
        self.options = options
        self.whichException = options[0]

        self.w = Window((300, 120),
                        'Choose exception')

        self.w.options = RadioGroup((MARGIN, MARGIN, 140, len(options)*20),
                                    options,
                                    callback=self.optionsCallback)
        self.w.options.set(0)

        self.w.cancel = Button((-(90*2+MARGIN*2), -(vanillaControlsSize['ButtonRegularHeight']+MARGIN), 90, vanillaControlsSize['ButtonRegularHeight']),
                               'Cancel',
                               callback=self.cancelCallback)

        self.w.submit = Button((-(90+MARGIN), -(vanillaControlsSize['ButtonRegularHeight']+MARGIN), 90, vanillaControlsSize['ButtonRegularHeight']),
                               'Submit',
                               callback=self.submitCallback)

        self.w.open()

    def optionsCallback(self, sender):
        self.whichException = self.options[sender.get()]

    def cancelCallback(self, sender):
        self.w.close()

    def submitCallback(self, sender):
        self.w.close()






