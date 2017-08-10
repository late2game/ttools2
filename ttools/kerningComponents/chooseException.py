#!/usr/bin/env python
# coding: utf-8

from ..userInterfaceValues import vanillaControlsSize
from vanilla import FloatingWindow, RadioGroup, Button
from defconAppKit.windows.baseWindow import BaseWindowController

MARGIN = 12

class ChooseExceptionWindow(BaseWindowController):
    lastEvent = None

    def __init__(self, options, callback):
        self.options = options
        self.callback = callback
        self.whichException = options[0]

        self.w = FloatingWindow((300, 120),
                        'Choose exception')

        self.w.optionsRadio = RadioGroup((MARGIN, MARGIN, 140, len(options)*20),
                                    options,
                                    callback=self.optionsCallback)
        self.w.optionsRadio.set(0)

        self.w.cancel = Button((-(90*2+MARGIN*2), -(vanillaControlsSize['ButtonRegularHeight']+MARGIN), 90, vanillaControlsSize['ButtonRegularHeight']),
                               'Cancel',
                               callback=self.cancelCallback)

        self.w.submit = Button((-(90+MARGIN), -(vanillaControlsSize['ButtonRegularHeight']+MARGIN), 90, vanillaControlsSize['ButtonRegularHeight']),
                               'Submit',
                               callback=self.submitCallback)

        self.w.open()

    def get(self):
        return self.whichException

    def enable(self, value):
        if value is True:
            self.w.center()
            self.w.show()
        else:
            self.w.hide()

    def close(self):
        self.whichException = None
        self.w.close()

    def setOptions(self, options):
        self.options = options
        optionsRepresentation = [', '.join(opt) for opt in self.options]

        delattr(self.w, 'optionsRadio')
        self.w.optionsRadio = RadioGroup((MARGIN, MARGIN, 140, len(options)*20),
                                    optionsRepresentation,
                                    callback=self.optionsCallback)

    def optionsCallback(self, sender):
        self.whichException = self.options[sender.get()]

    def cancelCallback(self, sender):
        self.lastEvent = 'cancel'
        self.whichException = None
        self.callback(self)
        self.w.hide()

    def submitCallback(self, sender):
        self.lastEvent = 'submit'
        self.callback(self)
        self.w.hide()
