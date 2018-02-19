#!/usr/bin/env python
# coding: utf-8

"""elements for the top bar"""

### Modules
# custom
from ..ui import userInterfaceValues
reload(userInterfaceValues)
from ..ui.userInterfaceValues import vanillaControlsSize

# standard
import os, codecs, types
from collections import OrderedDict
from defconAppKit.tools.textSplitter import splitText
from vanilla import Group, EditText, PopUpButton, SquareButton, TextBox
from vanilla.dialogs import getFolder

### Constants
MARGIN_RGT = 15
MARGIN_COL = 10

RESOURCES_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'resources')
SPACING_TEXTS_FOLDER_PATH = os.path.join(RESOURCES_FOLDER, 'spacingTexts')

### Classes and functions
def loadSpacingTexts(folderName):
    spacingTextDB = OrderedDict()
    spacingTextPaths = [os.path.join(folderName, pth) for pth in os.listdir(folderName) if pth.endswith('.txt')]
    spacingTextPaths.sort()
    for eachPath in spacingTextPaths:
        with codecs.open(eachPath, 'r', 'utf-8') as spacingText:
            spacingRows = [word.strip() for word in spacingText if word]
        cleanTextName = os.path.basename(eachPath).replace('.txt', '')
        if cleanTextName[0:2].isdigit() and cleanTextName[2] == '_':
            cleanTextName = cleanTextName[3:]
        spacingTextDB[cleanTextName] = spacingRows
    return spacingTextDB

class Typewriter(Group):

    # attrs
    glyphNamesToDisplay = []
    title = 'Typewriter'

    leftGlyphNames = []
    centerGlyphNames = []
    rightGlyphNames = []
    typewriterGlyphNames = []

    siblingsWidth = 40

    def __init__(self, posSize, unicodeMinimum, callback):
        Group.__init__(self, posSize)
        self.callback = callback
        self.unicodeMinimum = unicodeMinimum
        ctrlWidth = posSize[2]

        self.leftSiblingEdit = EditText((0, 0, self.siblingsWidth, vanillaControlsSize['EditTextRegularHeight']),
                                        callback=self.leftSiblingEditCallback)

        self.typewriterEdit = EditText((self.siblingsWidth+MARGIN_COL, 0, -(self.siblingsWidth+MARGIN_COL), vanillaControlsSize['EditTextRegularHeight']),
                                       callback=self.typewriterEditCallback)

        self.rightSiblingEdit = EditText((-self.siblingsWidth, 0, self.siblingsWidth, vanillaControlsSize['EditTextRegularHeight']),
                                         callback=self.rightSiblingEditCallback)

    def leftSiblingEditCallback(self, sender):
        if sender.get() is not None:
            self.leftGlyphNames = splitText(sender.get(), self.unicodeMinimum)
        else:
            self.leftGlyphNames = []
        self.callback(self)

    def typewriterEditCallback(self, sender):
        centerText = u'{}'.format(sender.get())

        if centerText is not None:
            # we try to support new line chars
            if r'\n ' in centerText:
                self.centerGlyphNames = []
                someLines = centerText.split(r'\n ')
                for indexLine, eachLine in enumerate(someLines):
                    glyphNames = splitText(eachLine, self.unicodeMinimum)
                    self.centerGlyphNames.extend(glyphNames)
                    if indexLine != len(someLines)-1:
                        self.centerGlyphNames.append('.newLine')
            else:
                self.centerGlyphNames = splitText(centerText, self.unicodeMinimum)
        else:
            self.centerGlyphNames = []
        self.callback(self)

    def rightSiblingEditCallback(self, sender):
        if sender.get() is not None:
            self.rightGlyphNames = splitText(sender.get(), self.unicodeMinimum)
        else:
            self.rightGlyphNames = []
        self.callback(self)

    def setUnicodeMinimum(self, unicodeMinimum):
        assert isinstance(unicodeMinimum, DictType), 'unicode minimum is not a dict'
        self.unicodeMinimum = unicodeMinimum

    def get(self):
        self.typewriterGlyphNames = []
        for eachGlyphName in self.centerGlyphNames:
            self.typewriterGlyphNames.extend(self.leftGlyphNames)
            self.typewriterGlyphNames.extend([eachGlyphName])
            self.typewriterGlyphNames.extend(self.rightGlyphNames)
        return self.typewriterGlyphNames

    def show(self, onOff):
        assert onOff in (True, False)
        self.leftSiblingEdit.show(onOff)
        self.typewriterEdit.show(onOff)
        self.rightSiblingEdit.show(onOff)


class TextStringsControls(Group):

    # attrs
    stringOptions = ('Waterfall', 'Shuffled')
    title = 'Loaded Strings'

    def __init__(self, posSize, unicodeMinimum, callback):
        Group.__init__(self, posSize)
        self.unicodeMinimum = unicodeMinimum
        self.callback = callback
        self._initTexts(SPACING_TEXTS_FOLDER_PATH)

        jumpingX = 1
        textModePopUpWidth = 86
        self.textModePopUp = PopUpButton((jumpingX, 0, textModePopUpWidth, vanillaControlsSize['PopUpButtonRegularHeight']),
                                         self.stringOptions,
                                         callback=self.textModePopUpCallback)

        openTextsFolderButtonWdt = 86
        jumpingX += textModePopUpWidth + MARGIN_COL
        self.openTextsFolderButton = SquareButton((jumpingX, 0, openTextsFolderButtonWdt, vanillaControlsSize['PopUpButtonRegularHeight']+1),
                                                  'Load texts...',
                                                  sizeStyle='small',
                                                  callback=self.openTextsFolderButtonCallback)

        jumpingX += textModePopUpWidth + MARGIN_COL
        textFilePopUpWidth = 120
        self.textFilePopUp = PopUpButton((jumpingX, 0, textFilePopUpWidth, vanillaControlsSize['PopUpButtonRegularHeight']),
                                         self.editTexts.keys(),
                                         callback=self.textFilePopUpCallback)

        jumpingX += textFilePopUpWidth + MARGIN_COL
        textLinePopUpWidth = 50
        self.textLinePopUp = PopUpButton((jumpingX, 0, textLinePopUpWidth, vanillaControlsSize['PopUpButtonRegularHeight']),
                                         ['{:0>2d}'.format(item) for item in range(1, len(self.chosenTxt)+1)],
                                         callback=self.textLinePopUpCallback)

        jumpingX += textLinePopUpWidth + MARGIN_COL
        arrowWidth = 30
        self.arrowUp = SquareButton((jumpingX, 0, arrowWidth, vanillaControlsSize['PopUpButtonRegularHeight']),
                                    u'↑',
                                    callback=self.arrowUpCallback)
        self.arrowUp.bind(key='uparrow', modifiers=[])

        jumpingX += arrowWidth + MARGIN_COL
        self.arrowDw = SquareButton((jumpingX, 0, arrowWidth, vanillaControlsSize['PopUpButtonRegularHeight']),
                                    u'↓',
                                    callback=self.arrowDwCallback)
        self.arrowDw.bind(key='downarrow', modifiers=[])

        jumpingX += arrowWidth + MARGIN_COL

        self.selectedLine = TextBox((jumpingX, 0, -MARGIN_RGT, vanillaControlsSize['TextBoxRegularHeight']),
                                    self.chosenLine)

    def _initTexts(self, folderName):
        self.editTexts = loadSpacingTexts(folderName)
        self.chosenStringOption = self.stringOptions[0]
        self.chosenTxt = self.editTexts[self.editTexts.keys()[0]]
        self.stringIndex = 0
        self.chosenLine = self.chosenTxt[self.stringIndex]

    def setUnicodeMinimum(self, unicodeMinimum):
        assert isinstance(unicodeMinimum, DictType), 'unicode minimum is not a dict'
        self.unicodeMinimum = unicodeMinimum

    def get(self):
        return self.chosenStringOption, splitText(self.chosenLine, self.unicodeMinimum)

    def show(self, onOff):
        assert onOff in (True, False)
        self.textModePopUp.show(onOff)
        self.textFilePopUp.show(onOff)
        self.textLinePopUp.show(onOff)
        self.openTextsFolderButton.show(onOff)
        self.arrowUp.show(onOff)
        self.arrowDw.show(onOff)
        self.selectedLine.show(onOff)

    def textModePopUpCallback(self, sender):
        self.chosenStringOption = self.stringOptions[sender.get()]
        self.callback(self)

    def openTextsFolderButtonCallback(self, sender):
        textFolder = u'{}'.format(getFolder('Choose a folder for texts files')[0])
        self._initTexts(textFolder)
        self.textFilePopUp.setItems(self.editTexts.keys())
        self.textLinePopUp.setItems(['{:0>2d}'.format(item) for item in range(1, len(self.chosenTxt)+1)])
        self.callback(self)

    def textFilePopUpCallback(self, sender):
        self.chosenTxt = self.editTexts[self.editTexts.keys()[sender.get()]]
        self.stringIndex = 0
        self.chosenLine = self.chosenTxt[self.stringIndex]

        self.textLinePopUp.setItems(['{:0>2d}'.format(item) for item in range(1, len(self.chosenTxt)+1)])
        self.selectedLine.set(self.chosenLine)
        self.callback(self)

    def textLinePopUpCallback(self, sender):
        self.stringIndex = sender.get()
        self.chosenLine = self.chosenTxt[self.stringIndex]
        self.selectedLine.set(self.chosenLine)
        self.callback(self)

    def arrowUpCallback(self, sender):
        self.stringIndex -= 1
        if self.stringIndex < 0:
            self.stringIndex = -abs(-self.stringIndex % len(self.chosenTxt))
        else:
            self.stringIndex = self.stringIndex % len(self.chosenTxt)

        self.chosenLine = self.chosenTxt[self.stringIndex]
        self.selectedLine.set(self.chosenLine)
        self.textLinePopUp.set(self.chosenTxt.index(self.chosenLine))
        self.callback(self)

    def arrowDwCallback(self, sender):
        self.stringIndex += 1
        if self.stringIndex < 0:
            self.stringIndex = -abs(-self.stringIndex % len(self.chosenTxt))
        else:
            self.stringIndex = self.stringIndex % len(self.chosenTxt)

        self.chosenLine = self.chosenTxt[self.stringIndex]
        self.selectedLine.set(self.chosenLine)
        self.textLinePopUp.set(self.chosenTxt.index(self.chosenLine))
        self.callback(self)
