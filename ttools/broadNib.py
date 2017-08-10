#!/usr/bin/env python
# coding: utf-8

#############
# Broad Nib #
#############

### Modules
# custom
import miscFunctions
reload(miscFunctions)
from miscFunctions import collectIDsFromSelectedPoints

import calcFunctions
reload(calcFunctions)
from calcFunctions import interpolateValue, calcDistance

import bezierTools
reload(bezierTools)
from bezierTools import calcPointOnBezier, collectsPointsOnBezierCurve
from bezierTools import collectsPointsOnBezierCurveWithFixedDistance


# standard
import sys
import math
import traceback
from fontTools.misc.transform import Identity
from AppKit import NSColor, NSFont, NSFontAttributeName
from AppKit import NSForegroundColorAttributeName
from vanilla import FloatingWindow, CheckBox, TextBox
from vanilla import EditText, SquareButton, RadioGroup
from robofab.pens.filterPen import thresholdGlyph, flattenGlyph
from mojo.events import addObserver, removeObserver
from mojo.UI import UpdateCurrentGlyphView
from mojo.roboFont import CurrentGlyph, RGlyph
from lib.eventTools.eventManager import getActiveEventTool
from lib.tools.defaults import getDefault
from mojo.drawingTools import *

### Constants
SHAPE_OPTIONS = ['Rect', 'Oval']
MASTER_COLOR = (45/255., 90/255., 150/255.)
SUB_COLOR = (180/255., 240/255., 170/255.)
BLACK_COLOR = (0,0,0)

# glyph lib key
PLUGIN_KEY = 'broadNib'
bodySizeCaption = 9

# component heights
CheckBoxHeight = 18
TextBoxHeight = 14
EditTextHeight = 19
SquareButtonHeight = 19

# colors
LIGHT_YELLOW = getDefault('glyphViewPreviewBackgroundColor')


### Extra functions
def robofabRect(glyph, x, y, width, height):
    """custom rect routine robofab-flavour code, this is used for expansion"""
    x1, y1 = x, y-height/2.
    x2, y2 = x+width/2., y
    x3, y3 = x, y+height/2.
    x4, y4 = x-width/2., y

    pen = glyph.getPen()
    pen.moveTo((x1, y1))
    pen.lineTo((x2, y2))
    pen.lineTo((x3, y3))
    pen.lineTo((x4, y4))
    pen.lineTo((x1, y1))
    pen.closePath()

def robofabOval(glyph, x, y, width, height):
    """custom oval routine robofab-flavour code, this is used for expansion"""

    sqr = .62
    x1, y1 = x, y-height/2.
    x2, y2 = x+width/2., y
    x3, y3 = x, y+height/2.
    x4, y4 = x-width/2., y

    bcpVer = sqr*height/2.
    bcpHor = sqr*width/2.

    pen = glyph.getPen()
    pen.moveTo((x1, y1))
    pen.curveTo((x1+bcpHor, y1), (x2, y2-bcpVer), (x2, y2))
    pen.curveTo((x2, y2+bcpVer), (x3+bcpHor, y3), (x3, y3))
    pen.curveTo((x3-bcpHor, y3), (x4, y4+bcpVer), (x4, y4))
    pen.curveTo((x4, y4-bcpVer), (x1-bcpHor, y1), (x1, y1))
    pen.closePath()


### Plugin
class BroadNib(object):

    preview = False
    drawValues = False
    elementShape = SHAPE_OPTIONS[0]

    pluginWidth = 120
    pluginHeight = 300

    marginTop = 10
    marginRgt = 10
    marginBtm = 10
    marginLft = 10
    marginRow = 8

    netWidth = pluginWidth - marginLft - marginRgt

    def __init__(self):

        # init window
        self.win = FloatingWindow((self.pluginWidth, self.pluginHeight), "Broad Nib")

        # checkBox preview
        jumpingY = self.marginTop
        self.win.preview = CheckBox((self.marginLft, jumpingY, self.netWidth, CheckBoxHeight),
                                    "Preview",
                                    value=self.preview,
                                    sizeStyle='small',
                                    callback=self.previewCallback)

        jumpingY += CheckBoxHeight
        self.win.shapeRadio = RadioGroup((self.marginLft+10, jumpingY, self.netWidth, 32),
                                         SHAPE_OPTIONS,
                                         sizeStyle='small',
                                         callback=self.shapeRadioCallback)
        self.win.shapeRadio.enable(False)
        self.win.shapeRadio.set(0)

        # checkBox draw values
        jumpingY += self.marginRow + self.win.shapeRadio.getPosSize()[3] - 3
        self.win.drawValues = CheckBox((self.marginLft, jumpingY, self.netWidth, CheckBoxHeight),
                                       "Draw Values",
                                       value=self.drawValues,
                                       sizeStyle='small',
                                       callback=self.drawValuesCallback)

        # oval width
        jumpingY += self.marginRow + CheckBoxHeight
        self.win.widthCaption = TextBox((self.marginLft, jumpingY+3, self.netWidth*.5, TextBoxHeight),
                                        "Width:",
                                        sizeStyle='small')

        self.win.widthEdit = EditText((self.marginLft+self.netWidth*.5, jumpingY, self.netWidth*.4, EditTextHeight),
                                      sizeStyle='small',
                                      callback=self.widthEditCallback)

        # oval height
        jumpingY += self.marginRow + EditTextHeight
        self.win.heightCaption = TextBox((self.marginLft, jumpingY+3, self.netWidth*.5, TextBoxHeight),
                                         "Height:",
                                         sizeStyle='small')

        self.win.heightEdit = EditText((self.marginLft+self.netWidth*.5, jumpingY, self.netWidth*.4, EditTextHeight),
                                       sizeStyle='small',
                                       callback=self.heightEditCallback)

        # oval angle
        jumpingY += self.marginRow + EditTextHeight
        self.win.angleCaption = TextBox((self.marginLft, jumpingY+3, self.netWidth*.5, TextBoxHeight),
                                        "Angle:",
                                        sizeStyle='small')

        self.win.angleEdit = EditText((self.marginLft+self.netWidth*.5, jumpingY, self.netWidth*.4, EditTextHeight),
                                      sizeStyle='small',
                                      callback=self.angleEditCallback)

        # add
        jumpingY += self.marginRow + EditTextHeight
        self.win.addToLib = SquareButton((self.marginLft, jumpingY, self.netWidth, SquareButtonHeight),
                                         "Add to lib",
                                         sizeStyle='small',
                                         callback=self.addToLibCallback)

        # clear
        jumpingY += self.marginRow + EditTextHeight
        self.win.clearLib = SquareButton((self.marginLft, jumpingY, self.netWidth, SquareButtonHeight),
                                         "Clear lib",
                                         sizeStyle='small',
                                         callback=self.clearLibCallback)

        jumpingY += self.marginRow + EditTextHeight
        self.win.expandToForeground = SquareButton((self.marginLft, jumpingY, self.netWidth, SquareButtonHeight),
                                      "Expand",
                                      sizeStyle='small',
                                      callback=self.expandToForegroundCallback)

        # managing observers
        addObserver(self, "_drawBackground", "drawBackground")
        addObserver(self, "_drawBackground", "drawInactive")
        addObserver(self, "_drawBlack", "drawPreview")
        self.win.bind("close", self.closing)

        # adjust window
        jumpingY += self.marginRow + EditTextHeight
        self.win.setPosSize((200, 200, self.pluginWidth, jumpingY))

        # opening window
        self.win.open()

    def previewCallback(self, sender):
        self.preview = bool(sender.get())
        self.win.shapeRadio.enable(self.preview)
        UpdateCurrentGlyphView()

    def shapeRadioCallback(self, sender):
        self.elementShape = SHAPE_OPTIONS[sender.get()]
        UpdateCurrentGlyphView()

    def drawValuesCallback(self, sender):
        self.drawValues = bool(sender.get())
        UpdateCurrentGlyphView()

    def widthEditCallback(self, sender):
        try:
            self.nibWidth = int(sender.get())
        except ValueError:
            print traceback.format_exc()
            self.nibWidth = None
            self.win.widthEdit.set('')

    def heightEditCallback(self, sender):
        try:
            self.nibHeight = int(sender.get())
        except ValueError:
            print traceback.format_exc()
            self.nibHeight = None
            self.win.heightEdit.set('')

    def angleEditCallback(self, sender):
        try:
            self.nibAngle = int(sender.get())
        except ValueError:
            print traceback.format_exc()
            self.nibAngle = None
            self.win.angleEdit.set('')

    def addToLibCallback(self, sender):
        assert self.nibWidth is not None, 'nibWidth is None'
        assert self.nibHeight is not None, 'nibHeight is None'
        assert self.nibAngle is not None, 'nibAngle is None'

        if PLUGIN_KEY not in CurrentGlyph().lib:
            CurrentGlyph().lib[PLUGIN_KEY] = {}

        selectedIDs = collectIDsFromSelectedPoints(CurrentGlyph())
        for eachSelectedID in selectedIDs:
            CurrentGlyph().lib[PLUGIN_KEY][eachSelectedID] = {'width': self.nibWidth,
                                                              'height': self.nibHeight,
                                                              'angle': self.nibAngle}
        CurrentGlyph().update()
        UpdateCurrentGlyphView()

    def clearLibCallback(self, sender):
        if PLUGIN_KEY in CurrentGlyph().lib:
            del CurrentGlyph().lib[PLUGIN_KEY]
        CurrentGlyph().update()
        UpdateCurrentGlyphView()

    def expandToForegroundCallback(self, sender):
        self._drawElements(CurrentGlyph(), None, 2, 'foreground')

    def loadDataFromLib(self, glyph, ID):
        nibData = glyph.lib[PLUGIN_KEY][ID]
        self.win.widthEdit.set('%s' % nibData['width'])
        self.win.heightEdit.set('%s' % nibData['height'])
        self.win.angleEdit.set('%s' % nibData['angle'])
        self.nibWidth = nibData['width']
        self.nibHeight = nibData['height']
        self.nibAngle = nibData['angle']

    def _drawBackground(self, infoDict):
        assert self.elementShape in SHAPE_OPTIONS

        glyph = infoDict['glyph']
        currentTool = getActiveEventTool()
        view = currentTool.getNSView()
        textAttributes = {NSFontAttributeName: NSFont.systemFontOfSize_(bodySizeCaption),
                          NSForegroundColorAttributeName: NSColor.blackColor()}

        # load data if point is selected
        if PLUGIN_KEY in glyph.lib:
            for eachContour in glyph:
                for eachPt in eachContour.points:
                    if eachPt.selected is True and eachPt.type != 'offCurve' and eachPt.naked().uniqueID in glyph.lib[PLUGIN_KEY]:
                        self.loadDataFromLib(glyph, eachPt.naked().uniqueID)

        # draw interpolateValued ovals
        if self.preview is True and PLUGIN_KEY in glyph.lib:
            self._drawElements(glyph, SUB_COLOR, 4, 'canvas')

        # draw master ovals
        if self.preview is True and PLUGIN_KEY in glyph.lib:
            for eachContour in glyph:
                for eachSegment in eachContour:
                    ID = eachSegment.onCurve.naked().uniqueID
                    if ID in glyph.lib[PLUGIN_KEY]:
                        elementDict = glyph.lib[PLUGIN_KEY][ID]
                        save()
                        fill(*MASTER_COLOR)
                        translate(eachSegment.onCurve.x,
                                  eachSegment.onCurve.y)
                        rotate(elementDict['angle'])

                        if self.elementShape == 'Oval':
                            oval(-elementDict['width']/2., -elementDict['height']/2., elementDict['width'], elementDict['height'])
                        else:
                            rect(-elementDict['width']/2., -elementDict['height']/2., elementDict['width'], elementDict['height'])
                        restore()

        # draw values
        if self.drawValues is True and PLUGIN_KEY in glyph.lib:
            for eachContour in glyph:
                for eachSegment in eachContour:
                    ID = eachSegment.onCurve.naked().uniqueID
                    if ID in glyph.lib[PLUGIN_KEY]:
                        nibData = glyph.lib[PLUGIN_KEY][ID]
                        values = '%s: %s\n%s: %s\n%s: %s' % ('width', nibData['width'], 'height', nibData['height'], 'angle', nibData['angle'])
                        view._drawTextAtPoint(values,
                                              textAttributes,
                                              (eachSegment.onCurve.x, eachSegment.onCurve.y),
                                              yOffset=2.8*bodySizeCaption)

    def _drawBlack(self, infoDict):
        glyph = infoDict['glyph']
        if self.preview is True and PLUGIN_KEY in glyph.lib:
            # background
            fill(*LIGHT_YELLOW)
            rect(-1000, -1000, 2000, 2000)

            # calligraphy
            self._drawElements(glyph, BLACK_COLOR, 4, 'canvas')

    def _drawElements(self, glyph, color, distance, mode):
        assert mode == 'canvas' or mode == 'foreground'
        assert self.elementShape in SHAPE_OPTIONS

        if mode == 'foreground':
            phantomGlyph = RGlyph()

        for eachContour in glyph:
            for indexSegment, eachSegment in enumerate(eachContour):
                if indexSegment != len(eachContour)-1:
                    nextSegment = eachContour[indexSegment+1]
                else:
                    if eachContour.open is True:
                        continue
                    else:
                        nextSegment = eachContour[0]

                pt1 = eachSegment.onCurve.x, eachSegment.onCurve.y
                pt4 = nextSegment.onCurve.x, nextSegment.onCurve.y

                if nextSegment.offCurve:
                    pt2 = nextSegment.offCurve[0].x, nextSegment.offCurve[0].y
                    pt3 = nextSegment.offCurve[1].x, nextSegment.offCurve[1].y
                else:
                    pt2 = pt1
                    pt3 = pt4
                pt1 = eachSegment.onCurve.x, eachSegment.onCurve.y
                pt4 = nextSegment.onCurve.x, nextSegment.onCurve.y

                if eachSegment.onCurve.naked().uniqueID in glyph.lib[PLUGIN_KEY] and \
                   nextSegment.onCurve.naked().uniqueID in glyph.lib[PLUGIN_KEY]:
                    startLib = glyph.lib[PLUGIN_KEY][eachSegment.onCurve.naked().uniqueID]
                    endLib = glyph.lib[PLUGIN_KEY][nextSegment.onCurve.naked().uniqueID]

                    bezPoints = collectsPointsOnBezierCurveWithFixedDistance(pt1, pt2, pt3, pt4, distance)
                    for indexBezPt, eachBezPt in enumerate(bezPoints):
                        factor = indexBezPt/float(len(bezPoints))
                        width = interpolateValue(startLib['width'], endLib['width'], factor)
                        height = interpolateValue(startLib['height'], endLib['height'], factor)
                        angle = interpolateValue(startLib['angle'], endLib['angle'], factor)

                        if mode == 'canvas':
                            save()
                            fill(*color)
                            translate(eachBezPt[0][0], eachBezPt[0][1])
                            rotate(angle)
                            
                            if self.elementShape == 'Oval':
                                oval(-width/2., -height/2., width, height)
                            else:
                                rect(-width/2., -height/2., width, height)
                            restore()

                        else:
                            matrix = Identity
                            matrix = matrix.translate(eachBezPt[0][0], eachBezPt[0][1])
                            matrix = matrix.rotate(math.radians(angle))

                            if self.elementShape == 'Oval':
                                robofabOval(phantomGlyph, 0, 0, width, height)
                            else:
                                robofabRect(phantomGlyph, 0, 0, width, height)
                            phantomGlyph[len(phantomGlyph)-1].transform(matrix)

        if mode == 'foreground':
            phantomGlyph.removeOverlap()
            flattenGlyph(phantomGlyph, 20)
            thresholdGlyph(phantomGlyph, 5)
            glyph.getLayer('foreground', clear=True).appendGlyph(phantomGlyph, (0, 0))


    def closing(self, sender):
        removeObserver(self, "drawBackground")
        removeObserver(self, "drawInactive")
        removeObserver(self, "drawPreview")

### Instructions
if __name__ == '__main__':
    bn = BroadNib()
