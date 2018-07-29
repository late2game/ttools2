#!/usr/bin/env python
# coding: utf-8

###############
# Grid Fitter #
###############

### Modules
# custom
import ui.userInterfaceValues
reload(ui.userInterfaceValues)
from ui.userInterfaceValues import vanillaControlsSize

# standard
from mojo.roboFont import AllFonts, CurrentFont, version
from vanilla import FloatingWindow, PopUpButton, EditText, TextBox, Button

### Constants
FONT_TARGET_OPTIONS = ['All Fonts', 'Current Font']
FONT_TARGET_2_FUNC = {
    'All Fonts': AllFonts,
    'Current Font': CurrentFont}

GLYPH_TARGET_OPTIONS = ['All Glyphs', 'Selection', 'Current Glyph']

PLUGIN_TITLE = 'TT Grid Fitter'
PLUGIN_WIDTH = 230
MARGIN_HOR = 10
MARGIN_VER = 8
NET_WIDTH = PLUGIN_WIDTH - MARGIN_HOR*2

### Functions & Procedures
def gridFit(glyph, cellSide):
    # points
    for eachContour in glyph:
        for eachBcp in eachContour.bPoints:
            if eachBcp.anchor[0] % cellSide != 0 or eachBcp.anchor[1] % cellSide != 0:
                distance = -(eachBcp.anchor[0] % cellSide), -(eachBcp.anchor[1] % cellSide)
                if version[0] == '2':
                    eachBcp.moveBy(distance)
                else:
                    eachBcp.move(distance)

    # bPoints
    for eachContour in glyph:
        for eachBcp in eachContour.bPoints:
            if eachBcp.bcpIn[0] % cellSide != 0 or eachBcp.bcpIn[1] % cellSide != 0:
                eachBcp.bcpIn = eachBcp.bcpIn[0]-(eachBcp.bcpIn[0] % cellSide), eachBcp.bcpIn[1]-(eachBcp.bcpIn[1] % cellSide)

            if eachBcp.bcpOut[0] % cellSide != 0 or eachBcp.bcpOut[1] % cellSide != 0:
                eachBcp.bcpOut = eachBcp.bcpOut[0]-(eachBcp.bcpOut[0] % cellSide), eachBcp.bcpOut[1]-(eachBcp.bcpOut[1] % cellSide)
    if version[0] == '2':
        glyph.changed()
    else:
        glyph.update()


class GridFitter(object):

    def __init__(self):
        self.fontTarget = FONT_TARGET_OPTIONS[0]
        self.glyphTarget = GLYPH_TARGET_OPTIONS[0]
        self.gridSize = 4

        self.w = FloatingWindow((0, 0, PLUGIN_WIDTH, 400), PLUGIN_TITLE)
        jumpingY = MARGIN_VER

        # font target
        self.w.fontTargetPopUp = PopUpButton((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['PopUpButtonRegularHeight']),
                                             FONT_TARGET_OPTIONS,
                                             callback=self.fontTargetPopUpCallback)
        jumpingY += vanillaControlsSize['PopUpButtonRegularHeight'] + MARGIN_VER

        # glyph target
        self.w.glyphTargetPopUp = PopUpButton((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['PopUpButtonRegularHeight']),
                                              GLYPH_TARGET_OPTIONS,
                                              callback=self.glyphTargetPopUpCallback)
        jumpingY += vanillaControlsSize['PopUpButtonRegularHeight'] + MARGIN_VER

        # grid size captions
        self.w.gridSizeCaption = TextBox((MARGIN_HOR, jumpingY+2, NET_WIDTH*.32, vanillaControlsSize['TextBoxRegularHeight']),
                                         'Grid Size:')

        # grid size edit
        self.w.gridSizeEdit = EditText((MARGIN_HOR+NET_WIDTH*.32, jumpingY, NET_WIDTH*.3, vanillaControlsSize['EditTextRegularHeight']),
                                       text='%d' % self.gridSize,
                                       callback=self.gridSizeEditCallback)
        jumpingY += vanillaControlsSize['EditTextRegularHeight'] + MARGIN_VER

        # fit button
        self.w.fitButton = Button((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['ButtonRegularHeight']),
                                  'Fit!',
                                  callback=self.fitButtonCallback)
        jumpingY += vanillaControlsSize['ButtonRegularHeight'] + MARGIN_VER

        self.w.setPosSize((0, 0, PLUGIN_WIDTH, jumpingY))
        self.w.open()


    def fontTargetPopUpCallback(self, sender):
        self.fontTarget = FONT_TARGET_OPTIONS[sender.get()]

    def glyphTargetPopUpCallback(self, sender):
        self.glyphTarget = GLYPH_TARGET_OPTIONS[sender.get()]

    def gridSizeEditCallback(self, sender):
        try:
            self.gridSize = int(sender.get())
        except ValueError:
            self.w.gridSizeEdit.set('%d' % self.gridSize)

    def fitButtonCallback(self, sender):
        if self.fontTarget == 'All Fonts':
            fontsToProcess = AllFonts()
        else:
            fontsToProcess = [CurrentFont()]

        for eachFont in fontsToProcess:
            if self.glyphTarget == 'All Glyphs':
                glyphNamesToProcess = eachFont.glyphOrder
            elif self.glyphTarget == 'Selection':
                glyphNamesToProcess = CurrentFont().selection
            else:
                glyphNamesToProcess = [CurrentGlyph().name]

            for eachName in glyphNamesToProcess:
                eachGlyph = eachFont[eachName]
                gridFit(eachGlyph, self.gridSize)


if __name__ == '__main__':
    gf = GridFitter()