#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################
# TT Kerning controller #
#########################

### Modules
# custom
import miscFunctions
reload(miscFunctions)
from miscFunctions import loadKerningTexts, buildPairsFromString

import userInterfaceValues
reload(userInterfaceValues)
from userInterfaceValues import vanillaControlsSize

# standard
import os
import json
from mojo.drawingTools import *
from mojo.roboFont import AllFonts
from mojo.canvas import CanvasGroup
from operator import itemgetter
from defconAppKit.windows.baseWindow import BaseWindowController
from vanilla import Window, Group, PopUpButton, List, EditText
from vanilla import CheckBoxListCell, TextBox, SquareButton, HorizontalLine
from vanilla import VerticalLine


### Constants
PLUGIN_TITLE = 'TT Kerning editor'

# func
KERNING_TEXT_FOLDER = 'kerningTexts'
KERNING_STATUS_PATH = 'lastKerningStatus.json'

# colors
LIGHT_RED = (1,0,0,.4)
LIGHT_GREEN = (0,1,0,.4)
BLACK = (0,0,0)

# ui
MARGIN_VER = 8
MARGIN_HOR = 8
MARGIN_COL = 4

LEFT_COLUMN = 200
PLUGIN_WIDTH = 1000
PLUGIN_HEIGHT = 800

TEXT_MARGIN = 200 #upm

WORD_CONTROL_HEIGHT = 100

SYSTEM_FONT_NAME = '.HelveticaNeueDeskInterface-Regular'
SYSTEM_FONT_NAME_BOLD = '.HelveticaNeueDeskInterface-Bold'

"""
Desired keys

A: -4
D: +4
W: previous word
S: following word

return: mark the word as "done"

←: move cursor
→: move cursor
↑: move cursor
↓: move cursor

<: preview mode

"""


### Controllers
class KerningController(BaseWindowController):
    """docstring for KerningController"""

    displayedWord = ''
    displayedPairs = []
    activePair = None

    openedFonts = None
    navCursor_X = 0    # related to pairs
    navCursor_Y = 0    # related to active fonts

    def __init__(self):
        super(KerningController, self).__init__()

        # load opened fonts
        self.updateOpenedFonts()

        # ui
        self.w = Window((0, 0, PLUGIN_WIDTH, PLUGIN_HEIGHT),
                        PLUGIN_TITLE,
                        minSize=(PLUGIN_WIDTH, PLUGIN_HEIGHT))
        self.w.bind('resize', self.mainWindowResize)

        self.jumping_Y = MARGIN_VER
        self.jumping_X = MARGIN_HOR
        self.w.wordListController = WordListController((self.jumping_X, self.jumping_Y, LEFT_COLUMN, 290),
                                                       callback=self.wordListControllerCallback)
        self.displayedWord = self.w.wordListController.get()
        self.displayedPairs = buildPairsFromString(self.displayedWord)
        self.activePair = self.displayedPairs[0]

        self.jumping_Y += self.w.wordListController.getPosSize()[3]+4
        self.w.word_font_separationLine = HorizontalLine((self.jumping_X, self.jumping_Y, LEFT_COLUMN, vanillaControlsSize['HorizontalLineThickness']))

        self.jumping_Y += MARGIN_VER
        self.w.fontController = FontsController((self.jumping_X, self.jumping_Y, LEFT_COLUMN, 200),
                                                self.openedFonts,
                                                callback=self.fontControllerCallback)
        self.activeFonts = self.w.fontController.get()

        self.jumping_X += LEFT_COLUMN+MARGIN_COL*2
        self.jumping_Y = MARGIN_VER
        self.w.displayedWordCaption = TextBox((self.jumping_X, self.jumping_Y, -1, vanillaControlsSize['TextBoxRegularHeight']),
                                              self.displayedWord)

        self.jumping_Y += self.w.displayedWordCaption.getPosSize()[3]+MARGIN_COL
        self.initWordDisplays()

        self.w.open()

    def updateOpenedFonts(self):
        openedFonts = [f for f in AllFonts() if f.path is not None]
        self.openedFonts = sorted(openedFonts, key=lambda f:os.path.basename(f.path))

    def deleteWordDisplays(self):
        for eachI in range(len(self.activeFonts)):
            delattr(self.w, 'wordCtrl_%#02d' % (eachI+1))
        self.jumping_Y = MARGIN_VER+vanillaControlsSize['TextBoxRegularHeight']

    def initWordDisplays(self):
        windowWidth, windowHeight = self.w.getPosSize()[2], self.w.getPosSize()[3]
        netTotalWindowHeight = windowHeight-MARGIN_COL-MARGIN_VER*2-vanillaControlsSize['TextBoxRegularHeight']-MARGIN_HOR*(len(self.activeFonts)-1)
        singleWindowHeight = netTotalWindowHeight/len(self.activeFonts)
        rightColumnWidth = windowWidth-LEFT_COLUMN-MARGIN_COL

        self.jumping_Y = MARGIN_VER+vanillaControlsSize['TextBoxRegularHeight']+MARGIN_COL
        for eachI in range(len(self.activeFonts)):
            wordCtrl = WordDisplay((self.jumping_X, self.jumping_Y, rightColumnWidth, singleWindowHeight),
                                     self.displayedWord,
                                     self.displayedPairs,
                                     self.activeFonts[eachI])
            self.jumping_Y += singleWindowHeight + MARGIN_HOR
            setattr(self.w, 'wordCtrl_%#02d' % (eachI+1), wordCtrl)

    def updateWordDisplays(self):
        for eachI in range(len(self.activeFonts)):
            eachDisplay = getattr(self.w, 'wordCtrl_%#02d' % (eachI+1))
            eachDisplay.displayedWord = self.displayedWord
            eachDisplay.wordCanvasGroup.update()

    def nextWord(self):
        self.w.wordListController.nextWord()
        self.displayedWord = self.w.wordListController.get()
        self.displayedPairs = buildPairsFromString(self.displayedWord)
        if len(self.displayedPairs) > (self.navCursor_X+1):
            self.activePair = self.displayedPairs[self.navCursor_X]
        else:
            self.activePair = self.displayedPairs[0]

    def previousWord(self):
        self.w.wordListController.previousWord()
        self.displayedWord = self.w.wordListController.get()
        self.displayedPairs = buildPairsFromString(self.displayedWord)
        if len(self.displayedPairs) > (self.navCursor_X+1):
            self.activePair = self.displayedPairs[self.navCursor_X]
        else:
            self.activePair = self.displayedPairs[0]

    # cursor methods
    def cursorLeft(self):
        self.navCursor_X = (self.navCursor_X-1)%len(self.displayedPairs)
        getattr(self.w, 'wordCtrl_%#02d' % (self.navCursor_Y+1)).setActivePairIndex(self.navCursor_X)

    def cursorRight(self):
        self.navCursor_X = (self.navCursor_X+1)%len(self.displayedPairs)
        getattr(self.w, 'wordCtrl_%#02d' % (self.navCursor_Y+1)).setActivePairIndex(self.navCursor_X)

    def cursorUp(self):
        self.navCursor_Y = (self.navCursor_Y-1)%len(self.activeFonts)
        getattr(self.w, 'wordCtrl_%#02d' % (self.navCursor_Y)).setActivePairIndex(None)   # old
        getattr(self.w, 'wordCtrl_%#02d' % (self.navCursor_Y+1)).setActivePairIndex(self.navCursor_X)   # new

    def cursorDown(self):
        self.navCursor_Y = (self.navCursor_Y+1)%len(self.activeFonts)
        getattr(self.w, 'wordCtrl_%#02d' % (self.navCursor_Y)).setActivePairIndex(None)   # old
        getattr(self.w, 'wordCtrl_%#02d' % (self.navCursor_Y+1)).setActivePairIndex(self.navCursor_X)   # new

    ### callbacks
    def mainWindowResize(self, mainWindow):
        windowWidth, windowHeight = mainWindow.getPosSize()[2], mainWindow.getPosSize()[3]
        rightColumnWidth = windowWidth - LEFT_COLUMN

        # caption
        prevdisplayedWordCaptionSize = self.w.displayedWordCaption.getPosSize()
        self.w.displayedWordCaption.setPosSize((prevdisplayedWordCaptionSize[0], prevdisplayedWordCaptionSize[1], rightColumnWidth, prevdisplayedWordCaptionSize[3]))

        # displayers
        initY = MARGIN_VER+vanillaControlsSize['TextBoxRegularHeight']+MARGIN_COL
        netTotalWindowHeight = windowHeight-initY-MARGIN_VER-MARGIN_HOR*(len(self.activeFonts)-1)
        singleWordDisplayHeight = netTotalWindowHeight/len(self.activeFonts)

        y = initY
        for eachI in range(len(self.activeFonts)):
            getattr(self.w, 'wordCtrl_%#02d' % (eachI+1)).adjustSize((self.jumping_X, y, rightColumnWidth, singleWordDisplayHeight))
            y += singleWordDisplayHeight+MARGIN_HOR

    def wordListControllerCallback(self, sender):
        self.displayedWord = sender.get()
        self.w.displayedWordCaption.set(self.displayedWord)
        self.updateWordDisplays()

    def fontControllerCallback(self, sender):
        self.deleteWordDisplays()
        self.activeFonts = sender.get()
        self.initWordDisplays()


class WordDisplay(Group):

    def __init__(self, posSize, displayedWord, displayedPairs, fontObj, activePair=None, pairIndex=None):
        super(WordDisplay, self).__init__(posSize)

        self.displayedWord = displayedWord
        self.displayedPairs = displayedPairs
        self.fontObj = fontObj
        self.activePair = activePair
        self.pairIndex = pairIndex

        width, height = posSize[2], posSize[3]
        self.wordCanvasGroup = CanvasGroup((0, 0, 0, 0),
                                           # canvasSize=(width, height),
                                           delegate=self,
                                           # autohidesScrollers=False,
                                           # drawsBackground=True
                                           )

    def adjustSize(self, posSize):
        x, y, width, height = posSize
        self.setPosSize((x, y, width, height))
        self.wordCanvasGroup.setPosSize((0, 0, width, height))
        self.wordCanvasGroup.resize(width, height)
        self.wordCanvasGroup.update()

    def setActivePairIndex(self, pairIndex):
        self.pairIndex = pairIndex
        self.activePair = self.displayedPairs[pairIndex]

    def _drawCorrection(self, correction, displayHeight, descender, unitsPerEm):
        save()

        if correction > 0:
            fill(*LIGHT_GREEN)
        else:
            fill(*LIGHT_RED)
        rect(0, descender, correction, unitsPerEm)

        fill(*BLACK)
        stroke(None)
        translate(0, unitsPerEm)
        scale(1/(displayHeight/2000))
        font(SYSTEM_FONT_NAME)
        fontSize(10)
        textWidth, textHeight = textSize('%s' % correction)
        textBox('%s' % correction, (-textWidth/2., -textHeight, textWidth, textHeight), align='center')
        restore()

    def _drawGlyphOutlines(self, glyphToDisplay):
        save()
        fill(*BLACK)
        stroke(None)
        drawGlyph(glyphToDisplay)
        restore()

    def _drawMetricsData(self, width, leftMargin, rightMargin, offset, displayHeight):
        save()
        fill(*BLACK)
        stroke(None)
        translate(0, offset)

        scale(1/(displayHeight/2000))
        font(SYSTEM_FONT_NAME)
        fontSize(10)
        textBox(u'%s' % width, (0, -11, width*displayHeight/2000, 11), align='center')
        textBox(u'%s       %s' % (leftMargin, rightMargin),  (0, -22, width*displayHeight/2000, 11), align='center')
        restore()

    def draw(self):
        displayHeight = self.getPosSize()[3]

        try:
            save()
            translate(MARGIN_HOR, 0)
            scale(displayHeight/2000)   # the canvas is virtually 2000upm scaled according to ctrl size

            descender, unitsPerEm = self.fontObj.info.descender, self.fontObj.info.unitsPerEm
            flatKerning = self.fontObj.naked().flatKerning
            prevGlyphName = None

            translate(0, 700)
            for indexChar, eachGlyphName in enumerate(self.displayedWord):
                glyphToDisplay = self.fontObj[eachGlyphName]

                # handling kerning correction
                if indexChar > 0:
                    if (prevGlyphName, eachGlyphName) in flatKerning:
                        correction = flatKerning[(prevGlyphName, eachGlyphName)]
                        self._drawCorrection(correction, displayHeight, descender, unitsPerEm)
                        translate(correction, 0)

                # # draw metrics info
                self._drawMetricsData(glyphToDisplay.width, glyphToDisplay.leftMargin, glyphToDisplay.rightMargin, descender*2, displayHeight)

                # # drawing just the black letter
                self._drawGlyphOutlines(glyphToDisplay)
                translate(glyphToDisplay.width, 0)
                prevGlyphName = eachGlyphName

            restore()

        except Exception:
            pass


class FontsController(Group):

    activeFontsAmount = 1
    activeFonts = []
    maxFontsAmount = 4

    def __init__(self, posSize, openedFonts, callback):
        super(FontsController, self).__init__(posSize)
        self.callback = callback
        x, y, self.ctrlWidth, self.ctrlHeight = posSize

        self.openedFonts = openedFonts
        self.displayedFontNames = [os.path.basename(f.path) for f in self.openedFonts]
        self.activeFonts.append(self.openedFonts[0])

        self.jumping_Y = 0
        self.activeFontsCaption = TextBox((0, self.jumping_Y, 130, vanillaControlsSize['TextBoxRegularHeight']),
                                          'how many fonts?')

        activeFontsCaptionWidth = self.activeFontsCaption.getPosSize()[2]
        self.activeFontsAmountPopUp = PopUpButton((-(self.ctrlWidth-activeFontsCaptionWidth), self.jumping_Y, self.ctrlWidth-activeFontsCaptionWidth, vanillaControlsSize['PopUpButtonRegularHeight']),
                                                  ['%s' % i for i in range(1, self.maxFontsAmount+1)],
                                                  callback=self.activeFontsAmountPopUpCallback)

        for eachI in range(self.activeFontsAmount):
            self.jumping_Y += vanillaControlsSize['PopUpButtonRegularHeight']+MARGIN_HOR/2.
            singleFontCtrl = PopUpButton((0, self.jumping_Y, self.ctrlWidth, vanillaControlsSize['PopUpButtonRegularHeight']),
                                         self.displayedFontNames,
                                         callback=self.singleFontCtrlCallback)
            setattr(self, 'singleFontCtrl_%#02d' % (eachI+1), singleFontCtrl)

    def get(self):
        return list(self.activeFonts)

    def setOpenedFonts(self, openedFonts):
        self.openedFonts = openedFonts
        self.displayedFontNames = [os.path.basename(f.path) for f in self.openedFonts]
        for eachI in range(0, self.activeFontsAmount):
            getattr(self, 'singleFontCtrl_%#02d' % (eachI+1)).setItems(self.displayedFontNames)

    def activeFontsAmountPopUpCallback(self, sender):
        gonnaBeActiveFontsAmount = sender.get()+1
        if gonnaBeActiveFontsAmount == self.activeFontsAmount:  # do nothing
            return None

        elif gonnaBeActiveFontsAmount > self.activeFontsAmount: # add ctrls
            for eachI in range(self.activeFontsAmount, gonnaBeActiveFontsAmount):
                self.jumping_Y += vanillaControlsSize['PopUpButtonRegularHeight']+MARGIN_HOR/2.
                singleFontCtrl = PopUpButton((0, self.jumping_Y, self.ctrlWidth, vanillaControlsSize['PopUpButtonRegularHeight']),
                                             self.displayedFontNames,
                                             callback=self.singleFontCtrlCallback)
                setattr(self, 'singleFontCtrl_%#02d' % (eachI+1), singleFontCtrl)
                self.activeFonts.append(self.openedFonts[0])

        else:                                                   # delete ctrls
            for eachI in range(gonnaBeActiveFontsAmount, self.activeFontsAmount):
                self.jumping_Y -= vanillaControlsSize['PopUpButtonRegularHeight']+MARGIN_HOR/2.
                delattr(self, 'singleFontCtrl_%#02d' % (eachI+1))
                self.activeFonts.pop()

        self.activeFontsAmount = gonnaBeActiveFontsAmount
        self.callback(self)

    def singleFontCtrlCallback(self, sender):
        for eachI in range(self.activeFontsAmount):
            if hasattr(self, 'singleFontCtrl_%#02d' % (eachI+1)) is True:
                if getattr(self, 'singleFontCtrl_%#02d' % (eachI+1)) is sender:
                    self.activeFonts[eachI] = self.openedFonts[sender.get()]
                    break
        self.callback(self)


class WordListController(Group):
    """this controller takes good care of word list flow"""

    def __init__(self, posSize, callback):
        super(WordListController, self).__init__(posSize)
        x, y, self.ctrlWidth, self.ctrlHeight = posSize
        self.callback = callback

        # handling kerning words
        self.kerningWordsDB = loadKerningTexts(KERNING_TEXT_FOLDER)
        self.kerningTextBaseNames = self.kerningWordsDB.keys()
        self.activeKerningTextBaseName = self.kerningTextBaseNames[0]
        self.wordsWorkingList = self.kerningWordsDB[self.activeKerningTextBaseName]
        self.wordsDisplayList = list(self.wordsWorkingList)
        self.activeWord = self.wordsWorkingList[0]['word']
        self.wordFilter = ''

        jumping_Y = 0
        self.kerningVocabularyPopUp = PopUpButton((0, jumping_Y, self.ctrlWidth, vanillaControlsSize['PopUpButtonRegularHeight']),
                                                  self.kerningTextBaseNames,
                                                  callback=self.kerningVocabularyPopUpCallback)

        wordsColumnDescriptors = [
            {'title': 'word', 'width': self.ctrlWidth-60, 'editable': False},
            {'title': 'done?', 'width': 35, 'cell': CheckBoxListCell(), 'editable': False}]

        jumping_Y += self.kerningVocabularyPopUp.getPosSize()[3] + MARGIN_VER
        self.wordsListCtrl = List((0, jumping_Y, self.ctrlWidth, 200),
                                  self.wordsDisplayList,
                                  enableDelete=False,
                                  allowsMultipleSelection=False,
                                  columnDescriptions=wordsColumnDescriptors,
                                  selectionCallback=self.wordsListCtrlSelectionCallback,
                                  doubleClickCallback=self.wordsListCtrlDoubleClickCallback)

        jumping_Y += self.wordsListCtrl.getPosSize()[3] + MARGIN_VER
        self.wordsFilterCtrl = EditText((-70, jumping_Y-1, 70, vanillaControlsSize['EditTextRegularHeight']),
                                        placeholder='filter...',
                                        callback=self.wordsFilterCtrlCallback)

        self.wordsDone = len([row['done?'] for row in self.wordsWorkingList if row['done?'] != 0])
        self.infoCaption = TextBox((0, jumping_Y+2, self.ctrlWidth-self.wordsFilterCtrl.getPosSize()[2], vanillaControlsSize['TextBoxRegularHeight']),
                                   'done: %d/%d' % (self.wordsDone, len(self.wordsWorkingList)))

        jumping_Y += self.wordsFilterCtrl.getPosSize()[3] + MARGIN_VER
        self.loadStatus = SquareButton((0, jumping_Y, 90, vanillaControlsSize['ButtonRegularHeight']+2),
                                       'Load status',
                                       callback=self.loadStatusCallback)

        self.saveButton = SquareButton((-90, jumping_Y, 90, vanillaControlsSize['ButtonRegularHeight']+2),
                                       'Save status',
                                       callback=self.saveButtonCallback)

    def get(self):
        return self.activeWord

    def nextWord(self):
        activeWordIndex = self.wordsDisplayList.index(self.activeWord)
        nextWordIndex = (activeWordIndex+1)%len(self.wordsDisplayList)
        self.activeWord = self.wordsDisplayList[nextWordIndex]
        self.wordsListCtrl.setSelection([nextWordIndex])

    def previousWord(self):
        activeWordIndex = self.wordsDisplayList.index(self.activeWord)
        nextWordIndex = (activeWordIndex-1)%len(self.wordsDisplayList)
        self.activeWord = self.wordsDisplayList[nextWordIndex]
        self.wordsListCtrl.setSelection([nextWordIndex])

    def updateInfoCaption(self):
        self.infoCaption.set('done: %d/%d' % (self.wordsDone, len(self.wordsWorkingList)))

    # ctrls callbacks
    def kerningVocabularyPopUpCallback(self, sender):
        self.activeKerningTextBaseName = self.kerningTextBaseNames[sender.get()]
        self.wordsWorkingList = self.kerningWordsDB[self.activeKerningTextBaseName]
        self.activeWord = self.wordsWorkingList[0]['word']
        self.wordsListCtrl.set(self.wordsWorkingList)
        self.callback(self)

    def wordsListCtrlSelectionCallback(self, sender):
        """this takes care of word count"""
        self.wordsDisplayList = [{'word': row['word'], 'done?': row['done?']} for row in sender.get()]
        for eachDisplayedRow in self.wordsDisplayList:
            for indexWorkingRow, eachWorkingRow in enumerate(self.wordsWorkingList):
                if eachWorkingRow['word'] == eachDisplayedRow['word']:
                    self.wordsWorkingList[indexWorkingRow] = eachDisplayedRow
        self.wordsDone = len([row['done?'] for row in self.wordsWorkingList if row['done?'] != 0])
        self.updateInfoCaption()

    def wordsListCtrlDoubleClickCallback(self, sender):
        self.activeWord = self.wordsDisplayList[sender.getSelection()[0]]['word']
        self.callback(self)

    def wordsFilterCtrlCallback(self, sender):
        self.wordFilter = sender.get()
        self.wordsDisplayList = [row for row in self.wordsWorkingList if self.wordFilter in row['word']]
        self.wordsListCtrl.set(self.wordsDisplayList)
        if len(self.wordsDisplayList) == 0:
            self.activeWord = None
        else:
            if self.activeWord not in [row['word'] for row in self.wordsDisplayList]:
                self.activeWord = self.wordsDisplayList[0]['word']
        self.callback(self)

    def loadStatusCallback(self, sender):
        if os.path.exists(KERNING_STATUS_PATH) is True:
            jsonFile = open(KERNING_STATUS_PATH, 'w')
            statusDictionary = json.load(jsonFile)
            jsonFile.close()

            # unwrap dictionaries
            self.kerningWordsDB = statusDictionary['kerningWordsDB']
            self.kerningTextBaseNames = statusDictionary['kerningTextBaseNames']
            self.activeKerningTextBaseName = statusDictionary['activeKerningTextBaseName']
            self.wordsWorkingList = statusDictionary['wordsWorkingList']
            self.wordsDisplayList = statusDictionary['wordsDisplayList']
            self.activeWord = statusDictionary['activeWord']
            self.wordFilter = statusDictionary['wordFilter']

            # adjust controllers
            self.kerningVocabularyPopUp.setItems(self.kerningTextBaseNames)
            self.kerningVocabularyPopUp.set(self.kerningTextBaseNames[self.kerningTextBaseNames.index(self.activeKerningTextBaseName)])
            self.wordsListCtrl.set(self.wordsDisplayList)
            self.wordsListCtrl.setSelection([self.wordsDisplayList.index(self.activeWord)])
            self.updateInfoCaption()

        else:
            print 'there is no previous status to load'

    def saveButtonCallback(self, sender):
        statusDict = {
            'kerningWordsDB': self.kerningWordsDB,
            'kerningTextBaseNames': self.kerningTextBaseNames,
            'activeKerningTextBaseName': self.activeKerningTextBaseName,
            'wordsWorkingList': self.wordsWorkingList,
            'wordsDisplayList': self.wordsDisplayList,
            'activeWord': self.activeWord,
            'wordFilter': self.wordFilter}
        jsonFile = open(KERNING_STATUS_PATH, 'w')
        json.dump(statusDict, jsonFile, indent=4)
        jsonFile.write('\n')
        jsonFile.close()


kc = KerningController()
