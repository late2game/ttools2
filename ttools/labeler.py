#!/usr/bin/env python
# coding: utf-8

#########################################
# Add quickly labels to selected points #
#########################################

### Modules
# custom
import ui.userInterfaceValues
reload(ui.userInterfaceValues)
from ui.userInterfaceValues import vanillaControlsSize

# standard
from mojo.roboFont import CurrentGlyph
from mojo.UI import UpdateCurrentGlyphView
from vanilla import FloatingWindow, Group, SquareButton, EditText
from vanilla import HorizontalLine

### Constants
PLUGIN_WIDTH = 260
MARGIN_HOR = 10
MARGIN_VER = 8
MARGIN_COL = 6
NET_WIDTH = PLUGIN_WIDTH - MARGIN_HOR*2


### Classes
def attachLabelToSelectedPoints(labelName):
    myGlyph = CurrentGlyph()
    for eachContour in myGlyph:
        for eachPt in eachContour.points:
            if eachPt.selected is True:
                eachPt.name = labelName
    myGlyph.update()
    UpdateCurrentGlyphView()

class Labeler(object):

    labelCltrIndex = 0

    def __init__(self):

        # init window
        self.w = FloatingWindow((PLUGIN_WIDTH, 300), 'labeler.py')

        self.jumpingY = MARGIN_VER
        self.w.labelCtrl_0 = LabelCtrl((MARGIN_HOR, self.jumpingY, NET_WIDTH, vanillaControlsSize['EditTextRegularHeight']),
                                       index=self.labelCltrIndex,
                                       callback=self.labelCtrlsCallback)
        self.jumpingY += vanillaControlsSize['EditTextRegularHeight'] + MARGIN_VER

        self.w.separation = HorizontalLine((MARGIN_HOR, self.jumpingY, NET_WIDTH, vanillaControlsSize['HorizontalLineThickness']))
        self.w.clearButton = SquareButton((MARGIN_HOR, self.jumpingY+vanillaControlsSize['HorizontalLineThickness'] + MARGIN_VER, NET_WIDTH, vanillaControlsSize['ButtonRegularHeight']),
                                          'Clear Glyph Labels',
                                          sizeStyle='small',
                                          callback=self.clearButtonCallback)

        # resize window
        self._computeWindowHeight()
        self.w.resize(PLUGIN_WIDTH, self.windowHeight)

        # open window
        self.w.open()

    def _computeWindowHeight(self):
        self.windowHeight = self.jumpingY + vanillaControlsSize['ButtonRegularHeight'] + vanillaControlsSize['HorizontalLineThickness'] + MARGIN_VER*2

    def _updateCtrlsPos(self):
        self.w.separation.setPosSize((MARGIN_HOR, self.jumpingY, NET_WIDTH, vanillaControlsSize['HorizontalLineThickness']))
        self.w.clearButton.setPosSize((MARGIN_HOR, self.jumpingY+vanillaControlsSize['HorizontalLineThickness'] + MARGIN_VER, NET_WIDTH, vanillaControlsSize['ButtonRegularHeight']))

    def labelCtrlsCallback(self, sender):
        lastAction, labelName = sender.get()

        if lastAction == 'attach':
            attachLabelToSelectedPoints(labelName)

        elif lastAction == 'add':
            self.labelCltrIndex += 1
            labelCtrl = LabelCtrl((MARGIN_HOR, self.jumpingY, NET_WIDTH, vanillaControlsSize['EditTextRegularHeight']),
                                  index=self.labelCltrIndex,
                                  callback=self.labelCtrlsCallback)
            setattr(self.w, 'labelCtrl_{:d}'.format(labelCtrl.index), labelCtrl)

            self.jumpingY += vanillaControlsSize['EditTextRegularHeight'] + MARGIN_VER
            self._computeWindowHeight()
            self._updateCtrlsPos()
            self.w.resize(PLUGIN_WIDTH, self.windowHeight)

        elif lastAction == 'subtract':
            delattr(self.w, 'labelCtrl_{:d}'.format(labelCtrl.index))
            self.jumpingY -= vanillaControlsSize['EditTextRegularHeight'] + MARGIN_VER
            self.w.resize(PLUGIN_WIDTH, self.windowHeight)

        # else: # None


    def clearButtonCallback(self, sender):
        myGlyph = CurrentGlyph()
        for eachContour in myGlyph:
            for eachPt in eachContour.points:
                if eachPt.name is not None:
                    eachPt.name = None
        myGlyph.update()


class LabelCtrl(Group):
    # ui attrs
    attachButtonWidth = NET_WIDTH *.2
    labelNameEditWidth = NET_WIDTH *.6 - MARGIN_COL*3
    plusButtonWidth = NET_WIDTH *.1
    lessButtonWidth = NET_WIDTH *.1

    # func attrs
    ACTIONS = ['add', 'subtract', 'attach', None]
    labelName = None
    lastAction = None

    def __init__(self, posSize, index, callback):
        super(LabelCtrl, self).__init__(posSize)
        self.callback = callback
        self.index = index

        self.jumpingX = 0
        self.attachButton = SquareButton((self.jumpingX, 0, self.attachButtonWidth, vanillaControlsSize['EditTextRegularHeight']),
                                         'Attach',
                                         sizeStyle='small',
                                         callback=self.attachButtonCallback)

        self.jumpingX += MARGIN_COL + self.attachButtonWidth
        self.labelNameEdit = EditText((self.jumpingX, 0, self.labelNameEditWidth, vanillaControlsSize['EditTextRegularHeight']),
                                      callback=self.labelNameEditCallback)

        self.jumpingX += MARGIN_COL + self.labelNameEditWidth
        self.plusButton = SquareButton((self.jumpingX, 0, self.plusButtonWidth, vanillaControlsSize['EditTextRegularHeight']),
                                       '+',
                                       sizeStyle='small',
                                       callback=self.plusButtonCallback)

        self.jumpingX += MARGIN_COL + self.lessButtonWidth
        self.lessButton = SquareButton((self.jumpingX, 0, self.lessButtonWidth, vanillaControlsSize['EditTextRegularHeight']),
                                       '-',
                                       sizeStyle='small',
                                       callback=self.lessButtonCallback)

    def get(self):
        return self.lastAction, self.labelName

    def attachButtonCallback(self, sender):
        self.lastAction = 'attach'
        assert self.lastAction in self.ACTIONS
        self.callback(self)

    def labelNameEditCallback(self, sender):
        self.labelName = sender.get()
        self.lastAction = None
        assert self.lastAction in self.ACTIONS
        self.callback(self)

    def plusButtonCallback(self, sender):
        self.lastAction = 'add'
        assert self.lastAction in self.ACTIONS
        self.callback(self)

    def lessButtonCallback(self, sender):
        self.lastAction = 'subtract'
        assert self.lastAction in self.ACTIONS
        self.callback(self)


if __name__ == '__main__':
    lb = Labeler()
