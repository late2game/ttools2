#!/usr/bin/env python
# -*- coding: utf-8 -*-

# custom modules
import kerningMisc
reload(kerningMisc)
import exceptionTools
reload(exceptionTools)

from kerningMisc import whichGroup, getCorrection, buildPairsFromString
from kerningMisc import checkIfPairOverlaps
from kerningMisc import CANVAS_SCALING_FACTOR_INIT
from ..userInterfaceValues import vanillaControlsSize
from exceptionTools import checkPairConflicts, isPairException, calcWiggle

# standard modules
import traceback
from defconAppKit.tools.textSplitter import splitText
import mojo.drawingTools as dt
from vanilla import Group
from mojo.canvas import CanvasGroup
from collections import namedtuple

# costants
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
SYMMETRICAL_BACKGROUND_COLOR = (1, 0, 1, .15)

BLACK = (0, 0, 0)
WHITE = (1,1,1)
LIGHT_RED = (1, 0, 0, .4)
LIGHT_GREEN = (0, 1, 0, .4)
LIGHT_BLUE = (0, 0, 1, .4)
LIGHT_GRAY = (0, 0, 0, .4)

# object
class WordDisplay(Group):

    def __init__(self, posSize, displayedWord, canvasScalingFactor, fontObj, isKerningDisplayActive, areGroupsShown, areCollisionsShown, isSidebearingsActive, isMetricsActive, isColorsActive, isPreviewOn, isSymmetricalEditingOn, indexPair):
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
        self.areGroupsShown = areGroupsShown
        self.areCollisionsShown = areCollisionsShown
        self.isSidebearingsActive = isSidebearingsActive
        self.isMetricsActive = isMetricsActive
        self.isColorsActive = isColorsActive
        self.isPreviewOn = isPreviewOn
        self.isSymmetricalEditingOn = isSymmetricalEditingOn

        self.ctrlWidth, self.ctrlHeight = posSize[2], posSize[3]

        self.checkPairsQuality()
        self.wordCanvasGroup = CanvasGroup((0, 0, 0, 0),
                                           delegate=self)

    def checkPairsQuality(self):
        for eachPair in self.displayedPairs:
            status, pairsDB = checkPairConflicts(eachPair, self.fontObj)
            if status is False:
                print 'conflicting pairs'
                print 'please check the DB:', pairsDB

    def getActivePair(self):
        return self.activePair

    def setSymmetricalEditingMode(self, value):
        self.isSymmetricalEditingOn = value

    def setPreviewMode(self, value):
        self.isPreviewOn = value

    def setGraphicsBooleans(self, isKerningDisplayActive, areGroupsShown, areCollisionsShown, isSidebearingsActive, isMetricsActive, isColorsActive):
        self.isKerningDisplayActive = isKerningDisplayActive
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
        self.displayedWord = displayedWord
        self.displayedPairs = buildPairsFromString(self.displayedWord, self.fontObj)
        self.checkPairsQuality()

    def setScalingFactor(self, scalingFactor):
        self.canvasScalingFactor = scalingFactor

    def setActivePairIndex(self, indexPair):
        self.indexPair = indexPair
        if self.indexPair is not None:
            self.activePair = self.displayedPairs[self.indexPair]
        else:
            self.activePair = None

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
        dt.scale(1/(self.getPosSize()[3]/(self.canvasScalingFactor*self.fontObj.info.unitsPerEm)))
        dt.font(SYSTEM_FONT_NAME)
        dt.fontSize(BODY_SIZE)
        textWidth, textHeight = dt.textSize('%s' % correction)
        dt.textBox('%s' % correction, (-textWidth/2., -textHeight/2., textWidth, textHeight), align='center')

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
        reverseScalingFactor = 1/(self.getPosSize()[3]/(self.canvasScalingFactor*self.fontObj.info.unitsPerEm))

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

        textWidth, textHeight = dt.textSize(u'%s' % glyphToDisplay.width)
        dt.textBox(u'%d' % glyphToDisplay.width, (0, 0, glyphToDisplay.width, textHeight*2), align='center')
        dt.textBox(u'\n%d' % glyphToDisplay.leftMargin, (0, 0, glyphToDisplay.width/2., textHeight*2), align='center')
        dt.textBox(u'\n%d' % glyphToDisplay.rightMargin, (glyphToDisplay.width/2., 0, glyphToDisplay.width/2., textHeight*2), align='center')
        dt.restore()

    def _drawBaseline(self, glyphName):
        glyphToDisplay = self.fontObj[glyphName]

        dt.save()
        dt.stroke(*BLACK)
        dt.fill(None)
        # reversed scaling factor
        dt.strokeWidth(1/(self.getPosSize()[3]/(self.canvasScalingFactor*self.fontObj.info.unitsPerEm)))
        dt.line((0, 0), (glyphToDisplay.width, 0))
        dt.restore()

    def _drawSidebearings(self, glyphName):
        glyphToDisplay = self.fontObj[glyphName]

        dt.save()
        dt.stroke(*BLACK)
        dt.fill(None)

        # reversed scaling factor
        dt.strokeWidth(1/(self.getPosSize()[3]/(self.canvasScalingFactor*self.fontObj.info.unitsPerEm)))

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
            lftReference = whichGroup(prevGlyphName, 'lft', self.fontObj)
            rgtReference = whichGroup(eachGlyphName, 'rgt', self.fontObj)

        prevGlyph, eachGlyph = self.fontObj[prevGlyphName], self.fontObj[eachGlyphName]
        reverseScalingFactor = 1/(self.getPosSize()[3]/(self.canvasScalingFactor*self.fontObj.info.unitsPerEm))

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
            dt.save()

            # this is for safety reason, user should be notified about possible unwanted kerning corrections
            if self.isSymmetricalEditingOn is True:
                dt.save()
                dt.fill(*SYMMETRICAL_BACKGROUND_COLOR)
                dt.rect(0, 0, self.getPosSize()[2], self.getPosSize()[3])
                dt.restore()

            dt.scale(self.getPosSize()[3]/(self.canvasScalingFactor*self.fontObj.info.unitsPerEm))   # the canvas is virtually scaled according to self.canvasScalingFactor value and canvasSize
            dt.translate(TEXT_MARGIN, 0)

            # group glyphs
            dt.translate(0, 600)

            if self.areGroupsShown is True:
                dt.save()
                prevGlyphName = None
                glyphsToDisplay = splitText(self.displayedWord, self.fontObj.naked().unicodeData)
                for indexChar, eachGlyphName in enumerate(glyphsToDisplay):
                    eachGlyph = self.fontObj[eachGlyphName]

                    # this is for kerning
                    if indexChar > 0:
                        correction, kerningReference, pairKind = getCorrection((prevGlyphName, eachGlyphName), self.fontObj)

                        if kerningReference:
                            exceptionStatus, doesExists, exceptionParents = isPairException(kerningReference, self.fontObj)
                            if exceptionStatus is True and self.isPreviewOn is False:
                                self._drawException((prevGlyphName, eachGlyphName), correction)

                        if (indexChar-1) == self.indexPair and self.isPreviewOn is False:
                            self._drawGlyphOutlinesFromGroups((prevGlyphName, eachGlyphName), kerningReference, correction)

                        if correction and correction != 0:
                            dt.translate(correction, 0)

                    dt.translate(eachGlyph.width, 0)
                    prevGlyphName = eachGlyphName
                dt.restore()

            # background loop
            dt.save()
            prevGlyphName = None
            glyphsToDisplay = splitText(self.displayedWord, self.fontObj.naked().unicodeData)
            for indexChar, eachGlyphName in enumerate(glyphsToDisplay):
                eachGlyph = self.fontObj[eachGlyphName]

                # this is for kerning
                if indexChar > 0:
                    correction, kerningReference, pairKind = getCorrection((prevGlyphName, eachGlyphName), self.fontObj)
                    if correction and correction != 0:
                        if self.isColorsActive is True and self.isPreviewOn is False:
                            self._drawColoredCorrection(correction)
                        if self.isMetricsActive is True and self.isPreviewOn is False:
                            self._drawMetricsCorrection(correction)
                        dt.translate(correction, 0)

                    if (indexChar-1) == self.indexPair:
                        self._drawCursor(correction, pairKind)

                # # draw metrics info
                if self.isMetricsActive is True and self.isPreviewOn is False:
                    self._drawMetricsData(eachGlyphName, 52)

                if self.isSidebearingsActive is True and self.isPreviewOn is False:
                    self._drawBaseline(eachGlyphName)
                    self._drawSidebearings(eachGlyphName)

                dt.translate(eachGlyph.width, 0)
                prevGlyphName = eachGlyphName
            dt.restore()

            # foreground loop
            dt.save()
            prevGlyphName = None
            glyphsToDisplay = splitText(self.displayedWord, self.fontObj.naked().unicodeData)
            for indexChar, eachGlyphName in enumerate(glyphsToDisplay):
                eachGlyph = self.fontObj[eachGlyphName]

                # this is for kerning
                if indexChar > 0:
                    correction, kerningReference, pairKind = getCorrection((prevGlyphName, eachGlyphName), self.fontObj)

                    if correction and correction != 0:
                        dt.translate(correction, 0)

                    if (indexChar-1) == self.indexPair and self.areCollisionsShown is True:
                        self._drawCollisions((prevGlyphName, eachGlyphName))

                self._drawGlyphOutlines(eachGlyphName)
                dt.translate(eachGlyph.width, 0)

                prevGlyphName = eachGlyphName
            dt.restore()

            # main restore, it wraps the three loops
            dt.restore()

        except Exception:
            print traceback.format_exc()
