#!/usr/bin/env python
# coding: utf-8

################
# Corner Tools #
################

### Modules
# custom
import constants
reload(constants)
from constants import MODIFIERS

import ui.userInterfaceValues
reload(ui.userInterfaceValues)
from ui.userInterfaceValues import vanillaControlsSize

import extraTools.roundingTools
reload(extraTools.roundingTools)
from extraTools.roundingTools import attachLabelToSelectedPoints, makeGlyphRound

# standard
from mojo.roboFont import CurrentFont, CurrentGlyph, version
from mojo.events import addObserver, removeObserver
from mojo.UI import UpdateCurrentGlyphView
from defconAppKit.windows.baseWindow import BaseWindowController
from vanilla import Window, Group, EditText, SquareButton
from vanilla import List, HorizontalLine, TextBox, PopUpButton, ComboBox
from vanilla.dialogs import message

### Constants
PLUGIN_TITLE = 'TT Round Corners'
PLUGIN_WIDTH = 320
PLUGIN_HEIGHT = 600

MARGIN_VER = 8
MARGIN_HOR = 8
MARGIN_ROW = 4
NET_WIDTH = PLUGIN_WIDTH - MARGIN_HOR*2

PLUGIN_LIB_NAME = 'com.ttools.roundCornersData'


### Functions
def pushRoundingsDataIntoFont(aFont, someData):
    aFont.lib[PLUGIN_LIB_NAME] = [dict(aDict) for aDict in someData]
    if version[0] == '2':
        aFont.changed()
    else:
        aFont.update()


def loadRoundingsDataFromFont(aFont):
    if PLUGIN_LIB_NAME in aFont.lib:
        return [dict(aDict) for aDict in aFont.lib[PLUGIN_LIB_NAME]]


### Classes
class CornersRounder(BaseWindowController):

    LABELS_AMOUNT = 4

    layerNames = None
    targetLayerName = None
    sourceLayerName = None

    roundingsData = None



    def __init__(self):
        super(CornersRounder, self).__init__()

        self._initRoundingsData()

        if CurrentFont() is not None:
            self.layerNames = ['foreground'] + CurrentFont().layerOrder
            self.sourceLayerName = self.layerNames[1]
            self.targetLayerName = self.layerNames[0]

            if PLUGIN_LIB_NAME in CurrentFont().lib:
                self.roundingsData = loadRoundingsDataFromFont(CurrentFont())

        self.w = Window((0, 0, PLUGIN_WIDTH, PLUGIN_HEIGHT), PLUGIN_TITLE)

        jumpingY = MARGIN_VER
        for eachI in range(self.LABELS_AMOUNT):
            singleLabel = Label((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['EditTextRegularHeight']),
                                attachCallback=self.attachCallback,
                                labelName='')

            setattr(self.w, 'label{:d}'.format(eachI), singleLabel)
            jumpingY += MARGIN_ROW+vanillaControlsSize['EditTextRegularHeight']
        self._alignLabelCtrlsToRoundingsData()

        jumpingY += MARGIN_ROW
        self.w.sepLineOne = HorizontalLine((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['HorizontalLineThickness']))
        jumpingY += MARGIN_ROW*2

        # tables
        labelListWdt = 78
        marginTable = 1
        angleListWdt = (NET_WIDTH-labelListWdt-marginTable*3)//3
        tableLineHeight = 16
        tableHgt = 89

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
        self._alignListsToRoundingsData()
        jumpingY += tableHgt+MARGIN_ROW*2

        rgtX = MARGIN_HOR+NET_WIDTH*.52
        midWdt = NET_WIDTH*.48
        self.w.saveButton = SquareButton((MARGIN_HOR, jumpingY, midWdt, vanillaControlsSize['ButtonRegularHeight']*1.5),
                                         'Save Data',
                                         callback=self.saveButtonCallback)

        self.w.loadButton = SquareButton((rgtX, jumpingY, midWdt, vanillaControlsSize['ButtonRegularHeight']*1.5),
                                         'Load Data',
                                         callback=self.loadButtonCallback)

        jumpingY += vanillaControlsSize['ButtonRegularHeight']*1.5 + MARGIN_ROW*2
        self.w.sepLineTwo = HorizontalLine((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['HorizontalLineThickness']))
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

        self.setUpBaseWindowBehavior()
        addObserver(self, '_updateLayersData', 'fontBecameCurrent')
        addObserver(self, '_keyDown', 'keyDown')

        self.w.open()

    # private methods
    def _makeEmptyDict(self):
        return dict(labelName='',
                    fortyFiveRad='',
                    fortyFiveBcp='',
                    ninetyRad='',
                    ninetyBcp='',
                    hundredThirtyFiveRad='',
                    hundredThirtyFiveBcp='')

    def _initRoundingsData(self):
        self.roundingsData = [self._makeEmptyDict(),
                              self._makeEmptyDict(),
                              self._makeEmptyDict(),
                              self._makeEmptyDict()]

    def _updateLayersData(self):
        self.layerNames = ['foreground'] + CurrentFont().layerOrder
        self.w.sourceLayerPopUp.setItems(self.layers)
        self.w.targetLayerCombo.setItems(self.layers)

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

    def _alignLabelCtrlsToRoundingsData(self):
        for eachI in range(self.LABELS_AMOUNT):
            try:
                labelName = self.roundingsData[eachI]['labelName']
            except IndexError as e:
                labelName = ''
            getattr(self.w, 'label{:d}'.format(eachI)).setLabelName(labelName)

    def _extractDataFromRoundings(self, keyTitle):
        listData = [{'rad': aDict['{}Rad'.format(keyTitle)], 'bcp': aDict['{}Bcp'.format(keyTitle)]} for aDict in self.roundingsData]
        return listData

    def _alignListsToRoundingsData(self):
        labelNameListData = [{'labelName': aDict['labelName']} for aDict in self.roundingsData]
        self.w.labelNameList.set(labelNameListData)
        fortyFiveListData = self._extractDataFromRoundings('fortyFive')
        self.w.fortyFiveList.set(fortyFiveListData)
        ninetyListData = self._extractDataFromRoundings('ninety')
        self.w.ninetyList.set(ninetyListData)
        hundredThirtyFiveListData = self._extractDataFromRoundings('hundredThirtyFive')
        self.w.hundredThirtyFiveList.set(hundredThirtyFiveListData)

    def _roundCurrentGlyph(self):
        if CurrentGlyph() is not None:
            makeGlyphRound(CurrentGlyph(),
                           self.roundingsData,
                           sourceLayerName=self.sourceLayerName,
                           targetLayerName=self.targetLayerName)
            UpdateCurrentGlyphView()
        else:
            message(u'No Current Glyph to round!')

    # callbacks
    def _keyDown(self, notification):
        glyph = notification['glyph']
        pressedKeys = notification['event'].charactersIgnoringModifiers()
        modifierFlags = notification['event'].modifierFlags()
        if modifierFlags in MODIFIERS and MODIFIERS[modifierFlags] == 'CMD_LEFT' and pressedKeys == 'r':
            self._roundCurrentGlyph()

    def windowCloseCallback(self, sender):
        removeObserver(self, 'fontBecameCurrent')
        removeObserver(self, 'keyDown')

    def attachCallback(self, sender):
        labelName = sender.get()
        attachLabelToSelectedPoints(labelName)

    def labelNameListCallback(self, sender):
        self._updateRoundingsLabels(sender.get())

    def fortyFiveListCallback(self, sender):
        self._updateRoundingsNumbers(sender.get(), 'fortyFive')

    def ninetyListCallback(self, sender):
        self._updateRoundingsNumbers(sender.get(), 'ninety')

    def hundredThirtyFiveListCallback(self, sender):
        self._updateRoundingsNumbers(sender.get(), 'hundredThirtyFive')

    def saveButtonCallback(self, sender):
        thisFont = CurrentFont()
        if thisFont is not None:
            pushRoundingsDataIntoFont(thisFont, self.roundingsData)
            message(u'Data saved into {} {}'.format(thisFont.info.familyName, thisFont.info.styleName))
        else:
            message(u'I do not know where to save these values ¯\_(ツ)_/¯')

    def loadButtonCallback(self, sender):
        thisFont = CurrentFont()
        if thisFont is not None:
            self.roundingsData = loadRoundingsDataFromFont(thisFont)
            self._alignListsToRoundingsData()
            self._alignLabelCtrlsToRoundingsData()
            message(u'Data loaded from {} {}'.format(thisFont.info.familyName, thisFont.info.styleName))
        else:
            message(u'I see no fonts opened, sorry ¯\_(ツ)_/¯')

    def sourceLayerPopUpCallback(self, sender):
        self.sourceLayerName = self.layerNames[sender.get()]

    def targetLayerComboCallback(self, sender):
        self.targetLayerName = sender.get()

    def roundGlyphButtonCallback(self, sender):
        self._roundCurrentGlyph()

    def roundFontButtonCallback(self, sender):
        if CurrentFont() is not None:
            for eachGlyph in CurrentFont():
                makeGlyphRound(eachGlyph,
                               self.roundingsData,
                               sourceLayerName=self.sourceLayerName,
                               targetLayerName=self.targetLayerName)
        else:
            message(u'No Current Glyph to round!')


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
