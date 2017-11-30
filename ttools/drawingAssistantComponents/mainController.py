#!/usr/bin/env python
# coding: utf-8

####################################
# Main DrawingAssistant Controller #
####################################

### Modules
# components
import sharedValues
reload(sharedValues)
from sharedValues import MARGIN_HOR, NET_WIDTH, PLUGIN_WIDTH
from sharedValues import STEM_KEY, DIAGONALS_KEY

import bcps
reload(bcps)
from bcps import BcpController

import grids
reload(grids)
from grids import MultipleGridController

import distances
reload(distances)
from distances import DistancesController

import neighbors
reload(neighbors)
from neighbors import NeighborsController

# custom
from ..ui import userInterfaceValues
reload(userInterfaceValues)
from ..ui.userInterfaceValues import vanillaControlsSize

from ..extraTools import miscFunctions
reload(miscFunctions)
from ..extraTools.miscFunctions import getOpenedFontFromPath

from ..extraTools import calcFunctions
reload(calcFunctions)
from ..extraTools.calcFunctions import intersectionBetweenSegments, calcAngle, calcDistance
from ..extraTools.calcFunctions import calcStemsData, calcDiagonalsData, calcMidPoint

# standard
import traceback
from math import cos, sin, radians, tan, ceil
from vanilla import FloatingWindow
from mojo.UI import AccordionView
import mojo.drawingTools as dt
from defconAppKit.windows.baseWindow import BaseWindowController
from mojo.roboFont import CurrentGlyph, CurrentFont, AllFonts, version
from mojo.events import addObserver, removeObserver
from mojo.UI import UpdateCurrentGlyphView, OpenGlyphWindow

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
            if eachFont.has_key(absGlyphName):
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
        self.w.bind('close', self.windowCloseCallback)

        # open window
        self.w.open()

    # drawing callbacks
    def _mouseDown(self, infoDict):
        mouseDownPoint = infoDict['point']
        mouseDownClickCount = infoDict['clickCount']

        # double click
        if mouseDownClickCount == 2:
            if self.lftNeighborActive is True and self.lftGlyphName:
                if version[0] == '2':
                    xMin, yMin, xMax, yMax = self.lftGlyph.bounds
                else:
                    xMin, yMin, xMax, yMax = self.lftGlyph.box
                if xMin < (mouseDownPoint.x+self.lftGlyph.width) < xMax and yMin < mouseDownPoint.y < yMax:
                    OpenGlyphWindow(glyph=self.lftGlyphName, newWindow=True)

            if self.rgtNeighborActive is True and self.rgtGlyphName:
                if version[0] == '2':
                    xMin, yMin, xMax, yMax = self.rgtGlyph.bounds
                else:
                    xMin, yMin, xMax, yMax = self.rgtGlyph.box
                if xMin < (mouseDownPoint.x-self.currentGlyph.width) < xMax and yMin < mouseDownPoint.y < yMax:
                    OpenGlyphWindow(glyph=self.rgtGlyph, newWindow=True)


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
            print traceback.format_exc()

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
            print traceback.format_exc()

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
            print traceback.format_exc()

    def _drawOffgridPoints(self, glyph, scalingFactor):
        dt.save()
        dt.fill(*RED_COLOR)
        dt.stroke(None)

        scaledRadius = OFFGRID_RADIUS*scalingFactor
        for eachContour in glyph:
            for eachPt in eachContour.bPoints:
                if eachPt.anchor[0] % 4 != 0 or eachPt.anchor[1] % 4 != 0:
                    dt.oval(eachPt.anchor[0]-scaledRadius/2., eachPt.anchor[1]-scaledRadius/2., scaledRadius, scaledRadius)

                if eachPt.bcpIn != (0,0):
                    bcpInAbs = eachPt.anchor[0]+eachPt.bcpIn[0], eachPt.anchor[1]+eachPt.bcpIn[1]
                    if bcpInAbs[0] % 4 != 0 or bcpInAbs[1] % 4 != 0:
                        dt.oval(bcpInAbs[0]-scaledRadius/2., bcpInAbs[1]-scaledRadius/2., scaledRadius, scaledRadius)

                if eachPt.bcpOut != (0,0):
                    bcpOutAbs = eachPt.anchor[0]+eachPt.bcpOut[0], eachPt.anchor[1]+eachPt.bcpOut[1]
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
            for indexBcp, eachBcp in enumerate(eachContour.bPoints):
                if eachBcp.bcpOut != (0, 0):
                    absBcpOut = eachBcp.anchor[0] + eachBcp.bcpOut[0], eachBcp.anchor[1] + eachBcp.bcpOut[1]
                    bcpOutAngle = calcAngle(eachBcp.anchor, absBcpOut)
                    bcpOutLenght = calcDistance(eachBcp.anchor, absBcpOut)
                    captionBcpOut = u'→%d' % bcpOutLenght
                    projOut_X = eachBcp.anchor[0]+cos(radians(bcpOutAngle))*bcpOutLenght/2.
                    projOut_Y = eachBcp.anchor[1]+sin(radians(bcpOutAngle))*bcpOutLenght/2.

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

                if eachBcp.bcpIn != (0, 0):
                    absBcpIn = eachBcp.anchor[0] + eachBcp.bcpIn[0], eachBcp.anchor[1] + eachBcp.bcpIn[1]
                    bcpInAngle = calcAngle(eachBcp.anchor, absBcpIn)
                    bcpInLenght = calcDistance(eachBcp.anchor, absBcpIn)
                    captionBcpIn = u'→%d' % bcpInLenght

                    projIn_X = eachBcp.anchor[0]+cos(radians(bcpInAngle))*bcpInLenght/2.
                    projIn_Y = eachBcp.anchor[1]+sin(radians(bcpInAngle))*bcpInLenght/2.

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

                    if handlesIntersection is not None:
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

                        projIn_X = nextBcp.anchor[0]+cos(radians(angleIn))*nextHandleInLen
                        projIn_Y = nextBcp.anchor[1]+sin(radians(angleIn))*nextHandleInLen
                        if angleIn != 0 and angleIn % 90 != 0:
                            captionSqrIn = u'%.2f%%, %d°' % (sqrIn, angleIn%180)
                        else:
                            captionSqrIn = '%.2f%%' % sqrIn
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
            for eachPt in eachContour.bPoints:
                dt.stroke(None)
                dt.fill(*LIGHT_GRAY_COLOR)
                dt.rect(eachPt.anchor[0]-scaledRadius/2., eachPt.anchor[1]-scaledRadius/2., scaledRadius, scaledRadius)

                if eachPt.bcpIn != (0, 0):
                    dt.stroke(None)
                    dt.fill(*LIGHT_GRAY_COLOR)
                    dt.oval(eachPt.anchor[0]+eachPt.bcpIn[0]-scaledRadius/2.,
                         eachPt.anchor[1]+eachPt.bcpIn[1]-scaledRadius/2.,
                         scaledRadius,
                         scaledRadius)

                    dt.stroke(*LIGHT_GRAY_COLOR)
                    dt.fill(None)
                    dt.line((eachPt.anchor[0], eachPt.anchor[1]),
                         (eachPt.anchor[0]+eachPt.bcpIn[0], eachPt.anchor[1]+eachPt.bcpIn[1]))

                if eachPt.bcpOut != (0, 0):
                    dt.stroke(None)
                    dt.fill(*LIGHT_GRAY_COLOR)
                    dt.oval(eachPt.anchor[0]+eachPt.bcpOut[0]-scaledRadius/2.,
                         eachPt.anchor[1]+eachPt.bcpOut[1]-scaledRadius/2.,
                         scaledRadius,
                         scaledRadius)

                    dt.stroke(*LIGHT_GRAY_COLOR)
                    dt.fill(None)
                    dt.line((eachPt.anchor[0], eachPt.anchor[1]),
                         (eachPt.anchor[0]+eachPt.bcpOut[0], eachPt.anchor[1]+eachPt.bcpOut[1]))

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
            dataToPlot = u'↑%d\n→%d' % (verDiff, horDiff)
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

            dataToPlot = u'∡%.1f ↗%d' % (angle%180, distance)
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
                if anotherFont.has_key(activeName):
                    setattr(self, eachGlyphAttrName, anotherFont[activeName])
                else:
                    setattr(self, eachGlyphAttrName, anotherFont[anotherFont.glyphOrder[0]])
                self.pushGlyphAttr(eachGlyphAttrName)

        self.neighborsController.setFontData(self.openedFontPaths)

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
