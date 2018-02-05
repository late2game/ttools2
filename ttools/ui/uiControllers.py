#!/usr/bin/env python
# coding: utf-8

##################################################
# some ui controllers shared among various tools #
##################################################

### Modules
# custom
import userInterfaceValues
reload(userInterfaceValues)
from userInterfaceValues import vanillaControlsSize

# standard
import os
from vanilla import Group, TextBox, SquareButton, CheckBox


### Constants
FONT_ROW_HEIGHT = 28
MARGIN_COL = 4


### Classes
class FontsOrderController(Group):

    fontsOrder = None

    def __init__(self, posSize, openedFonts, callback):
        super(FontsOrderController, self).__init__(posSize)
        self.callback = callback
        self.fontsOrder = openedFonts
        self.isDisplayedOrder = [True for font in self.fontsOrder]
        self._initFontsList()

    def _initFontsList(self):
        jumping_Y = 0
        for indexFont, eachFont in enumerate(self.fontsOrder):

            isTop = True if indexFont == 0 else False
            isBottom = True if indexFont  == len(self.fontsOrder)-1 else False

            fontRow = FontRow((0, jumping_Y, self.getPosSize()[2], FONT_ROW_HEIGHT),
                              indexFont+1,
                              eachFont,
                              isTop=isTop,
                              isBottom=isBottom,
                              directionCallback=self.fontRowDirectionCallback,
                              displayedCallback=self.fontRowDisplayedCallback)

            setattr(self, 'fontRow{:0>2d}'.format(indexFont+1), fontRow)
            jumping_Y += FONT_ROW_HEIGHT

    def _delFontsList(self):
        for indexFont, eachFont in enumerate(self.fontsOrder):
            delattr(self, 'fontRow{:0>2d}'.format(indexFont+1))

    def addFontToFontsOrder(self, fontToAdd):
        self._delFontsList()
        self.fontsOrder.append(fontToAdd)
        self.isDisplayedOrder.append(True)
        self._initFontsList()

    def setFontsOrder(self, fontsOrder):
        self._delFontsList()
        self.fontsOrder = fontsOrder
        self.isDisplayedOrder = [True for font in self.fontsOrder]
        self._initFontsList()

    def getFontsOrder(self):
        return self.fontsOrder

    def getIsDisplayedOrder(self):
        return self.isDisplayedOrder

    def fontRowDisplayedCallback(self, sender):
        isDisplayed = sender.getIsDisplayed()
        self.isDisplayedOrder[sender.index-1] = isDisplayed
        self.callback(self)

    def fontRowDirectionCallback(self, sender):
        direction, fontToSwap = sender.getDirection(), sender.getFont()
        assert direction in ['up', 'down']

        mainSwapIndex = self.fontsOrder.index(fontToSwap)
        subSwapIndex = mainSwapIndex-1 if direction == 'up' else mainSwapIndex+1

        self.fontsOrder[mainSwapIndex], self.fontsOrder[subSwapIndex] = self.fontsOrder[subSwapIndex], self.fontsOrder[mainSwapIndex]
        self.isDisplayedOrder[mainSwapIndex], self.isDisplayedOrder[subSwapIndex] = self.isDisplayedOrder[subSwapIndex], self.isDisplayedOrder[mainSwapIndex]

        for indexFont, eachFont in enumerate(self.fontsOrder):
            rowCtrl = getattr(self, 'fontRow{:0>2d}'.format(indexFont+1))
            rowCtrl.setFont(eachFont)
            rowCtrl.setIsDisplayed(self.isDisplayedOrder[indexFont])

        self.callback(self)


class FontRow(Group):

    lastDirection = None
    isDisplayed = True

    def __init__(self, posSize, index,
                 aFont, isTop, isBottom,
                 directionCallback, displayedCallback):
        super(FontRow, self).__init__(posSize)
        self.directionCallback = directionCallback
        self.displayedCallback = displayedCallback
        self.index = index
        self.ctrlFont = aFont

        squareButtonSide = FONT_ROW_HEIGHT-6

        self.check = CheckBox((0, 0, 16, vanillaControlsSize['CheckBoxRegularHeight']),
                              '',
                              value=self.isDisplayed,
                              callback=self.checkCallback)

        self.caption = TextBox((18, 2, 120, vanillaControlsSize['TextBoxRegularHeight']),
                               '{}'.format(self.ctrlFont.info.styleName))

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
        self.caption.set('{}'.format(self.ctrlFont.info.styleName))

    def getDirection(self):
        return self.lastDirection

    def setIsDisplayed(self, isDisplayed):
        self.isDisplayed = isDisplayed
        self.check.set(self.isDisplayed)

    def getIsDisplayed(self):
        return self.isDisplayed

    def getFont(self):
        return self.ctrlFont

    def checkCallback(self, sender):
        self.isDisplayed = bool(sender.get())
        self.displayedCallback(self)

    def buttonUpCallback(self, sender):
        self.lastDirection = 'up'
        self.directionCallback(self)

    def buttonDwCallback(self, sender):
        self.lastDirection = 'down'
        self.directionCallback(self)
