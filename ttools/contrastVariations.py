#!/usr/bin/env python
# coding: utf-8

######################
# Python Boilerplate #
######################

### Modules
# custom modules
import ui.userInterfaceValues
reload(ui.userInterfaceValues)
from ui.userInterfaceValues import vanillaControlsSize

# standard modules
from vanilla import FloatingWindow, Group, PopUpButton, TextBox, CheckBox, SquareButton

### Constants
PLUGIN_WIDTH = 230
PLUGIN_HEIGHT = 600

MARGIN_HOR = 10
MARGIN_VER = 8
NET_WIDTH = PLUGIN_WIDTH - MARGIN_HOR*2

SQUARE_BUTTON_HEIGHT = 30
CHECK_BOX_WIDTH = 22


### Classes
class CheckBoxStar(Group):

    direction = None
    possibleDirections = ['lft', 'rgt', 'top', 'btm']

    def __init__(self, posSize, callback):
        super(CheckBoxStar, self).__init__(posSize)

        ctrlWidth = posSize[2]
        ctrlHeight = posSize[3]

        self.lftCheck = CheckBox((0, ctrlHeight/2-vanillaControlsSize['CheckBoxRegularHeight']/2, CHECK_BOX_WIDTH, vanillaControlsSize['CheckBoxRegularHeight']),
                                 '',
                                 callback=self.lftCheckCallback)

        # self.lftArrow = TextBox((0, ctrlHeight/2, ),
        #                         u'←')

        self.rgtCheck = CheckBox((-CHECK_BOX_WIDTH, ctrlHeight/2-vanillaControlsSize['CheckBoxRegularHeight']/2, CHECK_BOX_WIDTH, vanillaControlsSize['CheckBoxRegularHeight']),
                                 '',
                                 callback=self.rgtCheckCallback)

        self.topCheck = CheckBox((ctrlWidth/2.-CHECK_BOX_WIDTH/2., 0, CHECK_BOX_WIDTH, vanillaControlsSize['CheckBoxRegularHeight']),
                                 '',
                                 callback=self.topCheckCallback)

        self.btmCheck = CheckBox((ctrlWidth/2.-CHECK_BOX_WIDTH/2., ctrlHeight-CHECK_BOX_WIDTH, CHECK_BOX_WIDTH, vanillaControlsSize['CheckBoxRegularHeight']),
                                 '',
                                 callback=self.btmCheckCallback)

    def get(self):
        assert self.direction in possibleDirections
        return self.direction

    def lftCheckCallback(self, sender):
        self.direction = 'lft'

    def rgtCheckCallback(self, sender):
        self.direction = 'rgt'

    def topCheckCallback(self, sender):
        self.direction = 'top'

    def btmCheckCallback(self, sender):
        self.direction = 'btm'

"""
↑→↓
"""

class ContrastController(object):

    def __init__(self):

        # base window
        self.w = FloatingWindow((0,0,PLUGIN_WIDTH, PLUGIN_HEIGHT))

        jumpingY = MARGIN_VER
        self.w.libChoice = PopUpButton((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['PopUpButtonRegularHeight']),
                                       ['A', 'B', 'C'],
                                       callback=self.libChoiceCallback)

        jumpingY += vanillaControlsSize['PopUpButtonRegularHeight'] + MARGIN_VER
        self.w.addButton = SquareButton((MARGIN_HOR, jumpingY, NET_WIDTH*.6, SQUARE_BUTTON_HEIGHT),
                                        'add stem',
                                        callback=self.addButtonCallback)

        self.w.checkBoxStar = CheckBoxStar((MARGIN_HOR+MARGIN_VER+NET_WIDTH*.6, jumpingY, NET_WIDTH*.35, NET_WIDTH*.35),
                                           callback=self.checkBoxStarCallback)

        jumpingY += SQUARE_BUTTON_HEIGHT + MARGIN_VER
        self.w.removeButton = SquareButton((MARGIN_HOR, jumpingY, NET_WIDTH*.6, SQUARE_BUTTON_HEIGHT),
                                           'remove stem',
                                           callback=self.removeButtonCallback)


        # lit up!
        self.w.open()


    def libChoiceCallback(self, sender):
        print sender.get()

    def addButtonCallback(self, sender):
        print 'hit addButtonCallback'

    def removeButtonCallback(self, sender):
        print 'hit removeButtonCallback'

    def checkBoxStarCallback(self, sender):
        print sender.get()




if __name__ == '__main__':
    cc = ContrastController()