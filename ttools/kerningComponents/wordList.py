#!/usr/bin/env python
# coding: utf-8

### Modules
# custom
import kerningMisc
reload(kerningMisc)
from kerningMisc import loadKerningTexts
from kerningMisc import MARGIN_VER

from ..ui import userInterfaceValues
reload(userInterfaceValues)
from ..ui.userInterfaceValues import vanillaControlsSize

# standard
import os
import json
from vanilla import Group, PopUpButton, List, EditText, TextBox
from vanilla import SquareButton, CheckBoxListCell
from vanilla.dialogs import getFile, putFile

### Constants
KERNING_TEXT_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'resources', 'kerningTexts')

### Classes
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
        self.wordsListCtrl = List((0, jumping_Y, self.ctrlWidth, 170),
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
        activeWordData = [wordData for wordData in self.wordsDisplayList if wordData['word'] == self.activeWord][0]
        activeWordIndex = self.wordsDisplayList.index(activeWordData)
        nextWordIndex = (activeWordIndex+1)%len(self.wordsDisplayList)
        self.activeWord = self.wordsDisplayList[nextWordIndex]['word']
        self.wordsListCtrl.setSelection([nextWordIndex])

    def previousWord(self):
        activeWordData = [wordData for wordData in self.wordsDisplayList if wordData['word'] == self.activeWord][0]
        activeWordIndex = self.wordsDisplayList.index(activeWordData)
        previousWordIndex = (activeWordIndex-1)%len(self.wordsDisplayList)
        self.activeWord = self.wordsDisplayList[previousWordIndex]['word']
        self.wordsListCtrl.setSelection([previousWordIndex])

    def switchActiveWordSolvedAttribute(self):
        activeWordData = [wordData for wordData in self.wordsDisplayList if wordData['word'] == self.activeWord][0]
        activeWordIndex = self.wordsDisplayList.index(activeWordData)
        if activeWordData['done?'] == 0:
            self.wordsDisplayList[activeWordIndex] = {'done?': 1, 'word': self.activeWord}
        else:
            self.wordsDisplayList[activeWordIndex] = {'done?': 0, 'word': self.activeWord}
        self.wordsListCtrl.set(self.wordsDisplayList)
        self.wordsListCtrl.setSelection([activeWordIndex])

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
        kerningStatusPath = getFile(title='Load Kerning Status JSON file',
                                    allowsMultipleSelection=False)[0]

        if os.path.splitext(os.path.basename(kerningStatusPath))[1] == '.json':
            jsonFile = open(kerningStatusPath, 'r')
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
            self.kerningVocabularyPopUp.set(self.kerningTextBaseNames.index(self.activeKerningTextBaseName))
            self.wordsListCtrl.set(self.wordsDisplayList)

            for indexRow, eachRow in enumerate(self.wordsDisplayList):
                if eachRow['word'] == self.activeWord:
                    self.wordsListCtrl.setSelection([indexRow])
                    break

            self.updateInfoCaption()
            self.callback(self)

        else:
            message('No JSON, no party!', 'Chosen file is not in the right format')

    def saveButtonCallback(self, sender):
        statusDict = {
            'kerningWordsDB': self.kerningWordsDB,
            'kerningTextBaseNames': self.kerningTextBaseNames,
            'activeKerningTextBaseName': self.activeKerningTextBaseName,
            'wordsWorkingList': self.wordsWorkingList,
            'wordsDisplayList': self.wordsDisplayList,
            'activeWord': self.activeWord,
            'wordFilter': self.wordFilter}

        kerningStatusPath = putFile(title='Save Kerning Status JSON file',
                                    fileName='kerningStatus.json',
                                    canCreateDirectories=True)

        jsonFile = open(kerningStatusPath, 'w')
        json.dump(statusDict, jsonFile, indent=4)
        jsonFile.write('\n')
        jsonFile.close()
