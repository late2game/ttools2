#!/usr/bin/env python
# -*- coding: utf-8 -*-

# custom modules
import kerningMisc
reload(kerningMisc)
from kerningMisc import MARGIN_VER
from ..userInterfaceValues import vanillaControlsSize 

# standard modules
from vanilla import Group, TextBox, Button, CheckBox

class GraphicsManager(Group):
    previousState = None

    def __init__(self, posSize, isSidebearingsActive, areGroupsShown, areCollisionsShown, isKerningDisplayActive, isMetricsActive, isColorsActive, callback):
        super(GraphicsManager, self).__init__(posSize)
        self.isKerningDisplayActive = isKerningDisplayActive
        self.areGroupsShown = areGroupsShown
        self.areCollisionsShown = areCollisionsShown
        self.isSidebearingsActive = isSidebearingsActive
        self.isMetricsActive = isMetricsActive
        self.isColorsActive = isColorsActive
        self.callback = callback

        self.ctrlWidth, self.ctrlHeight = posSize[2], posSize[3]

        jumping_Y = 0
        self.ctrlCaption = TextBox((0, jumping_Y, self.ctrlWidth, vanillaControlsSize['TextBoxRegularHeight']),
                                   'Display options:')

        jumping_Y = vanillaControlsSize['TextBoxRegularHeight'] + MARGIN_VER/2.
        indent = 16
        self.showKerningCheck = CheckBox((indent, jumping_Y, self.ctrlWidth-indent, vanillaControlsSize['CheckBoxRegularHeight']),
                                          'show kerning',
                                          value=self.isKerningDisplayActive,
                                          callback=self.showKerningCheckCallback)

        self.showKerningHiddenButton = Button((0,self.ctrlHeight+40,0,0),
                                              'hidden kerning button',
                                              callback=self.showKerningHiddenButtonCallback)
        # self.showKerningHiddenButton.show(False)
        self.showKerningHiddenButton.bind('k', ['command'])

        jumping_Y += vanillaControlsSize['CheckBoxRegularHeight']
        self.showGroupsCheck = CheckBox((indent, jumping_Y, self.ctrlWidth-indent, vanillaControlsSize['CheckBoxRegularHeight']),
                                        'show groups',
                                        value=self.areGroupsShown,
                                        callback=self.showGroupsCheckCallback)

        jumping_Y += vanillaControlsSize['CheckBoxRegularHeight']
        self.showCollisionsCheck = CheckBox((indent, jumping_Y, self.ctrlWidth-indent, vanillaControlsSize['CheckBoxRegularHeight']),
                                        'show collisions',
                                        value=self.areCollisionsShown,
                                        callback=self.showCollisionsCheckCallback)

        jumping_Y += vanillaControlsSize['CheckBoxRegularHeight']
        self.showSidebearingsCheck = CheckBox((indent, jumping_Y, self.ctrlWidth-indent, vanillaControlsSize['CheckBoxRegularHeight']),
                                          'show sidebearings',
                                          value=self.isSidebearingsActive,
                                          callback=self.showSidebearingsCheckCallback)

        jumping_Y += vanillaControlsSize['CheckBoxRegularHeight']
        self.showMetricsCheck = CheckBox((indent, jumping_Y, self.ctrlWidth-indent, vanillaControlsSize['CheckBoxRegularHeight']),
                                     'show metrics',
                                     value=self.isMetricsActive,
                                     callback=self.showMetricsCheckCallback)

        jumping_Y += vanillaControlsSize['CheckBoxRegularHeight']
        self.showColorsCheck = CheckBox((indent, jumping_Y, self.ctrlWidth-indent, vanillaControlsSize['CheckBoxRegularHeight']),
                                    'show corrections',
                                    value=self.isColorsActive,
                                    callback=self.showColorsCheckCallback)

    def get(self):
        return self.isKerningDisplayActive, self.areGroupsShown, self.areCollisionsShown, self.isSidebearingsActive, self.isMetricsActive, self.isColorsActive

    def switchControls(self, value):
        self.showSidebearingsCheck.enable(value)
        self.showMetricsCheck.enable(value)
        self.showColorsCheck.enable(value)
        self.showGroupsCheck.enable(value)
        self.showCollisionsCheck.enable(value)

    def showKerningCheckCallback(self, sender):
        self.isKerningDisplayActive = bool(sender.get())
        self.showColorsCheck.enable(bool(sender.get()))
        self.callback(self)

    def showGroupsCheckCallback(self, sender):
        self.areGroupsShown = bool(sender.get())
        self.callback(self)

    def showCollisionsCheckCallback(self, sender):
        self.areCollisionsShown = bool(sender.get())
        self.callback(self)

    def showKerningHiddenButtonCallback(self, sender):
        self.isKerningDisplayActive = not self.isKerningDisplayActive
        self.showKerningCheck.set(self.isKerningDisplayActive)
        self.callback(self)

    def showSidebearingsCheckCallback(self, sender):
        self.isSidebearingsActive = bool(sender.get())
        self.callback(self)

    def showMetricsCheckCallback(self, sender):
        self.isMetricsActive = bool(sender.get())
        self.callback(self)

    def showColorsCheckCallback(self, sender):
        self.isColorsActive = bool(sender.get())
        self.callback(self)