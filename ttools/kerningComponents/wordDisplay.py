#!/usr/bin/env python
# coding: utf-8

### Modules
# standard
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
import traceback
import importlib
from defconAppKit.tools.textSplitter import splitText
import mojo.drawingTools as dt
from vanilla import Group
from mojo.canvas import CanvasGroup
from collections import namedtuple

# custom
from . import kerningMisc
importlib.reload(kerningMisc)
from .kerningMisc import whichGroup, getCorrection, buildPairsFromString
from .kerningMisc import checkIfPairOverlaps
from .kerningMisc import CANVAS_SCALING_FACTOR_INIT

from . import exceptionTools
importlib.reload(exceptionTools)
from .exceptionTools import checkPairConflicts, isPairException, calcWiggle

from ..ui import userInterfaceValues
importlib.reload(userInterfaceValues)
from ..ui.userInterfaceValues import vanillaControlsSize

### Costants
Point = namedtuple('Point', ['x', 'y'])
TEXT_MARGIN = 100 #upm
COLLISION_BODY_SIZE = 200
EXCEPTION_RADIUS = 50

if '.SFNSText' in dt.installedFonts():
    SYSTEM_FONT_NAME = '.SFNSText'
else:
    SYSTEM_FONT_NAME = '.HelveticaNeueDeskInterface-Regular'

BODY_SIZE = 14
GROUP_NAME_BODY_SIZE = 12

# colors
NON_KERNED_COLOR = (0,0,0,.4)
GLYPH_COLOR = (1,0,0,.4)
GROUP_COLOR = (0,0,1,.4)

LAYERED_GLYPHS_COLOR = (0, 0, 1, .1)
FLIPPED_BACKGROUND_COLOR = (1, 0, 1, .15)
SYMMETRICAL_BACKGROUND_COLOR = (1, 1, 0, .15)

BLACK = (0, 0, 0)
WHITE = (1,1,1)
LIGHT_RED = (1, 0, 0, .4)
LIGHT_GREEN = (0, 1, 0, .4)
LIGHT_BLUE = (0, 0, 1, .4)
LIGHT_GRAY = (0, 0, 0, .4)

### Classes
class WordDisplay(Group):

    def __init__(self, posSize,
                       displayedWord,
                       canvasScalingFactor,
                       fontObj,
                       isKerningDisplayActive,
                       areVerticalLettersDrawn,
                       areGroupsShown,
                       areCollisionsShown,
                       isSidebearingsActive,
                       isMetricsActive,
                       isColorsActive,
                       isPreviewOn,
                       isSymmetricalEditingOn,
                       isFlippedEditingOn,
                       indexPair):

        super(WordDisplay, self).__init__(posSize)

        self.fontObj = fontObj
        self.displayedWord = displayedWord
        self.displayedPairs = buildPairsFromString(self.displayedWord, self.fontObj)
        self.indexPair = indexPair

        if indexPair is not None:
            self.activePair = self.displayedPairs[self.indexPair]
        else:
            self.activePair = None

        self.canvasScalingFactor = canvasScalingFactor
        self.isKerningDisplayActive = isKerningDisplayActive
        self.areVerticalLettersDrawn = areVerticalLettersDrawn
        self.areGroupsShown = areGroupsShown
        self.areCollisionsShown = areCollisionsShown
        self.isSidebearingsActive = isSidebearingsActive
        self.isMetricsActive = isMetricsActive
        self.isColorsActive = isColorsActive
        self.isPreviewOn = isPreviewOn

        self.isSymmetricalEditingOn = isSymmetricalEditingOn
        self.isFlippedEditingOn = isFlippedEditingOn

        self.ctrlWidth, self.ctrlHeight = posSize[2], posSize[3]

        self.checkPairsQuality()
        self.wordCanvasGroup = CanvasGroup((0, 0, 0, 0),
                                           delegate=self)

    def checkPairsQuality(self):
        for eachPair in self.displayedPairs:
            status, pairsDB = checkPairConflicts(eachPair, self.fontObj)
            if status is False:
                print('conflicting pairs')
                print('please check the DB:', pairsDB)

    def getActivePair(self):
        return self.activePair

    def switchGlyphFromGroup(self, location, indexPair):
        assert location in ['left', 'right']

        if self.activePair is None:
            self.setActivePairIndex(indexPair)

        if location == 'left':
            theElem, otherElem = self.activePair
        else:
            otherElem, theElem = self.activePair
        groupReference = whichGroup(theElem, location, self.fontObj)

        if self.areGroupsShown is True and groupReference is not None:
            nextElemIndex = (self.fontObj.groups[groupReference].index(theElem)+1) % len(self.fontObj.groups[groupReference])
            if location == 'left':
                self.activePair = self.fontObj.groups[groupReference][nextElemIndex], otherElem
            else:
                self.activePair = otherElem, self.fontObj.groups[groupReference][nextElemIndex]
            self.wordCanvasGroup.update()

    def setFlippedEditingMode(self, value):
        self.isFlippedEditingOn = value

    def setSymmetricalEditingMode(self, value):
        self.isSymmetricalEditingOn = value

    def setPreviewMode(self, value):
        self.isPreviewOn = value

    def setGraphicsBooleans(self, isKerningDisplayActive, areVerticalLettersDrawn, areGroupsShown, areCollisionsShown, isSidebearingsActive, isMetricsActive, isColorsActive):
        self.isKerningDisplayActive = isKerningDisplayActive
        self.areVerticalLettersDrawn = areVerticalLettersDrawn
        self.areGroupsShown = areGroupsShown
        self.areCollisionsShown = areCollisionsShown
        self.isSidebearingsActive = isSidebearingsActive
        self.isMetricsActive = isMetricsActive
        self.isColorsActive = isColorsActive

    def adjustSize(self, posSize):
        x, y, width, height = posSize
        self.setPosSize((x, y, width, height))
        self.wordCanvasGroup.setPosSize((0, 0, width, height))
        self.wordCanvasGroup.resize(width, height)
        self.wordCanvasGroup.update()

    def setDisplayedWord(self, displayedWord):
        previousLength = len(self.displayedPairs)
        self.displayedWord = displayedWord
        self.displayedPairs = buildPairsFromString(self.displayedWord, self.fontObj)
        if self.indexPair is not None:
            self.setActivePairIndex(self.indexPair)
        self.checkPairsQuality()

    def setScalingFactor(self, scalingFactor):
        self.canvasScalingFactor = scalingFactor

    def setActivePairIndex(self, indexPair):
        self.indexPair = indexPair
        if self.indexPair is not None:
            try:
                self.activePair = self.displayedPairs[self.indexPair]
            except IndexError:
                self.activePair = self.displayedPairs[-1]
                self.indexPair = len(self.displayedPairs)-1
        else:
            self.activePair = None

    def setCtrlSize(self, ctrlWidth, ctrlHeight):
        self.ctrlWidth = ctrlWidth
        self.ctrlHeight = ctrlHeight

    def _drawColoredCorrection(self, correction):
        dt.save()

        if correction > 0:
            dt.fill(*LIGHT_GREEN)
        else:
            dt.fill(*LIGHT_RED)
        dt.rect(0, self.fontObj.info.descender, correction, self.fontObj.info.unitsPerEm)
        dt.restore()

    def _drawMetricsCorrection(self, correction):
        dt.save()
        dt.fill(*BLACK)
        dt.stroke(None)
        dt.translate(0, self.fontObj.info.unitsPerEm+self.fontObj.info.descender+100)
        dt.scale(1/(self.ctrlHeight/(self.canvasScalingFactor*self.fontObj.info.unitsPerEm)))
        dt.font(SYSTEM_FONT_NAME)
        dt.fontSize(BODY_SIZE)
        textWidth, textHeight = dt.textSize('{}'.format(correction))
        dt.textBox('{}'.format(correction), (-textWidth/2., -textHeight/2., textWidth, textHeight), align='center')

        dt.restore()

    def _drawGlyphOutlines(self, glyphName):
        dt.save()
        dt.fill(*BLACK)
        dt.stroke(None)
        glyphToDisplay = self.fontObj[glyphName]
        dt.drawGlyph(glyphToDisplay)
        dt.restore()

    def _drawMetricsData(self, glyphName, offset):
        dt.save()
        glyphToDisplay = self.fontObj[glyphName]
        dt.translate(0, self.fontObj.info.descender)
        reverseScalingFactor = 1/(self.ctrlHeight/(self.canvasScalingFactor*self.fontObj.info.unitsPerEm))

        if self.isSidebearingsActive is True:
            dt.fill(None)
            dt.stroke(*BLACK)
            dt.strokeWidth(reverseScalingFactor)
            dt.line((0, 0), (0, -offset*reverseScalingFactor))
            dt.line((glyphToDisplay.width, 0), (glyphToDisplay.width, -offset*reverseScalingFactor))
        dt.restore()

        dt.save()
        dt.translate(0, self.fontObj.info.descender)
        dt.translate(0, -offset*reverseScalingFactor)
        dt.fill(*BLACK)

        dt.stroke(None)
        dt.font(SYSTEM_FONT_NAME)
        dt.fontSize(BODY_SIZE*reverseScalingFactor)

        textWidth, textHeight = dt.textSize(u'{}'.format(glyphToDisplay.width))
        dt.textBox(u'{:d}'.format(glyphToDisplay.width), (0, 0, glyphToDisplay.width, textHeight*2), align='center')
        dt.textBox(u'\n{:d}'.format(glyphToDisplay.leftMargin), (0, 0, glyphToDisplay.width/2., textHeight*2), align='center')
        dt.textBox(u'\n{:d}'.format(glyphToDisplay.rightMargin), (glyphToDisplay.width/2., 0, glyphToDisplay.width/2., textHeight*2), align='center')
        dt.restore()

    def _drawBaseline(self, glyphName):
        glyphToDisplay = self.fontObj[glyphName]

        dt.save()
        dt.stroke(*BLACK)
        dt.fill(None)
        # reversed scaling factor
        dt.strokeWidth(1/(self.ctrlHeight/(self.canvasScalingFactor*self.fontObj.info.unitsPerEm)))
        dt.line((0, 0), (glyphToDisplay.width, 0))
        dt.restore()

    def _drawSidebearings(self, glyphName):
        glyphToDisplay = self.fontObj[glyphName]

        dt.save()
        dt.stroke(*BLACK)
        dt.fill(None)

        # reversed scaling factor
        dt.strokeWidth(1/(self.ctrlHeight/(self.canvasScalingFactor*self.fontObj.info.unitsPerEm)))

        dt.fill(*LIGHT_GRAY)
        dt.line((0, self.fontObj.info.descender), (0, self.fontObj.info.descender+self.fontObj.info.unitsPerEm))
        dt.line((glyphToDisplay.width, self.fontObj.info.descender), (glyphToDisplay.width, self.fontObj.info.descender+self.fontObj.info.unitsPerEm))

        dt.restore()

    def _drawCursor(self, correction, pairKind):
        assert pairKind in ('gr2gr', 'gr2gl', 'gl2gr', 'gl2gl') or pairKind is None

        dt.save()

        if pairKind is None:
            lftColor = NON_KERNED_COLOR
            rgtColor = NON_KERNED_COLOR

        elif pairKind == 'gr2gr':
            lftColor = GROUP_COLOR
            rgtColor = GROUP_COLOR

        elif pairKind == 'gr2gl':
            lftColor = GROUP_COLOR
            rgtColor = GLYPH_COLOR

        elif pairKind == 'gl2gr':
            lftColor = GLYPH_COLOR
            rgtColor = GROUP_COLOR
        else:
            lftColor = GLYPH_COLOR
            rgtColor = GLYPH_COLOR

        lftGlyphName, rgtGlyphName = self.activePair
        lftGlyph = self.fontObj[lftGlyphName]
        rgtGlyph = self.fontObj[rgtGlyphName]

        lftCursorWidth = lftGlyph.width/2. + correction/2.
        rgtCursorWidth = rgtGlyph.width/2. + correction/2.
        cursorHeight = 50   # upm

        # lft
        dt.fill(*lftColor)
        dt.rect(-lftGlyph.width/2.-correction, self.fontObj.info.descender-cursorHeight+cursorHeight/2., lftCursorWidth, cursorHeight)
        
        # rgt
        dt.fill(*rgtColor)
        dt.rect(-correction/2., self.fontObj.info.descender-cursorHeight+cursorHeight/2., rgtCursorWidth, cursorHeight)
        dt.restore()

    def _drawGlyphOutlinesFromGroups(self, aPair, kerningReference, correction):
        prevGlyphName, eachGlyphName = aPair
        if kerningReference is not None:
            lftReference, rgtReference = kerningReference
        else:
            lftReference = whichGroup(prevGlyphName, 'left', self.fontObj)
            rgtReference = whichGroup(eachGlyphName, 'right', self.fontObj)

        prevGlyph, eachGlyph = self.fontObj[prevGlyphName], self.fontObj[eachGlyphName]
        reverseScalingFactor = 1/(self.ctrlHeight/(self.canvasScalingFactor*self.fontObj.info.unitsPerEm))

        # _L__ group
        if lftReference:
            if lftReference.startswith('@MMK_L_'):
                dt.save()
                dt.fill(*LAYERED_GLYPHS_COLOR)
                groupContent = self.fontObj.groups[lftReference]
                for eachGroupSibling in groupContent:
                    if eachGroupSibling != prevGlyphName:
                        glyphToDisplay = self.fontObj[eachGroupSibling]
                        dt.save()
                        dt.translate(-glyphToDisplay.width, 0) # back, according to his width, otherwise it does not coincide
                        dt.drawGlyph(glyphToDisplay)
                        dt.restore()

                dt.fill(*BLACK)    # caption
                dt.translate(-prevGlyph.width, 0) # we need a caption in the right place
                dt.font(SYSTEM_FONT_NAME)
                dt.fontSize(GROUP_NAME_BODY_SIZE*reverseScalingFactor)
                textWidth, textHeight = dt.textSize(lftReference)
                dt.text(lftReference, (glyphToDisplay.width/2.-textWidth/2., -GROUP_NAME_BODY_SIZE*reverseScalingFactor*2))
                dt.restore()

        # _R__ group
        if rgtReference:
            if rgtReference.startswith('@MMK_R_'):
                dt.save()
                dt.translate(correction, 0)
                dt.fill(*LAYERED_GLYPHS_COLOR)
                groupContent = self.fontObj.groups[rgtReference]
                for eachGroupSibling in groupContent:
                    if eachGroupSibling != eachGlyphName:
                        glyphToDisplay = self.fontObj[eachGroupSibling]
                        dt.drawGlyph(glyphToDisplay)

                dt.fill(*BLACK)
                dt.font(SYSTEM_FONT_NAME)
                dt.fontSize(GROUP_NAME_BODY_SIZE*reverseScalingFactor)
                textWidth, textHeight = dt.textSize(rgtReference)
                dt.text(rgtReference, (glyphToDisplay.width/2.-textWidth/2., -GROUP_NAME_BODY_SIZE*reverseScalingFactor*2))
                dt.restore()

    def _drawCollisions(self, aPair):
        dt.save()

        correction, kerningReference, pairKind = getCorrection(aPair, self.fontObj)

        if kerningReference is None:
            lftName, rgtName = aPair
        else:
            lftName, rgtName = kerningReference

        lftGlyphs = []
        if lftName.startswith('@MMK') is True:
            lftGlyphs = self.fontObj.groups[lftName]
        else:
            lftGlyphs = [lftName]

        rgtGlyphs = []
        if rgtName.startswith('@MMK') is True:
            rgtGlyphs = self.fontObj.groups[rgtName]
        else:
            rgtGlyphs = [rgtName]

        dt.fontSize(COLLISION_BODY_SIZE)

        breakCycle = False
        for eachLftName in lftGlyphs:
            for eachRgtName in rgtGlyphs:
                isTouching = checkIfPairOverlaps(self.fontObj[eachLftName], self.fontObj[eachRgtName])
                if isTouching:
                    dt.text(u'💥', (0, 0))
                    breakCycle = True
                    break

            if breakCycle is True:
                break
        dt.restore()

    def _drawException(self, aPair, correction):
        lftGlyphName, rgtGlyphName = aPair
        lftGlyph, rgtGlyph = self.fontObj[lftGlyphName], self.fontObj[rgtGlyphName]

        dt.save()
        dt.fill(None)
        dt.stroke(*LIGHT_GRAY)
        dt.strokeWidth(20)

        # calc wiggle line
        pt1 = Point(-lftGlyph.width, 0)
        pt2 = Point(rgtGlyph.width+correction, 0)
        wigglePoints = calcWiggle(pt1, pt2, 100, 100, .65)

        # draw wiggle line
        dt.newPath()
        dt.moveTo(wigglePoints[0])
        for eachBcpOut, eachBcpIn, eachAnchor in wigglePoints[1:]:
            dt.curveTo(eachBcpOut, eachBcpIn, eachAnchor)
        dt.drawPath()

        dt.restore()

    def draw(self):

        try:
            glyphsToDisplay = splitText(self.displayedWord, self.fontObj.naked().unicodeData)

            # if the user switches the glyphs from the groups
            # here we have to arrange the list of glyphnames properly
            if self.activePair is not None:
                lftName, rgtName = self.activePair
                glyphsToDisplay[self.indexPair]   = lftName
                glyphsToDisplay[self.indexPair+1] = rgtName

            # here we draw
            dt.save()

            # this is for safety reason, user should be notified about possible unwanted kerning corrections
            if self.isFlippedEditingOn is True:
                dt.save()
                dt.fill(*FLIPPED_BACKGROUND_COLOR)
                dt.rect(0, 0, self.ctrlWidth, self.ctrlHeight)
                dt.restore()

            if self.isSymmetricalEditingOn is True:
                dt.save()
                dt.fill(*SYMMETRICAL_BACKGROUND_COLOR)
                dt.rect(0, 0, self.ctrlWidth, self.ctrlHeight)
                dt.restore()

            dt.scale(self.ctrlHeight/(self.canvasScalingFactor*self.fontObj.info.unitsPerEm))   # the canvas is virtually scaled according to self.canvasScalingFactor value and canvasSize
            dt.translate(TEXT_MARGIN, 0)

            # group glyphs
            dt.translate(0, 600)

            if self.areGroupsShown is True:
                dt.save()
                prevGlyphName = None
                for indexChar, eachGlyphName in enumerate(glyphsToDisplay):
                    eachGlyph = self.fontObj[eachGlyphName]

                    # this is for kerning
                    if indexChar > 0:
                        correction, kerningReference, pairKind = getCorrection((prevGlyphName, eachGlyphName), self.fontObj)

                        if kerningReference:
                            exceptionStatus, doesExists, exceptionParents = isPairException(kerningReference, self.fontObj)
                            if exceptionStatus is True and self.isPreviewOn is False:
                                self._drawException((prevGlyphName, eachGlyphName), correction)

                        if (indexChar-1) == self.indexPair:
                            self._drawGlyphOutlinesFromGroups((prevGlyphName, eachGlyphName), kerningReference, correction)

                        if correction and correction != 0 and self.isKerningDisplayActive:
                            dt.translate(correction, 0)

                    dt.translate(eachGlyph.width, 0)
                    prevGlyphName = eachGlyphName
                dt.restore()

            # background loop
            dt.save()
            glyphsToDisplayTotalWidth = 0
            prevGlyphName = None
            for indexChar, eachGlyphName in enumerate(glyphsToDisplay):
                eachGlyph = self.fontObj[eachGlyphName]

                # this is for kerning
                if indexChar > 0:
                    correction, kerningReference, pairKind = getCorrection((prevGlyphName, eachGlyphName), self.fontObj)
                    if correction and correction != 0 and self.isKerningDisplayActive:
                        if self.isColorsActive is True and self.isPreviewOn is False:
                            self._drawColoredCorrection(correction)
                        if self.isMetricsActive is True and self.isPreviewOn is False:
                            self._drawMetricsCorrection(correction)
                        dt.translate(correction, 0)
                        glyphsToDisplayTotalWidth += correction

                    if (indexChar-1) == self.indexPair:
                        self._drawCursor(correction, pairKind)

                # # draw metrics info
                if self.isMetricsActive is True and self.isPreviewOn is False:
                    self._drawMetricsData(eachGlyphName, 52)

                if self.isSidebearingsActive is True and self.isPreviewOn is False:
                    self._drawBaseline(eachGlyphName)
                    self._drawSidebearings(eachGlyphName)

                dt.translate(eachGlyph.width, 0)
                glyphsToDisplayTotalWidth += eachGlyph.width
                prevGlyphName = eachGlyphName
            dt.restore()

            # foreground loop
            dt.save()
            prevGlyphName = None
            for indexChar, eachGlyphName in enumerate(glyphsToDisplay):
                eachGlyph = self.fontObj[eachGlyphName]

                # this is for kerning
                if indexChar > 0:
                    correction, kerningReference, pairKind = getCorrection((prevGlyphName, eachGlyphName), self.fontObj)

                    if correction and correction != 0 and self.isKerningDisplayActive:
                        dt.translate(correction, 0)

                self._drawGlyphOutlines(eachGlyphName)
                dt.translate(eachGlyph.width, 0)

                prevGlyphName = eachGlyphName
            dt.restore()

            # collisions loop
            if self.areCollisionsShown is True:
                dt.save()
                prevGlyphName = None
                for indexChar, eachGlyphName in enumerate(glyphsToDisplay):
                    eachGlyph = self.fontObj[eachGlyphName]

                    if indexChar > 0:
                        correction, kerningReference, pairKind = getCorrection((prevGlyphName, eachGlyphName), self.fontObj)

                        if correction and correction != 0 and self.isKerningDisplayActive:
                            dt.translate(correction, 0)

                        if (indexChar-1) == self.indexPair:
                            self._drawCollisions((prevGlyphName, eachGlyphName))

                    dt.translate(eachGlyph.width, 0)
                    prevGlyphName = eachGlyphName

                dt.restore()

            # main restore, it wraps the three loops
            dt.restore()

            if self.areVerticalLettersDrawn is True:
                # separate from the rest, we put the vertical letters
                dt.save()
                # we push the matrix forward
                dt.translate(self.ctrlWidth, 0)
                # then we rotate
                dt.rotate(90)
                # then we scale, but how much? a quarter of the main lettering
                dt.scale(self.ctrlHeight/(self.canvasScalingFactor*self.fontObj.info.unitsPerEm)*.25)
                # the reference is the baseline, so we have to put some air below the letters
                dt.translate(0, 600)   # upm value
                # let's define the graphics
                dt.fill(*BLACK)
                dt.stroke(None)
                # then we draw, we need a prevGlyphName in order to get kerning correction
                prevGlyphName = None
                # we iterate on the letters we need to draw + a space as a margin
                for indexChar, eachGlyphName in enumerate(['space']+glyphsToDisplay):
                    # accessing the glyph obj
                    eachGlyph = self.fontObj[eachGlyphName]
                    # if it isn't the first letter...
                    if indexChar > 0:
                        # ... we grab the kerning correction from the pair
                        correction, kerningReference, pairKind = getCorrection((prevGlyphName, eachGlyphName), self.fontObj)
                        # if there is any correction...
                        if correction and correction != 0 and self.isKerningDisplayActive:
                            # ... we apply it to the transformation matrix
                            dt.translate(correction, 0)
                    # then we draw the outlines
                    self._drawGlyphOutlines(eachGlyphName)
                    # and we move the transformation matrix according to glyph width
                    dt.translate(eachGlyph.width, 0)
                    # then we load the glyph to the prevGlyphName
                    prevGlyphName = eachGlyphName
                # restoring the vertical drawing
                dt.restore()

        except Exception:
            print(traceback.format_exc())
