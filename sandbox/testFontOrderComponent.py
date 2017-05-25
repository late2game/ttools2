#!/usr/bin/env python
# -*- coding: utf-8 -*-

from defconAppKit.windows.baseWindow import BaseWindowController
from vanilla import *
import os

vanillaControlsSize = {}
vanillaControlsSize['TextBoxRegularHeight'] = 17

FONT_ROW_HEIGHT = 30

class KerningController(BaseWindowController):

    def __init__(self):
        super(KerningController, self).__init__()

        self.w = Window((0,0,500,400),
                       'my window')

        self.w.myOrder = FontsOrder((0,0,300,200),
                                  AllFonts(),
                                  callback=self.myOrderCallback)

        self.w.open()

    def myOrderCallback(self, sender):
        print 'myOrderCallback'


class FontsOrder(Group):

    fontOrder = None

    def __init__(self, posSize, openedFonts, callback):
        super(FontsOrder, self).__init__(posSize)
        self.callback = callback
        self.fontOrder = openedFonts
        self._initFontsList()

    def _initFontsList(self):
        jumping_Y = 0
        for indexFont, eachFont in enumerate(self.fontOrder):
            fontRow = FontRow((0, jumping_Y, self.getPosSize()[2], FONT_ROW_HEIGHT),
                              indexFont+1,
                              eachFont,
                              isTop=False,
                              isBottom=False,
                              callback=self.fontRowCallback)
            setattr(self, 'fontRow%02d' % (indexFont+1), fontRow)
            jumping_Y += FONT_ROW_HEIGHT

    def _delFontsList(self):
        pass

    def fontRowCallback(self, sender):
        print 'fontRowCallback'


class FontRow(Group):

    def __init__(self, posSize, index, aFont, isTop, isBottom, callback):
        super(FontRow, self).__init__(posSize)

        self.callback = callback
        self.index = index

        ctrlX = 0
        self.caption = TextBox((0, 6, 140, vanillaControlsSize['TextBoxRegularHeight']),
                               '%s' % os.path.basename(aFont.path))
        ctrlX += self.caption.getPosSize()[2]

        self.buttonUp = SquareButton((ctrlX, 0, FONT_ROW_HEIGHT-3, FONT_ROW_HEIGHT-3),
                                     u'↑',
                                     callback=self.buttonUpCallback)
        if isTop is True:
            self.buttonUp.enable(False)

        ctrlX += self.buttonUp.getPosSize()[2]+4

        self.buttonDw = SquareButton((ctrlX, 0, FONT_ROW_HEIGHT-3, FONT_ROW_HEIGHT-3),
                                     u'↓',
                                     callback=self.buttonDwCallback)
        if isBottom is True:
            self.buttonDw.enable(False)

        ctrlX += self.buttonDw.getPosSize()[2]

    def setIndex(self, index):
        self.index = index
        width, height = self.getPosSize()[2:]
        self.setPosSize((0, self.index*FONT_ROW_HEIGHT, width, height))

    def setTop(self, isTop):
        self.isTop = isTop
        self.buttonUp.enable(not self.isTop)

    def setBottom(self, isBottom):
        self.isBottom = isBottom
        self.buttonDw.enable(not self.isBottom)

    def buttonUpCallback(self, sender):
        print 'buttonUpCallback'
        self.setIndex(self.index-1)
        self.callback(self)

    def buttonDwCallback(self, sender):
        print 'buttonDwCallback'
        self.setIndex(self.index+1)
        self.callback(self)


mk = KerningController()
