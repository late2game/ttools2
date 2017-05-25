from AppKit import NSView, NSColor, NSRectFill
from vanilla import *
from defconAppKit.windows.baseWindow import BaseWindowController
from defconAppKit.controls.openTypeControlsView import DefconAppKitTopAnchoredNSView


class SpacingMatrixView03(BaseWindowController):

    def __init__(self):
        width, height = 190, 140
        self.cm = Group((0, 0, width, 20))
        self.cm.pop = PopUpButton((1, 0, -1, 20),
                                       ['A', 'B'],
                                       callback=self.popCallback)

        view = DefconAppKitTopAnchoredNSView.alloc().init()
        view.addSubview_(self.cm.getNSView())
        view.setFrame_(((0, 0), (width+10, height*4-23)))
        self.cm.setPosSize((0, 0, width+10, height*4-22))
        self.w = FloatingWindow((0,0,500,400), 'Ciao', minSize=(500, 400))
        self.w.scrollView = ScrollView((5, 10, width+10, -41), view, drawsBackground=False, hasHorizontalScroller=False)
        self.w.open()


    def popCallback(self, sender):
        print sender.get()

SpacingMatrixView03()





"""
    self.cm = Group((0, 0, 0, 0))
    # ---
    self.cm.group1 = Group((5, height*0, width, height-10))
    self.cm.group1.baseLabel = TextBox((0, 0, width, 20), baseLabel)
    self.cm.group1.baseInput = EditText((0, 21, width, 22), calibrateModeStrings['group1.baseInput'], callback=self.updateCalibrateMode, continuous=False)
    self.cm.group1.markLabel = TextBox((0, 50, width, 20), markLabel)
    self.cm.group1.markInput = EditText((0, 71, width, 44), calibrateModeStrings['group1.markInput'], callback=self.updateCalibrateMode, continuous=False)
    self.cm.group1.divider = HorizontalLine((0, -1, -0, 1))
    # ---
    self.cm.group2 = Group((5, height*1, width, height-10))
    self.cm.group2.baseLabel = TextBox((0, 0, width, 20), baseLabel)
    self.cm.group2.baseInput = EditText((0, 21, width, 22), calibrateModeStrings['group2.baseInput'], callback=self.updateCalibrateMode, continuous=False)
    self.cm.group2.markLabel = TextBox((0, 50, width, 20), markLabel)
    self.cm.group2.markInput = EditText((0, 71, width, 44), calibrateModeStrings['group2.markInput'], callback=self.updateCalibrateMode, continuous=False)
    self.cm.group2.divider = HorizontalLine((0, -1, -0, 1))
    # ---
    self.cm.group3 = Group((5, height*2, width, height-10))
    self.cm.group3.baseLabel = TextBox((0, 0, width, 20), baseLabel)
    self.cm.group3.baseInput = EditText((0, 21, width, 22), calibrateModeStrings['group3.baseInput'], callback=self.updateCalibrateMode, continuous=False)
    self.cm.group3.markLabel = TextBox((0, 50, width, 20), markLabel)
    self.cm.group3.markInput = EditText((0, 71, width, 44), calibrateModeStrings['group3.markInput'], callback=self.updateCalibrateMode, continuous=False)
    self.cm.group3.divider = HorizontalLine((0, -1, -0, 1))
    # ---
    self.cm.group4 = Group((5, height*3, width, height-10))
    self.cm.group4.baseLabel = TextBox((0, 0, width, 20), baseLabel)
    self.cm.group4.baseInput = EditText((0, 21, width, 22), calibrateModeStrings['group4.baseInput'], callback=self.updateCalibrateMode, continuous=False)
    self.cm.group4.markLabel = TextBox((0, 50, width, 20), markLabel)
    self.cm.group4.markInput = EditText((0, 71, width, 44), calibrateModeStrings['group4.markInput'], callback=self.updateCalibrateMode, continuous=False)
    # ---
    view = DefconAppKitTopAnchoredNSView.alloc().init()
    view.addSubview_(self.cm.getNSView())
    view.setFrame_(((0, 0), (width+10, height*4-23)))
    self.cm.setPosSize((0, 0, width+10, height*4-22))
    self.w.scrollView = ScrollView((5, 10, width+10, -41), view, drawsBackground=False, hasHorizontalScroller=False)
    self.w.scrollView.getNSScrollView().setBorderType_(NSNoBorder)
    self.w.scrollView.getNSScrollView().setVerticalScrollElasticity_(1) # NSScrollElasticityNone
    self.w.scrollView.show(self.calibrateMode)

"""


