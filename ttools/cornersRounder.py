#!/usr/bin/env python
# coding: utf-8

################
# Corner Tools #
################

### Modules
# standard
import os, importlib
import logging
from builtins import range
from collections import OrderedDict
from mojo.roboFont import AllFonts, CurrentFont, CurrentGlyph, version
from mojo.events import addObserver, removeObserver
from mojo.UI import UpdateCurrentGlyphView
from defconAppKit.windows.baseWindow import BaseWindowController
from vanilla import Window, Group, EditText, SquareButton
from vanilla import List, HorizontalLine, TextBox, PopUpButton, ComboBox
from vanilla.dialogs import message

# custom
from .ui import userInterfaceValues
importlib.reload(userInterfaceValues)
from .ui.userInterfaceValues import vanillaControlsSize

from .extraTools import roundingTools
importlib.reload(roundingTools)
from .extraTools.roundingTools import attachLabelToSelectedPoints, makeGlyphRound


### Constants
MODIFIERS = {1048840: 'CMD_LEFT',
             1048848: 'CMD_RIGHT',
             131330 : 'SHIFT_LEFT',
             131332 : 'SHIFT_RIGHT',
             524576 : 'ALT_LEFT',
             524608 : 'ALT_RIGHT',
             262401 : 'CTRL',
             8388864: 'FN'}

PLUGIN_TITLE = 'TT Round Corners'
PLUGIN_WIDTH = 360
PLUGIN_HEIGHT = 600

MARGIN_VER = 8
MARGIN_HOR = 8
MARGIN_ROW = 4
NET_WIDTH = PLUGIN_WIDTH - MARGIN_HOR*2

PLUGIN_LIB_NAME = 'com.ttools.roundCornersData'

# error messages
NO_DATA_INTO_FONT = u'No Roundings data stored into the font! \n(try to push the data inserted into the table)'
NO_GLYPH_TO_ROUND = u'No Current Glyph to round!'
FONT_MISMATCH = u'The font selected into the plugin does not match with the RF current font'
LAYERS_MATCH = u'source layer name and target layer name should be different'
DATA_PUSHED = u'Data pushed into {familyName} {styleName}'
NO_FONT_TO_PUSH = u'I do not know where to push these values ¯\\_(ツ)_/¯'

### Functions
def pushRoundingsDataIntoFont(aFont, someData):
    aFont.lib[PLUGIN_LIB_NAME] = [dict(aDict) for aDict in someData]
    if version[0] == '2':
        aFont.changed()
    else:
        aFont.update()

def pullRoundingsDataFromFont(aFont):
    if PLUGIN_LIB_NAME in aFont.lib:
        return [dict(aDict) for aDict in aFont.lib[PLUGIN_LIB_NAME]]

def makeRoundingsDataEmptyDict():
    return dict(labelName='',
                fortyFiveRad='',
                fortyFiveBcp='',
                ninetyRad='',
                ninetyBcp='',
                hundredThirtyFiveRad='',
                hundredThirtyFiveBcp='')

LABELS_AMOUNT = 8
DUMMY_ROUNDINGS = [makeRoundingsDataEmptyDict() for ii in range(LABELS_AMOUNT)]

### Classes
class CornersRounder(BaseWindowController):

    layerNames = []
    targetLayerName = None
    sourceLayerName = None

    roundingsData = None

    selectedFont = None
    allFonts = None

    def __init__(self):
        super(CornersRounder, self).__init__()

        self._initLogger()
        self.rounderLogger.info('we are on air! start: __init__()')

        self._updateFontsAttributes()
        if self.allFonts != []:
            self.selectedFont = self.allFonts[0]

        self._initRoundingsData()
        if self.selectedFont is not None:
            self.layerNames = ['foreground'] + self.selectedFont.layerOrder
            self.sourceLayerName = self.layerNames[0]
            self.targetLayerName = self.layerNames[0]

            if PLUGIN_LIB_NAME in self.selectedFont.lib:
                self.roundingsData = pullRoundingsDataFromFont(self.selectedFont)

        self.w = Window((0, 0, PLUGIN_WIDTH, PLUGIN_HEIGHT), PLUGIN_TITLE)

        jumpingY = MARGIN_VER
        self.w.fontPopUp = PopUpButton((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['PopUpButtonRegularHeight']),
                                       [os.path.basename(item.path) for item in self.allFonts],
                                       callback=self.fontPopUpCallback)

        jumpingY += vanillaControlsSize['PopUpButtonRegularHeight'] + MARGIN_VER
        self.w.sepLineOne = HorizontalLine((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['HorizontalLineThickness']))

        jumpingY += MARGIN_VER
        for eachI in range(LABELS_AMOUNT):
            singleLabel = Label((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['EditTextRegularHeight']),
                                attachCallback=self.attachCallback,
                                labelName='')

            setattr(self.w, 'label{:d}'.format(eachI), singleLabel)
            jumpingY += MARGIN_ROW+vanillaControlsSize['EditTextRegularHeight']
        self._fromRoundingsData2LabelCtrls()

        jumpingY += MARGIN_ROW
        self.w.sepLineTwo = HorizontalLine((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['HorizontalLineThickness']))
        jumpingY += MARGIN_ROW*2

        # tables
        labelListWdt = 78
        marginTable = 1
        angleListWdt = (NET_WIDTH-labelListWdt-marginTable*3)//3
        tableLineHeight = 16
        tableHgt = LABELS_AMOUNT*tableLineHeight + 33

        captionY = jumpingY
        captionOffset = 12
        jumpingY += vanillaControlsSize['TextBoxSmallHeight']+MARGIN_ROW

        labelColumnDesc = [{"title": "labelName", 'editable': True}]
        jumpingX = MARGIN_HOR

        self.w.labelNameList = List((jumpingX, jumpingY, labelListWdt, tableHgt),
                                    [],
                                    columnDescriptions=labelColumnDesc,
                                    showColumnTitles=True,
                                    editCallback=self.labelNameListCallback,
                                    rowHeight=tableLineHeight,
                                    drawHorizontalLines=True,
                                    drawVerticalLines=True,
                                    autohidesScrollers=True,
                                    allowsMultipleSelection=False)

        anglesColumnDesc = [{"title": "rad", 'editable': True},
                            {"title": "bcp", 'editable': True}]

        jumpingX += labelListWdt+marginTable
        self.w.fortyFiveCaption = TextBox((jumpingX+captionOffset, captionY, angleListWdt, vanillaControlsSize['TextBoxSmallHeight']),
                                          u'45°',
                                          sizeStyle='small')

        self.w.fortyFiveList = List((jumpingX, jumpingY, angleListWdt, tableHgt),
                                    [],
                                    columnDescriptions=anglesColumnDesc,
                                    showColumnTitles=True,
                                    rowHeight=tableLineHeight,
                                    editCallback=self.fortyFiveListCallback,
                                    drawHorizontalLines=True,
                                    drawVerticalLines=True,
                                    autohidesScrollers=True,
                                    allowsMultipleSelection=False)

        jumpingX += angleListWdt+marginTable
        self.w.ninetyCaption = TextBox((jumpingX+captionOffset, captionY, angleListWdt, vanillaControlsSize['TextBoxSmallHeight']),
                                       u'90°',
                                       sizeStyle='small')

        self.w.ninetyList = List((jumpingX, jumpingY, angleListWdt, tableHgt),
                                 [],
                                 columnDescriptions=anglesColumnDesc,
                                 showColumnTitles=True,
                                 rowHeight=tableLineHeight,
                                 editCallback=self.ninetyListCallback,
                                 drawHorizontalLines=True,
                                 drawVerticalLines=True,
                                 autohidesScrollers=True,
                                 allowsMultipleSelection=False)

        jumpingX += angleListWdt+marginTable
        self.w.hundredThirtyFiveCaption = TextBox((jumpingX+captionOffset, captionY, angleListWdt, vanillaControlsSize['TextBoxSmallHeight']),
                                                  u'135°',
                                                  sizeStyle='small')

        self.w.hundredThirtyFiveList = List((jumpingX, jumpingY, angleListWdt, tableHgt),
                                            [],
                                            columnDescriptions=anglesColumnDesc,
                                            showColumnTitles=True,
                                            rowHeight=tableLineHeight,
                                            editCallback=self.hundredThirtyFiveListCallback,
                                            drawHorizontalLines=True,
                                            drawVerticalLines=True,
                                            autohidesScrollers=True,
                                            allowsMultipleSelection=False)
        self._fromRoundingsData2Lists()
        jumpingY += tableHgt+MARGIN_ROW*2

        rgtX = MARGIN_HOR+NET_WIDTH*.52
        midWdt = NET_WIDTH*.48
        self.w.pushButton = SquareButton((MARGIN_HOR, jumpingY, midWdt, vanillaControlsSize['ButtonRegularHeight']*1.5),
                                         'Push Data',
                                         callback=self.pushButtonCallback)
        self.w.clearLibButton = SquareButton((rgtX, jumpingY, midWdt, vanillaControlsSize['ButtonRegularHeight']*1.5),
                                             'Clear Lib',
                                             callback=self.clearLibButtonCallback)

        jumpingY += vanillaControlsSize['ButtonRegularHeight']*1.5 + MARGIN_ROW*2
        self.w.sepLineThree = HorizontalLine((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['HorizontalLineThickness']))
        jumpingY += MARGIN_ROW*2

        self.w.sourceLayerCaption = TextBox((MARGIN_HOR, jumpingY, midWdt, vanillaControlsSize['TextBoxRegularHeight']),
                                            'source layer')
        self.w.targetLayerCaption = TextBox((rgtX, jumpingY, midWdt, vanillaControlsSize['TextBoxRegularHeight']),
                                            'target layer')

        jumpingY += vanillaControlsSize['TextBoxRegularHeight'] + MARGIN_ROW
        self.w.sourceLayerPopUp = PopUpButton((MARGIN_HOR, jumpingY, midWdt, vanillaControlsSize['PopUpButtonRegularHeight']),
                                              self.layerNames,
                                              callback=self.sourceLayerPopUpCallback)
        if self.layerNames and self.sourceLayerName:
            self.w.sourceLayerPopUp.set(self.layerNames.index(self.sourceLayerName))

        self.w.targetLayerCombo = ComboBox((rgtX, jumpingY, midWdt, vanillaControlsSize['PopUpButtonRegularHeight']),
                                           self.layerNames,
                                           callback=self.targetLayerComboCallback)
        if self.layerNames and self.targetLayerName:
            self.w.targetLayerCombo.set(self.targetLayerName)

        jumpingY += vanillaControlsSize['PopUpButtonRegularHeight'] + MARGIN_ROW*4
        self.w.roundGlyphButton = SquareButton((MARGIN_HOR, jumpingY, midWdt, vanillaControlsSize['ButtonRegularHeight']*1.5),
                                               u'Round Glyph (⌘+R)',
                                               callback=self.roundGlyphButtonCallback)
        self.w.roundGlyphButton.bind('r', ['command'])

        self.w.roundFontButton = SquareButton((rgtX, jumpingY, midWdt, vanillaControlsSize['ButtonRegularHeight']*1.5),
                                              'Round Font',
                                              callback=self.roundFontButtonCallback)
        jumpingY += vanillaControlsSize['ButtonRegularHeight']*1.5 + MARGIN_VER*2

        self.w.resize(PLUGIN_WIDTH, jumpingY)

        self._checkPushButton()
        self._checkRoundButtons()
        self.setUpBaseWindowBehavior()
        addObserver(self, 'fontDidOpenCallback', 'fontDidOpen')
        addObserver(self, 'fontDidCloseCallback', 'fontDidClose')
        addObserver(self, '_keyDown', 'keyDown')
        self.w.open()

    # private methods
    def _initLogger(self):
        # create a logger
        self.rounderLogger = logging.getLogger('rounderLogger')
        self.rounderLogger.setLevel(logging.INFO)
        # create file handler which logs info messages
        fileHandle = logging.FileHandler('cornersRounderLogger.log')
        fileHandle.setLevel(logging.INFO)
        # create console handler with a higher log level, only errors
        # create formatter and add it to the handlers
        formatter = logging.Formatter(u'%(asctime)s – %(message)s')
        fileHandle.setFormatter(formatter)
        # add the handlers to the logger
        self.rounderLogger.addHandler(fileHandle)

    def _initRoundingsData(self):
        self.roundingsData = [makeRoundingsDataEmptyDict() for ii in range(LABELS_AMOUNT)]

    def _updateFontsAttributes(self):
        self.allFonts = AllFonts()
        if self.allFonts == []:
            self.selectedFont = None

    def _updateRoundingsLabels(self, labels):
        for indexLabel, eachLabel in enumerate(labels):
            self.roundingsData[indexLabel]['labelName'] = '{}'.format(eachLabel['labelName'])

    def _updateRoundingsNumbers(self, data, keyStart):
        for indexRow, eachRow in enumerate(data):

            try:
                self.roundingsData[indexRow]['{}Rad'.format(keyStart)] = int(eachRow['rad'])
            except ValueError:
                self.roundingsData[indexRow]['{}Rad'.format(keyStart)] = ''

            try:
                self.roundingsData[indexRow]['{}Bcp'.format(keyStart)] = int(eachRow['bcp'])
            except ValueError:
                self.roundingsData[indexRow]['{}Bcp'.format(keyStart)] = ''

    def _fromRoundingsData2LabelCtrls(self):
        for eachI in range(LABELS_AMOUNT):
            try:
                labelName = self.roundingsData[eachI]['labelName']
            except IndexError as e:
                labelName = ''
            getattr(self.w, 'label{:d}'.format(eachI)).setLabelName(labelName)

    def _updateLayersCtrls(self):
        self.layerNames = ['foreground'] + self.selectedFont.layerOrder

        currentName = self.w.sourceLayerPopUp.getItems()[self.w.sourceLayerPopUp.get()]
        self.w.sourceLayerPopUp.setItems(self.layerNames)
        if currentName in self.layerNames:
            self.w.sourceLayerPopUp.set(self.layerNames.index(currentName))

        currentName = self.w.targetLayerCombo.get()
        self.w.targetLayerCombo.setItems(self.layerNames)
        if currentName in self.layerNames:
            self.w.targetLayerCombo.set(currentName)

    def _extractDataFromRoundings(self, keyTitle):
        listData = [{'rad': aDict['{}Rad'.format(keyTitle)], 'bcp': aDict['{}Bcp'.format(keyTitle)]} for aDict in self.roundingsData]
        return listData

    def _fromRoundingsData2Lists(self):
        labelNameListData = [{'labelName': aDict['labelName']} for aDict in self.roundingsData]
        self.w.labelNameList.set(labelNameListData)
        fortyFiveListData = self._extractDataFromRoundings('fortyFive')
        self.w.fortyFiveList.set(fortyFiveListData)
        ninetyListData = self._extractDataFromRoundings('ninety')
        self.w.ninetyList.set(ninetyListData)
        hundredThirtyFiveListData = self._extractDataFromRoundings('hundredThirtyFive')
        self.w.hundredThirtyFiveList.set(hundredThirtyFiveListData)

    def _roundCurrentGlyph(self):
        if self.sourceLayerName == self.targetLayerName:
            self.showMessage('ERROR', u'source layer name and target layer name should be different')
            return None

        currentGlyph = CurrentGlyph()
        if currentGlyph is not None:
            self.rounderLogger.info('start: _roundCurrentGlyph(), glyph {} from {} {}'.format(currentGlyph.name, self.selectedFont.info.familyName, self.selectedFont.info.styleName))
            selectedFont = currentGlyph.getParent()
            roundingsData = pullRoundingsDataFromFont(selectedFont)

            if roundingsData is not None:
                makeGlyphRound(currentGlyph,
                               roundingsData,
                               sourceLayerName=self.sourceLayerName,
                               targetLayerName=self.targetLayerName)
                UpdateCurrentGlyphView()
                self.rounderLogger.info('end: _roundCurrentGlyph(), glyph {} from {} {}'.format(currentGlyph.name, selectedFont.info.familyName, selectedFont.info.styleName))
        elif currentGlyph is not None:
            self.showMessage('ERROR', NO_DATA_INTO_FONT)
            self.rounderLogger.error(NO_DATA_INTO_FONT)

        else:
            self.showMessage('ERROR', NO_GLYPH_TO_ROUND)
            self.rounderLogger.error(NO_GLYPH_TO_ROUND)

    # observers callbacks
    def _keyDown(self, notification):
        glyph = notification['glyph']
        pressedKeys = notification['event'].charactersIgnoringModifiers()
        modifierFlags = notification['event'].modifierFlags()
        if modifierFlags in MODIFIERS and MODIFIERS[modifierFlags] == 'CMD_LEFT' and pressedKeys == 'r':
            self._roundCurrentGlyph()

    def fontDidOpenCallback(self, notification):
        if self.allFonts != []:
            currentName = os.path.basename(self.allFonts[self.w.fontPopUp.get()].path)
        else:
            currentName = None
        self._updateFontsAttributes()
        newNames = [os.path.basename(item.path) for item in self.allFonts]
        self.w.fontPopUp.setItems(newNames)

        if currentName is not None:
            self.w.fontPopUp.set(newNames.index(currentName))

    def fontDidCloseCallback(self, notification):
        self._updateFontsAttributes()
        newNames = [os.path.basename(item.path) for item in self.allFonts]
        self.w.fontPopUp.setItems(newNames)

        if self.allFonts != []:
            self.selectedFont = self.allFonts[0]
            self.roundingsData = pullRoundingsDataFromFont(self.selectedFont)
            if self.roundingsData is None:
                self._initRoundingsData()
            self._fromRoundingsData2Lists()
            self._fromRoundingsData2LabelCtrls()
        else:
            self.selectedFont = None
            self.roundingsData = None

    def windowCloseCallback(self, sender):
        removeObserver(self, 'fontDidOpen')
        removeObserver(self, 'fontDidClose')
        removeObserver(self, 'keyDown')
        self.rounderLogger.info('that\'s all folks!')

    # standard callbacks
    def fontPopUpCallback(self, sender):
        self.selectedFont = self.allFonts[sender.get()]
        self.roundingsData = pullRoundingsDataFromFont(self.selectedFont)
        if self.roundingsData is None:
            self._initRoundingsData()
        self._fromRoundingsData2Lists()
        self._fromRoundingsData2LabelCtrls()
        self._updateLayersCtrls()
        self._checkPushButton()

    def attachCallback(self, sender):
        labelName = sender.get()
        attachLabelToSelectedPoints(labelName)

    def _checkPushButton(self):
        if hasattr(self.w, 'pushButton') is True:
            if PLUGIN_LIB_NAME not in self.selectedFont.lib or self.roundingsData != self.selectedFont.lib[PLUGIN_LIB_NAME]:
                self.w.pushButton.enable(True)
            else:
                self.w.pushButton.enable(False)

    def labelNameListCallback(self, sender):
        self._updateRoundingsLabels(sender.get())
        self._checkPushButton()
        self._checkRoundButtons()

    def _checkRoundButtons(self):
        if hasattr(self.w, 'roundGlyphButton') is True and hasattr(self.w, 'roundFontButton'):
            if (PLUGIN_LIB_NAME in self.selectedFont.lib and self.roundingsData != self.selectedFont.lib[PLUGIN_LIB_NAME]) or self.roundingsData == DUMMY_ROUNDINGS:
                self.w.roundGlyphButton.enable(False)
                self.w.roundFontButton.enable(False)
            else:
                self.w.roundGlyphButton.enable(True)
                self.w.roundFontButton.enable(True)

    def fortyFiveListCallback(self, sender):
        self._updateRoundingsNumbers(sender.get(), 'fortyFive')
        self._checkPushButton()
        self._checkRoundButtons()

    def ninetyListCallback(self, sender):
        self._updateRoundingsNumbers(sender.get(), 'ninety')
        self._checkPushButton()
        self._checkRoundButtons()

    def hundredThirtyFiveListCallback(self, sender):
        self._updateRoundingsNumbers(sender.get(), 'hundredThirtyFive')
        self._checkPushButton()
        self._checkRoundButtons()

    def pushButtonCallback(self, sender):
        thisFont = self.selectedFont
        if thisFont is not None:
            pushRoundingsDataIntoFont(thisFont, self.roundingsData)
            self.showMessage('INFO', DATA_PUSHED.format(familyName=thisFont.info.familyName, styleName=thisFont.info.styleName))
            self.rounderLogger.info(DATA_PUSHED.format(familyName=thisFont.info.familyName, styleName=thisFont.info.styleName))
        else:
            self.showMessage('ERROR', NO_FONT_TO_PUSH)
            self.rounderLogger.error(NO_FONT_TO_PUSH)
        self._checkPushButton()
        self._checkRoundButtons()

    def clearLibButtonCallback(self, sender):
        if PLUGIN_LIB_NAME in self.selectedFont.lib:
            del self.selectedFont.lib[PLUGIN_LIB_NAME]
        self._initRoundingsData()
        self._fromRoundingsData2Lists()
        self._fromRoundingsData2LabelCtrls()
        self._checkPushButton()
        self._checkRoundButtons()

    def sourceLayerPopUpCallback(self, sender):
        self.sourceLayerName = self.layerNames[sender.get()]

    def targetLayerComboCallback(self, sender):
        self.targetLayerName = sender.get()

    def roundGlyphButtonCallback(self, sender):
        if self.selectedFont == CurrentFont():
            self._roundCurrentGlyph()
        else:
            self.showMessage('ERROR', FONT_MISMATCH)
            self.rounderLogger.error(FONT_MISMATCH)

    def roundFontButtonCallback(self, sender):
        if self.sourceLayerName == self.targetLayerName:
            self.showMessage('ERROR', LAYERS_MATCH)
            self.rounderLogger.error(LAYERS_MATCH)
            return None

        if self.selectedFont == CurrentFont():
            self.rounderLogger.info('start: roundFontButtonCallback(), {} {}'.format(selectedFont.info.familyName, selectedFont.info.styleName))
            for eachGlyph in self.selectedFont:
                makeGlyphRound(eachGlyph,
                               self.roundingsData,
                               sourceLayerName=self.sourceLayerName,
                               targetLayerName=self.targetLayerName)
            self.rounderLogger.info('end: roundFontButtonCallback(), {} {}'.format(selectedFont.info.familyName, selectedFont.info.styleName))

        else:
            self.showMessage('ERROR', FONT_MISMATCH)
            self.rounderLogger.error(FONT_MISMATCH)


class Label(Group):

    def __init__(self, posSize, attachCallback, labelName=None):
        super(Label, self).__init__(posSize)
        self.labelName = labelName
        self.attachCallback = attachCallback

        self.edit = EditText((0, 0, NET_WIDTH*.7, vanillaControlsSize['EditTextRegularHeight']),
                             text=self.labelName,
                             continuous=True,
                             callback=self.editCallback)

        self.button = SquareButton((NET_WIDTH*.72, 0, NET_WIDTH*.28, vanillaControlsSize['EditTextRegularHeight']),
                                   'attach!',
                                   callback=self.buttonCallback)

    def get(self):
        return self.labelName

    def setLabelName(self, labelName):
        self.labelName = labelName
        self.edit.set(self.labelName)

    def editCallback(self, sender):
        self.labelName = sender.get()

    def buttonCallback(self, sender):
        self.attachCallback(self)


### Instructions
if __name__ == '__main__':
    cr = CornersRounder()
