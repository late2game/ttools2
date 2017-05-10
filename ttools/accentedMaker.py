#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################
# TTools accented maker #
#########################

### Modules
# custom modules
import userInterfaceValues
reload(userInterfaceValues)
from userInterfaceValues import vanillaControlsSize, glyphCollectionColors

# standard modules
from AppKit import NSColor
from mojo.events import addObserver, removeObserver
from mojo.roboFont import AllFonts, CurrentFont
from defconAppKit.windows.baseWindow import BaseWindowController
from vanilla import FloatingWindow, Group, PopUpButton, ColorWell
from vanilla import CheckBox, TextBox, EditText, ComboBox, Button
from vanilla import HorizontalLine


### Constants
PLUGIN_TITLE = 'TT Accented Letters Maker'
PLUGIN_WIDTH = 200
PLUGIN_HEIGHT = 400

MARGIN_VER = 8
MARGIN_HOR = 8
MARGIN_ROW = 4
NET_WIDTH = PLUGIN_WIDTH - MARGIN_HOR*2

### Classes and functions
class AccentedMaker(BaseWindowController):

    fontOptions = []
    whichFont = None
    actions = ['Place Anchors', 'Build Accents']
    whichAction = actions[0]
    whichGlyphList = None
    isVerbose = False
    markEditedGlyphs = False
    markColor = glyphCollectionColors[glyphCollectionColors.keys()[0]]

    smallCapsAccents = False
    uppercaseAccents = False

    def __init__(self):
        super(AccentedMaker, self).__init__()

        self.allFonts = AllFonts()
        self.currentFont = CurrentFont()
        self.fontOptions = [self.allFonts, self.currentFont] + self.allFonts
        self.whichFont = self.fontOptions[0]
        self.pluginHeight = PLUGIN_HEIGHT

        self.w = FloatingWindow((0, 0, PLUGIN_WIDTH, self.pluginHeight),
                                PLUGIN_TITLE)

        self.w.sharedCtrls = SharedCtrls((MARGIN_HOR, MARGIN_VER, NET_WIDTH, 136),
                                         fontOptions=self.fontOptions,
                                         whichFont=self.whichFont,
                                         actions=self.actions,
                                         whichAction=self.whichAction,
                                         glyphLists=None,
                                         whichGlyphList=None,
                                         isVerbose=self.isVerbose,
                                         markColor=self.markColor,
                                         markEditedGlyphs=self.markEditedGlyphs,
                                         callback=self.sharedCtrlsCallback)
        self.w.separationLine = HorizontalLine((MARGIN_HOR, self.w.sharedCtrls.getPosSize()[3]+MARGIN_ROW, NET_WIDTH, vanillaControlsSize['HorizontalLineThickness']))

        dependantCtrlsHgt = MARGIN_VER+self.w.sharedCtrls.getPosSize()[3]+MARGIN_ROW
        self.w.anchorsCtrls = AnchorsCtrls((MARGIN_HOR, dependantCtrlsHgt, NET_WIDTH, 76),
                                           callbackAttr=self.anchorsVarsCallback,
                                           placeCallback=self.anchorsPlaceCallback,
                                           deleteCallback=self.anchorsDeleteCallback)

        self.w.buildingCtrls = BuildingCtrls((MARGIN_HOR, dependantCtrlsHgt, NET_WIDTH, 74),
                                             self.smallCapsAccents,
                                             self.uppercaseAccents,
                                             callbackAttrs=self.buildingVarsCallback,
                                             callbackCheck=self.checkAccentedCallback,
                                             callbackBuild=self.buildingAccentedCallback)
        self.w.buildingCtrls.show(False)

        addObserver(self, 'updateWhichFonts', "newFontDidOpen")
        addObserver(self, 'updateWhichFonts', "fontDidOpen")
        addObserver(self, 'updateWhichFonts', "fontWillClose")
        self.w.bind("close", self.closingPlugin)
        self.adjustPluginHeight()
        self.w.open()

    def adjustPluginHeight(self):
        if self.whichAction == 'Place Anchors':
            self.pluginHeight = MARGIN_VER+self.w.sharedCtrls.getPosSize()[3]+MARGIN_ROW+self.w.anchorsCtrls.getPosSize()[3]+MARGIN_VER
        else:
            self.pluginHeight = MARGIN_VER+self.w.sharedCtrls.getPosSize()[3]+MARGIN_ROW+self.w.buildingCtrls.getPosSize()[3]+MARGIN_VER
        self.w.resize(PLUGIN_WIDTH, self.pluginHeight)

    def switchDependantCtrl(self):
        if self.whichAction == 'Place Anchors':
            self.w.anchorsCtrls.show(True)
            self.w.buildingCtrls.show(False)
        else:
            self.w.anchorsCtrls.show(False)
            self.w.buildingCtrls.show(True)

    def updateWhichFonts(self, sender):
        self.allFonts = AllFonts()
        self.currentFont = CurrentFont()
        self.whichFont = [self.allFonts, self.currentFont] + self.allFonts

    def sharedCtrlsCallback(self, sender):
        self.whichFont = sender.getWhichFont()
        self.whichAction = sender.getWhichAction()
        self.switchDependantCtrl()
        self.adjustPluginHeight()

        self.whichGlyphList = sender.getWhichGlyphList()
        self.isVerbose = sender.getIsVerbose()
        self.markEditedGlyphs = sender.getMarkEditedGlyphs()

    def anchorsVarsCallback(self, sender):
        self.smallCapsAccents = sender.getSmallCapsAccents()
        self.uppercaseAccents = sender.getUppercaseAccents()

    def anchorsPlaceCallback(self, sender):
        print 'anchorsPlaceCallback'

    def anchorsDeleteCallback(self, sender):
        print 'anchorsDeleteCallback'

    def buildingVarsCallback(self, sender):
        print 'buildingVarsCallback'

    def checkAccentedCallback(self, sender):
        print 'checkAccentedCallback'

    def buildingAccentedCallback(self, sender):
        print 'buildingAccentedCallback'

    def closingPlugin(self, sender):
        removeObserver(self, "newFontDidOpen")
        removeObserver(self, "fontDidOpen")
        removeObserver(self, "fontWillClose")


class SharedCtrls(Group):

    def __init__(self, posSize, fontOptions, whichFont, actions,
                 whichAction, glyphLists, whichGlyphList, isVerbose,
                 markColor, markEditedGlyphs, callback):
        super(SharedCtrls, self).__init__(posSize)

        x, y, width, height = posSize
        self.fontOptions = fontOptions
        self.fontOptionsRepr = ['All Fonts', 'Current Font'] + ['%s %s' % (ff.info.familyName, ff.info.styleName) for ff in self.fontOptions[2:]]
        self.whichFont = whichFont
        self.actions = actions
        self.whichAction = whichAction
        self.glyphLists = glyphLists
        self.whichGlyphList = whichGlyphList
        self.isVerbose = isVerbose
        self.markColor = markColor
        self.markEditedGlyphs = markEditedGlyphs
        self.callback = callback

        jumpinY = 0
        self.popFonts = PopUpButton((1, jumpinY, width-1, vanillaControlsSize['PopUpButtonRegularHeight']),
                                    self.fontOptionsRepr,
                                    callback=self.popFontsCallback)

        jumpinY += vanillaControlsSize['PopUpButtonRegularHeight'] + MARGIN_ROW
        self.popAction = PopUpButton((1, jumpinY, width-1, vanillaControlsSize['PopUpButtonRegularHeight']),
                                    self.actions,
                                    callback=self.popActionCallback)

        jumpinY += vanillaControlsSize['PopUpButtonRegularHeight'] + MARGIN_ROW
        self.popGlyphList = PopUpButton((1, jumpinY, width-1, vanillaControlsSize['PopUpButtonRegularHeight']),
                                    ['a', 'b'],
                                    callback=self.popGlyphListCallback)

        jumpinY += vanillaControlsSize['PopUpButtonRegularHeight'] + MARGIN_ROW*2
        self.checkVerbose = CheckBox((0, jumpinY, width, vanillaControlsSize['CheckBoxRegularHeight']),
                                     "Verbose",
                                     callback=self.checkVerboseCallback)

        jumpinY += vanillaControlsSize['PopUpButtonRegularHeight'] + MARGIN_ROW
        self.checkMarkEditedColors = CheckBox((0, jumpinY, width*.35, vanillaControlsSize['CheckBoxRegularHeight']),
                                              "Color",
                                              value=self.markEditedGlyphs,
                                              callback=self.checkMarkEditedColorsCallback)

        self.popColors = PopUpButton((width*.4, jumpinY, width*.6, vanillaControlsSize['PopUpButtonRegularHeight']),
                                     glyphCollectionColors.keys(),
                                     callback=self.popColorsCallback)
        self.popColors.enable(self.markEditedGlyphs)

    # set public attrs
    def setFontOptions(self, fontOptions):
        originalIndex = self.fontOptions.index(self.whichFont)
        self.fontOptions = fontOptions
        self.fontOptionsRepr = ['All Fonts', 'Current Font'] + ['%s %s' % (ff.info.familyName, ff.info.styleName) for ff in self.fontOptions[2:]]
        self.popFont.setItems(self.fontOptions)

        if self.whichFont not in self.fontOptions:
            self.whichFont = self.fontOptions[0]
            self.whichFontRepr = 'All Fonts'
            self.popFonts.set(0)
        else:
            self.popFonts.set(originalIndex)

    # public attrs
    def getWhichFont(self):
        return self.whichFont

    def getWhichAction(self):
        return self.whichAction

    def getWhichGlyphList(self):
        return self.whichGlyphList

    def getIsVerbose(self):
        return self.isVerbose

    def getMarkEditedGlyphs(self):
        return self.markEditedGlyphs

    # callback
    def popFontsCallback(self, sender):
        self.whichFont = self.fontOptions[sender.get()]
        self.callback(self)

    def popActionCallback(self, sender):
        self.whichAction = self.actions[sender.get()]
        self.callback(self)

    def popGlyphListCallback(self, sender):
        self.whichGlyphList = None
        self.callback(self)

    def checkVerboseCallback(self, sender):
        self.isVerbose = bool(sender.get())
        self.callback(self)

    def checkMarkEditedColorsCallback(self, sender):
        self.markEditedGlyphs = bool(sender.get())
        self.popColors.enable(self.markEditedGlyphs)
        self.callback(self)

    def popColorsCallback(self, sender):
        self.markColor = glyphCollectionColors.values()[sender.get()]
        self.callback(self)


class AnchorsCtrls(Group):

    anchorName = ''
    anchorHeight = None

    def __init__(self, posSize, callbackAttrs, placeCallback, deleteCallback):
        super(AnchorsCtrls, self).__init__(posSize)
        self.callbackAttrs = callbackAttrs
        self.placeCallback = placeCallback
        self.deleteCallback = deleteCallback

        x, y, width, height = posSize

        jumpinY = 0
        self.heightCaption = TextBox((32, jumpinY, width/2., vanillaControlsSize['TextBoxRegularHeight']),
                                     'Height:')
        self.heightEditCallback = EditText((width/2., jumpinY, width/2., vanillaControlsSize['EditTextRegularHeight']),
                                           continuous=False,
                                           callback=self.heightEditCallback)

        jumpinY += self.heightEdit.getPosSize()[3] + MARGIN_ROW
        self.nameCaption = TextBox((32, jumpinY, width/2., vanillaControlsSize['TextBoxRegularHeight']),
                                   'Anchor:')
        self.nameCombo = ComboBox((width/2., jumpinY, width/2., vanillaControlsSize['ComboBoxRegularHeight']),
                                  ['top', '_top', 'bottom', '_bottom'],
                                  callback=self.nameComboCallback)

        jumpinY += self.nameCombo.getPosSize()[3] + MARGIN_ROW*2
        self.placeButton = Button((0, jumpinY, width*.45, vanillaControlsSize['ButtonRegularHeight']),
                                'Place',
                                callback=self.placeButtonCallback)

        self.deleteButton = Button((width*.55, jumpinY, width*.45, vanillaControlsSize['ButtonRegularHeight']),
                                'Delete',
                                callback=self.deleteButtonCallback)

    # public attrs
    def getHeight(self):
        return self.anchorHeight

    def getName(self):
        return self.anchorName

    # callbacks
    def heightEditCallback(self, sender):
        try:
            self.anchorHeight = int(sender.get())
            self.callbackAttrs(self)
        except ValueError:
            self.heightEdit.set('')

    def nameComboCallback(self, sender):
        self.anchorName = sender.get()
        self.callbackAttrs(self)

    def placeButtonCallback(self, sender):
        self.placeCallback(self)

    def deleteButtonCallback(self, sender):
        self.deleteCallback(self)


class BuildingCtrls(Group):

    def __init__(self, posSize, smallCapsAccents, uppercaseAccents, callback):
        super(BuildingCtrls, self).__init__(posSize)
        x, y, width, height = posSize
        self.smallCapsAccents = smallCapsAccents
        self.uppercaseAccents = uppercaseAccents
        self.callback = callback

        jumpinY = 0
        self.smallCapsCheck = CheckBox((0, jumpinY, width, vanillaControlsSize['CheckBoxRegularHeight']),
                                       'Use Small Caps accents',
                                       value=self.smallCapsAccents,
                                       callback=self.smallCapsCheckCallback)

        jumpinY += self.smallCapsCheck.getPosSize()[3] + MARGIN_ROW-2
        self.uppercaseCheck = CheckBox((0, jumpinY, width, vanillaControlsSize['CheckBoxRegularHeight']),
                                       'Use Uppercase accents',
                                       value=self.uppercaseAccents,
                                       callback=self.uppercaseCheckCallback)

        jumpinY += self.uppercaseCheck.getPosSize()[3] + MARGIN_ROW+2
        self.checkButton = Button((0, jumpinY, width*.45, vanillaControlsSize['ButtonRegularHeight']),
                                  'Check',
                                  callback=self.checkButtonCallback)
        self.buildButton = Button((width*.55, jumpinY, width*.45, vanillaControlsSize['ButtonRegularHeight']),
                                  'Build',
                                  callback=self.buildButtonCallback)

    def getSmallCapsAccents(self):
        return self.smallCapsAccents

    def getUppercaseAccents(self):
        return self.uppercaseAccents

    def smallCapsCheckCallback(self, sender):
        self.callback(self)

    def uppercaseCheckCallback(self, sender):
        self.callback(self)

    def checkButtonCallback(self, sender):
        self.callback(self)

    def buildButtonCallback(self, sender):
        self.callback(self)

### Instructions
if __name__ == '__main__':
    am = AccentedMaker()