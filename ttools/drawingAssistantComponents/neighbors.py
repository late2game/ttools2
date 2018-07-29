#!/usr/bin/env python
# coding: utf-8

###################
# neighbors ctrls #
###################

### Modules
from sharedValues import MARGIN_HOR, MARGIN_VER
from sharedValues import CURRENT_GLYPH_REPR, CURRENT_FONT_REPR

# custom
from ..ui.userInterfaceValues import vanillaControlsSize
from ..extraTools.miscFunctions import getOpenedFontFromPath

# standard
import os
from mojo.roboFont import AllFonts, CurrentFont, CurrentGlyph
from vanilla import Group, CheckBox, PopUpButton

### Functions and procedures
def makeGlyphList(aFont):
    if aFont:
        return [CURRENT_GLYPH_REPR, ' '.join('-'*5)] + aFont.glyphOrder
    else:
        return [CURRENT_GLYPH_REPR, ' '.join('-'*5)]

def makeFontList(openedFonts):
    return [CURRENT_FONT_REPR, ' '.join('-'*5)] + [os.path.basename(pth) for pth in openedFonts]


### Ctrl
class NeighborsController(Group):

    def __init__(self, posSize, openedFontPaths,
                       lftNeighborActive, lftFontPath, lftGlyphName,
                       cntNeighborActive, cntFontPath, cntGlyphName,
                       rgtNeighborActive, rgtFontPath, rgtGlyphName,
                       callback):

        Group.__init__(self, posSize)
        self.callback = callback
        self.ctrlHeight = posSize[3]

        self.neighborsDB = {}
        self.neighborsDB['lft'] = [lftNeighborActive, lftFontPath, lftGlyphName]
        self.neighborsDB['cnt'] = [cntNeighborActive, cntFontPath, cntGlyphName]
        self.neighborsDB['rgt'] = [rgtNeighborActive, rgtFontPath, rgtGlyphName]

        jumpin_X = 0
        self.lftController = SingleNeighborController((jumpin_X, 0, 60, self.ctrlHeight),
                                                      'Left',
                                                      isActive=lftNeighborActive,
                                                      openedFontPaths=openedFontPaths,
                                                      activeFontPath=lftFontPath,
                                                      activeGlyphName=lftGlyphName,
                                                      callback=self.lftControllerCallback)

        jumpin_X += 60+MARGIN_HOR
        self.cntController = SingleNeighborController((jumpin_X, 0, 60, self.ctrlHeight),
                                                      'Center',
                                                      isActive=cntNeighborActive,
                                                      openedFontPaths=openedFontPaths,
                                                      activeFontPath=cntFontPath,
                                                      activeGlyphName=cntGlyphName,
                                                      callback=self.cntControllerCallback)

        jumpin_X += 60+MARGIN_HOR
        self.rgtController = SingleNeighborController((jumpin_X, 0, 60, self.ctrlHeight),
                                                      'Right',
                                                      isActive=rgtNeighborActive,
                                                      openedFontPaths=openedFontPaths,
                                                      activeFontPath=rgtFontPath,
                                                      activeGlyphName=rgtGlyphName,
                                                      callback=self.rgtControllerCallback)

    def get(self):
        return self.neighborsDB

    def setFontData(self, openedFontPaths):
        self.lftController.setOpenedFonts(openedFontPaths)
        self.lftController.updateGlyphList()
        self.cntController.setOpenedFonts(openedFontPaths)
        self.cntController.updateGlyphList()
        self.rgtController.setOpenedFonts(openedFontPaths)
        self.rgtController.updateGlyphList()

    def lftControllerCallback(self, sender):
        self.neighborsDB['lft'] = sender.get()
        self.callback(self)

    def cntControllerCallback(self, sender):
        self.neighborsDB['cnt'] = sender.get()
        self.callback(self)

    def rgtControllerCallback(self, sender):
        self.neighborsDB['rgt'] = sender.get()
        self.callback(self)

class SingleNeighborController(Group):

    def __init__(self, posSize, title, isActive, openedFontPaths, activeFontPath, activeGlyphName, callback):
        Group.__init__(self, posSize)
        self.isActive = isActive
        self.openedFontPaths = openedFontPaths
        self.activeFontPath = activeFontPath
        self.activeGlyphName = activeGlyphName
        self.callback = callback
        ctrlWidth = posSize[2]

        # ui
        jumpingY = 4
        self.isActiveCheck = CheckBox((0, jumpingY, ctrlWidth, vanillaControlsSize['CheckBoxRegularHeight']),
                                      title,
                                      value=self.isActive,
                                      callback=self.isActiveCallback)

        jumpingY += vanillaControlsSize['CheckBoxRegularHeight']+2
        self.fontPop = PopUpButton((1, jumpingY, ctrlWidth-1, vanillaControlsSize['PopUpButtonRegularHeight']),
                                   makeFontList(openedFontPaths),
                                   callback=self.fontPopCallback)

        jumpingY += vanillaControlsSize['PopUpButtonRegularHeight']+MARGIN_VER

        if self.activeFontPath == CURRENT_FONT_REPR:
            activeFont = CurrentFont()
        else:
            activeFont = getOpenedFontFromPath(AllFonts(), self.activeFontPath)
        self.glyphPop = PopUpButton((1, jumpingY, ctrlWidth-1, vanillaControlsSize['ComboBoxRegularHeight']),
                                      makeGlyphList(activeFont),
                                      callback=self.glyphPopCallback)

    def updateCurrentGlyph(self):
        pass
        # if self.glyphPop.get() == 0:
        #     glyphName = CurrentGlyphWindow().getGlyph().name
        #     if self.activeFont.has_key(glyphName):
        #         self.activeGlyph = self.activeFont[glyphName]
        #     else:
        #         self.activeGlyph = None
        #     self.callback(self)

    def get(self):
        return self.isActive, self.activeFontPath, self.activeGlyphName

    def setOpenedFonts(self, openedFontPaths):
        self.openedFontPaths = openedFontPaths
        if self.openedFontPaths:
            fontList = makeFontList(self.openedFontPaths)
            self.fontPop.setItems(fontList)
            self.fontPop.set(fontList.index(self.activeFontPath))
        else:
            self.fontPop.setItems([])

    def updateGlyphList(self):
        if self.activeFontPath == CURRENT_FONT_REPR:
            activeFont = CurrentFont()
        else:
            activeFont = getOpenedFontFromPath(AllFonts(), self.activeFontPath)
        activeGlyphOrder = makeGlyphList(activeFont)
        self.glyphPop.setItems(activeGlyphOrder)
        self.glyphPop.set(activeGlyphOrder.index(self.activeGlyphName))

    def isActiveCallback(self, sender):
        self.isActive = bool(sender.get())
        self.callback(self)

    def fontPopCallback(self, sender):
        if sender.get() > 1:
            self.activeFontPath = self.openedFontPaths[sender.get()-2]
            activeFont = getOpenedFontFromPath(AllFonts(), self.activeFontPath)
        else:
            self.fontPop.set(0)
            self.activeFontPath = CURRENT_FONT_REPR
            activeFont = CurrentFont()

        activeGlyphOrder = makeGlyphList(activeFont)
        self.glyphPop.setItems(activeGlyphOrder)

        if self.activeGlyphName not in activeFont:
            self.activeGlyphName = activeGlyphOrder[0]

        self.glyphPop.set(activeGlyphOrder.index(self.activeGlyphName))
        self.callback(self)

    def glyphPopCallback(self, sender):
        if self.activeFontPath == CURRENT_FONT_REPR:
            activeFont = CurrentFont()
        else:
            activeFont = getOpenedFontFromPath(AllFonts(), self.activeFontPath)

        if sender.get() == 0:
            self.activeGlyphName = CurrentGlyph().name
        elif sender.get() == 1:
            self.activeGlyphName = None
        else:
            self.activeGlyphName = self.glyphPop.getItems()[sender.get()]

        self.callback(self)

