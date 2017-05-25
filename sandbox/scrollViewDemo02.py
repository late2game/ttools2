#!/usr/bin/env python
# -*- coding: utf-8 -*-

######################
# Python Boilerplate #
######################

### Modules
from defconAppKit.controls.openTypeControlsView import DefconAppKitTopAnchoredNSView
from defconAppKit.windows.baseWindow import BaseWindowController
from vanilla import *

### Constants

### Instructions
class MyWindow(BaseWindowController):

    def __init__(self, ctrlsAmount):
        super(MyWindow, self).__init__()
        self.ctrlsAmount = ctrlsAmount

        self.w = Window((0, 0, 200, 300),
                        'my window')

        jumpinY = 4
        self.w.threeButton = Button((20, jumpinY, 40, 16),
                                    '3',
                                    callback=self.threeButtonCallback)

        self.w.fourButton = Button((70, jumpinY, 40, 16),
                                    '4',
                                    callback=self.fourButtonCallback)

        self.myCtrls = MyGroupOfCtrls((0, 0, 160, 100), self.ctrlsAmount)

        self.myCtrlsView = DefconAppKitTopAnchoredNSView.alloc().init()
        self.myCtrlsView.addSubview_(self.myCtrls.getNSView())
        self.myCtrlsView.setFrame_(((20, jumpinY), (160+50, 50)))

        jumpinY += 28
        self.w.myScrollView = ScrollView((20, jumpinY, 160, 50),
                                         self.thisView,
                                         drawsBackground=False,
                                         autohidesScrollers=False,
                                         hasHorizontalScroller=True,
                                         hasVerticalScroller=True)

        self.w.open()

    def threeButtonCallback(self, sender):
        self.ctrlsAmount = 3
        self.myCtrls.initCtrls(self.ctrlsAmount)

    def fourButtonCallback(self, sender):
        self.ctrlsAmount = 4
        self.myCtrls.initCtrls(self.ctrlsAmount)


class MyGroupOfCtrls(Group):

    def __init__(self, posSize, ctrlsAmount):
        super(MyGroupOfCtrls, self).__init__(posSize)
        self.ctrlsAmount = ctrlsAmount
        self.jumpinY = 0
        self.initCtrls(self.ctrlsAmount)

    def delCtrls(self):
        for eachI in range(self.ctrlsAmount):
            if hasattr(self, 'popUp%#02d' % eachI) is True:
                delattr(self, 'popUp%#02d' % eachI)
                self.jumpinY -= 24

    def initCtrls(self, amount):
        self.delCtrls()
        for eachI in range(self.ctrlsAmount):
            ctrl = PopUpButton((0, self.jumpinY, 50, 20),
                               ['a', 'b'])
            setattr(self, 'popUp%#02d' % eachI, ctrl)
            self.jumpinY += 24

mw = MyWindow(3)





