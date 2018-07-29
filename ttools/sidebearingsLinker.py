#!/usr/bin/env python
# coding: utf-8

#######################
# Sidebearings linker #
#######################

### Modules
from __future__ import division

# custom
import ui.userInterfaceValues
reload(ui.userInterfaceValues)
from ui.userInterfaceValues import vanillaControlsSize

# standard
import os
from collections import OrderedDict
import mojo.drawingTools as dt
from mojo.canvas import CanvasGroup
from mojo.roboFont import AllFonts
from mojo.events import addObserver, removeObserver
from vanilla import FloatingWindow, CheckBoxListCell, List, SquareButton
from vanilla import HorizontalLine, PopUpButton
from defconAppKit.windows.baseWindow import BaseWindowController
from vanilla.dialogs import putFile, message, getFile, askYesNo

### Constants
PLUGIN_WIDTH = 340
PLUGIN_HEIGHT = 1
PLUGIN_TITLE = 'TTools Linked Sidebearings'

MARGIN_HOR = 10
MARGIN_VER = 10
MARGIN_ROW = 10

BLACK = (0,0,0)
GRAY = (.4, .4, .4)
RED = (1,0,0)
BLUE = (0,0,1)

CANVAS_HEIGHT = 100
UPM_MARGIN = 300

LIST_WIDE_COL = 89
LIST_NARROW_COL = 18

NET_WIDTH = PLUGIN_WIDTH - MARGIN_HOR*2

PLUGIN_LIB_NAME = 'com.ttools.linkedSidebearings'

### Extra Functions
def getNamesFrom(someFonts):
    return [os.path.basename(item.path) for item in someFonts]

def loadLinksFromFont(aFont):
    links = []
    for eachGlyphName in aFont.glyphOrder:
        eachGlyph = aFont[eachGlyphName]
        if PLUGIN_LIB_NAME in eachGlyph.lib:
            thisLib = eachGlyph.lib[PLUGIN_LIB_NAME]
            dataFromGlyph = {'servant': eachGlyphName,
                             'lft': thisLib['lft'],
                             'lftActive': thisLib['lftActive'],
                             'rgt': thisLib['rgt'],
                             'rgtActive': thisLib['rgtActive']}
        else:
            dataFromGlyph = {'servant': eachGlyphName,
                             'lft': '',
                             'lftActive': False,
                             'rgt': '',
                             'rgtActive': False}
        links.append(dataFromGlyph)
    return links

def drawLock(closed, startingX, glyphQuota, scalingFactor):
    dt.save()
    dt.fill(*BLACK)
    dt.translate(startingX, 0)
    dt.scale(scalingFactor, scalingFactor)
    dt.translate(0, glyphQuota)
    dt.fontSize(300)
    if closed is True:
        txt = u'🔒'
    else:
        txt = u'🔓'
    txtWdt, txtHgt = dt.textSize(txt)
    dt.text(txt, (-txtWdt/2, 0))
    dt.restore()

def drawReferenceGlyph(aGlyph, scalingFactor, startingX, left=False, right=False):
    dt.save()
    dt.fill(*BLACK)
    dt.stroke(None)
    dt.translate(startingX, 0)
    dt.scale(scalingFactor, scalingFactor)
    dt.translate(0, -aGlyph.getParent().info.descender)
    dt.translate(-aGlyph.width/2, 0)
    dt.fill(*BLACK)
    dt.drawGlyph(aGlyph)

    descender = aGlyph.getParent().info.descender
    unitsPerEm = aGlyph.getParent().info.unitsPerEm
    baseTck = 40
    if left is True:
        dt.fill(*RED)
        dt.rect(0, -baseTck, aGlyph.leftMargin, baseTck)
        dt.rect(0, descender, 8, unitsPerEm)

    if right is True:
        dt.fill(*BLUE)
        dt.rect(aGlyph.width-aGlyph.rightMargin, -baseTck, aGlyph.rightMargin, baseTck)
        dt.rect(aGlyph.width, descender, 8, unitsPerEm)

    dt.restore()


### Class
class SidebearingsLinker(BaseWindowController):

    allFonts = []

    servantSubscriptions = []
    masterSubscriptions = []
    displayedSubscriptions = []

    currentRow = None
    selectedFont = None

    def __init__(self, willOpen=True):
        super(SidebearingsLinker, self).__init__()

        # collecting fonts
        self.allFonts = AllFonts()
        if self.allFonts != []:
            self.selectedFont = self.allFonts[0]

        # interface
        self.w = FloatingWindow((PLUGIN_WIDTH, PLUGIN_HEIGHT), PLUGIN_TITLE)

        jumpingY = MARGIN_VER
        self.w.fontPopUp = PopUpButton((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['PopUpButtonRegularHeight']),
                                       getNamesFrom(self.allFonts),
                                       callback=self.fontPopUpCallback)

        jumpingY += vanillaControlsSize['PopUpButtonRegularHeight'] + MARGIN_ROW
        self.w.canvas = CanvasGroup((MARGIN_HOR, jumpingY, NET_WIDTH, CANVAS_HEIGHT), delegate=self)

        jumpingY += CANVAS_HEIGHT + MARGIN_ROW
        linksColumnDescriptions = [{"title": "left", 'key': 'lft', 'width': LIST_WIDE_COL},
                                   {"title": "active", "cell": CheckBoxListCell(), 'key': 'lftActive', 'width': LIST_NARROW_COL},
                                   {"title": "glyph", 'key': 'servant', 'width': LIST_WIDE_COL, "editable": False},
                                   {"title": "active", "cell": CheckBoxListCell(), 'key': 'rgtActive', 'width': LIST_NARROW_COL},
                                   {"title": "right", 'key': 'rgt', 'width': LIST_WIDE_COL}]

        if self.selectedFont is not None:
            links = loadLinksFromFont(self.selectedFont)
        else:
            links = []

        self.w.linksList = List((MARGIN_HOR, jumpingY, NET_WIDTH, 200),
                                links,
                                showColumnTitles=False,
                                allowsMultipleSelection=False,
                                drawVerticalLines=True,
                                columnDescriptions=linksColumnDescriptions,
                                selectionCallback=self.selectionLinksListCallback,
                                editCallback=self.editLinksListCallback)

        if self.selectedFont is not None:
            self.w.linksList.setSelection([0])
            self.currentRow = self.w.linksList[0]
            self.matchDisplayedSubscriptions()

        jumpingY += self.w.linksList.getPosSize()[3] + MARGIN_ROW
        buttonWidth = (NET_WIDTH-MARGIN_HOR)/2
        self.w.linkAllButton = SquareButton((MARGIN_HOR, jumpingY, buttonWidth, vanillaControlsSize['ButtonRegularHeight']*1.5),
                                            'Link All',
                                            callback=self.linkAllButtonCallback)

        self.w.unlockAllButton = SquareButton((MARGIN_HOR*2+buttonWidth, jumpingY, buttonWidth, vanillaControlsSize['ButtonRegularHeight']*1.5),
                                              'Unlink All',
                                              callback=self.unlockAllButtonCallback)

        jumpingY += vanillaControlsSize['ButtonRegularHeight']*1.5 + MARGIN_ROW
        self.w.separationLineOne = HorizontalLine((MARGIN_HOR, jumpingY, NET_WIDTH, vanillaControlsSize['HorizontalLineThickness']))

        jumpingY += MARGIN_ROW
        self.w.pushIntoFontButton = SquareButton((MARGIN_HOR, jumpingY, buttonWidth, vanillaControlsSize['ButtonRegularHeight']*1.5),
                                                 'Push into font',
                                                 callback=self.pushIntoFontButtonCallback)
        self.w.pushIntoFontButton.enable(False)

        self.w.clearLibsButton = SquareButton((MARGIN_HOR*2+buttonWidth, jumpingY, buttonWidth, vanillaControlsSize['ButtonRegularHeight']*1.5),
                                              'Clear Libs',
                                              callback=self.clearLibsButtonCallback)

        jumpingY += vanillaControlsSize['ButtonRegularHeight']*1.5 + MARGIN_ROW
        self.w.loadFromTable = SquareButton((MARGIN_HOR, jumpingY, buttonWidth, vanillaControlsSize['ButtonRegularHeight']*1.5),
                                            'Load from table',
                                            callback=self.loadFromTableCallback)
        self.w.loadFromTable.enable(True)

        self.w.exportTable = SquareButton((MARGIN_HOR*2+buttonWidth, jumpingY, buttonWidth, vanillaControlsSize['ButtonRegularHeight']*1.5),
                                          'Export table',
                                          callback=self.exportTableCallback)
        self.w.exportTable.enable(True)

        jumpingY += vanillaControlsSize['ButtonRegularHeight']*1.5 + MARGIN_VER*2
        self.w.resize(PLUGIN_WIDTH, jumpingY)

        self.setUpBaseWindowBehavior()

        if self.selectedFont is not None:
            self.matchSubscriptions()
            result = askYesNo('Warning', 'Do you want to align servants to masters?')
            if bool(result) is True:
                self._alignServantsToMasters()

        addObserver(self, "drawOnGlyphCanvas", "draw")
        addObserver(self, "drawOnGlyphCanvas", "drawInactive")
        addObserver(self, 'fontDidOpenCallback', 'fontDidOpen')
        addObserver(self, 'fontDidCloseCallback', 'fontDidClose')
        if willOpen is True:
            self.w.open()

    # drawing callbacks
    def drawOnGlyphCanvas(self, infoDict):
        glyphOnCanvas = infoDict['glyph']
        scalingFactor = infoDict['scale']
        bodySize = .25
        horizontalOffset = 80

        if PLUGIN_LIB_NAME in glyphOnCanvas.lib:
            thisLib = glyphOnCanvas.lib[PLUGIN_LIB_NAME]
        else:
            return None

        lftGlyph = None
        if thisLib['lft'] != '':
            lftGlyph = self.selectedFont[thisLib['lft']]

        rgtGlyph = None
        if thisLib['rgt'] != '':
            rgtGlyph = self.selectedFont[thisLib['rgt']]

        try:
            dt.fill(*GRAY)

            if lftGlyph is not None:
                dt.save()
                dt.translate(-lftGlyph.width*bodySize-horizontalOffset, -self.selectedFont.info.unitsPerEm*bodySize)

                # glyph
                dt.scale(bodySize)
                dt.drawGlyph(lftGlyph)

                # lock
                if thisLib['lftActive'] is True:
                    txt = u'🔒'
                else:
                    txt = u'🔓'
                dt.fontSize(300)
                txtWdt, txtHgt = dt.textSize(txt)
                dt.text(txt, (-txtWdt, 0))
                dt.restore()

            if rgtGlyph is not None:
                dt.save()
                dt.translate(glyphOnCanvas.width+horizontalOffset, -self.selectedFont.info.unitsPerEm*bodySize)
                dt.scale(bodySize)
                dt.drawGlyph(rgtGlyph)

                # lock
                if thisLib['rgtActive'] is True:
                    txt = u'🔒'
                else:
                    txt = u'🔓'
                dt.fontSize(300)
                dt.text(txt, (rgtGlyph.width, 0))

                dt.restore()

        except Exception as error:
            print(error)

    def draw(self):
        try:
            if self.selectedFont is not None and self.currentRow is not None:
                scalingFactor = CANVAS_HEIGHT/(self.selectedFont.info.unitsPerEm+UPM_MARGIN)

                if self.currentRow['lft'] in self.selectedFont:
                    lftGlyph = self.selectedFont[self.currentRow['lft']]
                    if lftGlyph is not None:
                        drawReferenceGlyph(aGlyph=lftGlyph,
                                           scalingFactor=scalingFactor,
                                           startingX=NET_WIDTH*(1/6),
                                           left=True,
                                           right=False)

                    drawLock(closed=self.currentRow['lftActive'],
                             startingX=NET_WIDTH*(2/6),
                             glyphQuota=self.selectedFont.info.xHeight,
                             scalingFactor=scalingFactor)

                if self.currentRow['servant'] in self.selectedFont:
                    servantGlyph = self.selectedFont[self.currentRow['servant']]
                    if servantGlyph is not None:
                        drawReferenceGlyph(aGlyph=servantGlyph,
                                           scalingFactor=scalingFactor,
                                           startingX=NET_WIDTH*(3/6),
                                           left=True,
                                           right=True)

                if self.currentRow['rgt'] in self.selectedFont:
                    rgtGlyph = self.selectedFont[self.currentRow['rgt']]
                    if rgtGlyph is not None:
                        drawReferenceGlyph(aGlyph=rgtGlyph,
                                           scalingFactor=scalingFactor,
                                           startingX=NET_WIDTH*(5/6),
                                           right=True)

                    drawLock(closed=self.currentRow['rgtActive'],
                             startingX=NET_WIDTH*(4/6),
                             glyphQuota=self.selectedFont.info.xHeight,
                             scalingFactor=scalingFactor)

        except Exception as error:
            print(error)

    # observers
    def unsubscribeGlyphs(self):
        for eachGlyph in self.servantSubscriptions:
            eachGlyph.removeObserver(self, "Glyph.WidthChanged")
        self.servantSubscriptions = list()
        for eachGlyph in self.masterSubscriptions:
            eachGlyph.removeObserver(self, "Glyph.WidthChanged")
        self.masterSubscriptions = list()

    def unsubscribeDisplayedGlyphs(self):
        for eachGlyph in self.displayedSubscriptions:
            eachGlyph.removeObserver(self, "Glyph.Changed")
        self.displayedSubscriptions = list()

    def matchDisplayedSubscriptions(self):
        self.unsubscribeDisplayedGlyphs()

        if self.currentRow['lft'] != '':
            lftGlyph = self.selectedFont[self.currentRow['lft']]
            if lftGlyph not in self.displayedSubscriptions:
                lftGlyph.addObserver(self, 'displayedGlyphChanged', 'Glyph.Changed')
                self.displayedSubscriptions.append(lftGlyph)

        if self.currentRow['rgt'] != '':
            rgtGlyph = self.selectedFont[self.currentRow['rgt']]
            if rgtGlyph not in self.displayedSubscriptions:
                rgtGlyph.addObserver(self, 'displayedGlyphChanged', 'Glyph.Changed')
                self.displayedSubscriptions.append(rgtGlyph)

        if self.currentRow['servant'] != '':
            servantGlyph = self.selectedFont[self.currentRow['servant']]
            if servantGlyph not in self.displayedSubscriptions:
                servantGlyph.addObserver(self, 'displayedGlyphChanged', 'Glyph.Changed')
                self.displayedSubscriptions.append(servantGlyph)

    def matchSubscriptions(self):
        self.unsubscribeGlyphs()

        for servantGlyph in self.selectedFont:
            if PLUGIN_LIB_NAME in servantGlyph.lib:
                thisLib = servantGlyph.lib[PLUGIN_LIB_NAME]

                if (thisLib['lft'] != '' and thisLib['lftActive'] is True) or (thisLib['rgt'] != '' and thisLib['rgtActive'] is True):
                    if servantGlyph not in self.servantSubscriptions:
                        servantGlyph.addObserver(self, "servantGlyphChanged", "Glyph.WidthChanged")
                        self.servantSubscriptions.append(servantGlyph)

                    # servants
                    if thisLib['lftActive'] is True and thisLib['lft'] != '':
                        lftMaster = self.selectedFont[thisLib['lft']]
                        if lftMaster not in self.masterSubscriptions:
                            lftMaster.addObserver(self, "masterGlyphChanged", "Glyph.WidthChanged")
                            self.masterSubscriptions.append(lftMaster)

                    if thisLib['rgtActive'] is True and thisLib['rgt'] != '':
                        rgtMaster = self.selectedFont[thisLib['rgt']]
                        if rgtMaster not in self.masterSubscriptions:
                            rgtMaster.addObserver(self, "masterGlyphChanged", "Glyph.WidthChanged")
                            self.masterSubscriptions.append(rgtMaster)

    def servantGlyphChanged(self, notification):
        glyph = notification.object
        warningMessage = 'The glyph <{servantName}> is linked to <{masterName}>, do you want to broke the link?'

        if PLUGIN_LIB_NAME in glyph.lib:
            thisLib = glyph.lib[PLUGIN_LIB_NAME]

            if thisLib['lftActive'] is True:
                lftMaster = self.selectedFont[thisLib['lft']]
                if glyph.leftMargin != lftMaster.leftMargin:
                    result = askYesNo('Warning', warningMessage.format(servantName=glyph.name, masterName=lftMaster.name))
                    if bool(result) is False:
                        glyph.leftMargin = lftMaster.leftMargin
                        thisLib['lftActive'] = True
                    else:
                        thisLib['lftActive'] = False

            if thisLib['rgtActive'] is True:
                rgtMaster = self.selectedFont[thisLib['rgt']]
                if glyph.rightMargin != rgtMaster.rightMargin:
                    result = askYesNo('Warning', warningMessage.format(servantName=glyph.name, masterName=rgtMaster.name))
                    if bool(result) is False:
                        glyph.rightMargin = rgtMaster.rightMargin
                        thisLib['rgtActive'] = True
                    else:
                        thisLib['rgtActive'] = False

            links = loadLinksFromFont(self.selectedFont)
            self.w.linksList.set(links)
        self.w.canvas.update()

    def masterGlyphChanged(self, notification):
        masterGlyph = notification.object
        for eachGlyph in self.selectedFont:
            if PLUGIN_LIB_NAME in eachGlyph.lib:
                thisLib = eachGlyph.lib[PLUGIN_LIB_NAME]
                if thisLib['lft'] == masterGlyph.name and thisLib['lftActive'] is True:
                    eachGlyph.leftMargin = masterGlyph.leftMargin
                if thisLib['rgt'] == masterGlyph.name and thisLib['rgtActive'] is True:
                    eachGlyph.rightMargin = masterGlyph.rightMargin
        self.w.canvas.update()

    def displayedGlyphChanged(self, notification):
        self.w.canvas.update()

    # callbacks
    def fontDidOpenCallback(self, notification):
        self.allFonts = AllFonts()

        if self.selectedFont is not None:
            previousFontName = self.w.fontPopUp.getItems()[self.w.fontPopUp.get()]
        else:
            self.selectedFont = self.allFonts[0]
            previousFontName = None

        newNames = getNamesFrom(self.allFonts)
        self.w.fontPopUp.setItems(newNames)

        if previousFontName is not None:
            self.w.fontPopUp.set(newNames.index(previousFontName))

        links = loadLinksFromFont(self.selectedFont)
        self.w.linksList.set(links)
        self.w.linksList.setSelection([0])
        self.currentRow = self.w.linksList[self.w.linksList.getSelection()[0]]
        self.matchSubscriptions()
        self.matchDisplayedSubscriptions()

    def fontDidCloseCallback(self, notification):
        self.allFonts = AllFonts()

        if self.selectedFont is None and self.allFonts != []:
            self.selectedFont = self.allFonts[0]
            links = loadLinksFromFont(self.selectedFont)
            self.w.linksList.set(links)

        currentFontName = self.w.fontPopUp.getItems()[self.w.fontPopUp.get()]
        newNames = getNamesFrom(self.allFonts)
        self.w.fontPopUp.setItems(newNames)

        if self.allFonts != []:
            if currentName in newNames:
                self.w.fontPopUp.set(newNames.index(currentName))
            else:
                self.w.fontPopUp.set(newNames.index(os.path.basename(self.selectedFont)))

    def fontPopUpCallback(self, sender):
        if self._compareLibsToList() is False:
            result = askYesNo('Some changes were not pushed into font, would you like to do it now? Otherwise the changes will be lost')
            if bool(result) is True:
                self.pushIntoFontButtonCallback(sender=None)
        self.selectedFont = self.allFonts[sender.get()]
        links = loadLinksFromFont(self.selectedFont)
        self.w.linksList.set(links)

    def selectionLinksListCallback(self, sender):
        if sender.getSelection() == []:
            sender.setSelection([0])
        self.currentRow = sender[sender.getSelection()[0]]
        self.matchDisplayedSubscriptions()
        self.w.canvas.update()

    def editLinksListCallback(self, sender):
        self.w.canvas.update()
        self.w.pushIntoFontButton.enable(not self._compareLibsToList())

    def linkAllButtonCallback(self, sender):
        for eachRow in self.w.linksList:
            if eachRow['lft'] != '':
                eachRow['lftActive'] = True
            if eachRow['rgt'] != '':
                eachRow['rgtActive'] = True

    def unlockAllButtonCallback(self, sender):
        for eachRow in self.w.linksList:
            if eachRow['lft'] is not None:
                eachRow['lftActive'] = False
            if eachRow['rgt'] is not None:
                eachRow['rgtActive'] = False

    def pushIntoFontButtonCallback(self, sender):
        for eachRow in self.w.linksList:
            eachGlyph = self.selectedFont[eachRow['servant']]
            newLib = {'lft': eachRow['lft'],
                      'lftActive': bool(eachRow['lftActive']),
                      'rgt': eachRow['rgt'],
                      'rgtActive': bool(eachRow['rgtActive'])}

            if newLib['lft'] == '' and newLib['rgt'] == '':
                if PLUGIN_LIB_NAME in eachGlyph.lib:
                    del eachGlyph.lib[PLUGIN_LIB_NAME]
            else:
                eachGlyph.lib[PLUGIN_LIB_NAME] = newLib

        self.matchSubscriptions()
        self._alignServantsToMasters()
        self.w.pushIntoFontButton.enable(False)

    def clearLibsButtonCallback(self, sender):
        for eachGlyph in self.selectedFont:
            if PLUGIN_LIB_NAME in eachGlyph.lib:
                del eachGlyph.lib[PLUGIN_LIB_NAME]
        selectionIndex = self.w.linksList.getSelection()
        links = loadLinksFromFont(self.selectedFont)
        self.w.linksList.set(links)
        self.w.linksList.setSelection(selectionIndex)

    def loadFromTableCallback(self, sender):
        loadingPath = getFile("Select table with linked sidebearings")
        if loadingPath is None:
            return None

        with open(loadingPath[0], 'r') as linksTable:
            rawTable = [item for item in linksTable.readlines()]

        changedItems = []
        toBeLinksList = list(self.selectedFont.glyphOrder)
        for indexRow, eachRow in enumerate(rawTable):
            lft, lftActive, servant, rgtActive, rgt = [item.strip() for item in eachRow.split('\t')]
            servantResult = self._isGlyphNameAllowed(servant)
            lftResult = self._isGlyphNameAllowed(lft)
            rgtResult = self._isGlyphNameAllowed(rgt)

            if all([servantResult, lftResult, rgtResult]) is False:
                message('Line {} contains a mistake'.format(indexRow+1), 'One or more glyphs [lft:<{}> servant:<{}> rgt:<{}>] are not allowed in this font'.format(lft, servant, rgt))
                return None

            if servant in toBeLinksList:
                servantIndex = toBeLinksList.index(servant)
                toBeLinksList[servantIndex] = {'lft': lft,
                                               'lftActive': True if lftActive == 'True' else False,
                                               'servant': servant,
                                               'rgt': rgt,
                                               'rgtActive': True if rgtActive == 'True' else False}
                changedItems.append(servantIndex)

        for eachUnchangedIndex in [ii for ii in range(len(toBeLinksList)) if ii not in changedItems]:
            toBeLinksList[eachUnchangedIndex] = {'lft': '',
                                                 'lftActive': False,
                                                 'servant': toBeLinksList[eachUnchangedIndex],
                                                 'rgt': '',
                                                 'rgtActive': False}

        self.w.linksList.set(toBeLinksList)
        self._compareLibsToList()

    def exportTableCallback(self, sender):
        savingPath = putFile("")
        if savingPath is None:
            return None

        with open(savingPath, 'w') as linksTable:
            for eachRow in self.w.linksList:
                if eachRow['lft'] != '' or eachRow['rgt'] != '':
                    linksTable.write('{lft}\t{lftActive}\t{servant}\t{rgtActive}\t{rgt}\n'.format(**eachRow))

    def windowCloseCallback(self, sender):
        self.unsubscribeGlyphs()
        self.unsubscribeDisplayedGlyphs()
        removeObserver(self, 'fontDidOpen')
        removeObserver(self, 'fontDidClose')
        removeObserver(self, "draw")
        removeObserver(self, "drawInactive")
        super(SidebearingsLinker, self).windowCloseCallback(sender)

    # private methods
    def _isGlyphNameAllowed(self, glyphName):
        if glyphName == '':
            return True
        elif glyphName not in self.selectedFont:
            return False
        else:
            return True

    def _compareLibsToList(self):
        inFont = loadLinksFromFont(self.selectedFont)
        return inFont == [item for item in self.w.linksList]

    def _alignServantsToMasters(self):
        for eachGlyph in self.selectedFont:
            if PLUGIN_LIB_NAME in eachGlyph.lib:
                thisLib = eachGlyph.lib[PLUGIN_LIB_NAME]

                if thisLib['lftActive'] is True and thisLib['lft'] != '':
                    lftMaster = self.selectedFont[thisLib['lft']]
                    eachGlyph.leftMargin = lftMaster.leftMargin

                if thisLib['rgtActive'] is True and thisLib['rgt'] != '':
                    rgtMaster = self.selectedFont[thisLib['rgt']]
                    eachGlyph.rightMargin = rgtMaster.rightMargin

if __name__ == '__main__':
    sb = SidebearingsLinker()
