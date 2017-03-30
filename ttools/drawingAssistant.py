#!/usr/bin/env python
# -*- coding: utf-8 -*-

#####################
# Drawing Assistant #
#####################

### Modules
# custom
import userInterfaceValues
reload(userInterfaceValues)
from userInterfaceValues import vanillaControlsSize

import calcFunctions
reload(calcFunctions)
from calcFunctions import intersectionBetweenSegments, calcAngle, calcDistance
from calcFunctions import calcStemsData, calcDiagonalsData, calcMidPoint

import miscFunctions
reload(miscFunctions)
from miscFunctions import collectIDsFromSelectedPoints, guessStemPoints
from miscFunctions import getOpenedFontFromPath

# standard
import os, sys
from math import cos, sin, radians, tan, ceil
from mojo.UI import UpdateCurrentGlyphView, AccordionView
from vanilla import FloatingWindow, CheckBox, Group
from vanilla import TextBox, EditText, ColorWell, SquareButton
from vanilla import PopUpButton, ComboBox
from mojo.drawingTools import *
from mojo.UI import OpenGlyphWindow
from defconAppKit.windows.baseWindow import BaseWindowController
from AppKit import NSColor
from mojo.events import addObserver, removeObserver

### Constants
PLUGIN_TITLE = 'TTdrawingAssistant'
STEM_KEY = 'TTdrawingAssistant_stems'
DIAGONALS_KEY = 'TTdrawingAssistant_diagonals'

GRID_TOLERANCE = 2

# ui
BODYSIZE_CAPTION = 11
SQR_CAPTION_OFFSET = 4
BCP_RADIUS = 4
OFFGRID_RADIUS = 20

SYSTEM_FONT_NAME = '.HelveticaNeueDeskInterface-Regular'
SYSTEM_FONT_NAME_BOLD = '.HelveticaNeueDeskInterface-Bold'

BLACK_COLOR = (0, 0, 0)
LIGHT_GRAY_COLOR = (.6, .6, .6)
RED_COLOR = (1,0,0)
WHITE_COLOR = (1, 1, 1)

STEM_COLOR = (1, 127/255., 102/255., 1)
DIAGONAL_COLOR = (102/255., 124/255., 1, 1)
DIAGONAL_OFFSET = 3

GRID_COLOR_ONE = (1, 0.4, 0.4, 1)
GRID_COLOR_TWO = (0.4, 0.64, 1, 1)
GRID_COLOR_THREE = (0.88, 0.4, 1, 1)
GRID_COLOR_FOUR = (0.4, 1, 0.64, 1)
GRID_COLOR_FIVE = (0.88, 1, 0.4, 1)
GRID_COLOR_INIT = [GRID_COLOR_ONE, GRID_COLOR_TWO, GRID_COLOR_THREE, GRID_COLOR_FOUR, GRID_COLOR_FIVE]

PLUGIN_WIDTH = 230

MARGIN_HOR = 10
MARGIN_VER = 8

NET_WIDTH = PLUGIN_WIDTH - MARGIN_HOR*2

"""
BaseWindowController methods
    def setUpBaseWindowBehavior(self)
    def windowCloseCallback(self, sender)
    def windowSelectCallback(self, sender)
    def windowDeselectCallback(self, sender)
    def startProgress(self, text="", tickCount=None)
    def showMessage(self, messageText, informativeText, callback=None)
    def showAskYesNo(self, messageText, informativeText, callback)
    def showGetFolder(self, callback)
    def showGetFile(self, fileTypes, callback, allowsMultipleSelection=False)
    def showPutFile(self, fileTypes, callback, fileName=None, directory=None, accessoryView=None)

"""


def textQualities(scaledFontSize, weight='regular', color=BLACK_COLOR):
    stroke(None)
    fill(*color)
    if weight == 'bold':
        font(SYSTEM_FONT_NAME_BOLD)
    else:
        font(SYSTEM_FONT_NAME)
    fontSize(scaledFontSize)


class MultipleGridController(Group):

    def __init__(self, posSize, gridActive, ctrlsAmount, activeCtrls, offgridActive, callback):
        Group.__init__(self, posSize)
        assert activeCtrls <= ctrlsAmount

        self.ctrlHeight = posSize[3]
        self.gridActive = gridActive
        self.ctrlsAmount = ctrlsAmount
        self.activeCtrls = activeCtrls
        self.offgridActive = offgridActive
        self.gridIndexes = ['%d' % integ for integ in range(1, ctrlsAmount+1)]
        self.callback = callback

        self.gridsDB = [{'horizontal': False, 'vertical': False, 'step': None, 'color': color} for color in GRID_COLOR_INIT]

        jumpin_Y = 4
        self.gridActiveCheck = CheckBox((0, jumpin_Y, NET_WIDTH*.6, vanillaControlsSize['CheckBoxRegularHeight']),
                                        "Show grids",
                                        value=self.gridActive,
                                        callback=self.gridActiveCheckCallback)

        for eachI in range(1, ctrlsAmount+1):
            jumpin_Y += vanillaControlsSize['EditTextRegularHeight'] + MARGIN_VER
            gridCtrl = SingleGridController((0, jumpin_Y, NET_WIDTH, vanillaControlsSize['EditTextRegularHeight']),
                                            index=eachI,
                                            isVertical=False,
                                            isHorizontal=False,
                                            step=None,
                                            gridColor=GRID_COLOR_INIT[eachI-1],
                                            callback=self.gridCtrlCallback)
            gridCtrl.enable(self.gridActive)
            setattr(self, 'grid%#02d' % eachI, gridCtrl)

        jumpin_Y += vanillaControlsSize['EditTextRegularHeight'] + MARGIN_VER
        self.showOffgridCheck = CheckBox((0, jumpin_Y, NET_WIDTH, vanillaControlsSize['CheckBoxRegularHeight']),
                                         "Show offgrid points",
                                         value=self.offgridActive,
                                         callback=self.showOffgridCheckCallback)

    def get(self):
        return self.gridActive, self.gridsDB, self.offgridActive

    def gridCtrlCallback(self, sender):
        ctrlIndex, ctrlDB = sender.get()
        self.gridsDB[ctrlIndex] = ctrlDB
        self.callback(self)

    def gridActiveCheckCallback(self, sender):
        self.gridActive = bool(sender.get())
        for eachI in range(1, self.ctrlsAmount+1):
            gridCtrl = getattr(self, 'grid%#02d' % eachI)
            gridCtrl.enable(self.gridActive)
        self.callback(self)

    def showOffgridCheckCallback(self, sender):
        self.offgridActive = bool(sender.get())
        self.callback(self)


class SingleGridController(Group):
    """this controller takes care of canvas grid drawing"""

    def __init__(self, posSize, index, isVertical, isHorizontal, step, gridColor, callback):
        Group.__init__(self, posSize)

        # from arguments to attributes
        self.ctrlX, self.ctrlY, self.ctrlWidth, self.ctrlHeight = posSize
        self.index = index
        self.isVertical = isVertical
        self.isHorizontal = isHorizontal
        self.step = step
        self.gridColor = gridColor
        self.callback = callback

        # ctrls
        jumpin_X = 12
        self.indexText = TextBox((jumpin_X, 0, 16, vanillaControlsSize['TextBoxRegularHeight']), '%d)' % index)
        jumpin_X += self.indexText.getPosSize()[2]

        self.stepCtrl = EditText((jumpin_X, 0, 38, vanillaControlsSize['EditTextRegularHeight']),
                                 callback=self.stepCtrlCallback)
        jumpin_X += self.stepCtrl.getPosSize()[2] + 16

        self.isHorizontalCheck = CheckBox((jumpin_X, 0, 32, vanillaControlsSize['CheckBoxRegularHeight']),
                                          "H",
                                          value=self.isHorizontal,
                                          callback=self.isHorizontalCheckCallback)
        jumpin_X += self.isHorizontalCheck.getPosSize()[2]+2

        self.isVerticalCheck = CheckBox((jumpin_X, 0, 32, vanillaControlsSize['CheckBoxRegularHeight']),
                                        "V",
                                        value=self.isVertical,
                                        callback=self.isVerticalCheckCallback)
        jumpin_X += self.isVerticalCheck.getPosSize()[2]+10

        self.whichColorWell = ColorWell((jumpin_X, 0, 46, self.ctrlHeight),
                                        color=NSColor.colorWithCalibratedRed_green_blue_alpha_(*gridColor),
                                        callback=self.whichColorWellCallback)

    def enable(self, onOff):
        self.indexText.enable(onOff)
        self.stepCtrl.enable(onOff)
        self.isHorizontalCheck.enable(onOff)
        self.isVerticalCheck.enable(onOff)
        self.whichColorWell.enable(onOff)

    def get(self):
        return self.index-1, {'horizontal': self.isHorizontal, 'vertical': self.isVertical, 'step': self.step, 'color': self.gridColor}

    def stepCtrlCallback(self, sender):
        try:
            self.step = int(sender.get())
            self.callback(self)
        except ValueError as error:
            print error

    def isHorizontalCheckCallback(self, sender):
        self.isHorizontal = bool(sender.get())
        self.callback(self)

    def isVerticalCheckCallback(self, sender):
        self.isVertical = bool(sender.get())
        self.callback(self)

    def whichColorWellCallback(self, sender):
        calibratedColor = sender.get()
        self.gridColor = (calibratedColor.redComponent(),
                          calibratedColor.greenComponent(),
                          calibratedColor.blueComponent(),
                          calibratedColor.alphaComponent())
        self.callback(self)


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
        self.addStemButton = SquareButton((0, jumpin_Y, self.ctrlWidth*.45, vanillaControlsSize['ButtonRegularHeight']*2),
                                          "Add\nStem",
                                          callback=self.addStemButtonCallback)

        self.addDiagonalsButton = SquareButton((-self.ctrlWidth*.45-MARGIN_HOR, jumpin_Y, self.ctrlWidth*.45, vanillaControlsSize['ButtonRegularHeight']*2),
                                               "Add\nDiagonal",
                                               callback=self.addDiagonalsButtonCallback)

        jumpin_Y += vanillaControlsSize['ButtonRegularHeight']*2+MARGIN_VER
        self.deleteButton = SquareButton((0, jumpin_Y, -MARGIN_HOR, vanillaControlsSize['ButtonRegularHeight']*1.5),
                                         "Delete",
                                         callback=self.deleteButtonCallback)

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
            self.currentGlyph.prepareUndo(undoTitle='create a %s lib' % STEM_KEY)
            self.currentGlyph.lib[STEM_KEY] = []
            self.currentGlyph.performUndo()

        selectedPointsIDs = collectIDsFromSelectedPoints(self.currentGlyph)
        if len(selectedPointsIDs) < 2:
            return None

        elif len(selectedPointsIDs) == 2:
            if tuple(selectedPointsIDs) not in self.currentGlyph.lib[STEM_KEY]:
                self.currentGlyph.prepareUndo(undoTitle='append a stem to %s lib' % STEM_KEY)
                self.currentGlyph.lib[STEM_KEY].append(tuple(selectedPointsIDs))
                self.currentGlyph.performUndo()

        else:      # more than 2
            guessedStems = guessStemPoints(self.currentGlyph)
            for eachStem in guessedStems:
                if eachStem not in self.currentGlyph.lib[STEM_KEY]:
                    self.currentGlyph.prepareUndo(undoTitle='append a stem to %s lib' % STEM_KEY)
                    self.currentGlyph.lib[STEM_KEY].append(eachStem)
                    self.currentGlyph.performUndo()

        self.currentGlyph.update()

    def addDiagonalsButtonCallback(self, sender):
        if self.currentGlyph and DIAGONALS_KEY not in self.currentGlyph.lib:
            self.currentGlyph.prepareUndo(undoTitle='create a %s lib' % DIAGONALS_KEY)
            self.currentGlyph.lib[DIAGONALS_KEY] = []
            self.currentGlyph.performUndo()

        selectedPointsIDs = collectIDsFromSelectedPoints(self.currentGlyph)
        if len(selectedPointsIDs) == 2:
            if tuple(selectedPointsIDs) not in self.currentGlyph.lib[DIAGONALS_KEY]:
                self.currentGlyph.prepareUndo(undoTitle='append a stem to %s lib' % DIAGONALS_KEY)
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
                            self.currentGlyph.prepareUndo(undoTitle='remove a stem from %s lib' % STEM_KEY)
                            self.currentGlyph.lib[STEM_KEY].remove(eachStem)
                            self.currentGlyph.performUndo()

            if DIAGONALS_KEY in self.currentGlyph.lib:
                for eachID in selectedPointsIDs:
                    originalStemStatus = self.currentGlyph.lib[DIAGONALS_KEY]
                    for eachStem in originalStemStatus:
                        if eachID in eachStem:
                            self.currentGlyph.prepareUndo(undoTitle='remove a stem from %s lib' % DIAGONALS_KEY)
                            self.currentGlyph.lib[DIAGONALS_KEY].remove(eachStem)
                            self.currentGlyph.performUndo()
            self.currentGlyph.update()
        else:
            return None


class NeighborsController(Group):

    def __init__(self, posSize, openedFonts, lftNeighborActive, lftFont, lftGlyph, cntNeighborActive, cntFont, cntGlyph, rgtNeighborActive, rgtFont, rgtGlyph, callback):
        Group.__init__(self, posSize)
        self.callback = callback
        self.ctrlHeight = posSize[3]

        self.neighborsDB = {}
        self.neighborsDB['lft'] = [lftNeighborActive, lftFont, lftGlyph]
        self.neighborsDB['cnt'] = [cntNeighborActive, cntFont, cntGlyph]
        self.neighborsDB['rgt'] = [rgtNeighborActive, rgtFont, rgtGlyph]

        jumpin_X = 0
        self.lftController = SingleNeighborController((jumpin_X, 0, 60, self.ctrlHeight),
                                                      'Left',
                                                      isActive=lftNeighborActive,
                                                      openedFonts=openedFonts,
                                                      activeFont=lftFont,
                                                      activeGlyph=lftGlyph,
                                                      callback=self.lftControllerCallback)

        jumpin_X += 60+MARGIN_HOR
        self.cntController = SingleNeighborController((jumpin_X, 0, 60, self.ctrlHeight),
                                                      'Center',
                                                      isActive=cntNeighborActive,
                                                      openedFonts=openedFonts,
                                                      activeFont=cntFont,
                                                      activeGlyph=cntGlyph,
                                                      callback=self.cntControllerCallback)

        jumpin_X += 60+MARGIN_HOR
        self.rgtController = SingleNeighborController((jumpin_X, 0, 60, self.ctrlHeight),
                                                      'Right',
                                                      isActive=rgtNeighborActive,
                                                      openedFonts=openedFonts,
                                                      activeFont=rgtFont,
                                                      activeGlyph=rgtGlyph,
                                                      callback=self.rgtControllerCallback)

    def get(self):
        return self.neighborsDB

    def setFontData(self, openedFonts):
        self.lftController.setOpenedFonts(openedFonts)
        self.lftController.updateGlyphList()
        self.cntController.setOpenedFonts(openedFonts)
        self.cntController.updateGlyphList()
        self.rgtController.setOpenedFonts(openedFonts)
        self.rgtController.updateGlyphList()

    def lftControllerCallback(self, sender):
        self.neighborsDB['lft'] = list(sender.get())
        self.callback(self)

    def cntControllerCallback(self, sender):
        self.neighborsDB['cnt'] = list(sender.get())
        self.callback(self)

    def rgtControllerCallback(self, sender):
        self.neighborsDB['rgt'] = list(sender.get())
        self.callback(self)


class SingleNeighborController(Group):

    chosenFont = None
    glyphName = None
    isActive = False

    def __init__(self, posSize, title, isActive, openedFonts, activeFont, activeGlyph, callback):
        Group.__init__(self, posSize)
        self.isActive = isActive
        self.openedFonts = openedFonts
        self.activeFont = activeFont
        self.activeGlyph = activeGlyph
        self.callback = callback
        ctrlWidth = posSize[2]

        if self.activeFont:
            activeGlyphOrder = self.activeFont.glyphOrder
        else:
            activeGlyphOrder = []

        jumpingY = 4
        self.isActiveCheck = CheckBox((0, jumpingY, ctrlWidth, vanillaControlsSize['CheckBoxRegularHeight']),
                                      title,
                                      value=self.isActive,
                                      callback=self.isActiveCallback)

        jumpingY += vanillaControlsSize['CheckBoxRegularHeight']+2
        self.fontPop = PopUpButton((1, jumpingY, ctrlWidth-1, vanillaControlsSize['PopUpButtonRegularHeight']),
                                   [os.path.basename(pth) for pth in openedFonts],
                                   callback=self.fontPopCallback)

        jumpingY += vanillaControlsSize['PopUpButtonRegularHeight']+MARGIN_VER
        self.glyphPop = PopUpButton((1, jumpingY, ctrlWidth-1, vanillaControlsSize['ComboBoxRegularHeight']),
                                      activeGlyphOrder,
                                      callback=self.glyphPopCallback)

    def get(self):
        return self.isActive, self.activeFont, self.activeGlyph

    def setOpenedFonts(self, openedFonts):
        self.openedFonts = openedFonts

        if self.openedFonts:
            self.fontPop.setItems([os.path.basename(pth) for pth in openedFonts])
            self.fontPop.set(self.openedFonts.index(self.activeFont.path))
        else:
            self.fontPop.setItems([])

    def updateGlyphList(self):
        if self.activeFont:
            self.glyphPop.setItems(self.activeFont.glyphOrder)
            self.glyphPop.set(self.activeFont.glyphOrder.index(self.activeGlyph.name))
        else:
            self.glyphPop.setItems([])

    def isActiveCallback(self, sender):
        self.isActive = bool(sender.get())
        self.callback(self)

    def fontPopCallback(self, sender):
        self.activeFont = getOpenedFontFromPath(AllFonts(), self.openedFonts[sender.get()])
        self.glyphPop.setItems(self.activeFont.glyphOrder)
        if self.activeFont.has_key(self.activeGlyph.name):
            self.activeGlyph = self.activeFont[self.activeGlyph.name]
        else:
            self.activeGlyph = self.activeFont[self.activeFont.glyphOrder[0]]
        self.glyphPop.set(self.activeFont.glyphOrder.index(self.activeGlyph.name))
        self.callback(self)

    def glyphPopCallback(self, sender):
        self.activeGlyph = self.activeFont[self.activeFont.glyphOrder[sender.get()]]
        self.callback(self)


class DrawingAssistant(BaseWindowController):
    """the aim of this plugin is to provide useful visualizations on glyph canvas"""

    # switches
    sqrActive = False
    bcpLengthActive = False
    gridActive = False
    offgridActive = False
    stemActive = False
    diagonalActive = False

    openedFonts = []

    lftNeighborActive = False
    lftFont = None
    lftGlyph = None
    cntNeighborActive = False
    cntFont = None
    cntGlyph = None
    rgtNeighborActive = False
    rgtFont = None
    rgtGlyph = None

    gridsDB = []

    def __init__(self):

        # collect currentGlyph (if available)
        self.currentGlyph = CurrentGlyph()

        # collect opened fonts
        if AllFonts():
            self.collectOpenedFonts()

        # init fonts
        if self.openedFonts:
            self._initFontsAndGlyphs()

        # init views
        self.bcpController = BcpController((MARGIN_HOR, 0, NET_WIDTH, vanillaControlsSize['CheckBoxRegularHeight']*2.5),
                                           sqrActive=self.sqrActive,
                                           bcpLengthActive=self.bcpLengthActive,
                                           callback=self.bcpControllerCallback)

        self.gridController = MultipleGridController((MARGIN_HOR, 0, NET_WIDTH, 220),
                                                     gridActive=self.gridActive,
                                                     ctrlsAmount=5,
                                                     activeCtrls=0,
                                                     offgridActive=self.offgridActive,
                                                     callback=self.gridControllerCallback)

        self.distancesController = DistancesController((MARGIN_HOR, 0, NET_WIDTH, 148),
                                                       stemActive=self.stemActive,
                                                       diagonalActive=self.diagonalActive,
                                                       currentGlyph=self.currentGlyph,
                                                       callback=self.distancesControllerCallback)

        self.neighborsController = NeighborsController((MARGIN_HOR, 0, NET_WIDTH, 94),
                                                       openedFonts=self.openedFonts,
                                                       lftNeighborActive=self.lftNeighborActive,
                                                       lftFont=self.lftFont,
                                                       lftGlyph=self.lftGlyph,
                                                       cntNeighborActive=self.cntNeighborActive,
                                                       cntFont=self.cntFont,
                                                       cntGlyph=self.cntGlyph,
                                                       rgtNeighborActive=self.rgtNeighborActive,
                                                       rgtFont=self.rgtFont,
                                                       rgtGlyph=self.rgtGlyph,
                                                       callback=self.neighborsControllerCallback)

        # collect views
        accordionItems = [
                {'label': 'bcp controller',       'view': self.bcpController,       'size': self.bcpController.ctrlHeight,       'collapsed': False, 'canResize': False},
                {'label': 'grid controller',      'view': self.gridController,      'size': self.gridController.ctrlHeight,      'collapsed': False, 'canResize': False},
                {'label': 'distances controller', 'view': self.distancesController, 'size': self.distancesController.ctrlHeight, 'collapsed': False, 'canResize': False},
                {'label': 'neighbors controller', 'view': self.neighborsController, 'size': self.neighborsController.ctrlHeight, 'collapsed': False, 'canResize': False},
            ]

        # init window with accordion obj
        totalHeight = self.bcpController.ctrlHeight + self.gridController.ctrlHeight + self.distancesController.ctrlHeight + self.neighborsController.ctrlHeight + 18*4
        self.w = FloatingWindow((0, 0, PLUGIN_WIDTH, totalHeight),
                                PLUGIN_TITLE,
                                minSize=(PLUGIN_WIDTH, 200),
                                maxSize=(PLUGIN_WIDTH, totalHeight+10))
        self.w.accordionView = AccordionView((0, 0, -0, -0), accordionItems)

        # add observers
        addObserver(self, "_draw", "draw")
        addObserver(self, "_draw", "drawInactive")
        addObserver(self, "_drawPreview", "drawPreview")
        addObserver(self, "_mouseDown", "mouseDown")
        addObserver(self, "_drawBackground", "drawBackground")
        addObserver(self, '_updateGlyphData', 'viewDidChangeGlyph')
        addObserver(self, "aFontIsOpening", "newFontDidOpen")
        addObserver(self, "aFontIsOpening", "fontDidOpen")
        addObserver(self, "aFontIsClosing", "fontWillClose")
        self.w.bind('close', self.windowCloseCallback)

        # open window
        self.w.open()

    # drawing callbacks
    def _mouseDown(self, infoDict):
        mouseDownPoint = infoDict['point']
        mouseDownClickCount = infoDict['clickCount']

        # double click
        if mouseDownClickCount == 2:
            if self.lftNeighborActive is True and self.lftGlyph:
                xMin, yMin, xMax, yMax = self.lftGlyph.box
                if xMin < (mouseDownPoint.x+self.lftGlyph.width) < xMax and yMin < mouseDownPoint.y < yMax:
                    OpenGlyphWindow(glyph=self.lftGlyph, newWindow=True)

            if self.rgtNeighborActive is True and self.rgtGlyph:
                xMin, yMin, xMax, yMax = self.rgtGlyph.box
                if xMin < (mouseDownPoint.x-self.currentGlyph.width) < xMax and yMin < mouseDownPoint.y < yMax:
                    OpenGlyphWindow(glyph=self.rgtGlyph, newWindow=True)


    def _draw(self, infoDict):
        currentGlyph = infoDict['glyph']
        scalingFactor = infoDict['scale']

        try:
            if self.lftGlyph and self.lftNeighborActive is True:
                self._drawGlyphOutline(self.lftGlyph, scalingFactor, offset_X=-self.lftGlyph.width)
            if self.rgtGlyph and self.rgtNeighborActive is True:
                self._drawGlyphOutline(self.rgtGlyph, scalingFactor, offset_X=currentGlyph.width)

            if self.sqrActive is True and 2 > scalingFactor:
                self._drawSquarings(currentGlyph, scalingFactor)
                if self.lftGlyph and self.lftNeighborActive is True:
                    self._drawSquarings(self.lftGlyph, scalingFactor, offset_X=-self.lftGlyph.width)
                if self.rgtGlyph and self.rgtNeighborActive is True:
                    self._drawSquarings(self.rgtGlyph, scalingFactor, offset_X=currentGlyph.width)

            if self.bcpLengthActive is True and 2 > scalingFactor:
                self._drawBcpLenght(currentGlyph, scalingFactor, 2)
                if self.lftGlyph and self.lftNeighborActive is True:
                    self._drawBcpLenght(self.lftGlyph, scalingFactor, offset_X=-self.lftGlyph.width)
                if self.rgtGlyph and self.rgtNeighborActive is True:
                    self._drawBcpLenght(self.rgtGlyph, scalingFactor, offset_X=currentGlyph.width)

        except Exception as error:
            print error
            print sys.exc_info()

    def _drawPreview(self, infoDict):
        currentGlyph = infoDict['glyph']
        scalingFactor = infoDict['scale']

        try:
            if self.lftGlyph and self.lftNeighborActive is True:
                self._drawGlyphBlack(self.lftGlyph, scalingFactor, offset_X=-self.lftGlyph.width)
            if self.rgtGlyph and self.rgtNeighborActive is True:
                self._drawGlyphBlack(self.rgtGlyph, scalingFactor, offset_X=currentGlyph.width)
        except Exception as error:
            print error
            print sys.exc_info()

    def _drawBackground(self, infoDict):
        currentGlyph = infoDict['glyph']
        scalingFactor = infoDict['scale']

        try:
            if self.gridActive is True and 2 > scalingFactor:
                offsetFromOrigin = infoDict['view'].offset()
                visibleRect = infoDict['view'].visibleRect()
                frameOrigin = int(visibleRect.origin.x-offsetFromOrigin[0]), int(visibleRect.origin.y-offsetFromOrigin[1])
                frameSize = int(visibleRect.size.width), int(visibleRect.size.height)
                self._drawGrids(frameOrigin, frameSize, currentGlyph.getParent().info.italicAngle, scalingFactor)

            if self.stemActive is True and 1 > scalingFactor:
                self._drawStems(currentGlyph, scalingFactor)
                if self.lftGlyph and self.lftNeighborActive is True:
                    self._drawStems(self.lftGlyph, scalingFactor, offset_X=-self.lftGlyph.width)
                if self.rgtGlyph and self.rgtNeighborActive is True:
                    self._drawStems(self.rgtGlyph, scalingFactor, offset_X=currentGlyph.width)

            if self.diagonalActive is True and 1 > scalingFactor:
                self._drawDiagonals(currentGlyph, scalingFactor)
                if self.lftGlyph and self.lftNeighborActive is True:
                    self._drawDiagonals(self.lftGlyph, scalingFactor, offset_X=-self.lftGlyph.width)
                if self.rgtGlyph and self.rgtNeighborActive is True:
                    self._drawDiagonals(self.rgtGlyph, scalingFactor, offset_X=currentGlyph.width)

            if self.cntNeighborActive is True:
                self._drawCentralBackgroundGlyph(self.cntGlyph)

            if self.offgridActive is True:
                print self.offgridActive
                self._drawOffgridPoints(currentGlyph, scalingFactor)

        except Exception as error:
            print error
            print sys.exc_info()

    def _drawOffgridPoints(self, glyph, scalingFactor):
        save()
        fill(*RED_COLOR)
        stroke(None)

        scaledRadius = OFFGRID_RADIUS*scalingFactor
        for eachContour in glyph:
            for eachPt in eachContour.bPoints:
                if eachPt.anchor[0] % 4 != 0 or eachPt.anchor[1] % 4 != 0:
                    oval(eachPt.anchor[0]-scaledRadius/2., eachPt.anchor[1]-scaledRadius/2., scaledRadius, scaledRadius)

                if eachPt.bcpIn != (0,0):
                    bcpInAbs = eachPt.anchor[0]+eachPt.bcpIn[0], eachPt.anchor[1]+eachPt.bcpIn[1]
                    if bcpInAbs[0] % 4 != 0 or bcpInAbs[1] % 4 != 0:
                        oval(bcpInAbs[0]-scaledRadius/2., bcpInAbs[1]-scaledRadius/2., scaledRadius, scaledRadius)

                if eachPt.bcpOut != (0,0):
                    bcpOutAbs = eachPt.anchor[0]+eachPt.bcpOut[0], eachPt.anchor[1]+eachPt.bcpOut[1]
                    if bcpOutAbs[0] % 4 != 0 or bcpOutAbs[1] % 4 != 0:
                        oval(bcpOutAbs[0]-scaledRadius/2., bcpOutAbs[1]-scaledRadius/2., scaledRadius, scaledRadius)
        restore()

    def _drawCentralBackgroundGlyph(self, glyph):
        save()
        fill(*LIGHT_GRAY_COLOR)
        drawGlyph(glyph)
        restore()

    def _drawGrids(self, frameOrigin, frameSize, italicAngle, scalingFactor):
        for eachGridDescription in reversed(self.gridsDB):
            gridColor = eachGridDescription['color']
            isHorizontal = eachGridDescription['horizontal']
            isVertical = eachGridDescription['vertical']
            gridStep = eachGridDescription['step']

            if isHorizontal is False and isVertical is False:
                continue
            if not gridStep:
                continue

            save()
            skew(-italicAngle, 0)
            stroke(*gridColor)
            strokeWidth(1*scalingFactor)
            fill(None)

            if isVertical is True:
                # to the right (from 0)
                extraSlant = int(ceil(tan(radians(italicAngle))*frameOrigin[1]))
                for eachX in range(0, frameOrigin[0]+frameSize[0]+extraSlant, gridStep):
                    line((eachX, frameOrigin[1]-GRID_TOLERANCE), (eachX, frameOrigin[1]+frameSize[1]+GRID_TOLERANCE))

                # to the left (from 0)
                extraSlant = int(ceil(tan(radians(italicAngle))*(frameSize[1]+frameOrigin[1])))
                for eachX in [i for i in range(frameOrigin[0]+extraSlant, 0) if i % gridStep == 0]:
                    line((eachX, frameOrigin[1]-GRID_TOLERANCE), (eachX, frameOrigin[1]+frameSize[1]+GRID_TOLERANCE))

            if isHorizontal is True:
                # to the top (from baseline)
                for eachY in range(0, frameOrigin[1]+frameSize[1], gridStep):
                    line((frameOrigin[0]-GRID_TOLERANCE, eachY), (frameOrigin[0]+frameSize[0]+GRID_TOLERANCE, eachY))

                # to the bottom (from baseline)
                for eachY in [i for i in range(frameOrigin[1], 0) if i % gridStep == 0]:
                    line((frameOrigin[0]-GRID_TOLERANCE, eachY), (frameOrigin[0]+frameSize[0]+GRID_TOLERANCE, eachY))

            restore()

    def _drawBcpLenght(self, glyph, scalingFactor, offset_X=0):
        for eachContour in glyph:
            for indexBcp, eachBcp in enumerate(eachContour.bPoints):
                if eachBcp.bcpOut != (0, 0):
                    absBcpOut = eachBcp.anchor[0] + eachBcp.bcpOut[0], eachBcp.anchor[1] + eachBcp.bcpOut[1]
                    bcpOutAngle = calcAngle(eachBcp.anchor, absBcpOut)
                    bcpOutLenght = calcDistance(eachBcp.anchor, absBcpOut)
                    captionBcpOut = u'→%d' % bcpOutLenght
                    projOut_X = eachBcp.anchor[0]+cos(radians(bcpOutAngle))*bcpOutLenght/2.
                    projOut_Y = eachBcp.anchor[1]+sin(radians(bcpOutAngle))*bcpOutLenght/2.

                    textQualities(BODYSIZE_CAPTION*scalingFactor)
                    textWidth, textHeight = textSize(captionBcpOut)

                    save()
                    translate(projOut_X+offset_X, projOut_Y)
                    rotate(bcpOutAngle % 90)
                    belowRect = (-textWidth/2.-1, -textHeight/2.-1, textWidth+2, textHeight+2, 1)
                    fill(0, 0, 0, .7)
                    roundedRect(*belowRect)

                    textRect = (-textWidth/2., -textHeight/2., textWidth, textHeight)
                    textQualities(BODYSIZE_CAPTION*scalingFactor, weight='bold', color=WHITE_COLOR)
                    textBox(captionBcpOut, textRect, align='center')
                    restore()

                if eachBcp.bcpIn != (0, 0):
                    absBcpIn = eachBcp.anchor[0] + eachBcp.bcpIn[0], eachBcp.anchor[1] + eachBcp.bcpIn[1]
                    bcpInAngle = calcAngle(eachBcp.anchor, absBcpIn)
                    bcpInLenght = calcDistance(eachBcp.anchor, absBcpIn)
                    captionBcpIn = u'→%d' % bcpInLenght

                    projIn_X = eachBcp.anchor[0]+cos(radians(bcpInAngle))*bcpInLenght/2.
                    projIn_Y = eachBcp.anchor[1]+sin(radians(bcpInAngle))*bcpInLenght/2.

                    textQualities(BODYSIZE_CAPTION*scalingFactor)
                    textWidth, textHeight = textSize(captionBcpIn)

                    save()
                    translate(projIn_X+offset_X, projIn_Y)
                    rotate(bcpInAngle % 90)

                    belowRect = (-textWidth/2.-1, -textHeight/2.-1, textWidth+2, textHeight+2, 1)
                    fill(0, 0, 0, .7)
                    roundedRect(*belowRect)

                    textQualities(BODYSIZE_CAPTION*scalingFactor, weight='bold', color=WHITE_COLOR)
                    textRect = (-textWidth/2., -textHeight/2., textWidth, textHeight)
                    textBox(captionBcpIn, textRect, align='center')
                    restore()

    def _drawSquarings(self, glyph, scalingFactor, offset_X=0):
        for eachContour in glyph:
            for indexBcp, eachBcp in enumerate(eachContour.bPoints):

                if eachBcp.bcpOut != (0, 0):
                    nextBcp = eachContour.bPoints[(indexBcp+1) % len(eachContour.bPoints)]

                    absBcpOut = (eachBcp.anchor[0]+eachBcp.bcpOut[0], eachBcp.anchor[1]+eachBcp.bcpOut[1])
                    angleOut = calcAngle(eachBcp.anchor, absBcpOut)
                    handleOutLen = calcDistance(eachBcp.anchor, absBcpOut)

                    absBcpIn = (nextBcp.anchor[0]+nextBcp.bcpIn[0], nextBcp.anchor[1]+nextBcp.bcpIn[1])
                    angleIn = calcAngle(nextBcp.anchor, absBcpIn)
                    nextHandleInLen = calcDistance(nextBcp.anchor, absBcpIn)

                    handlesIntersection = intersectionBetweenSegments(eachBcp.anchor,
                                                                      absBcpOut,
                                                                      absBcpIn,
                                                                      nextBcp.anchor)

                    maxOutLen = calcDistance(eachBcp.anchor, handlesIntersection)
                    maxInLen = calcDistance(nextBcp.anchor, handlesIntersection)

                    sqrOut = handleOutLen/maxOutLen
                    sqrIn = nextHandleInLen/maxInLen

                    projOut_X = eachBcp.anchor[0]+cos(radians(angleOut))*handleOutLen
                    projOut_Y = eachBcp.anchor[1]+sin(radians(angleOut))*handleOutLen
                    if angleOut != 0 and angleOut % 90 != 0:
                        captionSqrOut = u'%.2f%%, %d°' % (sqrOut, angleOut%180)
                    else:
                        captionSqrOut = '%.2f%%' % sqrOut
                    captionSqrOut = captionSqrOut.replace('0.', '')

                    save()
                    translate(projOut_X+offset_X, projOut_Y)
                    textQualities(BODYSIZE_CAPTION*scalingFactor)
                    textWidth, textHeight = textSize(captionSqrOut)
                    if angleOut == 90:          # text above
                        textRect = (-textWidth/2., SQR_CAPTION_OFFSET*scalingFactor, textWidth, textHeight)
                    elif angleOut == -90:       # text below
                        textRect = (-textWidth/2., -textHeight-SQR_CAPTION_OFFSET*scalingFactor, textWidth, textHeight)
                    elif -90 < angleOut < 90:   # text on the right
                        textRect = (SQR_CAPTION_OFFSET*scalingFactor, -textHeight/2., textWidth, textHeight)
                    else:                       # text on the left
                        textRect = (-textWidth-SQR_CAPTION_OFFSET*scalingFactor, -textHeight/2., textWidth, textHeight)
                    textBox(captionSqrOut, textRect, align='center')
                    restore()

                    projIn_X = nextBcp.anchor[0]+cos(radians(angleIn))*nextHandleInLen
                    projIn_Y = nextBcp.anchor[1]+sin(radians(angleIn))*nextHandleInLen
                    if angleIn != 0 and angleIn % 90 != 0:
                        captionSqrIn = u'%.2f%%, %d°' % (sqrIn, angleIn%180)
                    else:
                        captionSqrIn = '%.2f%%' % sqrIn
                    captionSqrIn = captionSqrIn.replace('0.', '')

                    save()
                    translate(projIn_X+offset_X, projIn_Y)
                    textQualities(BODYSIZE_CAPTION*scalingFactor)
                    textWidth, textHeight = textSize(captionSqrIn)
                    if angleIn == 90:          # text above
                        textRect = (-textWidth/2., SQR_CAPTION_OFFSET*scalingFactor, textWidth, textHeight)
                    elif angleIn == -90:       # text below
                        textRect = (-textWidth/2., -textHeight-SQR_CAPTION_OFFSET*scalingFactor, textWidth, textHeight)
                    elif -90 < angleIn < 90:   # text on the right
                        textRect = (SQR_CAPTION_OFFSET*scalingFactor, -textHeight/2., textWidth, textHeight)
                    else:                      # text on the left
                        textRect = (-textWidth-SQR_CAPTION_OFFSET*scalingFactor, -textHeight/2., textWidth, textHeight)
                    textBox(captionSqrIn, textRect, align='center')
                    restore()

    def _drawGlyphOutline(self, glyph, scalingFactor, offset_X=0):
        save()
        translate(offset_X, 0)

        fill(None)
        strokeWidth(1*scalingFactor)
        stroke(*LIGHT_GRAY_COLOR)
        drawGlyph(glyph)

        scaledRadius = BCP_RADIUS*scalingFactor

        for eachContour in glyph:
            for eachPt in eachContour.bPoints:
                stroke(None)
                fill(*LIGHT_GRAY_COLOR)
                rect(eachPt.anchor[0]-scaledRadius/2., eachPt.anchor[1]-scaledRadius/2., scaledRadius, scaledRadius)

                if eachPt.bcpIn != (0, 0):
                    stroke(None)
                    fill(*LIGHT_GRAY_COLOR)
                    oval(eachPt.anchor[0]+eachPt.bcpIn[0]-scaledRadius/2.,
                         eachPt.anchor[1]+eachPt.bcpIn[1]-scaledRadius/2.,
                         scaledRadius,
                         scaledRadius)

                    stroke(*LIGHT_GRAY_COLOR)
                    fill(None)
                    line((eachPt.anchor[0], eachPt.anchor[1]),
                         (eachPt.anchor[0]+eachPt.bcpIn[0], eachPt.anchor[1]+eachPt.bcpIn[1]))

                if eachPt.bcpOut != (0, 0):
                    stroke(None)
                    fill(*LIGHT_GRAY_COLOR)
                    oval(eachPt.anchor[0]+eachPt.bcpOut[0]-scaledRadius/2.,
                         eachPt.anchor[1]+eachPt.bcpOut[1]-scaledRadius/2.,
                         scaledRadius,
                         scaledRadius)

                    stroke(*LIGHT_GRAY_COLOR)
                    fill(None)
                    line((eachPt.anchor[0], eachPt.anchor[1]),
                         (eachPt.anchor[0]+eachPt.bcpOut[0], eachPt.anchor[1]+eachPt.bcpOut[1]))

        restore()

    def _drawGlyphBlack(self, glyph, scalingFactor, offset_X=0):
        save()
        translate(offset_X, 0)

        fill(*BLACK_COLOR)
        stroke(None)
        drawGlyph(glyph)

        restore()

    def _drawStems(self, currentGlyph, scalingFactor, offset_X=0):
        if STEM_KEY not in currentGlyph.lib:
            return None

        stemData = calcStemsData(currentGlyph, STEM_KEY)
        for PTs, DIFFs, middlePoint in stemData:
            pt1, pt2 = PTs
            horDiff, verDiff = DIFFs

            save()
            translate(offset_X, 0)
            stroke(*self.stemColor)
            fill(None)
            strokeWidth(1*scalingFactor)

            newPath()
            if horDiff > verDiff:  # ver
                rightPt, leftPt = PTs
                if pt1.x > pt2.x:
                    rightPt, leftPt = leftPt, rightPt
                moveTo((leftPt.x, leftPt.y))
                curveTo((leftPt.x-horDiff/2, leftPt.y), (rightPt.x+horDiff/2, rightPt.y), (rightPt.x, rightPt.y))

            else:                  # hor
                topPt, btmPt = PTs
                if pt2.y > pt1.y:
                    btmPt, topPt = topPt, btmPt
                moveTo((btmPt.x, btmPt.y))
                curveTo((btmPt.x, btmPt.y+verDiff/2), (topPt.x, topPt.y-verDiff/2), (topPt.x, topPt.y))
            drawPath()
            restore()

            save()
            translate(offset_X, 0)
            textQualities(BODYSIZE_CAPTION*scalingFactor)
            dataToPlot = u'↑%d\n→%d' % (verDiff, horDiff)
            textWidth, textHeight = textSize(dataToPlot)
            textRect = (middlePoint[0]-textWidth/2., middlePoint[1]-textHeight/2., textWidth, textHeight)
            textBox(dataToPlot, textRect, align='center')
            restore()

    def _drawDiagonals(self, currentGlyph, scalingFactor, offset_X=0):
        if DIAGONALS_KEY not in currentGlyph.lib:
            return None

        diagonalsData = calcDiagonalsData(currentGlyph, DIAGONALS_KEY)
        for ptsToDisplay, angle, distance in diagonalsData:
            pt1, pt2 = ptsToDisplay

            save()
            stroke(*self.diagonalColor)
            fill(None)
            strokeWidth(1*scalingFactor)

            if 90 < angle <= 180 or -180 < angle < -90:
                direction = -1
                adjustedAngle = angle+180+90
            else:
                direction = 1
                adjustedAngle = angle+90

            diagonalPt1 = pt1[0]+cos(radians(adjustedAngle))*((DIAGONAL_OFFSET-1)*direction), pt1[1]+sin(radians(adjustedAngle))*((DIAGONAL_OFFSET-1)*direction)
            diagonalPt2 = pt2[0]+cos(radians(adjustedAngle))*((DIAGONAL_OFFSET-1)*direction), pt2[1]+sin(radians(adjustedAngle))*((DIAGONAL_OFFSET-1)*direction)
            offsetPt1 = pt1[0]+cos(radians(adjustedAngle))*DIAGONAL_OFFSET*direction, pt1[1]+sin(radians(adjustedAngle))*DIAGONAL_OFFSET*direction
            offsetPt2 = pt2[0]+cos(radians(adjustedAngle))*DIAGONAL_OFFSET*direction, pt2[1]+sin(radians(adjustedAngle))*DIAGONAL_OFFSET*direction

            line((pt1), (offsetPt1))
            line((pt2), (offsetPt2))
            line((diagonalPt1), (diagonalPt2))
            restore()

            save()
            textQualities(BODYSIZE_CAPTION*scalingFactor)
            offsetMidPoint = calcMidPoint(offsetPt1, offsetPt2)
            translate(offsetMidPoint[0], offsetMidPoint[1])

            if 90 < angle <= 180 or -180 < angle < -90:
                rotate(angle+180)
                textBoxY = -BODYSIZE_CAPTION*1.2*scalingFactor
            else:
                rotate(angle)
                textBoxY = 0

            dataToPlot = u'∡%.1f ↗%d' % (angle%180, distance)
            textWidth, textHeight = textSize(dataToPlot)
            textBox(dataToPlot, (-textWidth/2., textBoxY, textWidth, BODYSIZE_CAPTION*1.2*scalingFactor), align='center')
            restore()

    # ui callback
    def collectOpenedFonts(self):
        self.openedFonts = [f.path for f in AllFonts() if f.path is not None]
        self.openedFonts.sort()

    def aFontIsClosing(self, infoDict):
        willCloseFont = infoDict['font']
        self.openedFonts.remove(willCloseFont.path)

        for eachFontAttrName, eachGlyphAttrName in [('lftFont', 'lftGlyph'), ('cntFont', 'cntGlyph'), ('rgtFont', 'rgtGlyph')]:
            if getattr(self, eachFontAttrName) is willCloseFont:
                anotherFont = getOpenedFontFromPath(AllFonts(), self.openedFonts[0])
                setattr(self, eachFontAttrName, anotherFont)
                self.pushFontAttr(eachFontAttrName)

                activeName = getattr(self, eachGlyphAttrName).name
                if anotherFont.has_key(activeName):
                    setattr(self, eachGlyphAttrName, anotherFont[activeName])
                else:
                    setattr(self, eachGlyphAttrName, anotherFont[anotherFont.glyphOrder[0]])
                self.pushGlyphAttr(eachGlyphAttrName)

        self.neighborsController.setFontData(self.openedFonts)

    def pushFontAttr(self, attrName):
        fontToBePushed = getattr(self, attrName)
        self.neighborsController.neighborsDB[attrName][1] = fontToBePushed
        setattr(self.neighborsController, '%sController.activeFont' % attrName[:3], fontToBePushed)
        getattr(self.neighborsController, '%sController' % attrName[:3]).updateGlyphList()

    def pushGlyphAttr(self, attrName):
        glyphToBePushed = getattr(self, attrName)
        self.neighborsController.neighborsDB[attrName][2] = glyphToBePushed
        setattr(self.neighborsController, '%sController.activeGlyph' % attrName[:3], glyphToBePushed)
        getattr(self.neighborsController, '%sController' % attrName[:3]).updateGlyphList()

    def aFontIsOpening(self, infoDict):
        originalState = list(self.openedFonts)
        self.openedFonts.append(infoDict['font'].path)
        self.openedFonts.sort()
        if originalState == []:
            self._initFontsAndGlyphs()
            for eachFontAttrName, eachGlyphAttrName in [('lftFont', 'lftGlyph'), ('cntFont', 'cntGlyph'), ('rgtFont', 'rgtGlyph')]:
                self.pushFontAttr(eachFontAttrName)
                self.pushGlyphAttr(eachGlyphAttrName)

        self.neighborsController.setFontData(self.openedFonts)

    def _initFontsAndGlyphs(self):
        firstAvailableFont = getOpenedFontFromPath(AllFonts(), self.openedFonts[0])
        firstAvailableGlyph = firstAvailableFont[firstAvailableFont.glyphOrder[0]]
        for eachFontAttrName, eachGlyphAttrName in [('lftFont', 'lftGlyph'), ('cntFont', 'cntGlyph'), ('rgtFont', 'rgtGlyph')]:
            setattr(self, eachFontAttrName, firstAvailableFont)
            setattr(self, eachGlyphAttrName, firstAvailableGlyph)

    def _updateGlyphData(self, infoDict):
        if infoDict['glyph']:
            self.currentGlyph = infoDict['glyph']
            self.distancesController.setCurrentGlyph(self.currentGlyph)

    # controls callbacks
    def windowCloseCallback(self, sender):
        removeObserver(self, 'draw')
        removeObserver(self, 'drawInactive')
        removeObserver(self, 'drawBackground')
        removeObserver(self, "drawPreview")
        removeObserver(self, "mouseDown")
        removeObserver(self, 'viewDidChangeGlyph')
        removeObserver(self, 'newFontDidOpen')
        removeObserver(self, 'fontWillClose')
        removeObserver(self, 'fontDidOpen')

    def bcpControllerCallback(self, sender):
        self.sqrActive = sender.getSqr()
        self.bcpLengthActive = sender.getBcpLength()
        UpdateCurrentGlyphView()

    def gridControllerCallback(self, sender):
        self.gridActive, self.gridsDB, self.offgridActive = sender.get()
        UpdateCurrentGlyphView()

    def distancesControllerCallback(self, sender):
        self.stemActive, self.stemColor, self.diagonalActive, self.diagonalColor = sender.get()
        UpdateCurrentGlyphView()

    def neighborsControllerCallback(self, sender):
        neighborsDB = sender.get()
        self.lftNeighborActive = neighborsDB['lft'][0]
        self.lftFont = neighborsDB['lft'][1]
        self.lftGlyph = neighborsDB['lft'][2]
        self.cntNeighborActive = neighborsDB['cnt'][0]
        self.cntFont = neighborsDB['cnt'][1]
        self.cntGlyph = neighborsDB['cnt'][2]
        self.rgtNeighborActive = neighborsDB['rgt'][0]
        self.rgtFont = neighborsDB['rgt'][1]
        self.rgtGlyph = neighborsDB['rgt'][2]
        UpdateCurrentGlyphView()


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


da = DrawingAssistant()