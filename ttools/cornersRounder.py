#!/usr/bin/env python
# coding: utf-8

################
# Corner Tools #
################

### Modules
# custom
import ui.userInterfaceValues
reload(ui.userInterfaceValues)
from ui.userInterfaceValues import vanillaControlsSize

import extraTools.roundingTools
reload(extraTools.roundingTools)
from extraTools.roundingTools import attachLabelToSelectedPoints, makeGlyphRound

# standard
from mojo.events import addObserver, removeObserver
from mojo.UI import UpdateCurrentGlyphView
from defconAppKit.windows.baseWindow import BaseWindowController
from vanilla import FloatingWindow, Group, EditText, SquareButton
from vanilla import List, HorizontalLine, TextBox, PopUpButton, ComboBox
from vanilla.dialogs import message

### Constants
PLUGIN_TITLE = 'TT Round Corners'
PLUGIN_WIDTH = 280
PLUGIN_HEIGHT = 600

MARGIN_VER = 8
MARGIN_HOR = 8
MARGIN_ROW = 4
NET_WIDTH = PLUGIN_WIDTH - MARGIN_HOR*2

PLUGIN_LIB_NAME = 'com.ttools.roundCornersData'

### Functions
def pushRoudingsDataIntoFont(aFont, roundingsData):
    aFont.lib[PLUGIN_LIB_NAME] = roundingsData

def loadRoundingsDataFromFont(aFont):
    if PLUGIN_LIB_NAME in aFont.lib:
        return aFont.lib[PLUGIN_LIB_NAME]


### Classes
class CornersRounder(BaseWindowController):

    LABELS_AMOUNT = 4
    labels = ['standard', 'small', None, None]

    layerNames = None
    targetLayerName = None
    sourceLayerName = None

    roundingsData = None

    def __init__(self):
        super(CornersRounder, self).__init__()

        if CurrentFont():
            self.layerNames = ['foreground'] + CurrentFont().layerOrder
            self.sourceLayerName = self.layerNames[1]
            self.targetLayerName = self.layerNames[0]

            if PLUGIN_LIB_NAME in CurrentFont().lib:
                self.roundingsData = loadRoundingsDataFromFont(CurrentFont())
            else:
                self._initRoundingsData()

        self.w = FloatingWindow((0, 0, PLUGIN_WIDTH, PLUGIN_HEIGHT), PLUGIN_TITLE)

        jumpingY = MARGIN_VER
        for eachI in range(self.LABELS_AMOUNT):
            singleLabel = Label((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['EditTextRegularHeight']),
                                index=eachI,
                                labelNameCallback=self.labelCallback,
                                attachCallback=self.attachCallback,
                                labelName=self.labels[eachI])

            setattr(self.w, 'label{:d}'.format(eachI), singleLabel)
            jumpingY += MARGIN_ROW+vanillaControlsSize['EditTextRegularHeight']

        jumpingY += MARGIN_ROW
        self.w.sepLineOne = HorizontalLine((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['HorizontalLineThickness']))
        jumpingY += MARGIN_ROW*2

        # tables
        labelListWdt = 80
        marginTable = 2
        angleListWdt = (NET_WIDTH-labelListWdt-marginTable*3)//3
        tableLineHeight = 16
        tableHgt = 89

        captionY = jumpingY
        captionOffset = 12
        jumpingY += vanillaControlsSize['TextBoxSmallHeight']+MARGIN_ROW

        labelColumnDesc = [{"title": "label", 'editable': True}]
        jumpingX = MARGIN_HOR

        labelNameListData = [{'label': aDict['labelName']} for aDict in self.roundingsData]
        self.w.labelNameList = List((jumpingX, jumpingY, labelListWdt, tableHgt),
                                    labelNameListData,
                                    columnDescriptions=labelColumnDesc,
                                    showColumnTitles=True,
                                    rowHeight=tableLineHeight,
                                    drawHorizontalLines=True,
                                    drawVerticalLines=True,
                                    allowsMultipleSelection=False)

        anglesColumnDesc = [{"title": "rad", 'editable': True},
                            {"title": "bcp", 'editable': True}]

        jumpingX += labelListWdt+marginTable
        self.w.fortyFiveCaption = TextBox((jumpingX+captionOffset, captionY, angleListWdt, vanillaControlsSize['TextBoxSmallHeight']),
                                        u'45°',
                                        sizeStyle='small')

        fortyFiveListData = self._extractDataFromRoundings('fortyFive')
        self.w.fortyFiveList = List((jumpingX, jumpingY, angleListWdt, tableHgt),
                                    fortyFiveListData,
                                    columnDescriptions=anglesColumnDesc,
                                    showColumnTitles=True,
                                    rowHeight=tableLineHeight,
                                    editCallback=self.fortyFiveListCallback,
                                    drawHorizontalLines=True,
                                    drawVerticalLines=True,
                                    allowsMultipleSelection=False)

        jumpingX += angleListWdt+marginTable
        self.w.ninetyCaption = TextBox((jumpingX+captionOffset, captionY, angleListWdt, vanillaControlsSize['TextBoxSmallHeight']),
                                     u'90°',
                                     sizeStyle='small')

        ninetyListData = self._extractDataFromRoundings('ninety')
        self.w.ninetyList = List((jumpingX, jumpingY, angleListWdt, tableHgt),
                                 ninetyListData,
                                 columnDescriptions=anglesColumnDesc,
                                 showColumnTitles=True,
                                 rowHeight=tableLineHeight,
                                 editCallback=self.ninetyListCallback,
                                 drawHorizontalLines=True,
                                 drawVerticalLines=True,
                                 allowsMultipleSelection=False)

        jumpingX += angleListWdt+marginTable
        self.w.hundredThirtyFiveCaption = TextBox((jumpingX+captionOffset, captionY, angleListWdt, vanillaControlsSize['TextBoxSmallHeight']),
                                                  u'135°',
                                                  sizeStyle='small')

        hundredThirtyFiveListData = self._extractDataFromRoundings('hundredThirtyFive')
        self.w.hundredThirtyFiveList = List((jumpingX, jumpingY, angleListWdt, tableHgt),
                                            hundredThirtyFiveListData,
                                            columnDescriptions=anglesColumnDesc,
                                            showColumnTitles=True,
                                            rowHeight=tableLineHeight,
                                            editCallback=self.hundredThirtyFiveListCallack,
                                            drawHorizontalLines=True,
                                            drawVerticalLines=True,
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

        jumpingY += vanillaControlsSize['PopUpButtonRegularHeight']+ MARGIN_ROW*4
        self.w.roundGlyphButton = SquareButton((MARGIN_HOR, jumpingY, midWdt, vanillaControlsSize['ButtonRegularHeight']*1.5),
                                               'Round Glyph',
                                               callback=self.roundGlyphButtonCallback)

        self.w.roundFontButton = SquareButton((rgtX, jumpingY, midWdt, vanillaControlsSize['ButtonRegularHeight']*1.5),
                                              'Round Font',
                                              callback=self.roundFontButtonCallback)
        jumpingY += vanillaControlsSize['ButtonRegularHeight']*1.5 + MARGIN_VER*2

        addObserver(self, '_updateCurrentFontData', 'fontBecameCurrent')

        self.w.resize(PLUGIN_WIDTH, jumpingY)
        self.w.bind('close', self.windowCloseCallback)
        self.w.open()

    # private methods
    def _initRoundingsData(self):
        self.roundingsData = [
            dict(labelName='standard',
                 fortyFiveRad=32,
                 fortyFiveBcp=16,
                 ninetyRad=24,
                 ninetyBcp=16,
                 hundredThirtyFiveRad=32,
                 hundredThirtyFiveBcp=26),

            dict(labelName='small',
                 fortyFiveRad=24,
                 fortyFiveBcp=12,
                 ninetyRad=18,
                 ninetyBcp=12,
                 hundredThirtyFiveRad=24,
                 hundredThirtyFiveBcp=16),

            dict(labelName='',
                 fortyFiveRad='',
                 fortyFiveBcp='',
                 ninetyRad='',
                 ninetyBcp='',
                 hundredThirtyFiveRad='',
                 hundredThirtyFiveBcp=''),

            dict(labelName='',
                 fortyFiveRad='',
                 fortyFiveBcp='',
                 ninetyRad='',
                 ninetyBcp='',
                 hundredThirtyFiveRad='',
                 hundredThirtyFiveBcp='')]

    def _updateCurrentFontData(self):
        self._updateRoundingsData()
        self._updateLayersData()

    def _updateLayersData(self):
        self.layerNames = ['foreground'] + CurrentFont().layerOrder
        self.w.sourceLayerPopUp.setItems(self.layers)
        self.w.targetLayerCombo.setItems(self.layers)

    def _updateRoundingsData(self, data, keyStart):
        for indexRow, eachRow in enumerate(data):
            try:
                self.roundingsData[indexRow]['{}Rad'.format(keyStart)] = int(eachRow['rad'])
            except ValueError:
                self.roundingsData[indexRow]['{}Rad'.format(keyStart)] = ''

            try:
                self.roundingsData[indexRow]['{}Bcp'.format(keyStart)] = int(eachRow['bcp'])
            except ValueError:
                self.roundingsData[indexRow]['{}Bcp'.format(keyStart)] = ''

    def _extractDataFromRoundings(self, keyTitle):
        listData = [{'rad': aDict['{}Rad'.format(keyTitle)], 'bcp': aDict['{}Bcp'.format(keyTitle)]} for aDict in self.roundingsData]
        return listData

    def _alignListsToRoundingsData(self):
        fortyFiveListData = self._extractDataFromRoundings('fortyFive')
        self.w.fortyFiveList.set(fortyFiveListData)
        ninetyListData = self._extractDataFromRoundings('ninety')
        self.w.ninetyList.set(ninetyListData)
        hundredThirtyFiveListData = self._extractDataFromRoundings('hundredThirtyFive')
        self.w.hundredThirtyFiveList.set(hundredThirtyFiveListData)

    # callbacks
    def windowCloseCallback(self, sender):
        removeObserver(self, 'fontBecameCurrent')

    def labelCallback(self, sender):
        index, labelName = sender.get()
        self.labels[index] = labelName

    def attachCallback(self, sender):
        _, labelName = sender.get()
        attachLabelToSelectedPoints(labelName)

    def fortyFiveListCallback(self, sender):
        self._updateRoundingsData(sender.get(), 'fortyFive')

    def ninetyListCallback(self, sender):
        self._updateRoundingsData(sender.get(), 'ninety')

    def hundredThirtyFiveListCallack(self, sender):
        self._updateRoundingsData(sender.get(), 'hundredThirtyFive')

    def saveButtonCallback(self, sender):
        current = CurrentFont()
        if current is not None:
            pushRoudingsDataIntoFont(current, self.roundingsData)
            message('Data saved into {} {}'.format(current.info.family, current.info.styleName))
        else:
            message('I do not know where to save these values ¯\_(ツ)_/¯')

    def loadButtonCallback(self, sender):
        current = CurrentFont()
        if current is not None:
            self.roundingsData =loadRoundingsDataFromFont(current)
            self._alignListsToRoundingsData()
            message('Data loaded from {} {}'.format(current.info.family, current.info.styleName))
        else:
            message('I see no fonts opened, sorry ¯\_(ツ)_/¯')

    def sourceLayerPopUpCallback(self, sender):
        self.sourceLayerName = self.layerNames[sender.get()]

    def targetLayerComboCallback(self, sender):
        self.targetLayerName = sender.get()

    def roundGlyphButtonCallback(self, sender):
        if CurrentGlyph() is not None:
            makeGlyphRound(CurrentGlyph(),
                           self.roundingsData,
                           sourceLayerName=self.sourceLayerName,
                           targetLayerName=self.targetLayerName)
            UpdateCurrentGlyphView()
        else:
            message('No Current Glyph to round!')

    def roundFontButtonCallback(self, sender):
        if CurrentFont() is not None:
            for eachGlyph in CurrentFont():
                makeGlyphRound(eachGlyph,
                               self.roundingsData,
                               sourceLayerName=self.sourceLayerName,
                               targetLayerName=self.targetLayerName)
        else:
            message('No Current Glyph to round!')


class Label(Group):

    def __init__(self, posSize, index, labelNameCallback, attachCallback, labelName=None):
        super(Label, self).__init__(posSize)
        self.labelName = labelName
        self.index = index
        self.labelNameCallback = labelNameCallback
        self.attachCallback = attachCallback

        self.edit = EditText((0, 0, NET_WIDTH*.7, vanillaControlsSize['EditTextRegularHeight']),
                             text=self.labelName,
                             continuous=True,
                             callback=self.editCallback)

        self.button = SquareButton((NET_WIDTH*.72, 0, NET_WIDTH*.28, vanillaControlsSize['EditTextRegularHeight']),
                                   'attach!',
                                   callback=self.buttonCallback)

    def get(self):
        return self.index, self.labelName

    def editCallback(self, sender):
        self.labelName = sender.get()
        self.labelNameCallback(self)

    def buttonCallback(self, sender):
        self.attachCallback(self)


### Instructions
cr = CornersRounder()

