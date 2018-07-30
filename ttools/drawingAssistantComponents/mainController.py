#!/usr/bin/env python
# coding: utf-8

####################################
# Main DrawingAssistant Controller #
####################################

### Modules
# components
from __future__ import print_function
import importlib
import traceback
from math import cos, sin, radians, tan, ceil
from vanilla import FloatingWindow
from mojo.UI import AccordionView
import mojo.drawingTools as dt
from defconAppKit.windows.baseWindow import BaseWindowController
from mojo.roboFont import CurrentGlyph, CurrentFont, AllFonts, version
from mojo.events import addObserver, removeObserver
from mojo.UI import UpdateCurrentGlyphView, OpenGlyphWindow

# custom
import sharedValues
importlib.reload(sharedValues)
from sharedValues import MARGIN_HOR, NET_WIDTH, PLUGIN_WIDTH
from sharedValues import STEM_KEY, DIAGONALS_KEY
from sharedValues import CURRENT_FONT_REPR, CURRENT_GLYPH_REPR

import bcps
importlib.reload(bcps)
from bcps import BcpController

import grids
importlib.reload(grids)
from grids import MultipleGridController

import distances
importlib.reload(distances)
from distances import DistancesController

import neighbors
importlib.reload(neighbors)
from neighbors import NeighborsController

# custom
from ..ui import userInterfaceValues
importlib.reload(userInterfaceValues)
from ..ui.userInterfaceValues import vanillaControlsSize

from ..extraTools import miscFunctions
importlib.reload(miscFunctions)
from ..extraTools.miscFunctions import getOpenedFontFromPath

from ..extraTools import calcFunctions
importlib.reload(calcFunctions)
from ..extraTools.calcFunctions import intersectionBetweenSegments, calcAngle, calcDistance
from ..extraTools.calcFunctions import calcStemsData, calcDiagonalsData, calcMidPoint

### Constants
PLUGIN_TITLE = 'TT Drawing Assistant'

GRID_TOLERANCE = 2

# ui
BODYSIZE_CAPTION = 11
SQR_CAPTION_OFFSET = 4
BCP_RADIUS = 4
OFFGRID_RADIUS = 20

BLACK_COLOR = (0, 0, 0)
LIGHT_GRAY_COLOR = (.75, .75, .75)
RED_COLOR = (1,0,0)
WHITE_COLOR = (1, 1, 1)

DIAGONAL_OFFSET = 3

if '.SFNSText' in dt.installedFonts():
    SYSTEM_FONT_NAME = '.SFNSText'
    SYSTEM_FONT_NAME_BOLD = '.SFNSText-Bold'
else:
    SYSTEM_FONT_NAME = '.HelveticaNeueDeskInterface-Regular'
    SYSTEM_FONT_NAME_BOLD = '.HelveticaNeueDeskInterface-Bold'


### Functions & Procedures
def textQualities(scaledFontSize, weight='regular', color=BLACK_COLOR):
    dt.stroke(None)
    dt.fill(*color)
    if weight == 'bold':
        dt.font(SYSTEM_FONT_NAME_BOLD)
    else:
        dt.font(SYSTEM_FONT_NAME)
    dt.fontSize(scaledFontSize)

def chooseRightGlyph(aFontPath, aGlyphName):
    if aGlyphName == CURRENT_GLYPH_REPR:
        absGlyphName = CurrentGlyph().name
    else:
        absGlyphName = aGlyphName

    if aFontPath == CURRENT_FONT_REPR:
        absFontPath = CurrentFont().path
    else:
        absFontPath = aFontPath

    for eachFont in AllFonts():
        if eachFont.path == absFontPath:
            if absGlyphName in eachFont:
                return eachFont[absGlyphName]
    else:
        return None

### Ctrls
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
    lftFontPath = None
    lftGlyphName = None
    cntNeighborActive = False
    cntFontPath = None
    cntGlyphName = None
    rgtNeighborActive = False
    rgtFontPath = None
    rgtGlyphName = None

    gridsDB = []

    def __init__(self):
        super(DrawingAssistant, self).__init__()

        # collect currentGlyph (if available)
        self.currentGlyph = CurrentGlyph()

        # collect opened fonts
        if AllFonts():
            self.collectOpenedFontPaths()

        # init fonts
        if self.openedFontPaths:
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

        self.distancesController = DistancesController((MARGIN_HOR, 0, NET_WIDTH, 160),
                                                       stemActive=self.stemActive,
                                                       diagonalActive=self.diagonalActive,
                                                       currentGlyph=self.currentGlyph,
                                                       callback=self.distancesControllerCallback)

        self.neighborsController = NeighborsController((MARGIN_HOR, 0, NET_WIDTH, 94),
                                                       openedFontPaths=self.openedFontPaths,
                                                       lftNeighborActive=self.lftNeighborActive,
                                                       lftFontPath=self.lftFontPath,
                                                       lftGlyphName=self.lftGlyphName,
                                                       cntNeighborActive=self.cntNeighborActive,
                                                       cntFontPath=self.cntFontPath,
                                                       cntGlyphName=self.cntGlyphName,
                                                       rgtNeighborActive=self.rgtNeighborActive,
                                                       rgtFontPath=self.rgtFontPath,
                                                       rgtGlyphName=self.rgtGlyphName,
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
        addObserver(self, "_updateCurrentFont", "fontBecameCurrent")
        addObserver(self, '_updateCurrentGlyph', 'viewDidChangeGlyph')
        addObserver(self, "aFontIsOpening", "newFontDidOpen")
        addObserver(self, "aFontIsOpening", "fontDidOpen")
        addObserver(self, "aFontIsClosing", "fontWillClose")
        self.setUpBaseWindowBehavior()

        # open window
        self.w.open()

    # drawing callbacks
    def _mouseDown(self, infoDict):
        mouseDownPoint = infoDict['point']
        mouseDownClickCount = infoDict['clickCount']

        # double click
        if mouseDownClickCount == 2:
            if self.lftNeighborActive is True and self.lftGlyphName:
                lftGlyph = chooseRightGlyph(self.lftFontPath, self.lftGlyphName)
                if version[0] == '2':
                    xMin, yMin, xMax, yMax = lftGlyph.bounds
                else:
                    xMin, yMin, xMax, yMax = lftGlyph.box
                if xMin < (mouseDownPoint.x+lftGlyph.width) < xMax and yMin < mouseDownPoint.y < yMax:
                    OpenGlyphWindow(glyph=lftGlyph, newWindow=True)

            if self.rgtNeighborActive is True and self.rgtGlyphName:
                rgtGlyph = chooseRightGlyph(self.rgtFontPath, self.rgtGlyphName)
                if version[0] == '2':
                    xMin, yMin, xMax, yMax = rgtGlyph.bounds
                else:
                    xMin, yMin, xMax, yMax = rgtGlyph.box
                if xMin < (mouseDownPoint.x-self.currentGlyph.width) < xMax and yMin < mouseDownPoint.y < yMax:
                    OpenGlyphWindow(glyph=rgtGlyph, newWindow=True)


    def _draw(self, infoDict):
        glyphOnCanvas = infoDict['glyph']
        scalingFactor = infoDict['scale']

        if self.lftGlyphName and self.lftNeighborActive is True:
            lftGlyph = chooseRightGlyph(self.lftFontPath, self.lftGlyphName)
        if self.rgtGlyphName and self.rgtNeighborActive is True:
            rgtGlyph = chooseRightGlyph(self.rgtFontPath, self.rgtGlyphName)

        try:
            if self.lftGlyphName and self.lftNeighborActive is True:
                self._drawGlyphOutline(lftGlyph, scalingFactor, offset_X=-lftGlyph.width)
            if self.rgtGlyphName and self.rgtNeighborActive is True:
                self._drawGlyphOutline(rgtGlyph, scalingFactor, offset_X=glyphOnCanvas.width)

            if self.sqrActive is True and 2 > scalingFactor:
                self._drawSquarings(glyphOnCanvas, scalingFactor)
                if self.lftGlyphName and self.lftNeighborActive is True:
                    self._drawSquarings(lftGlyph, scalingFactor, offset_X=-lftGlyph.width)
                if self.rgtGlyphName and self.rgtNeighborActive is True:
                    self._drawSquarings(rgtGlyph, scalingFactor, offset_X=glyphOnCanvas.width)

            if self.bcpLengthActive is True and 2 > scalingFactor:
                self._drawBcpLenght(glyphOnCanvas, scalingFactor, 2)
                if self.lftGlyphName and self.lftNeighborActive is True:
                    self._drawBcpLenght(lftGlyph, scalingFactor, offset_X=-lftGlyph.width)
                if self.rgtGlyphName and self.rgtNeighborActive is True:
                    self._drawBcpLenght(rgtGlyph, scalingFactor, offset_X=glyphOnCanvas.width)

        except Exception as error:
            print(traceback.format_exc())

    def _drawPreview(self, infoDict):
        glyphOnCanvas = infoDict['glyph']
        scalingFactor = infoDict['scale']

        if self.lftGlyphName and self.lftNeighborActive is True:
            lftGlyph = chooseRightGlyph(self.lftFontPath, self.lftGlyphName)
        if self.rgtGlyphName and self.rgtNeighborActive is True:
            rgtGlyph = chooseRightGlyph(self.rgtFontPath, self.rgtGlyphName)

        try:
            if self.lftGlyphName and self.lftNeighborActive is True:
                self._drawGlyphBlack(lftGlyph, scalingFactor, offset_X=-lftGlyph.width)
            if self.rgtGlyphName and self.rgtNeighborActive is True:
                self._drawGlyphBlack(rgtGlyph, scalingFactor, offset_X=glyphOnCanvas.width)
        except Exception as error:
            print(traceback.format_exc())

    def _drawBackground(self, infoDict):
        glyphOnCanvas = infoDict['glyph']
        scalingFactor = infoDict['scale']

        if self.lftGlyphName and self.lftNeighborActive is True:
            lftGlyph = chooseRightGlyph(self.lftFontPath, self.lftGlyphName)
        if self.rgtGlyphName and self.rgtNeighborActive is True:
            rgtGlyph = chooseRightGlyph(self.rgtFontPath, self.rgtGlyphName)

        try:
            if self.gridActive is True and 2 > scalingFactor:
                offsetFromOrigin = infoDict['view'].offset()
                visibleRect = infoDict['view'].visibleRect()
                frameOrigin = int(visibleRect.origin.x-offsetFromOrigin[0]), int(visibleRect.origin.y-offsetFromOrigin[1])
                frameSize = int(visibleRect.size.width), int(visibleRect.size.height)
                self._drawGrids(frameOrigin, frameSize, glyphOnCanvas.getParent().info.italicAngle, scalingFactor)

            if self.diagonalActive is True and 1 > scalingFactor:
                self._drawDiagonals(glyphOnCanvas, scalingFactor)
                if self.lftGlyphName and self.lftNeighborActive is True:
                    self._drawDiagonals(lftGlyph, scalingFactor, offset_X=-lftGlyph.width)
                if self.rgtGlyphName and self.rgtNeighborActive is True:
                    self._drawDiagonals(rgtGlyph, scalingFactor, offset_X=glyphOnCanvas.width)

            if self.cntNeighborActive is True:
                cntGlyph = chooseRightGlyph(self.cntFontPath, self.cntGlyphName)
                self._drawCentralBackgroundGlyph(cntGlyph)

            if self.stemActive is True and 1.5 > scalingFactor:
                self._drawStems(glyphOnCanvas, scalingFactor)
                if self.lftGlyphName and self.lftNeighborActive is True:
                    self._drawStems(lftGlyph, scalingFactor, offset_X=-lftGlyph.width)
                if self.rgtGlyphName and self.rgtNeighborActive is True:
                    self._drawStems(rgtGlyph, scalingFactor, offset_X=glyphOnCanvas.width)

            if self.offgridActive is True:
                self._drawOffgridPoints(glyphOnCanvas, scalingFactor)

        except Exception as error:
            print(traceback.format_exc())

    def _drawOffgridPoints(self, glyph, scalingFactor):
        dt.save()
        dt.fill(*RED_COLOR)
        dt.stroke(None)

        scaledRadius = OFFGRID_RADIUS*scalingFactor
        for eachContour in glyph:
            for eachBPT in eachContour.bPoints:
                if eachBPT.anchor[0] % 4 != 0 or eachBPT.anchor[1] % 4 != 0:
                    dt.oval(eachBPT.anchor[0]-scaledRadius/2., eachBPT.anchor[1]-scaledRadius/2., scaledRadius, scaledRadius)

                if eachBPT.bcpIn != (0,0):
                    bcpInAbs = eachBPT.anchor[0]+eachBPT.bcpIn[0], eachBPT.anchor[1]+eachBPT.bcpIn[1]
                    if bcpInAbs[0] % 4 != 0 or bcpInAbs[1] % 4 != 0:
                        dt.oval(bcpInAbs[0]-scaledRadius/2., bcpInAbs[1]-scaledRadius/2., scaledRadius, scaledRadius)

                if eachBPT.bcpOut != (0,0):
                    bcpOutAbs = eachBPT.anchor[0]+eachBPT.bcpOut[0], eachBPT.anchor[1]+eachBPT.bcpOut[1]
                    if bcpOutAbs[0] % 4 != 0 or bcpOutAbs[1] % 4 != 0:
                        dt.oval(bcpOutAbs[0]-scaledRadius/2., bcpOutAbs[1]-scaledRadius/2., scaledRadius, scaledRadius)
        dt.restore()

    def _drawCentralBackgroundGlyph(self, glyph):
        dt.save()
        dt.fill(*LIGHT_GRAY_COLOR)
        dt.drawGlyph(glyph)
        dt.restore()

    def _drawGrids(self, frameOrigin, frameSize, italicAngle, scalingFactor):
        if not italicAngle:
            italicAngle = 0

        for eachGridDescription in reversed(self.gridsDB):
            gridColor = eachGridDescription['color']
            isHorizontal = eachGridDescription['horizontal']
            isVertical = eachGridDescription['vertical']
            gridStep = eachGridDescription['step']

            if isHorizontal is False and isVertical is False:
                continue
            if not gridStep:
                continue

            dt.save()
            dt.skew(-italicAngle, 0)
            dt.stroke(*gridColor)
            dt.strokeWidth(.5*scalingFactor)
            dt.fill(None)

            if isVertical is True:
                # to the right (from 0)
                extraSlant = int(ceil(tan(radians(italicAngle))*frameOrigin[1]))
                for eachX in range(0, frameOrigin[0]+frameSize[0]+extraSlant, gridStep):
                    dt.line((eachX, frameOrigin[1]-GRID_TOLERANCE), (eachX, frameOrigin[1]+frameSize[1]+GRID_TOLERANCE))

                # to the left (from 0)
                extraSlant = int(ceil(tan(radians(italicAngle))*(frameSize[1]+frameOrigin[1])))
                for eachX in [i for i in range(frameOrigin[0]+extraSlant, 0) if i % gridStep == 0]:
                    dt.line((eachX, frameOrigin[1]-GRID_TOLERANCE), (eachX, frameOrigin[1]+frameSize[1]+GRID_TOLERANCE))

            if isHorizontal is True:
                # to the top (from baseline)
                for eachY in range(0, frameOrigin[1]+frameSize[1], gridStep):
                    dt.line((frameOrigin[0]-GRID_TOLERANCE, eachY), (frameOrigin[0]+frameSize[0]+GRID_TOLERANCE, eachY))

                # to the bottom (from baseline)
                for eachY in [i for i in range(frameOrigin[1], 0) if i % gridStep == 0]:
                    dt.line((frameOrigin[0]-GRID_TOLERANCE, eachY), (frameOrigin[0]+frameSize[0]+GRID_TOLERANCE, eachY))

            dt.restore()

    def _drawBcpLenght(self, glyph, scalingFactor, offset_X=0):
        for eachContour in glyph:
            for indexBPT, eachBPT in enumerate(eachContour.bPoints):
                if eachBPT.bcpOut != (0, 0):
                    absBcpOut = eachBPT.anchor[0] + eachBPT.bcpOut[0], eachBPT.anchor[1] + eachBPT.bcpOut[1]
                    bcpOutAngle = calcAngle(eachBPT.anchor, absBcpOut)
                    bcpOutLenght = calcDistance(eachBPT.anchor, absBcpOut)
                    captionBcpOut = u'→{:d}'.format(int(bcpOutLenght))
                    projOut_X = eachBPT.anchor[0]+cos(radians(bcpOutAngle))*bcpOutLenght/2.
                    projOut_Y = eachBPT.anchor[1]+sin(radians(bcpOutAngle))*bcpOutLenght/2.

                    textQualities(BODYSIZE_CAPTION*scalingFactor, weight='bold')
                    textWidth, textHeight = dt.textSize(captionBcpOut)

                    dt.save()
                    dt.translate(projOut_X+offset_X, projOut_Y)
                    dt.rotate(bcpOutAngle % 90)
                    belowRect = (-textWidth/2.-1, -textHeight/2.-1, textWidth+2, textHeight+2, 1)
                    dt.fill(0, 0, 0, .7)
                    dt.roundedRect(*belowRect)

                    textRect = (-textWidth/2., -textHeight/2., textWidth, textHeight)
                    textQualities(BODYSIZE_CAPTION*scalingFactor, weight='bold', color=WHITE_COLOR)
                    dt.textBox(captionBcpOut, textRect, align='center')
                    dt.restore()

                if eachBPT.bcpIn != (0, 0):
                    absBcpIn = eachBPT.anchor[0] + eachBPT.bcpIn[0], eachBPT.anchor[1] + eachBPT.bcpIn[1]
                    bcpInAngle = calcAngle(eachBPT.anchor, absBcpIn)
                    bcpInLenght = calcDistance(eachBPT.anchor, absBcpIn)
                    captionBcpIn = u'→{:d}'.format(int(bcpInLenght))

                    projIn_X = eachBPT.anchor[0]+cos(radians(bcpInAngle))*bcpInLenght/2.
                    projIn_Y = eachBPT.anchor[1]+sin(radians(bcpInAngle))*bcpInLenght/2.

                    textQualities(BODYSIZE_CAPTION*scalingFactor, weight='bold')
                    textWidth, textHeight = dt.textSize(captionBcpIn)

                    dt.save()
                    dt.translate(projIn_X+offset_X, projIn_Y)
                    dt.rotate(bcpInAngle % 90)

                    belowRect = (-textWidth/2.-1, -textHeight/2.-1, textWidth+2, textHeight+2, 1)
                    dt.fill(0, 0, 0, .7)
                    dt.roundedRect(*belowRect)

                    textQualities(BODYSIZE_CAPTION*scalingFactor, weight='bold', color=WHITE_COLOR)
                    textRect = (-textWidth/2., -textHeight/2., textWidth, textHeight)
                    dt.textBox(captionBcpIn, textRect, align='center')
                    dt.restore()

    def _drawSquarings(self, glyph, scalingFactor, offset_X=0):
        for eachContour in glyph:
            for indexBPT, eachBPT in enumerate(eachContour.bPoints):

                if eachBPT.bcpOut != (0, 0):
                    nextBPT = eachContour.bPoints[(indexBPT+1) % len(eachContour.bPoints)]

                    absBcpOut = (eachBPT.anchor[0]+eachBPT.bcpOut[0], eachBPT.anchor[1]+eachBPT.bcpOut[1])
                    angleOut = calcAngle(eachBPT.anchor, absBcpOut)
                    handleOutLen = calcDistance(eachBPT.anchor, absBcpOut)

                    absBcpIn = (nextBPT.anchor[0]+nextBPT.bcpIn[0], nextBPT.anchor[1]+nextBPT.bcpIn[1])
                    angleIn = calcAngle(nextBPT.anchor, absBcpIn)
                    nextHandleInLen = calcDistance(nextBPT.anchor, absBcpIn)

                    handlesIntersection = intersectionBetweenSegments(eachBPT.anchor,
                                                                      absBcpOut,
                                                                      absBcpIn,
                                                                      nextBPT.anchor)

                    if handlesIntersection is not None:
                        maxOutLen = calcDistance(eachBPT.anchor, handlesIntersection)
                        maxInLen = calcDistance(nextBPT.anchor, handlesIntersection)

                        sqrOut = handleOutLen/maxOutLen
                        sqrIn = nextHandleInLen/maxInLen

                        projOut_X = eachBPT.anchor[0]+cos(radians(angleOut))*handleOutLen
                        projOut_Y = eachBPT.anchor[1]+sin(radians(angleOut))*handleOutLen
                        if angleOut != 0 and angleOut % 90 != 0:
                            captionSqrOut = u'{:.0%}, {:d}°'.format(sqrOut, int(angleOut%180))
                        else:
                            captionSqrOut = '{:.0%}'.format(sqrOut)
                        captionSqrOut = captionSqrOut.replace('0.', '')

                        dt.save()
                        dt.translate(projOut_X+offset_X, projOut_Y)
                        textQualities(BODYSIZE_CAPTION*scalingFactor)
                        textWidth, textHeight = dt.textSize(captionSqrOut)
                        if angleOut == 90:          # text above
                            textRect = (-textWidth/2., SQR_CAPTION_OFFSET*scalingFactor, textWidth, textHeight)
                        elif angleOut == -90:       # text below
                            textRect = (-textWidth/2., -textHeight-SQR_CAPTION_OFFSET*scalingFactor, textWidth, textHeight)
                        elif -90 < angleOut < 90:   # text on the right
                            textRect = (SQR_CAPTION_OFFSET*scalingFactor, -textHeight/2., textWidth, textHeight)
                        else:                       # text on the left
                            textRect = (-textWidth-SQR_CAPTION_OFFSET*scalingFactor, -textHeight/2., textWidth, textHeight)
                        dt.textBox(captionSqrOut, textRect, align='center')
                        dt.restore()

                        projIn_X = nextBPT.anchor[0]+cos(radians(angleIn))*nextHandleInLen
                        projIn_Y = nextBPT.anchor[1]+sin(radians(angleIn))*nextHandleInLen
                        if angleIn != 0 and angleIn % 90 != 0:
                            captionSqrIn = u'{:.0%}, {:d}°'.format(sqrIn, int(angleIn%180))
                        else:
                            captionSqrIn = '{:.0%}'.format(sqrIn)
                        captionSqrIn = captionSqrIn.replace('0.', '')

                        dt.save()
                        dt.translate(projIn_X+offset_X, projIn_Y)
                        textQualities(BODYSIZE_CAPTION*scalingFactor)
                        textWidth, textHeight = dt.textSize(captionSqrIn)
                        if angleIn == 90:          # text above
                            textRect = (-textWidth/2., SQR_CAPTION_OFFSET*scalingFactor, textWidth, textHeight)
                        elif angleIn == -90:       # text below
                            textRect = (-textWidth/2., -textHeight-SQR_CAPTION_OFFSET*scalingFactor, textWidth, textHeight)
                        elif -90 < angleIn < 90:   # text on the right
                            textRect = (SQR_CAPTION_OFFSET*scalingFactor, -textHeight/2., textWidth, textHeight)
                        else:                      # text on the left
                            textRect = (-textWidth-SQR_CAPTION_OFFSET*scalingFactor, -textHeight/2., textWidth, textHeight)
                        dt.textBox(captionSqrIn, textRect, align='center')
                        dt.restore()

    def _drawGlyphOutline(self, glyph, scalingFactor, offset_X=0):
        dt.save()
        dt.translate(offset_X, 0)

        dt.fill(None)
        dt.strokeWidth(1*scalingFactor)
        dt.stroke(*LIGHT_GRAY_COLOR)
        dt.drawGlyph(glyph)

        scaledRadius = BCP_RADIUS*scalingFactor

        for eachContour in glyph:
            for eachBPT in eachContour.bPoints:
                dt.stroke(None)
                dt.fill(*LIGHT_GRAY_COLOR)
                dt.rect(eachBPT.anchor[0]-scaledRadius/2., eachBPT.anchor[1]-scaledRadius/2., scaledRadius, scaledRadius)

                if eachBPT.bcpIn != (0, 0):
                    dt.stroke(None)
                    dt.fill(*LIGHT_GRAY_COLOR)
                    dt.oval(eachBPT.anchor[0]+eachBPT.bcpIn[0]-scaledRadius/2.,
                         eachBPT.anchor[1]+eachBPT.bcpIn[1]-scaledRadius/2.,
                         scaledRadius,
                         scaledRadius)

                    dt.stroke(*LIGHT_GRAY_COLOR)
                    dt.fill(None)
                    dt.line((eachBPT.anchor[0], eachBPT.anchor[1]),
                         (eachBPT.anchor[0]+eachBPT.bcpIn[0], eachBPT.anchor[1]+eachBPT.bcpIn[1]))

                if eachBPT.bcpOut != (0, 0):
                    dt.stroke(None)
                    dt.fill(*LIGHT_GRAY_COLOR)
                    dt.oval(eachBPT.anchor[0]+eachBPT.bcpOut[0]-scaledRadius/2.,
                         eachBPT.anchor[1]+eachBPT.bcpOut[1]-scaledRadius/2.,
                         scaledRadius,
                         scaledRadius)

                    dt.stroke(*LIGHT_GRAY_COLOR)
                    dt.fill(None)
                    dt.line((eachBPT.anchor[0], eachBPT.anchor[1]),
                         (eachBPT.anchor[0]+eachBPT.bcpOut[0], eachBPT.anchor[1]+eachBPT.bcpOut[1]))

        dt.restore()

    def _drawGlyphBlack(self, glyph, scalingFactor, offset_X=0):
        dt.save()
        dt.translate(offset_X, 0)

        dt.fill(*BLACK_COLOR)
        dt.stroke(None)
        dt.drawGlyph(glyph)

        dt.restore()

    def _drawStems(self, currentGlyph, scalingFactor, offset_X=0):
        if STEM_KEY not in currentGlyph.lib:
            return None

        stemData = calcStemsData(currentGlyph, STEM_KEY)
        for PTs, DIFFs, middlePoint in stemData:
            pt1, pt2 = PTs
            horDiff, verDiff = DIFFs

            dt.save()
            dt.translate(offset_X, 0)
            dt.stroke(*self.stemColor)
            dt.fill(None)
            dt.strokeWidth(1*scalingFactor)

            dt.newPath()
            if horDiff > verDiff:  # ver
                rightPt, leftPt = PTs
                if pt1.x > pt2.x:
                    rightPt, leftPt = leftPt, rightPt
                dt.moveTo((leftPt.x, leftPt.y))
                dt.curveTo((leftPt.x-horDiff/2, leftPt.y), (rightPt.x+horDiff/2, rightPt.y), (rightPt.x, rightPt.y))

            else:                  # hor
                topPt, btmPt = PTs
                if pt2.y > pt1.y:
                    btmPt, topPt = topPt, btmPt
                dt.moveTo((btmPt.x, btmPt.y))
                dt.curveTo((btmPt.x, btmPt.y+verDiff/2), (topPt.x, topPt.y-verDiff/2), (topPt.x, topPt.y))
            dt.drawPath()
            dt.restore()

            dt.save()
            dt.translate(offset_X, 0)
            textQualities(BODYSIZE_CAPTION*scalingFactor)
            dataToPlot = u'↑{:d}\n→{:d}'.format(int(verDiff), int(horDiff))
            textWidth, textHeight = dt.textSize(dataToPlot)
            textRect = (middlePoint[0]-textWidth/2., middlePoint[1]-textHeight/2., textWidth, textHeight)
            dt.textBox(dataToPlot, textRect, align='center')
            dt.restore()

    def _drawDiagonals(self, currentGlyph, scalingFactor, offset_X=0):
        if DIAGONALS_KEY not in currentGlyph.lib:
            return None

        diagonalsData = calcDiagonalsData(currentGlyph, DIAGONALS_KEY)
        for ptsToDisplay, angle, distance in diagonalsData:
            pt1, pt2 = ptsToDisplay

            dt.save()
            dt.stroke(*self.diagonalColor)
            dt.fill(None)
            dt.strokeWidth(1*scalingFactor)

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

            dt.line((pt1), (offsetPt1))
            dt.line((pt2), (offsetPt2))
            dt.line((diagonalPt1), (diagonalPt2))
            dt.restore()

            dt.save()
            textQualities(BODYSIZE_CAPTION*scalingFactor)
            offsetMidPoint = calcMidPoint(offsetPt1, offsetPt2)
            dt.translate(offsetMidPoint[0], offsetMidPoint[1])

            if 90 < angle <= 180 or -180 < angle < -90:
                dt.rotate(angle+180)
                textBoxY = -BODYSIZE_CAPTION*1.2*scalingFactor
            else:
                dt.rotate(angle)
                textBoxY = 0

            dataToPlot = u'∡{:.1f} ↗{:d}'.format(angle%180, int(distance))
            textWidth, textHeight = dt.textSize(dataToPlot)
            dt.textBox(dataToPlot, (-textWidth/2., textBoxY, textWidth, BODYSIZE_CAPTION*1.2*scalingFactor), align='center')
            dt.restore()

    # ui callback
    def collectOpenedFontPaths(self):
        self.openedFontPaths = [f.path for f in AllFonts() if f.path is not None]
        self.openedFontPaths.sort()

    def aFontIsClosing(self, infoDict):
        willCloseFont = infoDict['font']
        self.openedFontPaths.remove(willCloseFont.path)

        for eachFontAttrName, eachGlyphAttrName in [('lftFontPath', 'lftGlyphName'), ('cntFontPath', 'cntGlyphName'), ('rgtFontPath', 'rgtGlyphName')]:
            if getattr(self, eachFontAttrName) is willCloseFont:
                anotherFont = getOpenedFontFromPath(AllFonts(), self.openedFontPaths[0])
                setattr(self, eachFontAttrName, anotherFont)
                self.pushFontAttr(eachFontAttrName)

                activeName = getattr(self, eachGlyphAttrName).name
                if activeName in anotherFont:
                    setattr(self, eachGlyphAttrName, anotherFont[activeName])
                else:
                    setattr(self, eachGlyphAttrName, anotherFont[anotherFont.glyphOrder[0]])
                self.pushGlyphAttr(eachGlyphAttrName)

        self.neighborsController.setFontData(self.openedFontPaths)

    def pushFontAttr(self, attrName):
        fontToBePushed = getattr(self, attrName)
        self.neighborsController.neighborsDB[attrName][1] = fontToBePushed
        setattr(self.neighborsController, '{}Controller.activeFont'.format(attrName[:3], fontToBePushed))
        getattr(self.neighborsController, '{}Controller'.format(attrName[:3]).updateGlyphList())

    def pushGlyphAttr(self, attrName):
        glyphToBePushed = getattr(self, attrName)
        self.neighborsController.neighborsDB[attrName][2] = glyphToBePushed
        setattr(self.neighborsController, '{}Controller.activeGlyph'.format(attrName[:3], glyphToBePushed))
        getattr(self.neighborsController, '{}Controller'.format(attrName[:3]).updateGlyphList())

    def aFontIsOpening(self, infoDict):
        originalState = list(self.openedFontPaths)
        self.openedFontPaths.append(infoDict['font'].path)
        self.openedFontPaths.sort()
        if originalState == []:
            self._initFontsAndGlyphs()
            for eachFontAttrName, eachGlyphAttrName in [('lftFontPath', 'lftGlyphName'), ('cntFontPath', 'cntGlyphName'), ('rgtFontPath', 'rgtGlyphName')]:
                self.pushFontAttr(eachFontAttrName)
                self.pushGlyphAttr(eachGlyphAttrName)
        self.neighborsController.setFontData(self.openedFontPaths)

    def _initFontsAndGlyphs(self):
        for eachFontAttrName, eachGlyphAttrName in [('lftFontPath', 'lftGlyphName'), ('cntFontPath', 'cntGlyphName'), ('rgtFontPath', 'rgtGlyphName')]:
            setattr(self, eachFontAttrName, CURRENT_FONT_REPR)
            setattr(self, eachGlyphAttrName, CURRENT_GLYPH_REPR)

    def _updateCurrentGlyph(self, infoDict):
        if infoDict['glyph']:
            # update distances
            self.currentGlyph = infoDict['glyph']
            self.distancesController.setCurrentGlyph(self.currentGlyph)
            # update neighbors
            self.neighborsController.lftController.updateCurrentGlyph()
            self.neighborsController.cntController.updateCurrentGlyph()
            self.neighborsController.rgtController.updateCurrentGlyph()

    def _updateCurrentFont(self, infoDict):
        if infoDict['font']:
            self.currentGlyph = CurrentGlyph()
            self.distancesController.setCurrentGlyph(self.currentGlyph)
            # update neighbors
            self.neighborsController.lftController.updateCurrentGlyph()
            self.neighborsController.cntController.updateCurrentGlyph()
            self.neighborsController.rgtController.updateCurrentGlyph()

    # controls callbacks
    def windowCloseCallback(self, sender):
        removeObserver(self, 'draw')
        removeObserver(self, 'drawInactive')
        removeObserver(self, 'drawBackground')
        removeObserver(self, 'drawPreview')
        removeObserver(self, 'mouseDown')
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
        self.lftFontPath = neighborsDB['lft'][1]
        self.lftGlyphName = neighborsDB['lft'][2]
        self.cntNeighborActive = neighborsDB['cnt'][0]
        self.cntFontPath = neighborsDB['cnt'][1]
        self.cntGlyphName = neighborsDB['cnt'][2]
        self.rgtNeighborActive = neighborsDB['rgt'][0]
        self.rgtFontPath = neighborsDB['rgt'][1]
        self.rgtGlyphName = neighborsDB['rgt'][2]
        UpdateCurrentGlyphView()
