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

BLACK = (0,0,0)
RED = (1,0,0)
BLUE = (0,0,1)

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
    currentRow = None
    selectedFont = None

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

    # canvas callback
    def draw(self):
        try:
            if self.selectedFont is not None and self.currentRow is not None:
                scalingFactor = CANVAS_HEIGHT/(self.selectedFont.info.unitsPerEm+UPM_MARGIN)

                if self.currentRow['lft'] in self.selectedFont:
                    lftGl = self.selectedFont[self.currentRow['lft']]
                    if lftGl is not None:
                        drawReferenceGlyph(aGlyph=lftGl,
                                           scalingFactor=scalingFactor,
                                           startingX=NET_WIDTH*(1/6),
                                           left=True,
                                           right=False)

                    drawLock(closed=self.currentRow['lftActive'],
                             startingX=NET_WIDTH*(2/6),
                             glyphQuota=self.selectedFont.info.xHeight,
                             scalingFactor=scalingFactor)

                if self.currentRow['master'] in self.selectedFont:
                    masterGl = self.selectedFont[self.currentRow['master']]
                    if masterGl is not None:
                        drawReferenceGlyph(aGlyph=masterGl,
                                           scalingFactor=scalingFactor,
                                           startingX=NET_WIDTH*(3/6),
                                           left=True,
                                           right=True)

                if self.currentRow['rgt'] in self.selectedFont:
                    rgtGl = self.selectedFont[self.currentRow['rgt']]
                    if rgtGl is not None:
                        drawReferenceGlyph(aGlyph=rgtGl,
                                           scalingFactor=scalingFactor,
                                           startingX=NET_WIDTH*(5/6),
                                           right=True)

                    drawLock(closed=self.currentRow['rgtActive'],
                             startingX=NET_WIDTH*(4/6),
                             glyphQuota=self.selectedFont.info.xHeight,
                             scalingFactor=scalingFactor)

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
        self.currentRow = self.w.linksList[self.w.linksList.getSelection()[0]]
        self.w.canvas.update()

    def editLinksListCallback(self, sender):
        self.w.canvas.update()

    def linkAllButtonCallback(self, sender):
        for eachRow in self.w.linksList:
            if eachRow['lft'] is not None:
                eachRow['lftActive'] = True
            if eachRow['rgt'] is not None:
                eachRow['rgtActive'] = True

    def unlockAllButtonCallback(self, sender):
        for eachRow in self.w.linksList:
            if eachRow['lft'] is not None:
                eachRow['lftActive'] = False
            if eachRow['rgt'] is not None:
                eachRow['rgtActive'] = False

    def pushIntoFontButtonCallback(self, sender):
        self.selectedFont.lib[PLUGIN_LIB_NAME] = [item for item in self.w.linksList]

    def clearLibButtonCallback(self, sender):
        del self.selectedFont.lib[PLUGIN_LIB_NAME]

    def loadFromTableCallback(self, sender):
        loadingPath = getFile("Select table with linked sidebearings")
        with open(loadingPath, 'r') as linksTable:
            linksList = []
            for eachRow in linksTable.readlines():
                lft, lftActive, master, rgtActive, rgt = eachRow.split('\t')
                linksList.append({'lft': lft,
                                  'lftActive': lftActive,
                                  'master': master,
                                  'rgt': rgt,
                                  'rgtActive': rgtActive})
        # here we should perform some checks, sanitize data
        # self.w.linksList.setItems(linksList)

    def exportTableCallback(self, sender):
        savingPath = putFile("")
        if savingPath is not None:
            with open(savingPath, 'w') as linksTable:
                for eachRow in self.w.linksList:
                    linksTable.write('{lft}\t{lftActive}\t{master}\t{rgtActive}\t{rgt}'.format(eachRow))


if __name__ == '__main__':
    sb = SidebearingsLinker()
