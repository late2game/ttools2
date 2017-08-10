#!/usr/bin/env python
# coding: utf-8

from defconAppKit.windows.baseWindow import BaseWindowController
from vanilla import *
import os

vanillaControlsSize = {}
vanillaControlsSize['TextBoxRegularHeight'] = 17

FONT_ROW_HEIGHT = 30
MARGIN_COL = 4
LEFT_COLUMN = 200

class KerningController(BaseWindowController):

    fontsOrder = None

    def __init__(self):
        super(KerningController, self).__init__()

        self.fontsOrder = AllFonts()

        self.w = Window((0,0,500,400),
                        'my window')

        fontsOrderControllerHeight = FONT_ROW_HEIGHT*len(self.fontsOrder)
        self.w.myOrder = FontsOrderController((0, 0, LEFT_COLUMN, 200),
                                              self.fontsOrder,
                                              callback=self.myOrderCallback)
        self.w.open()

    def myOrderCallback(self, sender):
        self.fontsOrder = sender.getFontsOrder()


class FontsOrderController(Group):

    fontsOrder = None

    def __init__(self, posSize, openedFonts, callback):
        super(FontsOrderController, self).__init__(posSize)
        self.callback = callback
        self.fontsOrder = openedFonts
        self._initFontsList()

    def _initFontsList(self):
        jumping_Y = 0
        for indexFont, eachFont in enumerate(self.fontsOrder):

            if indexFont == 0:
                isTop = True
            else:
                isTop = False

            if indexFont == (len(self.fontsOrder)-1):
                isBottom = True
            else:
                isBottom = False

            fontRow = FontRow((0, jumping_Y, self.getPosSize()[2], FONT_ROW_HEIGHT),
                              indexFont+1,
                              eachFont,
                              isTop=isTop,
                              isBottom=isBottom,
                              callback=self.fontRowCallback)
            setattr(self, 'fontRow%02d' % (indexFont+1), fontRow)
            jumping_Y += FONT_ROW_HEIGHT

    def _delFontsList(self):
        for indexFont, eachFont in enumerate(self.fontsOrder):
            delattr(self, 'fontRow%02d' % (indexFont+1))

    def setFontsOrder(self, fontsOrder):
        self._delFontsList()
        self.fontsOrder = fontsOrder
        self._initFontsList()

    def getFontsOrder(self):
        return self.fontsOrder

    def fontRowCallback(self, sender):
        direction, fontToSwap = sender.getDirection(), sender.getFont()
        assert direction in ['up', 'down']

        mainToSwapIndex = self.fontsOrder.index(fontToSwap)
        if direction == 'up':
            subToSwapIndex = mainToSwapIndex-1
        else:
            subToSwapIndex = mainToSwapIndex+1
        self.fontsOrder[mainToSwapIndex], self.fontsOrder[subToSwapIndex] = self.fontsOrder[subToSwapIndex], self.fontsOrder[mainToSwapIndex]
        
        for indexFont, eachFont in enumerate(self.fontsOrder):
            getattr(self, 'fontRow%02d' % (indexFont+1)).setFont(eachFont)
        self.callback(self)


class FontRow(Group):

    lastDirection = None

    def __init__(self, posSize, index, aFont, isTop, isBottom, callback):
        super(FontRow, self).__init__(posSize)

        self.callback = callback
        self.index = index
        self.ctrlFont = aFont

        squareButtonSide = FONT_ROW_HEIGHT-3

        self.caption = TextBox((0, 6, 140, vanillaControlsSize['TextBoxRegularHeight']),
                               '%s' % os.path.basename(self.ctrlFont.path))

        self.buttonUp = SquareButton((-(squareButtonSide*2+MARGIN_COL), 0, squareButtonSide, squareButtonSide),
                                     u'↑',
                                     callback=self.buttonUpCallback)
        if isTop is True:
            self.buttonUp.show(False)

        self.buttonDw = SquareButton((-squareButtonSide, 0, squareButtonSide, squareButtonSide),
                                     u'↓',
                                     callback=self.buttonDwCallback)
        if isBottom is True:
            self.buttonDw.show(False)

    def setFont(self, aFont):
        self.ctrlFont = aFont
        self.caption.set('%s' % os.path.basename(self.ctrlFont.path))

    def getDirection(self):
        return self.lastDirection

    def getFont(self):
        return self.ctrlFont

    def buttonUpCallback(self, sender):
        self.lastDirection = 'up'
        self.callback(self)

    def buttonDwCallback(self, sender):
        self.lastDirection = 'down'
        self.callback(self)

mk = KerningController()
