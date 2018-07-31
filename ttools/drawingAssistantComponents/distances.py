#!/usr/bin/env python
# coding: utf-8

######################
# stem distance ctrl #
######################

### Modules
# standard
from __future__ import division
import importlib
from vanilla import Group, CheckBox, ColorWell, SquareButton
from AppKit import NSColor
from mojo.roboFont import version

# custom
import sharedValues
importlib.reload(sharedValues)
from sharedValues import MARGIN_HOR, MARGIN_VER
from sharedValues import STEM_KEY, DIAGONALS_KEY

# custom
from ..ui import userInterfaceValues
importlib.reload(userInterfaceValues)
from ..ui.userInterfaceValues import vanillaControlsSize

from ..extraTools import miscFunctions
importlib.reload(miscFunctions)
from ..extraTools.miscFunctions import collectIDsFromSelectedPoints, guessStemPoints


### Constants
STEM_COLOR = (1, 127/255., 102/255., 1)
DIAGONAL_COLOR = (102/255., 124/255., 1, 1)

### Ctrls
class DistancesController(Group):

    def __init__(self, posSize, stemActive, diagonalActive, currentGlyph, callback):
        Group.__init__(self, posSize)
        self.callback = callback
        self.ctrlWidth, self.ctrlHeight = posSize[2], posSize[3]
        self.stemActive = stemActive
        self.diagonalActive = diagonalActive
        self.currentGlyph = currentGlyph

        self.stemColor = STEM_COLOR
        self.diagonalColor = DIAGONAL_COLOR

        jumpin_Y = 4
        self.stemsCheck = CheckBox((0, jumpin_Y, self.ctrlWidth*.6, vanillaControlsSize['CheckBoxRegularHeight']),
                                   "Show stems",
                                   value=self.stemActive,
                                   callback=self.stemsCheckCallback)

        self.stemsColorWell = ColorWell((-MARGIN_HOR-46, jumpin_Y, 46, vanillaControlsSize['CheckBoxRegularHeight']),
                                        color=NSColor.colorWithCalibratedRed_green_blue_alpha_(*self.stemColor),
                                        callback=self.stemsColorWellCallback)

        jumpin_Y += vanillaControlsSize['CheckBoxRegularHeight'] + MARGIN_VER*.5
        self.diagonalsCheck = CheckBox((0, jumpin_Y, self.ctrlWidth*.6, vanillaControlsSize['CheckBoxRegularHeight']),
                                       "Show diagonals",
                                       value=self.diagonalActive,
                                       callback=self.diagonalsCheckCallback)

        self.diagonalsColorWell = ColorWell((-MARGIN_HOR-46, jumpin_Y, 46, vanillaControlsSize['CheckBoxRegularHeight']),
                                            color=NSColor.colorWithCalibratedRed_green_blue_alpha_(*self.diagonalColor),
                                            callback=self.diagonalsColorWellCallback)

        jumpin_Y += vanillaControlsSize['CheckBoxRegularHeight'] + MARGIN_VER
        self.addStemButton = SquareButton((0, jumpin_Y, self.ctrlWidth*.45, vanillaControlsSize['ButtonRegularHeight']*2.5),
                                          "Add\nStem",
                                          callback=self.addStemButtonCallback)

        self.addDiagonalsButton = SquareButton((-self.ctrlWidth*.45-MARGIN_HOR, jumpin_Y, self.ctrlWidth*.45, vanillaControlsSize['ButtonRegularHeight']*2.5),
                                               "Add\nDiagonal",
                                               callback=self.addDiagonalsButtonCallback)

        jumpin_Y += vanillaControlsSize['ButtonRegularHeight']*2.5+MARGIN_VER
        self.deleteButton = SquareButton((0, jumpin_Y, self.ctrlWidth*.45, vanillaControlsSize['ButtonRegularHeight']*1.5),
                                         "Delete",
                                         callback=self.deleteButtonCallback)

        self.clearLibButton = SquareButton((-self.ctrlWidth*.45-MARGIN_HOR, jumpin_Y, self.ctrlWidth*.45, vanillaControlsSize['ButtonRegularHeight']*1.5),
                                           "Clear lib",
                                           callback=self.clearLibButtonCallback)

    def setCurrentGlyph(self, glyph):
        self.currentGlyph = glyph

    def get(self):
        return self.stemActive, self.stemColor, self.diagonalActive, self.diagonalColor

    def stemsCheckCallback(self, sender):
        self.stemActive = bool(sender.get())
        self.callback(self)

    def stemsColorWellCallback(self, sender):
        calibratedColor = sender.get()
        self.stemColor = (calibratedColor.redComponent(),
                          calibratedColor.greenComponent(),
                          calibratedColor.blueComponent(),
                          calibratedColor.alphaComponent())
        self.callback(self)

    def diagonalsCheckCallback(self, sender):
        self.diagonalActive = bool(sender.get())
        self.callback(self)

    def diagonalsColorWellCallback(self, sender):
        calibratedColor = sender.get()
        self.diagonalColor = (calibratedColor.redComponent(),
                              calibratedColor.greenComponent(),
                              calibratedColor.blueComponent(),
                              calibratedColor.alphaComponent())
        self.callback(self)

    def addStemButtonCallback(self, sender):
        if self.currentGlyph and STEM_KEY not in self.currentGlyph.lib:
            self.currentGlyph.prepareUndo(undoTitle='create a {} lib'.format(STEM_KEY))
            self.currentGlyph.lib[STEM_KEY] = []
            self.currentGlyph.performUndo()

        selectedPointsIDs = collectIDsFromSelectedPoints(self.currentGlyph)
        if len(selectedPointsIDs) < 2:
            return None

        elif len(selectedPointsIDs) == 2:
            if tuple(selectedPointsIDs) not in self.currentGlyph.lib[STEM_KEY]:
                self.currentGlyph.prepareUndo(undoTitle='append a stem to {} lib'.format(STEM_KEY))
                self.currentGlyph.lib[STEM_KEY].append(tuple(selectedPointsIDs))
                self.currentGlyph.performUndo()

        else:      # more than 2
            guessedStems = guessStemPoints(self.currentGlyph)
            for eachStem in guessedStems:
                if eachStem not in self.currentGlyph.lib[STEM_KEY]:
                    self.currentGlyph.prepareUndo(undoTitle='append a stem to {} lib'.format(STEM_KEY))
                    self.currentGlyph.lib[STEM_KEY].append(eachStem)
                    self.currentGlyph.performUndo()
        if version[0] == '2':
            self.currentGlyph.changed()
        else:
            self.currentGlyph.update()

    def addDiagonalsButtonCallback(self, sender):
        if self.currentGlyph and DIAGONALS_KEY not in self.currentGlyph.lib:
            self.currentGlyph.prepareUndo(undoTitle='create a {} lib'.format(DIAGONALS_KEY))
            self.currentGlyph.lib[DIAGONALS_KEY] = []
            self.currentGlyph.performUndo()

        selectedPointsIDs = collectIDsFromSelectedPoints(self.currentGlyph)
        if len(selectedPointsIDs) == 2:
            if tuple(selectedPointsIDs) not in self.currentGlyph.lib[DIAGONALS_KEY]:
                self.currentGlyph.prepareUndo(undoTitle='append a stem to {} lib'.format(DIAGONALS_KEY))
                self.currentGlyph.lib[DIAGONALS_KEY].append(tuple(selectedPointsIDs))
                self.currentGlyph.performUndo()

    def deleteButtonCallback(self, sender):
        selectedPointsIDs = collectIDsFromSelectedPoints(self.currentGlyph)
        if len(selectedPointsIDs) > 0:
            if STEM_KEY in self.currentGlyph.lib:
                for eachID in selectedPointsIDs:
                    originalStemStatus = self.currentGlyph.lib[STEM_KEY]
                    for eachStem in originalStemStatus:
                        if eachID in eachStem:
                            self.currentGlyph.prepareUndo(undoTitle='remove a stem from {} lib'.format(STEM_KEY))
                            self.currentGlyph.lib[STEM_KEY].remove(eachStem)
                            self.currentGlyph.performUndo()

            if DIAGONALS_KEY in self.currentGlyph.lib:
                for eachID in selectedPointsIDs:
                    originalStemStatus = self.currentGlyph.lib[DIAGONALS_KEY]
                    for eachStem in originalStemStatus:
                        if eachID in eachStem:
                            self.currentGlyph.prepareUndo(undoTitle='remove a stem from {} lib'.format(DIAGONALS_KEY))
                            self.currentGlyph.lib[DIAGONALS_KEY].remove(eachStem)
                            self.currentGlyph.performUndo()
            if version[0] == '2':
                self.currentGlyph.changed()
            else:
                self.currentGlyph.update()
        else:
            return None

    def clearLibButtonCallback(self, sender):
        if STEM_KEY in self.currentGlyph.lib:
            del self.currentGlyph.lib[STEM_KEY]

        if DIAGONALS_KEY in self.currentGlyph.lib:
            del self.currentGlyph.lib[DIAGONALS_KEY]

