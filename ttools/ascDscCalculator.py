#!/usr/bin/env python
# coding: utf-8

#################################################
# Ascender / Descender family values calculator #
#################################################

### Modules
# custom
import ui.userInterfaceValues
reload(ui.userInterfaceValues)
from ui.userInterfaceValues import vanillaControlsSize

# standard
from mojo.roboFont import version, AllFonts
from vanilla import FloatingWindow, SquareButton
from vanilla import TextBox, HorizontalLine, CheckBox
from vanilla.dialogs import message
from defconAppKit.windows.baseWindow import BaseWindowController
from collections import namedtuple

### Constants
Extreme = namedtuple('Extreme', ['y', 'glyphName', 'styleName'])

PLUGIN_TITLE = 'TT Asc&Dsc Calculator'
PLUGIN_WIDTH = 300
PLUGIN_HEIGHT = 400

MARGIN_VER = 8
MARGIN_HOR = 8
MARGIN_ROW = 4
NET_WIDTH = PLUGIN_WIDTH - MARGIN_HOR*2

### Functions & Procedures
def findExtremes(aFont):
    aFamilyName = aFont.info.familyName
    aStyleName = aFont.info.styleName

    # init values
    fontLowerExtreme = Extreme(y=0, glyphName=None, styleName=None)
    fontHigherExtreme = Extreme(y=0, glyphName=None, styleName=None)
    # itearting over the glyphs
    for eachGlyph in aFont:
        if len(eachGlyph) > 0:
            if version[0] == '2':
                xMin, yMin, xMax, yMax = eachGlyph.bounds
            else:
                xMin, yMin, xMax, yMax = eachGlyph.box

                if yMin < fontLowerExtreme.y:
                    fontLowerExtreme = Extreme(y=yMin,
                                               glyphName=eachGlyph.name,
                                               styleName='{}'.format(aStyleName))
                if yMax > fontHigherExtreme.y:
                    fontHigherExtreme = Extreme(y=yMax,
                                               glyphName=eachGlyph.name,
                                               styleName='{}'.format(aStyleName))

    return fontLowerExtreme, fontHigherExtreme

def findFamilyExtremes(someFonts):

    # init values
    familyLowerExtreme = Extreme(y=0, glyphName=None, styleName=None)
    familyHigherExtreme = Extreme(y=0, glyphName=None, styleName=None)

    # iterating over the fonts
    for eachFont in someFonts:
        fontLowerExtreme, fontHigherExtreme = findExtremes(eachFont)

        if fontLowerExtreme.y < familyLowerExtreme.y:
            familyLowerExtreme = fontLowerExtreme
        if fontHigherExtreme.y > familyHigherExtreme.y:
            familyHigherExtreme = fontHigherExtreme

    return familyLowerExtreme, familyHigherExtreme


class AscenderDescenderCalculator(BaseWindowController):

    lowerExtreme = None
    higherExtreme = None

    is_hhea = False
    is_vhea = False
    is_osTwo = False
    is_usWin = False

    def __init__(self):
        self.w = FloatingWindow((0, 0, PLUGIN_WIDTH, PLUGIN_HEIGHT),
                                PLUGIN_TITLE)

        jumpingY = MARGIN_VER
        self.w.calcButton = SquareButton((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['ButtonRegularHeight']*1.5),
                                         'Measure Extremes',
                                         callback=self.calcButtonCallback)

        jumpingY += vanillaControlsSize['ButtonRegularHeight']*1.5+MARGIN_ROW
        self.w.topCaption = TextBox((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['TextBoxRegularHeight']),
                                    'Top: None')

        jumpingY += vanillaControlsSize['TextBoxRegularHeight']+MARGIN_ROW
        self.w.btmCaption = TextBox((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['TextBoxRegularHeight']),
                                    'Bottom: None')

        jumpingY += vanillaControlsSize['TextBoxRegularHeight']
        self.w.separationLine = HorizontalLine((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['TextBoxRegularHeight']))

        jumpingY += vanillaControlsSize['TextBoxRegularHeight']+MARGIN_ROW
        self.w.check_hhea = CheckBox((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['CheckBoxRegularHeight']),
                                     'hhea table',
                                     value=self.is_hhea,
                                     callback=self.check_hheaCallback)

        jumpingY += vanillaControlsSize['CheckBoxRegularHeight']+MARGIN_ROW
        self.w.check_vhea = CheckBox((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['CheckBoxRegularHeight']),
                                     'vhea table',
                                     value=self.is_vhea,
                                     callback=self.check_vheaCallback)

        jumpingY += vanillaControlsSize['CheckBoxRegularHeight']+MARGIN_ROW
        self.w.check_osTwo = CheckBox((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['CheckBoxRegularHeight']),
                                      'OS/2 table',
                                      value=self.is_osTwo,
                                      callback=self.check_osTwoCallback)

        jumpingY += vanillaControlsSize['CheckBoxRegularHeight']+MARGIN_ROW
        self.w.check_usWin = CheckBox((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['CheckBoxRegularHeight']),
                                      'usWin table',
                                      value=self.is_usWin,
                                      callback=self.check_usWinCallback)

        jumpingY += vanillaControlsSize['CheckBoxRegularHeight']+MARGIN_ROW
        self.w.writeButton = SquareButton((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['ButtonRegularHeight']*1.5),
                                          'Write values into fonts',
                                          callback=self.writeButtonCallback)

        jumpingY += vanillaControlsSize['ButtonRegularHeight']*1.5+MARGIN_VER*1.5
        self.w.resize(PLUGIN_WIDTH, jumpingY)
        self.w.open()

    def calcButtonCallback(self, sender):
        self.lowerExtreme, self.higherExtreme = findFamilyExtremes(AllFonts())
        self.updateCaptions()

    def updateCaptions(self):
        self.w.topCaption.set('Higher: {ex.y} ({ex.glyphName}, {ex.styleName})'.format(ex=self.higherExtreme))
        self.w.btmCaption.set('Lower: {ex.y} ({ex.glyphName}, {ex.styleName})'.format(ex=self.lowerExtreme))

    def check_hheaCallback(self, sender):
        self.is_hhea = bool(sender.get())

    def check_vheaCallback(self, sender):
        self.is_vhea = bool(sender.get())

    def check_osTwoCallback(self, sender):
        self.is_osTwo = bool(sender.get())

    def check_usWinCallback(self, sender):
        self.is_usWin = bool(sender.get())

    def writeButtonCallback(self, sender):

        if self.lowerExtreme is not None and self.higherExtreme is not None:

            for eachFont in AllFonts():
                if self.is_hhea is True:
                    eachFont.info.openTypeHheaAscender = self.higherExtreme.y
                    eachFont.info.openTypeHheaDescender = self.lowerExtreme.y

                if self.is_vhea is True:
                    eachFont.info.openTypeVheaVertTypoAscender = self.higherExtreme.y
                    eachFont.info.openTypeVheaVertTypoDescender = self.lowerExtreme.y

                if self.is_osTwo is True:
                    eachFont.info.openTypeOS2TypoAscender = self.higherExtreme.y
                    eachFont.info.openTypeOS2TypoDescender = self.lowerExtreme.y

                if self.is_usWin is True:
                    eachFont.info.openTypeOS2WinAscent = self.higherExtreme.y
                    eachFont.info.openTypeOS2WinDescent = self.lowerExtreme.y

        else:
            message('Calc Extremes first!')


### Instructions
adc = AscenderDescenderCalculator()
