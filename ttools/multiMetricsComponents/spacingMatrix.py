#!/usr/bin/env python
# coding: utf-8

"""here we draw and edit the metrics"""

### Modules
# custom
from ..ui import userInterfaceValues
reload(userInterfaceValues)
from ..ui.userInterfaceValues import vanillaControlsSize

# standard
import traceback
from AppKit import NSCenterTextAlignment
from vanilla import Group, EditText
import mojo.drawingTools as dt
from mojo.canvas import CanvasGroup

### Constants
SPACING_COL_WIDTH = 74
CAPTION_BODY_SIZE = 11
BASELINE_CORRECTION = 2

MARGIN_LFT = 15
MARGIN_HALFROW = 7

BLACK = (0, 0, 0)
GRAY = (0.4, 0.4, 0.4)
RED = (1,0,0)

if '.SFNSText' in dt.installedFonts():
    SYSTEM_FONT_NAME = '.SFNSText'
else:
    SYSTEM_FONT_NAME = '.HelveticaNeueDeskInterface-Regular'


### Factory
class SpacingMatrix(Group):

    lineViewSelectedGlyph = None
    activeGlyph = None
    activeSide = None
    activeElement = None

    def __init__(self, posSize, glyphNamesToDisplay, fontsOrder, callback):
        super(SpacingMatrix, self).__init__(posSize)
        self.glyphNamesToDisplay = glyphNamesToDisplay
        self.fontsOrder = fontsOrder
        self.callback = callback
        self.canvas = CanvasGroup((0,0,0,0), delegate=self)

    def setGlyphNamesToDisplay(self, glyphNamesToDisplay):
        self.glyphNamesToDisplay = glyphNamesToDisplay
        self.refreshActiveElements()

        if hasattr(self.canvas, 'activeEdit') is True:
            self.canvas.activeEdit.show(False)

    def setFontsOrder(self, fontsOrder):
        self.fontsOrder = fontsOrder

    def adjustSize(self, size):
        width, height = size
        x, y = self.getPosSize()[0:2]
        self.setPosSize((x, y, width, height))
        self.canvas.resize(width, height)
        self.update()

    def refreshActiveElements(self):
        self.activeGlyph = None
        self.activeSide = None
        self.activeElement = None
        self.update()

    def _killActiveEdit(self):
        if hasattr(self.canvas, 'activeEdit') is True:
            delattr(self.canvas, 'activeEdit')

    def mouseDown(self, notification):
        self._killActiveEdit()

        # origin is bottom left of the window, here we adjust the coordinates to the canvas
        pointerX, pointerY = notification.locationInWindow().x-MARGIN_LFT, notification.locationInWindow().y-MARGIN_HALFROW

        # translate abs coordinates to element indexes
        xRatio = pointerX/SPACING_COL_WIDTH
        indexGlyphName = int(xRatio)
        if indexGlyphName >= len(self.glyphNamesToDisplay):
            indexGlyphName = None
        # more on the left or more on the right?
        if round(xRatio % 1, 0) == 0:
            self.activeSide = 'lft'
        else:
            self.activeSide = 'rgt'

        if pointerY < len(self.fontsOrder)*vanillaControlsSize['EditTextSmallHeight']*2:
            yRatio = pointerY/(vanillaControlsSize['EditTextSmallHeight']*2)

            # it starts counting from the bottom, so I have to subtract the result from the length of the fonts order attribute
            indexFont = len(self.fontsOrder)-int(yRatio)

            # here I try to understand which ctrl has been clicked
            if round(yRatio % 1, 0) == 0:
                self.activeElement = 'margins'
            else:
                self.activeElement = 'width'
        else:
            indexFont = None

        # here I init a ctrl for changing metrics
        if indexGlyphName is None or indexFont is None:
            self.activeGlyph = None
            return None

        else:
            # this is the glyph which should be addressed by the active ctrl
            self.activeGlyph = self.fontsOrder[indexFont-1][self.glyphNamesToDisplay[indexGlyphName]]

            # how wide the ctrls? it depends
            if self.activeElement == 'margins':
                activeEditWidth = SPACING_COL_WIDTH/2.
            else:
                activeEditWidth = SPACING_COL_WIDTH

            # origin of vanilla ctrls is top left, but indexes are already ok for this, I guess
            if self.activeElement == 'margins' and self.activeSide == 'rgt':
                activeEditX = indexGlyphName*SPACING_COL_WIDTH+SPACING_COL_WIDTH/2.
            else:
                activeEditX = indexGlyphName*SPACING_COL_WIDTH

            if self.activeElement == 'margins':
                activeEditY = indexFont*vanillaControlsSize['EditTextSmallHeight']*2
            else:
                activeEditY = indexFont*vanillaControlsSize['EditTextSmallHeight']*2-vanillaControlsSize['EditTextSmallHeight']

            # here I choose the value to display in the ctrl
            if self.activeElement == 'width':
                activeValue = self.activeGlyph.width
            else:
                if self.activeSide == 'lft':
                    activeValue = self.activeGlyph.leftMargin
                else:
                    activeValue = self.activeGlyph.rightMargin

            self.canvas.activeEdit = CustomEditText((activeEditX, activeEditY, activeEditWidth, vanillaControlsSize['EditTextSmallHeight']),
                                                    sizeStyle='small',
                                                    continuous=False,
                                                    text='%d' % activeValue,
                                                    callback=self.activeEditCallback)
            self.canvas.activeEdit.centerAlignment()

    def activeEditCallback(self, sender):
        if self.activeGlyph and self.activeSide and self.activeElement:
            try:
                value = int(sender.get())

                if self.activeElement == 'width':
                    self.activeGlyph.width = value
                else:
                    if self.activeSide == 'lft':
                        self.activeGlyph.leftMargin = value
                    else:
                        self.activeGlyph.rightMargin = value

            except ValueError:
                self.canvas.activeEdit.set('')   # temp

        self._killActiveEdit()
        self.callback(self)
        self.update()

    def update(self):
        self.canvas.update()

    def draw(self):
        try:
            dt.save()
            dt.font(SYSTEM_FONT_NAME)
            dt.fontSize(CAPTION_BODY_SIZE)
            for indexGlyphName, eachGlyphName in enumerate(self.glyphNamesToDisplay):

                # in this way it does not draw what's outside the canvas frame!
                if SPACING_COL_WIDTH*indexGlyphName > self.getPosSize()[2]:
                    continue

                self._drawMatrixColumn(eachGlyphName)
                dt.translate(SPACING_COL_WIDTH, 0)

                self._setBoxQualities()
                dt.line((0, 0), (0, self.getPosSize()[3]))

            dt.restore()

        except Exception, error:
            print traceback.format_exc()

    def setLineViewSelectedGlyph(self, aGlyph):
        self.lineViewSelectedGlyph = aGlyph

    def _setTypeQualities(self, color):
        dt.fill(*color)
        dt.stroke(None)
        dt.fontSize(CAPTION_BODY_SIZE)
        dt.font(SYSTEM_FONT_NAME)

    def _setBoxQualities(self):
        dt.fill(None)
        dt.stroke(*GRAY)

    def _drawMatrixColumn(self, glyphName):
        dt.save()

        # definitive
        dt.translate(0, self.getPosSize()[3]-vanillaControlsSize['EditTextSmallHeight'])

        # top
        dt.fill(*BLACK)
        dt.stroke(None)

        textWidth, textHeight = dt.textSize(glyphName)
        self._setTypeQualities(BLACK)
        dt.text(glyphName, (SPACING_COL_WIDTH/2.-textWidth/2., BASELINE_CORRECTION))
        dt.translate(0, -vanillaControlsSize['EditTextSmallHeight'])

        # metrics
        for eachFont in self.fontsOrder:
            try:
                eachGlyph = eachFont[glyphName]
            except Exception, error:
                continue

            if eachGlyph == self.lineViewSelectedGlyph:
                color = RED
            else:
                color = BLACK

            # line over glyph width
            self._setBoxQualities()
            dt.line((0, vanillaControlsSize['EditTextSmallHeight']), (SPACING_COL_WIDTH, vanillaControlsSize['EditTextSmallHeight']))

            textWidth, textHeight = dt.textSize('%d' % eachGlyph.width)
            self._setTypeQualities(color)
            dt.text('%d' % eachGlyph.width, (SPACING_COL_WIDTH/2.-textWidth/2., BASELINE_CORRECTION))

            # line over sidebearings
            self._setBoxQualities()
            dt.line((0, 0), (SPACING_COL_WIDTH, 0))
            dt.translate(0, -vanillaControlsSize['EditTextSmallHeight'])

            textWidth, textHeight = dt.textSize('%d' % eachGlyph.leftMargin)
            self._setTypeQualities(color)
            dt.text('%d' % eachGlyph.leftMargin, (SPACING_COL_WIDTH/4.-textWidth/2., BASELINE_CORRECTION))

            self._setBoxQualities()
            dt.line((SPACING_COL_WIDTH/2., 0), (SPACING_COL_WIDTH/2., vanillaControlsSize['EditTextSmallHeight']))

            textWidth, textHeight = dt.textSize('%d' % eachGlyph.rightMargin)
            self._setTypeQualities(color)
            dt.text('%d' % eachGlyph.rightMargin, (SPACING_COL_WIDTH*3/4.-textWidth/2., BASELINE_CORRECTION))
            
            dt.translate(0, -vanillaControlsSize['EditTextSmallHeight'])

        dt.restore()


class CustomEditText(EditText):

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.nst = self.getNSTextField()

    def centerAlignment(self):
        self.nst.setAlignment_(NSCenterTextAlignment)
