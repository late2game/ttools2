# coding: utf-8

#######################
# Visual PDF reporter #
#######################

### Modules
# custom
import ui.userInterfaceValues
reload(ui.userInterfaceValues)
from ui.userInterfaceValues import vanillaControlsSize

import extraTools.miscFunctions
reload(extraTools.miscFunctions)
from extraTools.miscFunctions import catchFilesAndFolders

# third parties
import drawBot as db
from mojo.events import addObserver, removeObserver
from mojo.roboFont import AllFonts, OpenFont
from vanilla import Window, SquareButton, PopUpButton
from vanilla.dialogs import getFolder
from defconAppKit.windows.baseWindow import BaseWindowController
from defconAppKit.windows.progressWindow import ProgressWindow

# standard library
import os
import codecs
from datetime import datetime

### Constants
PLUGIN_WIDTH = 250
PLUGIN_TITLE = 'TTools Visual Reporter'
UI_MARGIN = 8
NET_WIDTH = PLUGIN_WIDTH-UI_MARGIN*2

FROM_MM_TO_PT = 2.834627813
PDF_MARGIN = 10*FROM_MM_TO_PT

BODY_SIZE_GLYPH = 18
BODY_SIZE_TEXT  = 11
TAB_WIDTH = 24*FROM_MM_TO_PT
TAB_LINE_HEIGHT = 24

baseNames = ['Air',
             'Hair',
             'Hairline',
             'Thin',
             'Light',
             'Blond',
             'Normal',
             'Medium',
             'SemiBold',
             'Bold',
             'Black',
             'Black']

STYLES_ORDER = []
for eachBaseName in baseNames:
    STYLES_ORDER.append(eachBaseName)
    STYLES_ORDER.append('{} Italic'.format(eachBaseName))
    STYLES_ORDER.append('{} Slanted'.format(eachBaseName))

GRAY = (.4, .4, .4)
BLACK = (0, 0, 0)
RED = (1, 0, 0)

TEMPLATE_FONT_PATH = os.path.join(os.path.dirname(__file__),
                                  'resources',
                                  'templates',
                                  'templateFont.ufo')

SMART_SETS_FOLDER = os.path.join(os.path.dirname(__file__),
                                 'resources',
                                 'smartSets')

### Functions 
def loadSmartSets():
    # loading smart sets path
    smartSetsPaths = catchFilesAndFolders(SMART_SETS_FOLDER, '.txt')
    # building a reference glyph order from smart sets
    smartSets = {}
    for eachPath in smartSetsPaths:
        smartSets[os.path.basename(eachPath)] = [name.strip() for name in codecs.open(eachPath, 'r', 'utf-8').readlines()]
    return sorted(smartSets.items(), key=lambda x: x[0])

SMART_SETS = loadSmartSets()

COLS = {'set': 0,
        'line': TAB_WIDTH*1.5,
        'unicode': TAB_WIDTH*2.5,
        'char': TAB_WIDTH*4,
        'glyph name': TAB_WIDTH*5,
        'template': TAB_WIDTH*8}


### Plugin
class VisualReporter(BaseWindowController):

    fontNames = []

    def __init__(self):
        super(VisualReporter, self).__init__()

        self.allFonts = AllFonts()
        self.sortAllFonts()
        self.collectFontNames()

        self.w = Window((0, 0, PLUGIN_WIDTH, 1),
                        PLUGIN_TITLE)

        jumpingY = UI_MARGIN
        self.w.fontsPopUp = PopUpButton((UI_MARGIN, jumpingY, NET_WIDTH, vanillaControlsSize['PopUpButtonRegularHeight']),
                                        self.fontNames,
                                        callback=None)

        jumpingY += vanillaControlsSize['PopUpButtonRegularHeight']+UI_MARGIN
        self.w.reportButton = SquareButton((UI_MARGIN, jumpingY, NET_WIDTH, vanillaControlsSize['ButtonRegularHeight']*1.5),
                                           'Generate PDF Report',
                                           callback=self.reportButtonCallback)
        jumpingY += vanillaControlsSize['ButtonRegularHeight']*1.5+UI_MARGIN

        self.setUpBaseWindowBehavior()
        addObserver(self, 'updateFontOptions', "newFontDidOpen")
        addObserver(self, 'updateFontOptions', "fontDidOpen")
        addObserver(self, 'updateFontOptions', "fontWillClose")
        self.w.bind("close", self.windowCloseCallback)
        self.w.resize(PLUGIN_WIDTH, jumpingY)
        self.w.open()

    def collectFontNames(self):
        self.fontNames = ['All Fonts']+[os.path.basename(item.path) for item in self.allFonts]

    def updateFontOptions(self, notification):
        self.allFonts = AllFonts()
        self.sortAllFonts()
        self.collectFontNames()
        previousFontName = self.w.fontsPopUp.get()
        self.w.fontsPopUp.setItems(self.fontNames)
        if previousFontName in self.fontNames:
            self.w.fontsPopUp.set(self.fontNames.index(previousFontName))

    def sortAllFonts(self):
        self.allFonts = sorted(self.allFonts, key=lambda x:STYLES_ORDER.index(x.info.styleName))

    def reportButtonCallback(self, sender):
        popUpIndex = self.w.fontsPopUp.get()
        if popUpIndex == 0:   # all fonts
            fontsToProcess = self.allFonts
        else:
            fontsToProcess = [self.allFonts[popUpIndex]]

        PDF_folder = getFolder('Choose where to save the reports')[0]
        templateFont = OpenFont(TEMPLATE_FONT_PATH, showUI=False)
        justNow = datetime.now()

        self._drawReport(referenceFont=templateFont,
                         someFonts=fontsToProcess,
                         glyphNames=templateFont.glyphOrder,
                         reportPath=os.path.join(PDF_folder, '{:0>4d}{:0>2d}{:0>2d}_templateCompliant.pdf'.format(justNow.year, justNow.month, justNow.day)),
                         caption='Template Compliant')

        leftovers = []
        for eachFont in fontsToProcess:
            leftovers.extend([name for name in eachFont.glyphOrder if name not in templateFont.glyphOrder and name not in leftovers])

        self._drawReport(referenceFont=templateFont,
                         someFonts=fontsToProcess,
                         glyphNames=leftovers,
                         reportPath=os.path.join(PDF_folder, '{:0>4d}{:0>2d}{:0>2d}_extraTemplate.pdf'.format(justNow.year, justNow.month, justNow.day)),
                         caption='Extra Template')

    def windowCloseCallback(self, sender):
        removeObserver(self, "newFontDidOpen")
        removeObserver(self, "fontDidOpen")
        removeObserver(self, "fontWillClose")
        super(VisualReporter, self).windowCloseCallback(sender)

    # drawing routines
    def _initPage(self, fontStyles):
        db.newPage('A3Landscape')
        db.fontSize(BODY_SIZE_TEXT)
        quota = db.height() - PDF_MARGIN
        self._drawHeader(quota, fontStyles)
        db.font('LucidaGrande')
        quota -= TAB_LINE_HEIGHT*2
        return quota

    def _drawHeader(self, quota, fontStyles):
        fontTitles = {}

        colIndex = int(COLS['template']/TAB_WIDTH)
        for eachFontStyle in fontStyles:
            colIndex += 1
            fontTitles[eachFontStyle] = colIndex*TAB_WIDTH

        headers = {k: v for (k, v) in COLS.items()+fontTitles.items()}
        db.font('LucidaGrande-Bold')
        for eachTitle, eachX in headers.items():
            db.text(eachTitle, (PDF_MARGIN+eachX, quota))

    def _drawReport(self, referenceFont, someFonts, glyphNames, reportPath, caption):
        assert isinstance(reportPath, str) or isinstance(reportPath, unicode), 'this should be a string or unicode'
        assert isinstance(glyphNames, list), 'this should be a list of glyphnames'
        assert isinstance(someFonts, list), 'this should be a list of RFont'

        prog = ProgressWindow(text='{}: drawing glyphs...'.format(caption), tickCount=len(glyphNames))

        try:
            db.newDrawing()

            twoLinesFontStyles = [ff.info.styleName.replace(' ', '\n') for ff in someFonts]
            quota = self._initPage(twoLinesFontStyles)
            for indexName, eachGlyphName in enumerate(glyphNames):
                db.save()
                db.translate(PDF_MARGIN, quota)

                # set name
                for eachSetName, eachGroup in SMART_SETS:
                    if eachGlyphName in eachGroup:
                        setName = eachSetName.replace('.txt', '')
                        break
                else:
                    setName = ''
                db.text(setName, (COLS['set'], 0))

                # line number
                db.fill(*BLACK)
                db.text('{:0>4d}'.format(indexName), (COLS['line'], 0))

                # unicode hex
                if eachGlyphName in referenceFont and referenceFont[eachGlyphName].unicode:
                    uniIntValue = referenceFont[eachGlyphName].unicode
                elif eachGlyphName in someFonts[0] and someFonts[0][eachGlyphName].unicode:
                    uniIntValue = someFonts[0][eachGlyphName].unicode
                else:
                    uniIntValue = None

                if uniIntValue:
                    uniHexValue = 'U+{:04X}'.format(uniIntValue)
                    db.fill(*BLACK)
                    db.text(uniHexValue, (COLS['unicode'], 0))

                # os char
                if uniIntValue:
                    txt = db.FormattedString()
                    txt.fontSize(BODY_SIZE_GLYPH)
                    txt.fill(*GRAY)
                    txt += 'H'
                    txt.fill(*BLACK)
                    txt += unichr(uniIntValue)
                    txt.fill(*GRAY)
                    txt += 'p'
                    db.text(txt, (COLS['char'], 0))

                # glyphname
                db.fontSize(BODY_SIZE_TEXT)
                db.text(eachGlyphName, (COLS['glyph name'], 0))

                # glyphs
                db.translate(COLS['template'], 0)
                for eachFont in [referenceFont] + someFonts:
                    if eachGlyphName in eachFont:
                        eachGlyph = eachFont[eachGlyphName]
                        lftRefGL = eachFont['H']
                        rgtRefGL = eachFont['p']

                        db.save()
                        db.scale(BODY_SIZE_GLYPH/eachFont.info.unitsPerEm)
                        db.fill(*GRAY)
                        db.drawGlyph(lftRefGL)
                        db.translate(lftRefGL.width, 0)
                        db.fill(*BLACK)
                        db.drawGlyph(eachGlyph)
                        db.translate(eachGlyph.width, 0)
                        db.fill(*GRAY)
                        db.drawGlyph(rgtRefGL)
                        db.restore()
                    db.translate(TAB_WIDTH, 0)
                db.restore()
                prog.update()

                quota -= TAB_LINE_HEIGHT
                if quota <= PDF_MARGIN:
                    quota = self._initPage(twoLinesFontStyles)

            prog.setTickCount(value=None)
            prog.update(text='{}: saving PDF...'.format(caption))

            db.saveImage(reportPath)
            db.endDrawing()

        except Exception as e:
            prog.close()
            raise e

        prog.close()


if __name__ == '__main__':
    vr = VisualReporter()
