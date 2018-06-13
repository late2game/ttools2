#!/usr/bin/env python
# coding: utf-8

#######################
# Sidebearings linker #
#######################

### Modules
# custom
import ui.userInterfaceValues
reload(ui.userInterfaceValues)
from ui.userInterfaceValues import vanillaControlsSize

# standard
import os
from collections import OrderedDict
import mojo.drawingTools as dt
from mojo.canvas import CanvasGroup
from mojo.roboFont import AllFonts, CurrentGlyph
from mojo.events import addObserver, removeObserver
from vanilla import FloatingWindow, CheckBoxListCell, List, SquareButton
from vanilla import HorizontalLine, PopUpButton
from defconAppKit.windows.baseWindow import BaseWindowController
from vanilla.dialogs import putFile

### Constants
PLUGIN_WIDTH = 340
PLUGIN_HEIGHT = 1
PLUGIN_TITLE = 'TTools Linked Sidebearings'

MARGIN_HOR = 10
MARGIN_VER = 10
MARGIN_ROW = 10

CANVAS_HEIGHT = 100
UPM_MARGIN = 300

LIST_WIDE_COL = 88
LIST_NARROW_COL = 20

NET_WIDTH = PLUGIN_WIDTH - MARGIN_HOR*2

PLUGIN_LIB_NAME = 'com.ttools.linkedSidebearings'

### Extra Functions
def getNamesFrom(someFonts):
    return [os.path.basename(item.path) for item in someFonts]

def makeDummyLinks(aFont):
    links = []
    for eachGlyphName in aFont.glyphOrder:
        links.append({'lft': '',
                      'lftActive': False,
                      'master': eachGlyphName,
                      'rgt': '',
                      'rgtActive': False})
    return links

def drawReferenceGlyph(aGlyph, scalingFactor, startingX):
    dt.save()
    dt.fill(0)
    dt.stroke(None)
    dt.translate(startingX, 0)
    dt.scale(scalingFactor, scalingFactor)
    dt.translate(0, -aGlyph.getParent().info.descender)
    dt.translate(-aGlyph.width/2, 0)
    dt.drawGlyph(aGlyph)
    dt.restore()


### Class
class SidebearingsLinker(BaseWindowController):

    allFonts = []
    selectedFont = None

    lftGl = None
    masterGl = None
    rgtGl = None

    def __init__(self):
        super(SidebearingsLinker, self).__init__()

        # collecting fonts
        self.allFonts = AllFonts()
        if self.allFonts != []:
            self.selectedFont = self.allFonts[0]

            if PLUGIN_LIB_NAME not in self.selectedFont.lib:
                self.selectedFont.lib[PLUGIN_LIB_NAME] = makeDummyLinks(self.selectedFont)

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
                                   {"title": "glyph", 'key': 'master', 'width': LIST_WIDE_COL, "editable": False},
                                   {"title": "active", "cell": CheckBoxListCell(), 'key': 'rgtActive', 'width': LIST_NARROW_COL},
                                   {"title": "right", 'key': 'rgt', 'width': LIST_WIDE_COL}]

        if self.selectedFont:
            listContent = self.selectedFont.lib[PLUGIN_LIB_NAME]
        else:
            listContent = []

        self.w.linksList = List((MARGIN_HOR, jumpingY, NET_WIDTH, 200),
                                listContent,
                                showColumnTitles=False,
                                allowsMultipleSelection=False,
                                columnDescriptions=linksColumnDescriptions,
                                selectionCallback=self.selectionLinksListCallback,
                                editCallback=self.editLinksListCallback)

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
        self.w.clearLibButton = SquareButton((MARGIN_HOR*2+buttonWidth, jumpingY, buttonWidth, vanillaControlsSize['ButtonRegularHeight']*1.5),
                                             'Clear Lib',
                                             callback=self.clearLibButtonCallback)

        jumpingY += vanillaControlsSize['ButtonRegularHeight']*1.5 + MARGIN_ROW
        self.w.loadFromTable = SquareButton((MARGIN_HOR, jumpingY, buttonWidth, vanillaControlsSize['ButtonRegularHeight']*1.5),
                                            'Load from table',
                                            callback=self.loadFromTableCallback)
        self.w.exportTable = SquareButton((MARGIN_HOR*2+buttonWidth, jumpingY, buttonWidth, vanillaControlsSize['ButtonRegularHeight']*1.5),
                                          'Export table',
                                          callback=self.exportTableCallback)

        jumpingY += vanillaControlsSize['ButtonRegularHeight']*1.5 + MARGIN_VER*2
        self.w.resize(PLUGIN_WIDTH, jumpingY)

        self.setUpBaseWindowBehavior()
        addObserver(self, 'fontDidOpenCallback', 'fontDidOpen')
        addObserver(self, 'fontDidCloseCallback', 'fontDidClose')
        self.w.open()

    # private methods
    def _updateListCtrls(self):
        self.w.linksList.setItems(self.selectedFontLinks)

    def _loadGlyphAttributes(self):
        row = self.w.linksList[self.w.linksList.getSelection()[0]]

        lftGlName = row['lft']
        if lftGlName != '':
            self.lftGl = self.selectedFont[lftGlName]
        else:
            self.lftGl = None

        masterGlName = row['master']
        if masterGlName != '':
            self.masterGl = self.selectedFont[masterGlName]
        else:
            self.masterGl = None

        rgtGlName = row['rgt']
        if rgtGlName != '':
            self.rgtGl = self.selectedFont[rgtGlName]
        else:
            self.rgtGl = None

    # canvas callback
    def draw(self):
        self._loadGlyphAttributes()
        try:
            if self.selectedFont is not None:
                scalingFactor = CANVAS_HEIGHT/(self.selectedFont.info.unitsPerEm+UPM_MARGIN)

                if self.lftGl is not None:
                    drawReferenceGlyph(aGlyph=self.lftGl,
                                       scalingFactor=scalingFactor,
                                       startingX=NET_WIDTH*(1/6))

                if self.masterGl is not None:
                    drawReferenceGlyph(aGlyph=self.masterGl,
                                       scalingFactor=scalingFactor,
                                       startingX=NET_WIDTH*(3/6))

                if self.rgtGl is not None:
                    drawReferenceGlyph(aGlyph=self.rgtGl,
                                       scalingFactor=scalingFactor,
                                       startingX=NET_WIDTH*(5/6))

        except Exception, error:
            print error

    # callbacks
    def fontDidOpenCallback(self, notification):
        self.allFonts = AllFonts()
        currentFontName = self.w.fontPopUp.getItems()[self.w.fontPopUp.get()]
        newNames = getNamesFrom(self.allFonts)
        self.w.fontPopUp.setItems(newNames)
        self.w.fontPopUp.set(newNames.index(currentName))

    def fontDidCloseCallback(self, notification):
        self.allFonts = AllFonts()

        if self.selectedFont is None and self.allFonts != []:
            self.selectedFont = self.allFonts[0]

        currentFontName = self.w.fontPopUp.getItems()[self.w.fontPopUp.get()]
        newNames = getNamesFrom(self.allFonts)
        self.w.fontPopUp.setItems(newNames)

        if self.allFonts != []:
            if currentName in newNames:
                self.w.fontPopUp.set(newNames.index(currentName))
            else:
                self.w.fontPopUp.set(newNames.index(os.path.basename(self.selectedFont)))

    def fontPopUpCallback(self, sender):
        self.selectedFont = self.allFonts[sender.get()]
        self._updateListCtrls()

    def selectionLinksListCallback(self, sender):
        self.w.canvas.update()

    def editLinksListCallback(self, sender):
        self.w.canvas.update()

    def linkAllButtonCallback(self, sender):
        for eachRow in self.w.linksList:
            eachRow['lftActive'] = True
            eachRow['rgtActive'] = True

    def unlockAllButtonCallback(self, sender):
        for eachRow in self.w.linksList:
            eachRow['lftActive'] = False
            eachRow['rgtActive'] = False

    def pushIntoFontButtonCallback(self, sender):
        self.selectedFont.lib[PLUGIN_LIB_NAME] = [item for item in self.w.linksList]

    def clearLibButtonCallback(self, sender):
        del self.selectedFont.lib[PLUGIN_LIB_NAME]

    def loadFromTableCallback(self, sender):
        loadingPath = getFile("")
        with open(loadingPath, 'r') as linksTable:
            linksList = []
            for eachRow in linksTable.readlines():
                lft, lftActive, master, rgtActive, rgt = eachRow.split('\t')
                linksList.append({'lft': lft,
                                  'lftActive': lftActive,
                                  'master': master,
                                  'rgt': rgt,
                                  'rgtActive': rgtActive})
        self.w.linksList.setItems(linksList)

    def exportTableCallback(self, sender):
        savingPath = putFile("")
        if savingPath is not None:
            with open(savingPath, 'w') as linksTable:
                for eachRow in self.w.linksList:
                    linksTable.write('{lft}\t{lftActive}\t{master}\t{rgtActive}\t{rgt}'.format(eachRow))


if __name__ == '__main__':
    sb = SidebearingsLinker()
