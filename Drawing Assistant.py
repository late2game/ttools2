#!/usr/bin/env python
# -*- coding: utf-8 -*-

#####################
# Drawing Assistant #
#####################

### Modules
# custom
import userInterfaceValues
reload(userInterfaceValues)
import calcFunctions
reload(calcFunctions)
from calcFunctions import intersectionBetweenSegments, calcAngle, calcDistance, interpolateValue, isBlackInBetween
from userInterfaceValues import vanillaControlsSize

# standard
import sys
from math import cos, sin, radians
from lib.eventTools.eventManager import getActiveEventTool
from mojo.UI import UpdateCurrentGlyphView, AccordionView
from vanilla import FloatingWindow, CheckBox, HorizontalLine, PopUpButton, Group
from vanilla import TextBox, EditText, ColorWell, SquareButton
from mojo.drawingTools import *
from defconAppKit.windows.baseWindow import BaseWindowController
from AppKit import NSFont, NSColor, NSFontAttributeName
from AppKit import NSForegroundColorAttributeName
from mojo.events import addObserver, removeObserver

### Constants
PLUGIN_KEY = 'TTdrawingAssistant'
GRID_TOLERANCE = 2

# ui
BODYSIZE_CAPTION = 10

BLACK_COLOR = NSColor.blackColor()

STEM_COLOR = (1, 127/255., 102/255., 1)
DIAGONAL_COLOR = (102/255., 124/255., 1, 1)

GRID_COLOR_ONE = (0.88, 1, 0.4, 1)
GRID_COLOR_TWO = (0.4, 1, 0.64, 1)
GRID_COLOR_THREE = (0.4, 0.64, 1, 1)
GRID_COLOR_FOUR = (0.88, 0.4, 1, 1)
GRID_COLOR_FIVE = (1, 0.4, 0.4, 1)
GRID_COLOR_INIT = [GRID_COLOR_ONE, GRID_COLOR_TWO, GRID_COLOR_THREE, GRID_COLOR_FOUR, GRID_COLOR_FIVE]

PLUGIN_WIDTH = 220

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


class MultipleGridController(Group):

    def __init__(self, posSize, gridActive, ctrlsAmount, activeCtrls, callback):
        Group.__init__(self, posSize)
        assert activeCtrls <= ctrlsAmount

        self.ctrlHeight = posSize[3]
        self.gridActive = gridActive
        self.ctrlsAmount = ctrlsAmount
        self.activeCtrls = activeCtrls
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

    def get(self):
        return self.gridActive, self.gridsDB

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

        self.stepCtrl = EditText((jumpin_X, 0, 24, vanillaControlsSize['EditTextRegularHeight']),
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

    def __init__(self, posSize, stemActive, diagonalActive, callback):
        Group.__init__(self, posSize)
        self.callback = callback
        self.ctrlWidth, self.ctrlHeight = posSize[2], posSize[3]
        self.stemActive = stemActive
        self.diagonalActive = diagonalActive

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
        self.distancesCheck = CheckBox((0, jumpin_Y, self.ctrlWidth*.6, vanillaControlsSize['CheckBoxRegularHeight']),
                                       "Show diagonals",
                                       value=self.diagonalActive,
                                       callback=self.distancesCheckCallback)

        self.distancesColorWell = ColorWell((-MARGIN_HOR-46, jumpin_Y, 46, vanillaControlsSize['CheckBoxRegularHeight']),
                                            color=NSColor.colorWithCalibratedRed_green_blue_alpha_(*self.diagonalColor),
                                            callback=self.distancesColorWellCallback)

        jumpin_Y += vanillaControlsSize['CheckBoxRegularHeight'] + MARGIN_VER
        self.addStemButton = SquareButton((0, jumpin_Y, self.ctrlWidth*.45, vanillaControlsSize['ButtonRegularHeight']*2),
                                          "Add\nStem",
                                          callback=self.addStemButtonCallback)

        self.addDistanceButton = SquareButton((-self.ctrlWidth*.45-MARGIN_HOR, jumpin_Y, self.ctrlWidth*.45, vanillaControlsSize['ButtonRegularHeight']*2),
                                              "Add\nDiagonal",
                                              callback=self.addDistanceButtonCallback)

        jumpin_Y += vanillaControlsSize['ButtonRegularHeight']*2+MARGIN_VER
        self.deleteButton = SquareButton((0, jumpin_Y, -MARGIN_HOR, vanillaControlsSize['ButtonRegularHeight']*1.5),
                                         "Delete",
                                         callback=self.deleteButtonCallback)


    def stemsCheckCallback(self, sender):
        print sender.get()
        self.callback(self)

    def stemsColorWellCallback(self, sender):
        calibratedColor = sender.get()
        self.stemColor = (calibratedColor.redComponent(),
                          calibratedColor.greenComponent(),
                          calibratedColor.blueComponent(),
                          calibratedColor.alphaComponent())
        self.callback(self)

    def distancesCheckCallback(self, sender):
        calibratedColor = sender.get()
        self.diagonalColor = (calibratedColor.redComponent(),
                              calibratedColor.greenComponent(),
                              calibratedColor.blueComponent(),
                              calibratedColor.alphaComponent())
        self.callback(self)

    def distancesColorWellCallback(self, sender):
        print sender.get()
        self.callback(self)

    def addStemButtonCallback(self, sender):
        print 'addStemButtonCallback button!'
        self.callback(self)

    def addDistanceButtonCallback(self, sender):
        print 'addStemButtonCallback button!'
        self.callback(self)

    def deleteButtonCallback(self, sender):
        print 'addStemButtonCallback button!'
        self.callback(self)



class DrawingAssistant(BaseWindowController):
    """the aim of this plugin is to provide useful visualizations on glyph canvas"""

    # modes
    sqrActive = False
    bcpLengthActive = False
    gridActive = False
    stemActive = False
    diagonalActive = False

    gridsDB = []

    def __init__(self):

        # init views
        self.bcpController = BcpController((MARGIN_HOR, 0, NET_WIDTH, vanillaControlsSize['CheckBoxRegularHeight']*2.5),
                                           sqrActive=self.sqrActive,
                                           bcpLengthActive=self.bcpLengthActive,
                                           callback=self.bcpController)

        self.gridController = MultipleGridController((MARGIN_HOR, 0, NET_WIDTH, 190),
                                                     gridActive=self.gridActive,
                                                     ctrlsAmount=5,
                                                     activeCtrls=0,
                                                     callback=self.gridControllerCallback)

        self.distancesController = DistancesController((MARGIN_HOR, 0, NET_WIDTH, 148),
                                                       stemActive=self.stemActive,
                                                       diagonalActive=self.diagonalActive,
                                                       callback=self.distancesControllerCallback)

        # collect views
        accordionItems = [
                {'label': 'bcp controller',       'view': self.bcpController,       'size': self.bcpController.ctrlHeight,       'collapsed': False, 'canResize': False},
                {'label': 'grid controller',      'view': self.gridController,      'size': self.gridController.ctrlHeight,      'collapsed': False, 'canResize': False},
                {'label': 'distances controller', 'view': self.distancesController, 'size': self.distancesController.ctrlHeight, 'collapsed': False, 'canResize': False},
            ]

        # init window with accordion obj
        self.w = FloatingWindow((0, 0, PLUGIN_WIDTH, 600), PLUGIN_KEY)
        self.w.accordionView = AccordionView((0, 0, -0, -0), accordionItems)

        # add observers
        addObserver(self, "_draw", "draw")
        addObserver(self, "_draw", "drawInactive")
        addObserver(self, "_drawBackground", "drawBackground")
        self.w.bind('close', self.windowCloseCallback)

        # open window
        self.w.open()

    # drawing methods
    def _draw(self, infoDict):
        currentGlyph = infoDict['glyph']
        scalingFactor = infoDict['scale']

        currentTool = getActiveEventTool()
        view = currentTool.getNSView()
        textAttributes = {NSFontAttributeName: NSFont.systemFontOfSize_(BODYSIZE_CAPTION),
                          NSForegroundColorAttributeName: BLACK_COLOR}

        try:

            if self.sqrActive is True and 1.5 > scalingFactor > .2:
                self._drawSquarings(currentGlyph, view, textAttributes, scalingFactor, 2)

            if self.bcpLengthActive is True and 1.5 > scalingFactor > .2:
                self._drawBcpLenght(currentGlyph, view, textAttributes, scalingFactor, 2)

        except Exception as error:
            print error
            print sys.exc_info()


    def _drawBackground(self, infoDict):
        currentGlyph = infoDict['glyph']
        scalingFactor = infoDict['scale']

        try:
            if self.gridActive is True and 1.5 > scalingFactor:
                offsetFromOrigin = infoDict['view'].offset()
                visibleRect = infoDict['view'].visibleRect()
                frameOrigin = int(visibleRect.origin.x-offsetFromOrigin[0]), int(visibleRect.origin.y-offsetFromOrigin[1])
                frameSize = int(visibleRect.size.width), int(visibleRect.size.height)
                self._drawGrids(currentGlyph, frameOrigin, frameSize, scalingFactor)

        except Exception as error:
            print error
            print sys.exc_info()


    def _drawGrids(self, currentGlyph, frameOrigin, frameSize, scalingFactor):
        for eachGridDescription in self.gridsDB:
            gridColor = eachGridDescription['color']
            isHorizontal = eachGridDescription['horizontal']
            isVertical = eachGridDescription['vertical']
            gridStep = eachGridDescription['step']

            if isHorizontal is False and isVertical is False:
                continue
            if not gridStep:
                continue

            stroke(*gridColor)
            strokeWidth(1*scalingFactor)
            fill(None)

            if isVertical is True:
                # to the right (from 0)
                for eachX in range(0, frameOrigin[0]+frameSize[0], gridStep):
                    line((eachX, frameOrigin[1]-GRID_TOLERANCE), (eachX, frameOrigin[1]+frameSize[1]+GRID_TOLERANCE))

                # to the left (from 0)
                for eachX in [i for i in range(frameOrigin[0], 0) if i % gridStep == 0]:
                    line((eachX, frameOrigin[1]-GRID_TOLERANCE), (eachX, frameOrigin[1]+frameSize[1]+GRID_TOLERANCE))

            if isHorizontal is True:
                # to the top (from baseline)
                for eachY in range(0, frameOrigin[1]+frameSize[1], gridStep):
                    line((frameOrigin[0]-GRID_TOLERANCE, eachY), (frameOrigin[0]+frameSize[0]+GRID_TOLERANCE, eachY))

                # to the bottom (from baseline)
                for eachY in [i for i in range(frameOrigin[1], 0) if i % gridStep == 0]:
                    line((frameOrigin[0]-GRID_TOLERANCE, eachY), (frameOrigin[0]+frameSize[0]+GRID_TOLERANCE, eachY))



    def _drawBcpLenght(self, glyph, view, textAttributes, scalingFactor, offset):
        for eachContour in glyph:
            for indexBcp, eachBcp in enumerate(eachContour.bPoints):
                prevBcp = eachContour.bPoints[indexBcp-1]
                postBcp = eachContour.bPoints[(indexBcp+1)%(len(eachContour.bPoints)-1)]

                relativePosIn_X = 0
                relativePosIn_Y = 0
                relativePosOut_X = 0
                relativePosOut_Y = 0
                if eachBcp.anchor[0]-postBcp.anchor[0] != 0:
                    relativePosOut_X = (eachBcp.anchor[0]-postBcp.anchor[0])/abs(eachBcp.anchor[0]-postBcp.anchor[0])
                if eachBcp.anchor[0]-prevBcp.anchor[0] != 0:
                    relativePosIn_X = (eachBcp.anchor[0]-prevBcp.anchor[0])/abs(eachBcp.anchor[0]-prevBcp.anchor[0])
                if eachBcp.anchor[1]-postBcp.anchor[1] != 0:
                    relativePosOut_Y = (eachBcp.anchor[1]-postBcp.anchor[1])/abs(eachBcp.anchor[1]-postBcp.anchor[1])
                if eachBcp.anchor[1]-prevBcp.anchor[1] != 0:
                    relativePosIn_Y = (eachBcp.anchor[1]-prevBcp.anchor[1])/abs(eachBcp.anchor[1]-prevBcp.anchor[1])

                if eachBcp.bcpOut != (0, 0):
                    absBcpOut = eachBcp.anchor[0] + eachBcp.bcpOut[0], eachBcp.anchor[1] + eachBcp.bcpOut[1]
                    bcpOutAngle = calcAngle(eachBcp.anchor, absBcpOut)
                    bcpOutLenght = calcDistance(eachBcp.anchor, absBcpOut)
                    captionBcpOut = u'→%d' % bcpOutLenght
                    projOut_X = eachBcp.anchor[0]+cos(radians(bcpOutAngle))*bcpOutLenght/2.
                    projOut_Y = eachBcp.anchor[1]+sin(radians(bcpOutAngle))*bcpOutLenght/2.

                    if 0 <= bcpOutAngle < 45 or 135 <= bcpOutAngle <= 225 or 315 <= bcpOutAngle < 360:
                        xOffset = 0
                        yOffset = BODYSIZE_CAPTION*relativePosOut_Y
                    else:
                        xOffset = BODYSIZE_CAPTION*relativePosOut_X
                        yOffset = BODYSIZE_CAPTION
                    view._drawTextAtPoint(captionBcpOut, textAttributes, (projOut_X+xOffset, projOut_Y), yOffset=yOffset)

                if eachBcp.bcpIn != (0, 0):
                    absBcpIn = eachBcp.anchor[0] + eachBcp.bcpIn[0], eachBcp.anchor[1] + eachBcp.bcpIn[1]
                    bcpInAngle = calcAngle(eachBcp.anchor, absBcpIn)
                    bcpInLenght = calcDistance(eachBcp.anchor, absBcpIn)
                    captionBcpIn = u'→%d' % bcpInLenght
                    projIn_X = eachBcp.anchor[0]+cos(radians(bcpInAngle))*bcpInLenght/2.
                    projIn_Y = eachBcp.anchor[1]+sin(radians(bcpInAngle))*bcpInLenght/2.

                    if 0 <= bcpInAngle < 45 or 135 <= bcpInAngle <= 225 or 315 <= bcpInAngle < 360:
                        xOffset = 0
                        yOffset = BODYSIZE_CAPTION*relativePosIn_Y
                    else:
                        xOffset = BODYSIZE_CAPTION*relativePosIn_X
                        yOffset = BODYSIZE_CAPTION
                    view._drawTextAtPoint(captionBcpIn, textAttributes, (projIn_X+xOffset, projIn_Y), yOffset=yOffset)


    def _drawSquarings(self, glyph, view, textAttributes, scalingFactor, offset):
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

                    projOut_X = eachBcp.anchor[0]+cos(radians(angleOut))*maxOutLen*(sqrOut+.12*scalingFactor)
                    projOut_Y = eachBcp.anchor[1]+sin(radians(angleOut))*maxOutLen*(sqrOut+.12*scalingFactor)
                    if angleOut != 0 and angleOut % 90 != 0:
                        captionSqrOut = u'%.2f%%, %d°' % (sqrOut, angleOut%180)
                    else:
                        captionSqrOut = '%.2f%%' % sqrOut
                    captionSqrOut = captionSqrOut.replace('0.', '')
                    view._drawTextAtPoint(captionSqrOut, textAttributes, (projOut_X, projOut_Y), yOffset=0)

                    projIn_X = nextBcp.anchor[0]+cos(radians(angleIn))*maxInLen*(sqrIn+.12*scalingFactor)
                    projIn_Y = nextBcp.anchor[1]+sin(radians(angleIn))*maxInLen*(sqrIn+.12*scalingFactor)
                    if angleIn != 0 and angleIn % 90 != 0:
                        captionSqrIn = u'%.2f%%, %d°' % (sqrIn, angleIn%180)
                    else:
                        captionSqrIn = '%.2f%%' % sqrIn
                    captionSqrIn = captionSqrIn.replace('0.', '')
                    view._drawTextAtPoint(captionSqrIn, textAttributes, (projIn_X, projIn_Y), yOffset=0)


    # callbacks
    def windowCloseCallback(self, sender):
        removeObserver(self, "draw")
        removeObserver(self, "drawInactive")
        removeObserver(self, "drawBackground")


    def bcpController(self, sender):
        self.sqrActive = sender.getSqr()
        self.bcpLengthActive = sender.getBcpLength()
        UpdateCurrentGlyphView()
    
    def gridControllerCallback(self, sender):
        self.gridActive, self.gridsDB = sender.get()
        UpdateCurrentGlyphView()

    def distancesControllerCallback(self, sender):
        print sender
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