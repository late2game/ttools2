#!/usr/bin/env python
# coding: utf-8

##################################
# Set sidebearings or set widths #
##################################

### Modules
# custom
import userInterfaceValues
reload(userInterfaceValues)
from userInterfaceValues import vanillaControlsSize

# standard
import types
from mojo.roboFont import AllFonts, CurrentFont
from mojo.tools import IntersectGlyphWithLine
from vanilla import FloatingWindow, Group, RadioGroup, PopUpButton
from vanilla import Button, TextBox, EditText, CheckBox

### Constants
PLUGIN_WIDTH = 220
PLUGIN_TITLE = 'Sidebearings and Widths'

MARGIN_HOR = 10
MARGIN_VER = 8
NET_WIDTH = PLUGIN_WIDTH - MARGIN_HOR*2

MODE_OPTIONS = ['Set Sidebearings', 'Set Widths']
FONT_TARGET_OPTIONS = ['All Fonts', 'Current Font']
GLYPH_TARGET_OPTIONS = ['All Glyphs', 'Selection', 'Current Glyph']

ACTION_BUTTON_MESSAGES = {
    'Set Sidebearings': 'Set Sidebearings! Set Sidebearings!',
    'Set Widths': 'Set Widths! Set Widths!'
    }

ARITHMETIC_OPERATOR = ['plus', 'minus', 'equal']
LOCATIONS = ['left', 'right', 'both']
WHERE_TO_ACT_OPTIONS = [u'←', 'center', u'→']


MARGINS_MANAGER_HEIGHT = 114
WIDTHS_MANAGER_HEIGHT = 86

### Classes and functions
def add(a, b):
    return a+b

def subtract(a, b):
    return a-b

def substitute(a, b):
    return b

OPERATORS_2_FUNCTION = {
    'plus': add,
    'minus': subtract,
    'equal': substitute}

def changeSidebearings(aGlyph, whichOperation, targetLocation, amount, isBeamActive, beamHeight):
    assert whichOperation in ARITHMETIC_OPERATOR
    assert targetLocation in LOCATIONS
    assert isinstance(amount, types.IntType)
    assert isinstance(isBeamActive, types.BooleanType)

    if isBeamActive is True:
        assert isinstance(beamHeight, types.IntType)
    else:
        beamHeight = None

    chosenFunction = OPERATORS_2_FUNCTION[whichOperation]

    # standard value, override if intersections
    lftProtrusion = 0
    rgtProtrusion = 0

    if isBeamActive is True:
        intersections = IntersectGlyphWithLine(aGlyph, ((0, beamHeight), (aGlyph.width, beamHeight)), addSideBearings=False)
        if intersections:
            intersections = sorted(intersections, key=lambda item:item[0])
            lftProtrusion = intersections[0][0]-aGlyph.leftMargin
            rgtProtrusion = aGlyph.width-intersections[-1][0]-aGlyph.rightMargin

    if targetLocation == 'left' or targetLocation == 'both':
        aGlyph.leftMargin = chosenFunction(aGlyph.leftMargin+lftProtrusion, amount)-lftProtrusion

    if targetLocation == 'right' or targetLocation == 'both':
        aGlyph.rightMargin = chosenFunction(aGlyph.rightMargin+rgtProtrusion, amount)-rgtProtrusion

def changeWidth(aGlyph, whichOperation, whereToAct, amount):
    assert whichOperation in ARITHMETIC_OPERATOR
    assert whereToAct in WHERE_TO_ACT_OPTIONS
    assert isinstance(amount, types.IntType)

    chosenFunction = OPERATORS_2_FUNCTION[whichOperation]
    newWidth = chosenFunction(aGlyph.width, amount)

    if whereToAct == u'→':
        aGlyph.width = newWidth
    elif whereToAct == u'←':
        aGlyph.leftMargin += newWidth-aGlyph.width
    else:               # center
        blackWidth = aGlyph.box[2]-aGlyph.box[0]
        whiteWidth = newWidth-blackWidth
        aGlyph.leftMargin = whiteWidth//2
        aGlyph.rightMargin = whiteWidth//2
        if whiteWidth % 2 == 1:
            aGlyph.leftMargin += 1


class SidebearingsAndWidthsManager(object):

    def __init__(self):
        self.fontTarget = FONT_TARGET_OPTIONS[0]
        self.glyphTarget = GLYPH_TARGET_OPTIONS[0]
        self.mode = MODE_OPTIONS[0]

        self.w = FloatingWindow((0, 0, PLUGIN_WIDTH, 400), PLUGIN_TITLE)
        self.topReferenceY = MARGIN_VER

        self.w.modePopUp = PopUpButton((MARGIN_HOR, self.topReferenceY, NET_WIDTH, vanillaControlsSize['PopUpButtonRegularHeight']),
                                       MODE_OPTIONS,
                                       callback=self.modePopUpCallback)
        self.topReferenceY += vanillaControlsSize['PopUpButtonRegularHeight']+MARGIN_VER

        self.w.fontTargetOptionsPopUp = PopUpButton((MARGIN_HOR, self.topReferenceY, NET_WIDTH, vanillaControlsSize['PopUpButtonRegularHeight']),
                                               FONT_TARGET_OPTIONS,
                                               callback=self.fontTargetOptionsPopUpCallback)
        self.topReferenceY += vanillaControlsSize['PopUpButtonRegularHeight']+MARGIN_VER

        self.w.glyphTargetOptionsPopUp = PopUpButton((MARGIN_HOR, self.topReferenceY, NET_WIDTH, vanillaControlsSize['PopUpButtonRegularHeight']),
                                                   GLYPH_TARGET_OPTIONS,
                                                   callback=self.glyphTargetOptionsPopUpCallback)
        self.topReferenceY += vanillaControlsSize['PopUpButtonRegularHeight']+MARGIN_VER

        self.w.sidebearingsCtrl = SidebearingsManager((MARGIN_HOR, self.topReferenceY, NET_WIDTH, MARGINS_MANAGER_HEIGHT),
                                            callback=self.sidebearingsCtrlCallback)
        self.w.sidebearingsCtrl.show(True)

        self.w.widthsCtrl = WidthsManager((MARGIN_HOR, self.topReferenceY, NET_WIDTH, WIDTHS_MANAGER_HEIGHT),
                                            callback=self.widthsCtrlCallback)
        self.w.widthsCtrl.show(False)

        self.w.actionButton = Button((MARGIN_HOR, -vanillaControlsSize['ButtonRegularHeight']*1.5, NET_WIDTH, vanillaControlsSize['ButtonRegularHeight']),
                                     ACTION_BUTTON_MESSAGES[self.mode],
                                     callback=self.actionButtonCallback)

        self.sidebearingsPluginHeight = self.topReferenceY+vanillaControlsSize['ButtonRegularHeight']+MARGINS_MANAGER_HEIGHT+MARGIN_VER*1.5
        self.widthsPluginHeight = self.topReferenceY+vanillaControlsSize['ButtonRegularHeight']+WIDTHS_MANAGER_HEIGHT+MARGIN_VER*1.5
        self.w.setPosSize((0, 0, PLUGIN_WIDTH, self.sidebearingsPluginHeight))
        self.w.open()

    def modePopUpCallback(self, sender):
        self.mode = MODE_OPTIONS[sender.get()]
        if self.mode == 'Set Sidebearings':
            self.w.actionButton.setTitle(ACTION_BUTTON_MESSAGES[self.mode])
            self.w.sidebearingsCtrl.show(True)
            self.w.widthsCtrl.show(False)
            self.w.resize(PLUGIN_WIDTH, self.sidebearingsPluginHeight)
        else:
            self.w.actionButton.setTitle(ACTION_BUTTON_MESSAGES[self.mode])
            self.w.sidebearingsCtrl.show(False)
            self.w.widthsCtrl.show(True)
            self.w.resize(PLUGIN_WIDTH, self.widthsPluginHeight)

    def fontTargetOptionsPopUpCallback(self, sender):
        self.fontTarget = FONT_TARGET_OPTIONS[sender.get()]

    def glyphTargetOptionsPopUpCallback(self, sender):
        self.glyphTarget = GLYPH_TARGET_OPTIONS[sender.get()]

    def sidebearingsCtrlCallback(self, sender):
        self.mrgWhichOperation, self.mrgTargetLocation, self.mrgAmount, self.mrgIsBeamActive, self.mrgBeamHeight = sender.get()

    def widthsCtrlCallback(self, sender):
        self.wdtWhichOperation, self.wdtWhereToAct, self.wdtWidth = sender.get()

    def actionButtonCallback(self, sender):
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

            for eachGlyphName in glyphNamesToProcess:
                eachGlyph = eachFont[eachGlyphName]

                if self.mode == 'Set Sidebearings':
                    changeSidebearings(eachGlyph, self.mrgWhichOperation, self.mrgTargetLocation, self.mrgAmount, self.mrgIsBeamActive, self.mrgBeamHeight)

                else:          # set widths
                    changeWidth(eachGlyph, self.wdtWhichOperation, self.wdtWhereToAct, self.wdtWidth)

class SidebearingsManager(Group):

    beamHeight = None
    amount = None

    def __init__(self, posSize, callback):
        super(SidebearingsManager, self).__init__(posSize)
        self.callback = callback

        jumpingY = 0
        self.operationRadio = RadioGroup((0, jumpingY, NET_WIDTH, vanillaControlsSize['EditTextRegularHeight']),
                                           ['plus', 'minus', 'equal'],
                                           isVertical=False,
                                           sizeStyle='small',
                                           callback=self.operationRadioCallback)
        self.operationRadio.set(2)
        self.whichOperation = ARITHMETIC_OPERATOR[2]
        jumpingY += vanillaControlsSize['EditTextRegularHeight']

        self.targetLocationRadio = RadioGroup((0, jumpingY, NET_WIDTH, vanillaControlsSize['EditTextRegularHeight']),
                                      LOCATIONS,
                                      isVertical=False,
                                      sizeStyle='small',
                                      callback=self.targetLocationRadioCallback)
        self.targetLocation = LOCATIONS[2]
        self.targetLocationRadio.set(2)
        jumpingY += vanillaControlsSize['EditTextRegularHeight'] + MARGIN_VER

        self.amountCaption = TextBox((0, jumpingY+2, NET_WIDTH*.28, vanillaControlsSize['TextBoxRegularHeight']),
                                     'Amount:')

        self.amountEdit = EditText((NET_WIDTH*.3, jumpingY, NET_WIDTH*.4, vanillaControlsSize['EditTextRegularHeight']),
                                   callback=self.amountEditCallback)
        jumpingY += vanillaControlsSize['EditTextRegularHeight'] + MARGIN_VER

        self.beamCheck = CheckBox((0, jumpingY+2, NET_WIDTH*.28, vanillaControlsSize['TextBoxRegularHeight']),
                                  'Beam:',
                                  callback=self.beamCheckCallback)
        self.isBeamActive = False

        self.beamEdit = EditText((NET_WIDTH*.3, jumpingY, NET_WIDTH*.4, vanillaControlsSize['EditTextRegularHeight']),
                                  callback=self.beamEditCallback)
        self.beamEdit.enable(False)
        jumpingY += vanillaControlsSize['EditTextRegularHeight'] + MARGIN_VER

    def get(self):
        return self.whichOperation, self.targetLocation, self.amount, self.isBeamActive, self.beamHeight

    def operationRadioCallback(self, sender):
        self.whichOperation = ARITHMETIC_OPERATOR[sender.get()]

        if self.whichOperation in ['plus', 'minus']:
            self.isBeamActive = False
            self.beamCheck.set(self.isBeamActive)
            self.beamCheck.enable(False)
            self.beamEdit.enable(self.isBeamActive)
        else:
            self.beamCheck.enable(True)
        self.callback(self)

    def targetLocationRadioCallback(self, sender):
        self.targetLocation = LOCATIONS[sender.get()]
        self.callback(self)

    def amountEditCallback(self, sender):
        try:
            self.amount = int(sender.get())
        except ValueError:
            self.amountEdit.set('%d' % self.amount)
        self.callback(self)

    def beamCheckCallback(self, sender):
        self.isBeamActive = bool(sender.get())
        self.beamEdit.enable(self.isBeamActive)
        self.callback(self)

    def beamEditCallback(self, sender):
        try:
            self.beamHeight = int(sender.get())
        except ValueError:
            self.beamEdit.set('%d' % self.beamHeight)
        self.callback(self)


class WidthsManager(Group):

    width = None

    def __init__(self, posSize, callback):
        super(WidthsManager, self).__init__(posSize)
        self.callback = callback

        jumpingY = 0
        self.operationRadio = RadioGroup((0, jumpingY, NET_WIDTH, vanillaControlsSize['EditTextRegularHeight']),
                                      ['plus', 'minus', 'equal'],
                                      isVertical=False,
                                      sizeStyle='small',
                                      callback=self.operationRadioCallback)
        self.whichOperation = ARITHMETIC_OPERATOR[2]
        self.operationRadio.set(2)
        jumpingY += vanillaControlsSize['EditTextRegularHeight']

        self.whereToActRadio = RadioGroup((0, jumpingY, NET_WIDTH, vanillaControlsSize['EditTextRegularHeight']),
                                      WHERE_TO_ACT_OPTIONS,
                                      isVertical=False,
                                      sizeStyle='small',
                                      callback=self.whereToActRadioCallback)
        self.whereToAct = WHERE_TO_ACT_OPTIONS[1]
        self.whereToActRadio.set(1)
        jumpingY += vanillaControlsSize['EditTextRegularHeight'] + MARGIN_VER

        self.widthCaption = TextBox((0, jumpingY+2, NET_WIDTH*.28, vanillaControlsSize['TextBoxRegularHeight']),
                                    'Width:')
        self.widthEdit = EditText((NET_WIDTH*.3, jumpingY, NET_WIDTH*.4, vanillaControlsSize['EditTextRegularHeight']),
                                  callback=self.widthEditCallback)

    def get(self):
        return self.whichOperation, self.whereToAct, self.width

    def operationRadioCallback(self, sender):
        self.whichOperation = ARITHMETIC_OPERATOR[sender.get()]
        self.callback(self)

    def whereToActRadioCallback(self, sender):
        self.whereToAct = WHERE_TO_ACT_OPTIONS[sender.get()]
        self.callback(self)

    def widthEditCallback(self, sender):
        try:
            self.width = int(sender.get())
        except ValueError:
            self.widthEdit.set('%d' % self.width)
        self.callback(self)


if __name__ == '__main__':
    mw = SidebearingsAndWidthsManager()
