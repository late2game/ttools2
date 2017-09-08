#!/usr/bin/env python
# coding: utf-8

################################
# TTools for fraction building #
################################

### Modules
# custom
import userInterfaceValues
reload(userInterfaceValues)
from userInterfaceValues import vanillaControlsSize

# standard
import types
from mojo.roboFont import AllFonts, CurrentFont
from vanilla import FloatingWindow, PopUpButton, TextBox, EditText, Button

### Constants
LC_LIGATURES = [(('f', 'j'), "f_j"),
                (('f', 'b'), "f_b"),
                (('f', 'h'), "f_h"),
                (('f', 'k'), "f_k"),
                (('f', 't'), "f_t"),
                (('t', 't'), "t_t"),
                (('t', 'f'), "t_f"),
                (('f', 'f', 'i'), "uniFB03"),
                (('f', 'f', 'j'), "f_f_j"),
                (('f', 'f', 'l'), "uniFB04"),
                (('f', 'f', 'b'), "f_f_b"),
                (('f', 'f', 'h'), "f_f_h"),
                (('f', 'f', 'k'), "f_f_k"),
                (('f', 'f', 't'), "f_f_t")]

FRACTIONS = [(("zero.numr", "fraction", "zero.dnom"), "percent"),
             (("zero.numr", "fraction", "zero.dnom", "zero.dnom"), "perthousand"),
             (("one.numr", "fraction", "two.dnom"), "onehalf"),
             (("one.numr", "fraction", "three.dnom"), "onethird"),
             (("two.numr", "fraction", "three.dnom"), "twothirds"),
             (("one.numr", "fraction", "four.dnom"), "onequarter"),
             (("three.numr", "fraction", "four.dnom"), "threequarters"),
             (("one.numr", "fraction", "five.dnom"), "uni2155"),
             (("two.numr", "fraction", "five.dnom"), "uni2156"),
             (("three.numr", "fraction", "five.dnom"), "uni2157"),
             (("four.numr", "fraction", "five.dnom"), "uni2158"),
             (("one.numr", "fraction", "six.dnom"), "uni2159"),
             (("five.numr", "fraction", "six.dnom"), "uni215A"),
             (("one.numr", "fraction", "eight.dnom"), "oneeighth"),
             (("three.numr", "fraction", "eight.dnom"), "threeeighths"),
             (("five.numr", "fraction", "eight.dnom"), "fiveeighths"),
             (("seven.numr", "fraction", "eight.dnom"), "seveneighths")]

MATH_CASE = [("plus", "plus.case"),
            ("minus", "minus.case"),
            ("multiply", "multiply.case"),
            ("divide", "divide.case"),
            ("equal", "equal.case"),
            ("less", "less.case"),
            ("greater", "greater.case"),
            ("plusminus", "plusminus.case"),
            ("lessequal", "lessequal.case"),
            ("greaterequal", "greaterequal.case"),
            ("notequal", "notequal.case"),
            ("logicalnot", "logicalnot.case"),
            ("asciitilde", "asciitilde.case"),
            ("approxequal", "approxequal.case"),
            ("numbersign", "numbersign.case"),
            ("infinity", "infinity.case")]

MATH_SC = [("plus", "plus.sc"),
           ("minus", "minus.sc"),
           ("multiply", "multiply.sc"),
           ("divide", "divide.sc"),
           ("equal", "equal.sc"),
           ("less", "less.sc"),
           ("greater", "greater.sc"),
           ("plusminus", "plusminus.sc"),
           ("lessequal", "lessequal.sc"),
           ("greaterequal", "greaterequal.sc"),
           ("notequal", "notequal.sc"),
           ("logicalnot", "logicalnot.sc"),
           ("asciitilde", "asciitilde.sc"),
           ("approxequal", "approxequal.sc"),
           ("numbersign", "numbersign.sc"),
           ("infinity", "infinity.sc")]


GLYPHLISTS_OPTIONS = ('LC ligatures', 'Fractions', 'Math Case', 'Math SC')
NAME_2_GLYPHLIST = {
    'LC ligatures': LC_LIGATURES,
    'Fractions': FRACTIONS,
    'Math Case': MATH_CASE,
    'Math SC': MATH_SC}

TARGET_OPTIONS = ['All Fonts', 'Current Font']

PLUGIN_TITLE = 'TT Copy and move'
PLUGIN_WIDTH = 230
MARGIN_HOR = 10
MARGIN_VER = 8
NET_WIDTH = PLUGIN_WIDTH - MARGIN_HOR*2

### Classes
class FractionMaker(object):

    isOffsetAllowed = False
    verticalOffset = 0

    def __init__(self):
        self.transferList = NAME_2_GLYPHLIST[GLYPHLISTS_OPTIONS[0]]
        self.target = TARGET_OPTIONS[0]

        self.w = FloatingWindow((0, 0, PLUGIN_WIDTH, 400), PLUGIN_TITLE)
        jumpingY = MARGIN_VER

        # target fonts
        self.w.targetFontsPopUp = PopUpButton((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['PopUpButtonRegularHeight']),
                                        TARGET_OPTIONS,
                                        callback=self.targetFontsPopUpCallback)
        jumpingY += vanillaControlsSize['PopUpButtonRegularHeight']+MARGIN_VER

        # transfer lists pop up
        self.w.glyphListPopUp = PopUpButton((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['PopUpButtonRegularHeight']),
                                            GLYPHLISTS_OPTIONS,
                                            callback=self.glyphListPopUpCallback)
        jumpingY += vanillaControlsSize['PopUpButtonRegularHeight']+MARGIN_VER

        # offset caption
        self.w.offsetCaption = TextBox((MARGIN_HOR, jumpingY+2, NET_WIDTH*.22, vanillaControlsSize['TextBoxRegularHeight']),
                                       'Offset:')

        # offset edit text
        self.w.offsetEdit = EditText((MARGIN_HOR+NET_WIDTH*.25, jumpingY, NET_WIDTH*.35, vanillaControlsSize['EditTextRegularHeight']),
                                     callback=self.offsetEditCallback)
        self.w.offsetEdit.set('%d' % self.verticalOffset)
        self.w.offsetEdit.enable(False)
        jumpingY += vanillaControlsSize['EditTextRegularHeight']+MARGIN_VER

        # clean button
        self.w.cleanButton = Button((MARGIN_HOR, jumpingY, NET_WIDTH*.45, vanillaControlsSize['ButtonRegularHeight']),
                                    'Clean',
                                    callback=self.cleanButtonCallback)

        # run button
        self.w.runButton = Button((MARGIN_HOR+NET_WIDTH*.55, jumpingY, NET_WIDTH*.45, vanillaControlsSize['ButtonRegularHeight']),
                                  'Run!',
                                  callback=self.runButtonCallback)
        jumpingY += vanillaControlsSize['ButtonRegularHeight']+MARGIN_VER

        self.w.setPosSize((0, 0, PLUGIN_WIDTH, jumpingY))
        self.w.open()


    def targetFontsPopUpCallback(self, sender):
        self.target = TARGET_OPTIONS[sender.get()]

    def glyphListPopUpCallback(self, sender):
        if GLYPHLISTS_OPTIONS[sender.get()].startswith('Math'):
            self.w.offsetEdit.enable(True)
        else:
            self.w.offsetEdit.enable(False)

        self.transferList = NAME_2_GLYPHLIST[GLYPHLISTS_OPTIONS[sender.get()]]
        self.isOffsetAllowed = False

    def offsetEditCallback(self, sender):
        try:
            self.verticalOffset = int(sender.get())
        except ValueError:
            self.w.offsetEdit.set('%d' % self.verticalOffset)

    def cleanButtonCallback(self, sender):
        if self.target == 'All Fonts':
            fontsToProcess = AllFonts()
        else:
            fontsToProcess = [CurrentFont()]

        for eachFont in fontsToProcess:
            for _, eachTarget in self.transferList:
                eachFont[eachTarget].clear()

    def runButtonCallback(self, sender):
        if self.target == 'All Fonts':
            fontsToProcess = AllFonts()
        else:
            fontsToProcess = [CurrentFont()]

        for eachFont in fontsToProcess:
            for eachSource, eachTarget in self.transferList:
                if eachTarget not in eachFont:
                    targetGlyph = eachFont.newGlyph(eachTarget)
                else:
                    targetGlyph = eachFont[eachTarget]
                    targetGlyph.clear()

                if isinstance(eachSource, types.StringType) is True:
                    targetGlyph.width = eachFont[eachSource].width
                    targetGlyph.appendComponent(eachSource, (0, self.verticalOffset))
                else:
                    offsetX = 0
                    for eachSourceGlyphName in eachSource:
                        targetGlyph.appendComponent(eachSourceGlyphName, (offsetX, 0))
                        offsetX += eachFont[eachSourceGlyphName].width
                    targetGlyph.width = offsetX


if __name__ == '__main__':
    fm = FractionMaker()
