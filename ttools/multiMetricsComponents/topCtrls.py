#!/usr/bin/env python
# coding: utf-8

"""elements for the top bar"""

### Modules
# custom
from ..userInterfaceValues import vanillaControlsSize

import spacingMisc
reload(spacingMisc)
from spacingMisc import convertLineToPseudoUnicode

# standard
from defconAppKit.tools.textSplitter import splitText
from vanilla import Group, EditText, PopUpButton, SquareButton, TextBox

### Constants
MARGIN_RGT = 15
MARGIN_COL = 10

### Factories
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
        if sender.get() is not None:
            self.centerGlyphNames = splitText(sender.get(), self.unicodeMinimum)
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
            self.typewriterGlyphNames += self.leftGlyphNames
            self.typewriterGlyphNames += [eachGlyphName]
            self.typewriterGlyphNames += self.rightGlyphNames
        return self.typewriterGlyphNames

    def show(self, onOff):
        assert onOff in [True, False]
        self.leftSiblingEdit.show(onOff)
        self.typewriterEdit.show(onOff)
        self.rightSiblingEdit.show(onOff)


class TextStringsControls(Group):

    # attrs
    stringOptions = ('Waterfall', 'Shuffled')
    title = 'Loaded Strings'

    def __init__(self, posSize, editTexts, callback):
        Group.__init__(self, posSize)
        self.callback = callback

        self.editTexts = editTexts
        self.editTextSortedKeys = self.editTexts.keys()
        self.editTextSortedKeys.sort()

        self.chosenStringOption = self.stringOptions[0]

        self.chosenTxt = self.editTexts[self.editTextSortedKeys[0]]
        self.stringIndex = 0
        self.chosenLine = self.chosenTxt[self.stringIndex].split(' ')

        textModePopUpWidth = 120
        self.textModePopUp = PopUpButton((1, 0, textModePopUpWidth, vanillaControlsSize['PopUpButtonRegularHeight']),
                                         self.stringOptions,
                                         callback=self.textModePopUpCallback)

        jumpingX = textModePopUpWidth + MARGIN_COL
        textFilePopUpWidth = 180
        self.textFilePopUp = PopUpButton((jumpingX, 0, textFilePopUpWidth, vanillaControlsSize['PopUpButtonRegularHeight']),
                                         self.editTextSortedKeys,
                                         callback=self.textFilePopUpCallback)

        jumpingX += textFilePopUpWidth + MARGIN_COL
        textLinePopUpWidth = 60
        self.textLinePopUp = PopUpButton((jumpingX, 0, textLinePopUpWidth, vanillaControlsSize['PopUpButtonRegularHeight']),
                                         ['%#02d' % item for item in xrange(1, len(self.chosenTxt)+1)],
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

        pseudoUniString = convertLineToPseudoUnicode(self.chosenLine)
        self.selectedLine = TextBox((jumpingX, 0, -MARGIN_RGT, vanillaControlsSize['TextBoxRegularHeight']),
                                    pseudoUniString)

    def get(self):
        return self.chosenStringOption, self.chosenLine

    def show(self, onOff):
        assert onOff in [True, False]
        self.textModePopUp.show(onOff)
        self.textFilePopUp.show(onOff)
        self.textLinePopUp.show(onOff)
        self.arrowUp.show(onOff)
        self.arrowDw.show(onOff)
        self.selectedLine.show(onOff)

    def textModePopUpCallback(self, sender):
        self.chosenStringOption = self.stringOptions[sender.get()]
        self.callback(self)

    def textFilePopUpCallback(self, sender):
        self.chosenTxt = self.editTexts[self.editTextSortedKeys[sender.get()]]
        self.stringIndex = 0
        self.chosenLine = self.chosenTxt[self.stringIndex].split(' ')

        self.textLinePopUp.setItems(['%#02d' % item for item in xrange(1, len(self.chosenTxt)+1)])
        self.selectedLine.set(convertLineToPseudoUnicode(self.chosenLine))
        self.callback(self)

    def textLinePopUpCallback(self, sender):
        self.stringIndex = sender.get()
        self.chosenLine = self.chosenTxt[self.stringIndex].split(' ')
        self.selectedLine.set(convertLineToPseudoUnicode(self.chosenLine))
        self.callback(self)

    def arrowUpCallback(self, sender):
        self.stringIndex -= 1
        if self.stringIndex < 0:
            self.stringIndex = -abs(-self.stringIndex % len(self.chosenTxt))
        else:
            self.stringIndex = self.stringIndex % len(self.chosenTxt)

        self.chosenLine = self.chosenTxt[self.stringIndex].split(' ')
        self.selectedLine.set(convertLineToPseudoUnicode(self.chosenLine))
        self.textLinePopUp.set(self.chosenTxt.index(' '.join(self.chosenLine)))
        self.callback(self)

    def arrowDwCallback(self, sender):
        self.stringIndex += 1
        if self.stringIndex < 0:
            self.stringIndex = -abs(-self.stringIndex % len(self.chosenTxt))
        else:
            self.stringIndex = self.stringIndex % len(self.chosenTxt)

        self.chosenLine = self.chosenTxt[self.stringIndex].split(' ')
        self.selectedLine.set(convertLineToPseudoUnicode(self.chosenLine))
        self.textLinePopUp.set(self.chosenTxt.index(' '.join(self.chosenLine)))
        self.callback(self)
