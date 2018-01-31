#!/usr/bin/env python
# coding: utf-8

#########################
# TTools accented maker #
#########################

### Modules
# custom modules
import ui.userInterfaceValues
reload(ui.userInterfaceValues)
from ui.userInterfaceValues import vanillaControlsSize, glyphCollectionColors

import extraTools.miscFunctions
reload(extraTools.miscFunctions)
from extraTools.miscFunctions import selectAnchorByName

# standard modules
import os, logging
from mojo.roboFont import version
from AppKit import NSColor
from math import radians, tan
from collections import OrderedDict
from mojo.events import addObserver, removeObserver
from mojo.roboFont import AllFonts, CurrentFont, version
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
BUILD_MISSING_GLYPH = u'we need "{glyphName}" in order to make {accentedName}'
BUILD_MISSING_ANCHOR = u'we need {anchorName} in "{glyphName}" in order to make {accentedName}'
NO_ANCHORS = u'there are no anchors in "{glyphName}"'

GLYPH_NOT_IN_FONT = u'"{glyphName}" not in {familyName} {styleName}'
NOT_READY = u'{accentedName} from {fontName} has been skipped because is not ready yet'

START_FUNC = u'Starting {funcName}'
END_FUNC = u'Ending {funcName}'
START_FONT = u'Starting font {familyName} {styleName}'
APPEND_ANCHOR = u'"{anchorName}" anchor placed at x: {anchorX} y: {anchorHeight} in "{glyphName}"'
REMOVE_ANCHOR = u'removed "{anchorName}" anchor from "{glyphName}"'
BUILT_GLYPH = u'{accentedName} built using {baseName} and {accentName} thanks to {anchorName} anchor'

### Classes and functions
class AccentedMaker(BaseWindowController):

    fontOptions = []
    whichFont = None
    actions = ['Place Anchors', 'Build Accents']
    whichAction = actions[0]
    whichGlyphList = None
    markEditedGlyphs = False
    markColor = glyphCollectionColors[glyphCollectionColors.keys()[0]]

    uppercaseAccents = False

    def __init__(self):
        super(AccentedMaker, self).__init__()
        self.initLogger()

        self.fontOptions = ['All Fonts', 'Current Font'] + AllFonts()
        self.whichFont = self.fontOptions[0]
        self.pluginHeight = PLUGIN_HEIGHT

        self.loadAccentedData()
        self.parseGlyphListsFromAccentedData()

        firstKey = self.glyphLists[self.whichAction].keys()[0]
        self.whichGlyphList = self.glyphLists[self.whichAction][firstKey]

        self.w = FloatingWindow((0, 0, PLUGIN_WIDTH, self.pluginHeight),
                                PLUGIN_TITLE)

        self.w.sharedCtrls = SharedCtrls((MARGIN_HOR, MARGIN_VER, NET_WIDTH, 104),
                                         fontOptions=self.fontOptions,
                                         whichFont=self.whichFont,
                                         actions=self.actions,
                                         whichAction=self.whichAction,
                                         glyphLists=self.glyphLists,
                                         whichGlyphList=self.whichGlyphList,
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
        self.w.bind("close", self.windowCloseCallback)
        self.setUpBaseWindowBehavior()
        self.adjustPluginHeight()
        self.w.open()

    def initLogger(self):
        # create a logger
        self.accentedLogger = logging.getLogger('accentedLogger')
        # create file handler which logs info messages
        fileBasedHandler = logging.FileHandler('accentedLettersMaker.log')
        fileBasedHandler.setLevel(logging.INFO)
        # create console handler with a higher log level, only errors
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(logging.ERROR)
        # create formatter and add it to the handlers
        formatter = logging.Formatter(u'%(asctime)s | %(levelname)s | line: %(lineno)d | %(funcName)s | %(message)s')
        fileBasedHandler.setFormatter(formatter)
        consoleHandler.setFormatter(formatter)
        # add the handlers to the logger
        self.accentedLogger.addHandler(fileBasedHandler)
        self.accentedLogger.addHandler(consoleHandler)

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
        self.accentedLogger.info(START_FUNC.format(funcName=self.deleteAnchors.__name__))
        fontsToProcess = self.prepareFontsToAction()
        for eachFont in fontsToProcess:
            self.accentedLogger.info(START_FONT.format(familyName=eachFont.info.familyName,
                                                       styleName=eachFont.info.styleName))
            for eachGlyphName in self.whichGlyphList:
                eachGlyph = eachFont[eachGlyphName]
                if self.markEditedGlyphs is True:
                    if version[0] == '2':
                        eachGlyph.markColor = self.markColor
                    else:
                        eachGlyph.mark = self.markColor

                for eachAnchor in eachGlyph.anchors:
                    eachGlyph.removeAnchor(eachAnchor)
                    self.accentedLogger.info(REMOVE_ANCHOR.format(anchorName=self.anchorName,
                                                             glyphName=eachGlyphName))
        self.accentedLogger.info(END_FUNC.format(funcName=self.deleteAnchors.__name__))

    def placeAnchors(self):
        assert self.anchorName is not None, '[WARNING] no anchor name provided'
        assert self.anchorHeight is not None, '[WARNING] no anchor height provided'
        self.accentedLogger.info(START_FUNC.format(funcName=self.placeAnchors.__name__))

        fontsToProcess = self.prepareFontsToAction()
        for eachFont in fontsToProcess:
            self.accentedLogger.info(START_FONT.format(familyName=eachFont.info.familyName,
                                                       styleName=eachFont.info.styleName))
            for eachGlyphName in self.whichGlyphList:
                if eachGlyphName in eachFont:
                    eachGlyph = eachFont[eachGlyphName]
                    if self.markEditedGlyphs is True:
                        if version[0] == '2':
                            eachGlyph.markColor = self.markColor
                        else:
                            eachGlyph.mark = self.markColor

                    if selectAnchorByName(eachGlyph, self.anchorName):
                        anchorToDel = selectAnchorByName(eachGlyph, self.anchorName)
                        eachGlyph.removeAnchor(anchorToDel)

                    if version[0] == '2':
                        xMin, yMin, xMax, yMax = eachGlyph.bounds
                    else:
                        xMin, yMin, xMax, yMax = eachGlyph.box

                    if eachFont.info.italicAngle:
                        anchorAngle = radians(-eachFont.info.italicAngle)
                    else:
                        anchorAngle = radians(0)

                    tangentOffset = tan(anchorAngle)*self.anchorHeight
                    anchorX = (eachGlyph.width - eachGlyph.angledLeftMargin - eachGlyph.angledRightMargin)/2 + eachGlyph.angledLeftMargin + tangentOffset
                    eachGlyph.appendAnchor(self.anchorName, (anchorX, self.anchorHeight))
                    self.accentedLogger.info(APPEND_ANCHOR.format(anchorName=self.anchorName,
                                                                  anchorX=anchorX,
                                                                  anchorHeight=self.anchorHeight,
                                                                  glyphName=eachGlyphName))
                else:
                    self.accentedLogger.error(GLYPH_NOT_IN_FONT.format(glyphName=eachGlyphName,
                                                                    familyName=eachFont.info.familyName,
                                                                    styleName=eachFont.info.styleName))
        self.accentedLogger.info(END_FUNC.format(funcName=self.placeAnchors.__name__))

    def checkAccented(self, isPrinting=True):
        report = []
        notReady = OrderedDict()

        fontsToProcess = self.prepareFontsToAction()
        for eachFont in fontsToProcess:
            toSkip = []
            report.append('Checking {} {}'.format(eachFont.info.familyName, eachFont.info.styleName))
            for eachAccentedName, eachBaseName, eachAccentName, eachAnchorName in self.whichGlyphList:

                # base glyph
                if eachFont.has_key(eachBaseName) is False:
                    report.append(BUILD_MISSING_GLYPH.format(glyphName=eachBaseName,
                                                       accentedName=eachAccentedName))
                    if eachAccentedName not in toSkip:
                        toSkip.append(eachAccentedName)
                else:
                    eachBaseGlyph = eachFont[eachBaseName]
                    if not eachBaseGlyph.anchors:
                        report.append(NO_ANCHORS.format(glyphName=eachBaseName))
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
                            report.append(BUILD_MISSING_ANCHOR.format(anchorName=eachAnchorName,
                                                                glyphName=eachBaseName,
                                                                accentedName=eachAccentedName))
                            if eachAccentedName not in toSkip:
                                toSkip.append(eachAccentedName)
                            if version[0] == '2':
                                eachBaseGlyph.markColor = ERROR_MARK_COLOR
                            else:
                                eachBaseGlyph.mark = ERROR_MARK_COLOR

                # accent
                if eachFont.has_key(eachAccentName) is False:
                    report.append(BUILD_MISSING_GLYPH.format(glyphName=eachAccentName,
                                                       accentedName=eachAccentedName))
                    if eachAccentedName not in toSkip:
                        toSkip.append(eachAccentedName)
                else:
                    eachAccentGlyph = eachFont[eachAccentName]
                    if not eachAccentGlyph.anchors:
                        report.append(NO_ANCHORS.format(glyphName=eachAccentName))
                        if eachAccentedName not in toSkip:
                            toSkip.append(eachAccentedName)
                        if version[0] == '2':
                            eachAccentGlyph.markColor = ERROR_MARK_COLOR
                        else:
                            eachAccentGlyph.mark = ERROR_MARK_COLOR
                    else:
                        for eachAnchor in eachAccentGlyph.anchors:
                            if eachAnchor.name == '_{}'.format(eachAnchorName):
                                break
                        else:
                            report.append(BUILD_MISSING_ANCHOR.format(anchorName=eachAnchorName,
                                                                glyphName=eachAccentName,
                                                                accentedName=eachAccentedName))
                            if eachAccentedName not in toSkip:
                                toSkip.append(eachAccentedName)
                            if version[0] == '2':
                                eachAccentGlyph.markColor = ERROR_MARK_COLOR
                            else:
                                eachAccentGlyph.mark = ERROR_MARK_COLOR

            notReady['{} {}'.format(eachFont.info.familyName, eachFont.info.styleName)] = toSkip
            report.append('End checking {} {}'.format(eachFont.info.familyName, eachFont.info.styleName))
            report.append('\n\n')

        if isPrinting is True:
            self.accentedLogger.error('\n'.join(report))

        return notReady


    def buildAccented(self):
        notReady = self.checkAccented(isPrinting=False)
        self.accentedLogger.info(START_FUNC.format(funcName=self.buildAccented.__name__))

        fontsToProcess = self.prepareFontsToAction()
        for eachFont in fontsToProcess:
            self.accentedLogger.info(START_FONT.format(familyName=eachFont.info.familyName,
                                                       styleName=eachFont.info.styleName))
            for eachAccentedName, eachBaseName, eachAccentName, eachAnchorName in self.whichGlyphList:
                if eachAccentedName in notReady['{} {}'.format(eachFont.info.familyName, eachFont.info.styleName)]:
                    self.accentedLogger.error(NOT_READY.format(fontName='{} {}'.format(eachFont.info.familyName, eachFont.info.styleName),
                                                                 accentedName=eachAccentedName))
                    continue

                eachBaseGlyph = eachFont[eachBaseName]
                eachBaseAnchor = selectAnchorByName(eachBaseGlyph, eachAnchorName)

                eachAccentGlyph = eachFont[eachAccentName]
                eachAccentAnchor = selectAnchorByName(eachAccentGlyph, '_{}'.format(eachAnchorName))

                if eachFont.has_key(eachAccentedName) is False:
                    eachAccentedGlyph = eachFont.newGlyph(eachAccentedName)
                else:
                    eachAccentedGlyph = eachFont[eachAccentedName]
                    eachAccentedGlyph.clear()

                eachAccentedGlyph.width = eachBaseGlyph.width
                eachAccentedGlyph.appendComponent(eachBaseName, (0,0), (1,1))

                accentOffsetX, accentOffsetY = eachBaseAnchor.x-eachAccentAnchor.x, eachBaseAnchor.y-eachAccentAnchor.y
                eachAccentedGlyph.appendComponent(eachAccentName, (accentOffsetX, accentOffsetY), (1,1))

                self.accentedLogger.info(BUILT_GLYPH.format(accentedName=eachAccentedName,
                                                            baseName=eachBaseName,
                                                            accentName=eachAccentName,
                                                            anchorName=eachAnchorName))

                if self.markEditedGlyphs is True:
                    if version[0] == '2':
                        eachAccentedGlyph.markColor = self.markColor
                    else:
                        eachAccentedGlyph.mark = self.markColor

        self.accentedLogger.info(END_FUNC.format(funcName=self.buildAccented.__name__))

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

        accentsCaseTop = ['{}.case'.format(name) for name in accentsTop]
        self.glyphLists['Place Anchors']['ACC CASE TOP'] = accentsCaseTop
        
        accentsCaseBtm = ['{}.case'.format(name) for name in accentsBtm]
        self.glyphLists['Place Anchors']['ACC CASE BTM'] = accentsCaseBtm

        ucBaseTop = []
        _ = [ucBaseTop.append(row[1]) for row in self.accentedData if row[1][0].isupper() and row[3] == 'top' and row[1] not in ucBaseTop]
        self.glyphLists['Place Anchors']['UC TOP'] = ucBaseTop
        
        ucBaseBtm = []
        _ = [ucBaseBtm.append(row[1]) for row in self.accentedData if row[1][0].isupper() and row[3] == 'bottom' and row[1] not in ucBaseBtm]
        self.glyphLists['Place Anchors']['UC BTM'] = ucBaseBtm

        lcBaseTop = []
        _ = [lcBaseTop.append(row[1]) for row in self.accentedData if row[1][0].islower() and row[3] == 'top' and row[1] not in lcBaseTop]
        self.glyphLists['Place Anchors']['LC TOP'] = lcBaseTop

        lcBaseBtm = []
        _ = [lcBaseBtm.append(row[1]) for row in self.accentedData if row[1][0].islower() and row[3] == 'bottom' and row[1] not in lcBaseBtm]
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
        lft, top, wdt, hgt = self.w.getPosSize()
        self.w.resize(wdt, self.pluginHeight)

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
                 whichAction, glyphLists, whichGlyphList,
                 markColor, markEditedGlyphs, callback):
        super(SharedCtrls, self).__init__(posSize)

        x, y, width, height = posSize
        self.fontOptions = fontOptions
        self.fontOptionsRepr = ['All Fonts', 'Current Font'] + ['{} {}'.format(ff.info.familyName, ff.info.styleName) for ff in self.fontOptions[2:]]
        self.whichFont = whichFont
        self.actions = actions
        self.whichAction = whichAction
        self.glyphLists = glyphLists
        self.whichGlyphList = whichGlyphList
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

        jumpinY += vanillaControlsSize['PopUpButtonRegularHeight'] + MARGIN_ROW +2
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
        self.fontOptionsRepr = ['All Fonts', 'Current Font'] + ['{} {}'.format(ff.info.familyName, ff.info.styleName) for ff in self.fontOptions[2:]]
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
