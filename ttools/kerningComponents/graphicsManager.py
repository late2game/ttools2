#!/usr/bin/env python
# coding: utf-8

### Modules
# custom
import kerningMisc
reload(kerningMisc)
from kerningMisc import MARGIN_VER

from ..ui import userInterfaceValues
reload(userInterfaceValues)
from ..ui.userInterfaceValues import vanillaControlsSize

# standard
from vanilla import Group, TextBox, Button, CheckBox

### Classes
class GraphicsManager(Group):
    previousState = None

    def __init__(self, posSize,
                       isSidebearingsActive,
                       areGroupsShown,
                       areCollisionsShown,
                       isKerningDisplayActive,
                       areVerticalLettersDrawn,
                       isCorrectionActive,
                       isMetricsActive,
                       isColorsActive,
                       callback):

        super(GraphicsManager, self).__init__(posSize)
        self.isKerningDisplayActive = isKerningDisplayActive
        self.areVerticalLettersDrawn = areVerticalLettersDrawn
        self.areGroupsShown = areGroupsShown
        self.areCollisionsShown = areCollisionsShown
        self.isSidebearingsActive = isSidebearingsActive
        self.isCorrectionActive = isCorrectionActive
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
                                        'show pair collision',
                                        value=self.areCollisionsShown,
                                        callback=self.showCollisionsCheckCallback)

        jumping_Y += vanillaControlsSize['CheckBoxRegularHeight']
        self.showSidebearingsCheck = CheckBox((indent, jumping_Y, self.ctrlWidth-indent, vanillaControlsSize['CheckBoxRegularHeight']),
                                          'show sidebearings',
                                          value=self.isSidebearingsActive,
                                          callback=self.showSidebearingsCheckCallback)

        jumping_Y += vanillaControlsSize['CheckBoxRegularHeight']
        self.showCorrectionCheck = CheckBox((indent, jumping_Y, self.ctrlWidth-indent, vanillaControlsSize['CheckBoxRegularHeight']),
                                     'show corrections amount',
                                     value=self.isCorrectionActive,
                                     callback=self.showCorrectionCheckCallback)

        jumping_Y += vanillaControlsSize['CheckBoxRegularHeight']
        self.showColorsCheck = CheckBox((indent, jumping_Y, self.ctrlWidth-indent, vanillaControlsSize['CheckBoxRegularHeight']),
                                    'show color bars',
                                    value=self.isColorsActive,
                                    callback=self.showColorsCheckCallback)

        jumping_Y += vanillaControlsSize['CheckBoxRegularHeight']
        self.showMetricsCheck = CheckBox((indent, jumping_Y, self.ctrlWidth-indent, vanillaControlsSize['CheckBoxRegularHeight']),
                                     'show metrics',
                                     value=self.isMetricsActive,
                                     callback=self.showMetricsCheckCallback)

        jumping_Y += vanillaControlsSize['CheckBoxRegularHeight']
        self.verticalLettersCheck = CheckBox((indent, jumping_Y, self.ctrlWidth-indent, vanillaControlsSize['CheckBoxRegularHeight']),
                                        'show vertical letters',
                                        value=self.areGroupsShown,
                                        callback=self.verticalLettersCheckCallback)

    def set(self, isKerningDisplayActive,
                  areVerticalLettersDrawn,
                  areGroupsShown,
                  areCollisionsShown,
                  isSidebearingsActive,
                  isCorrectionActive,
                  isMetricsActive,
                  isColorsActive):

        # update attributes
        self.isKerningDisplayActive = isKerningDisplayActive
        self.areVerticalLettersDrawn = areVerticalLettersDrawn
        self.areGroupsShown = areGroupsShown
        self.areCollisionsShown = areCollisionsShown
        self.isSidebearingsActive = isSidebearingsActive
        self.isCorrectionActive = isCorrectionActive
        self.isMetricsActive = isMetricsActive
        self.isColorsActive = isColorsActive

        # aligning controls
        self.showKerningCheck.set(self.isKerningDisplayActive)
        self.showGroupsCheck.set(self.areGroupsShown)
        self.showCollisionsCheck.set(self.areCollisionsShown)
        self.showSidebearingsCheck.set(self.isSidebearingsActive)
        self.showCorrectionCheck.set(self.isCorrectionActive)
        self.showColorsCheck.set(self.isColorsActive)
        self.showMetricsCheck.set(self.isMetricsActive)
        self.verticalLettersCheck.set(self.areVerticalLettersDrawn)


    def get(self):
        return (self.isKerningDisplayActive,
                self.areVerticalLettersDrawn,
                self.areGroupsShown,
                self.areCollisionsShown,
                self.isSidebearingsActive,
                self.isCorrectionActive,
                self.isMetricsActive,
                self.isColorsActive)

    def switchControls(self, value):
        self.showKerningCheck.enable(value)
        self.showSidebearingsCheck.enable(value)
        self.showGroupsCheck.enable(value)
        self.showCorrectionCheck.enable(value)
        self.showMetricsCheck.enable(value)
        self.showColorsCheck.enable(value)
        self.showCollisionsCheck.enable(value)
        self.verticalLettersCheck.enable(value)

    def showKerningCheckCallback(self, sender):
        self.isKerningDisplayActive = bool(sender.get())
        self.callback(self)

    def showGroupsCheckCallback(self, sender):
        self.areGroupsShown = bool(sender.get())
        self.callback(self)

    def verticalLettersCheckCallback(self, sender):
        self.areVerticalLettersDrawn = bool(sender.get())
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

    def showCorrectionCheckCallback(self, sender):
        self.isCorrectionActive = bool(sender.get())
        self.callback(self)

    def showMetricsCheckCallback(self, sender):
        self.isMetricsActive = bool(sender.get())
        self.callback(self)

    def showColorsCheckCallback(self, sender):
        self.isColorsActive = bool(sender.get())
        self.callback(self)
