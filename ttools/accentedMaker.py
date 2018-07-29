#!/usr/bin/env python
# coding: utf-8

#########################
# TTools accented maker #
#########################

### Modules
# custom modules
from __future__ import print_function
from __future__ import absolute_import
from .ui.userInterfaceValues import vanillaControlsSize, glyphCollectionColors
from .extraTools.miscFunctions import selectAnchorByName

# standard modules
import os
from mojo.roboFont import version
from AppKit import NSColor
from collections import OrderedDict
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

ERROR_MARK_COLOR = (1,0,0,1)

TABLE_PATH = os.path.join(os.path.dirname(__file__),
                          'resources',
                          'tables',
                          'accentedLettersTable.csv')

# message templates
MISSING_GLYPH = '\t[WARNING] we need {glyphName} in order to make {accentedName}' # {'glyphName': None, 'accentedName': None}
MISSING_ANCHOR = '\t[WARNING] we need {anchorName} in {glyphName} in order to make {accentedName}' # {'anchorName': None, 'glyphName': None, 'accentedName': None}
NO_ANCHORS = '\t[WARNING] there are no anchors in {glyphName}' # {'glyphName': None}

NOT_READY = '\t\t[WARNING] {accentedName} from {fontName} has been skipped because is not ready yet' # {'accentedName': None, 'fontName': None}

START_FUNC = 'Starting {funcName}'
END_FUNC = 'Ending {funcName}'
START_FONT = '\tStarting font {fontName}' # {'fontName': None}
APPEND_ANCHOR = '\t\t"{anchorName}" anchor placed at x: {anchorX} y: {anchorHeight} in {glyphName}' # {'anchorName': None, 'anchorX': None, 'anchorHeight': None, 'glyphName': None}
REMOVE_ANCHOR = '\t\tremoved "{anchorName}" anchor from {glyphName}' # {'anchorName': None, 'glyphName': None}
BUILT_GLYPH = '\t\t{accentedName} built using {baseName} and {accentName} thanks to {anchorName} anchor'


### Classes and functions
class AccentedMaker(BaseWindowController):

    fontOptions = []
    whichFont = None
    actions = ['Place Anchors', 'Build Accents']
    whichAction = actions[0]
    whichGlyphList = None
    isVerbose = False
    markEditedGlyphs = False
    firstMarkColorName = [kk for kk in glyphCollectionColors.keys()][0]
    markColor = glyphCollectionColors[firstMarkColorName]

    uppercaseAccents = False

    def __init__(self):
        super(AccentedMaker, self).__init__()

        self.fontOptions = ['All Fonts', 'Current Font'] + AllFonts()
        self.whichFont = self.fontOptions[0]
        self.pluginHeight = PLUGIN_HEIGHT

        self.loadAccentedData()
        self.parseGlyphListsFromAccentedData()

        firstKey = list(self.glyphLists[self.whichAction].keys())[0]
        self.whichGlyphList = self.glyphLists[self.whichAction][firstKey]

        self.w = FloatingWindow((0, 0, PLUGIN_WIDTH, self.pluginHeight),
                                PLUGIN_TITLE)

        self.w.sharedCtrls = SharedCtrls((MARGIN_HOR, MARGIN_VER, NET_WIDTH, 136),
                                         fontOptions=self.fontOptions,
                                         whichFont=self.whichFont,
                                         actions=self.actions,
                                         whichAction=self.whichAction,
                                         glyphLists=self.glyphLists,
                                         whichGlyphList=self.whichGlyphList,
                                         isVerbose=self.isVerbose,
                                         markColor=self.markColor,
                                         markEditedGlyphs=self.markEditedGlyphs,
                                         callback=self.sharedCtrlsCallback)
        self.w.separationLine = HorizontalLine((MARGIN_HOR, self.w.sharedCtrls.getPosSize()[3]+MARGIN_ROW, NET_WIDTH, vanillaControlsSize['HorizontalLineThickness']))

        dependantCtrlsHgt = MARGIN_VER+self.w.sharedCtrls.getPosSize()[3]+MARGIN_ROW
        self.w.anchorsCtrls = AnchorsCtrls((MARGIN_HOR, dependantCtrlsHgt, NET_WIDTH, 76),
                                           callbackAttrs=self.anchorsVarsCallback,
                                           placeCallback=self.anchorsPlaceCallback,
                                           deleteCallback=self.anchorsDeleteCallback)

        self.w.buildingCtrls = BuildingCtrls((MARGIN_HOR, dependantCtrlsHgt, NET_WIDTH, 50),
                                             self.uppercaseAccents,
                                             callbackAttrs=self.buildingVarsCallback,
                                             callbackCheck=self.checkAccentedCallback,
                                             callbackBuild=self.buildAccentedCallback)
        self.w.buildingCtrls.show(False)

        addObserver(self, 'updateFontOptions', "newFontDidOpen")
        addObserver(self, 'updateFontOptions', "fontDidOpen")
        addObserver(self, 'updateFontOptions', "fontWillClose")
        # self.w.bind("close", self.closingPlugin)
        self.setUpBaseWindowBehavior()
        self.adjustPluginHeight()
        self.w.open()

    # deal with font data
    def prepareFontsToAction(self):
        if self.whichFont == 'All Fonts':
            fontsToProcess = AllFonts()
        elif self.whichFont == 'Current Font':
            fontsToProcess = [CurrentFont()]
        else:
            fontsToProcess = [self.whichFont]
        return fontsToProcess

    def deleteAnchors(self):
        if self.isVerbose is True:
            print(START_FUNC.format(funcName=deleteAnchors.__name__))

        fontsToProcess = self.prepareFontsToAction()
        for eachFont in fontsToProcess:
            if self.isVerbose is True:
                print(START_FONT % {'fontName': '%s %s' % (eachFont.info.familyName, eachFont.info.styleName)})

            for eachGlyphName in self.whichGlyphList:

                eachGlyph = eachFont[eachGlyphName]
                if self.markEditedGlyphs is True:
                    if version[0] == '2':
                        eachGlyph.markColor = self.markColor
                    else:
                        eachGlyph.mark = self.markColor

                for eachAnchor in eachGlyph.anchors:
                    eachGlyph.removeAnchor(eachAnchor)
                    if self.isVerbose is True:
                        print(REMOVE_ANCHOR % {'anchorName': self.anchorName, 'glyphName': eachGlyphName})

        if self.isVerbose is True:
            print(END_FUNC.format(funcName=self.deleteAnchors.__name__))

    def placeAnchors(self):
        assert self.anchorName is not None, '[WARNING] no anchor name provided'
        assert self.anchorHeight is not None, '[WARNING] no anchor height provided'

        if self.isVerbose is True:
            print(START_FUNC.format(funcName=self.placeAnchors.__name__))

        fontsToProcess = self.prepareFontsToAction()
        for eachFont in fontsToProcess:
            if self.isVerbose is True:
                print(START_FONT % {'fontName': '%s %s' % (eachFont.info.familyName, eachFont.info.styleName)})

            for eachGlyphName in self.whichGlyphList:
                eachGlyph = eachFont[eachGlyphName]
                if self.markEditedGlyphs is True:
                    if version[0] == '2':
                        eachGlyph.markColor = self.markColor
                    else:
                        eachGlyph.mark = self.markColor

                if selectAnchorByName(eachGlyph, self.anchorName):
                    anchorToDel = selectAnchorByName(eachGlyph, self.anchorName)
                    eachGlyph.removeAnchor(anchorToDel)
                eachGlyph.appendAnchor(self.anchorName, (eachGlyph.width/2., self.anchorHeight))

                if self.isVerbose is True:
                    print(APPEND_ANCHOR % {'anchorName': self.anchorName, 'anchorX': eachGlyph.width/2., 'anchorHeight': self.anchorHeight, 'glyphName': eachGlyphName})

        if self.isVerbose is True:
            print(END_FUNC.format(funcName=self.placeAnchors.__name__))

    def checkAccented(self, isPrinting=True):
        report = []
        notReady = OrderedDict()

        fontsToProcess = self.prepareFontsToAction()
        for eachFont in fontsToProcess:
            toSkip = []
            report.append('Checking %s %s' % (eachFont.info.familyName, eachFont.info.styleName))
            for eachAccentedName, eachBaseName, eachAccentName, eachAnchorName in self.whichGlyphList:

                # base glyph
                if (eachBaseName in eachFont) is False:
                    report.append(MISSING_GLYPH % {'glyphName': eachBaseName, 'accentedName': eachAccentedName})
                    if eachAccentedName not in toSkip:
                        toSkip.append(eachAccentedName)
                else:
                    eachBaseGlyph = eachFont[eachBaseName]
                    if not eachBaseGlyph.anchors:
                        report.append(NO_ANCHORS % {'glyphName': eachBaseName})
                        if eachAccentedName not in toSkip:
                            toSkip.append(eachAccentedName)
                        if version[0] == '2':
                            eachBaseGlyph.markColor = ERROR_MARK_COLOR
                        else:
                            eachBaseGlyph.mark = ERROR_MARK_COLOR
                    else:
                        for eachAnchor in eachBaseGlyph.anchors:
                            if eachAnchor.name == eachAnchorName:
                                break
                        else:
                            report.append(MISSING_ANCHOR % {'anchorName': eachAnchorName, 'glyphName': eachBaseName, 'accentedName': eachAccentedName})
                            if eachAccentedName not in toSkip:
                                toSkip.append(eachAccentedName)
                            if version[0] == '2':
                                eachBaseGlyph.markColor = ERROR_MARK_COLOR
                            else:
                                eachBaseGlyph.mark = ERROR_MARK_COLOR

                # accent
                if (eachAccentName in eachFont) is False:
                    report.append(MISSING_GLYPH % {'glyphName': eachAccentName, 'accentedName': eachAccentedName})
                    if eachAccentedName not in toSkip:
                        toSkip.append(eachAccentedName)
                else:
                    eachAccentGlyph = eachFont[eachAccentName]
                    if not eachAccentGlyph.anchors:
                        report.append(NO_ANCHORS % {'glyphName': eachAccentName})
                        if eachAccentedName not in toSkip:
                            toSkip.append(eachAccentedName)
                        if version[0] == '2':
                            eachAccentGlyph.markColor = ERROR_MARK_COLOR
                        else:
                            eachAccentGlyph.mark = ERROR_MARK_COLOR
                    else:
                        for eachAnchor in eachAccentGlyph.anchors:
                            if eachAnchor.name == '_%s' % eachAnchorName:
                                break
                        else:
                            report.append(MISSING_ANCHOR % {'anchorName': eachAnchorName, 'glyphName': eachAccentName, 'accentedName': eachAccentedName})
                            if eachAccentedName not in toSkip:
                                toSkip.append(eachAccentedName)
                            if version[0] == '2':
                                eachAccentGlyph.markColor = ERROR_MARK_COLOR
                            else:
                                eachAccentGlyph.mark = ERROR_MARK_COLOR

            notReady['%s %s' % (eachFont.info.familyName, eachFont.info.styleName)] = toSkip
            report.append('End checking %s %s' % (eachFont.info.familyName, eachFont.info.styleName))
            report.append('\n\n')

        if isPrinting is True:
            print('\n'.join(report))

        return notReady


    def buildAccented(self):
        notReady = self.checkAccented(isPrinting=False)

        if self.isVerbose is True:
            print(START_FUNC.format(funcName=self.buildAccented.__name__))

        fontsToProcess = self.prepareFontsToAction()
        for eachFont in fontsToProcess:
            
            if self.isVerbose is True:
                print(START_FONT % {'fontName': '%s %s' % (eachFont.info.familyName, eachFont.info.styleName)})

            for eachAccentedName, eachBaseName, eachAccentName, eachAnchorName in self.whichGlyphList:

                if eachAccentedName in notReady['%s %s' % (eachFont.info.familyName, eachFont.info.styleName)]:
                    print(NOT_READY % {'fontName': '%s %s' % (eachFont.info.familyName, eachFont.info.styleName), 'accentedName': eachAccentedName})
                    continue

                eachBaseGlyph = eachFont[eachBaseName]
                eachBaseAnchor = selectAnchorByName(eachBaseGlyph, eachAnchorName)

                eachAccentGlyph = eachFont[eachAccentName]
                eachAccentAnchor = selectAnchorByName(eachAccentGlyph, '_%s' % eachAnchorName)

                if (eachAccentedName in eachFont) is False:
                    eachAccentedGlyph = eachFont.newGlyph(eachAccentedName)
                else:
                    eachAccentedGlyph = eachFont[eachAccentedName]
                    eachAccentedGlyph.clear()

                eachAccentedGlyph.width = eachBaseGlyph.width
                eachAccentedGlyph.appendComponent(eachBaseName, (0,0), (1,1))

                accentOffsetX, accentOffsetY = eachBaseAnchor.x-eachAccentAnchor.x, eachBaseAnchor.y-eachAccentAnchor.y
                eachAccentedGlyph.appendComponent(eachAccentName, (accentOffsetX, accentOffsetY), (1,1))

                if self.isVerbose is True:
                    print(BUILT_GLYPH % {'accentedName': eachAccentedName, 'baseName': eachBaseName, 'accentName': eachAccentName, 'anchorName': eachAnchorName})

                if self.markEditedGlyphs is True:
                    if version[0] == '2':
                        eachAccentedGlyph.markColor = self.markColor
                    else:
                        eachAccentedGlyph.mark = self.markColor

        if self.isVerbose is True:
            print(END_FUNC.format(funcName=self.buildAccented.__name__))

    # deal with table data
    def loadAccentedData(self):
        self.accentedData = [[cell.strip() for cell in row.split('\t')] for row in open(TABLE_PATH, 'r').readlines()]

    def parseGlyphListsFromAccentedData(self):
        assert self.accentedData is not None
        self.glyphLists = OrderedDict()

        # anchors
        self.glyphLists['Place Anchors'] = OrderedDict()
        accentsTop = []
        _ = [accentsTop.append(row[2]) for row in self.accentedData if row[3] == 'top' and row[2] not in accentsTop]
        self.glyphLists['Place Anchors']['ACC TOP'] = accentsTop
        
        accentsBtm = []
        _ = [accentsBtm.append(row[2]) for row in self.accentedData if row[3] == 'bottom' and row[2] not in accentsBtm]
        self.glyphLists['Place Anchors']['ACC BTM'] = accentsBtm

        accentsCaseTop = ['%s.case' % name for name in accentsTop]
        self.glyphLists['Place Anchors']['ACC CASE TOP'] = accentsCaseTop
        
        accentsCaseBtm = ['%s.case' % name for name in accentsBtm]
        self.glyphLists['Place Anchors']['ACC CASE BTM'] = accentsCaseBtm

        ucBaseTop = []
        _ = [ucBaseTop.append(row[1]) for row in self.accentedData if row[1][0].isupper() and row[3] == 'top']
        self.glyphLists['Place Anchors']['UC TOP'] = ucBaseTop
        
        ucBaseBtm = []
        _ = [ucBaseBtm.append(row[1]) for row in self.accentedData if row[1][0].isupper() and row[3] == 'bottom']
        self.glyphLists['Place Anchors']['UC BTM'] = ucBaseBtm

        lcBaseTop = []
        _ = [lcBaseTop.append(row[1]) for row in self.accentedData if row[1][0].islower() and row[3] == 'top']
        self.glyphLists['Place Anchors']['LC TOP'] = lcBaseTop

        lcBaseBtm = []
        _ = [lcBaseBtm.append(row[1]) for row in self.accentedData if row[1][0].islower() and row[3] == 'bottom']
        self.glyphLists['Place Anchors']['LC BTM'] = lcBaseBtm

        # build
        self.glyphLists['Build Accents'] = OrderedDict()
        self.glyphLists['Build Accents']['ALL'] = self.accentedData
        buildUC = [row for row in self.accentedData if row[1][0].isupper() is True]
        self.glyphLists['Build Accents']['UC'] = buildUC
        buildLC = [row for row in self.accentedData if row[1][0].islower() is True]
        self.glyphLists['Build Accents']['LC'] = buildLC


    # ui
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

    # observers
    def updateFontOptions(self, sender):
        self.fontOptions = ['All Fonts', 'Current Font'] + AllFonts()
        self.w.sharedCtrls.setFontOptions(self.fontOptions)

    # callbacks
    def sharedCtrlsCallback(self, sender):
        self.whichFont = sender.getWhichFont()
        self.whichAction = sender.getWhichAction()
        self.switchDependantCtrl()
        self.adjustPluginHeight()

        self.whichGlyphList = sender.getWhichGlyphList()
        self.isVerbose = sender.getIsVerbose()
        self.markEditedGlyphs, self.markColor = sender.getMarkEditedGlyphs()

    def anchorsVarsCallback(self, sender):
        self.anchorHeight = sender.getHeight()
        self.anchorName = sender.getName()

    def anchorsPlaceCallback(self, sender):
        self.placeAnchors()

    def anchorsDeleteCallback(self, sender):
        self.deleteAnchors()

    def buildingVarsCallback(self, sender):
        self.uppercaseAccents = sender.getUppercaseAccents()

    def checkAccentedCallback(self, sender):
        self.checkAccented()

    def buildAccentedCallback(self, sender):
        self.buildAccented()

    def windowCloseCallback(self, sender):
        removeObserver(self, "newFontDidOpen")
        removeObserver(self, "fontDidOpen")
        removeObserver(self, "fontWillClose")
        super(AccentedMaker, self).windowCloseCallback(sender)

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
                                        self.glyphLists[self.whichAction].keys(),
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
        self.popFonts.setItems(self.fontOptionsRepr)

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
        return self.markEditedGlyphs, self.markColor

    # callback
    def popFontsCallback(self, sender):
        self.whichFont = self.fontOptions[sender.get()]
        self.callback(self)

    def popActionCallback(self, sender):
        self.whichAction = self.actions[sender.get()]
        # update ctrls
        self.popGlyphList.setItems(self.glyphLists[self.whichAction].keys())

        # load first list of new section
        firstKey = self.glyphLists[self.whichAction].keys()[0]
        self.whichGlyphList = self.glyphLists[self.whichAction][firstKey]
        self.callback(self)

    def popGlyphListCallback(self, sender):
        rightKey = self.glyphLists[self.whichAction].keys()[sender.get()]
        self.whichGlyphList = self.glyphLists[self.whichAction][rightKey]
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
        self.heightEdit = EditText((width/2., jumpinY, width/2., vanillaControlsSize['EditTextRegularHeight']),
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

    uppercaseAccents = False

    def __init__(self, posSize, uppercaseAccents,
                 callbackAttrs, callbackCheck, callbackBuild):
        super(BuildingCtrls, self).__init__(posSize)
        x, y, width, height = posSize
        self.uppercaseAccents = uppercaseAccents
        self.callbackAttrs = callbackAttrs
        self.callbackCheck = callbackCheck
        self.callbackBuild = callbackBuild

        jumpinY = 0
        self.uppercaseCheck = CheckBox((0, jumpinY, width, vanillaControlsSize['CheckBoxRegularHeight']),
                                       'Use Uppercase accents',
                                       value=self.uppercaseAccents,
                                       callback=self.uppercaseCheckCallback)
        self.uppercaseCheck.enable(False)

        jumpinY += self.uppercaseCheck.getPosSize()[3] + MARGIN_ROW+2
        self.checkButton = Button((0, jumpinY, width*.45, vanillaControlsSize['ButtonRegularHeight']),
                                  'Check',
                                  callback=self.checkButtonCallback)
        self.buildButton = Button((width*.55, jumpinY, width*.45, vanillaControlsSize['ButtonRegularHeight']),
                                  'Build',
                                  callback=self.buildButtonCallback)

    def getUppercaseAccents(self):
        return self.uppercaseAccents

    def uppercaseCheckCallback(self, sender):
        self.callbackAttrs(self)

    def checkButtonCallback(self, sender):
        self.callbackCheck(self)

    def buildButtonCallback(self, sender):
        self.callbackBuild(self)


### Instructions
if __name__ == '__main__':
    am = AccentedMaker()