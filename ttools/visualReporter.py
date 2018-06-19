# coding: utf-8

#######################
# Visual PDF reporter #
#######################

### Modules
# custom
import ui.userInterfaceValues
reload(ui.userInterfaceValues)
from ui.userInterfaceValues import vanillaControlsSize

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
TAB_WIDTH = 21*FROM_MM_TO_PT
TAB_LINE_HEIGHT = 24

GRAY = (.4, .4, .4)
BLACK = (0, 0, 0)
RED = (1, 0, 0)

TEMPLATE_FONT_PATH = os.path.join(os.path.dirname(__file__),
                                  'resources',
                                  'templates',
                                  'templateFont.ufo')

### Plugin
class VisualReporter(BaseWindowController):

    fontNames = []

    def __init__(self):
        super(VisualReporter, self).__init__()

        self.allFonts = AllFonts()
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
        self.collectFontNames()
        previousFontName = self.w.fontsPopUp.get()
        self.w.fontsPopUp.setItems(self.fontNames)
        if previousFontName in self.fontNames:
            self.w.fontsPopUp.set(self.fontNames.index(previousFontName))

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
    def _initPage(self):
        db.newPage('A4')
        db.fontSize(BODY_SIZE_TEXT)
        quota = db.height() - PDF_MARGIN
        self._drawHeader(quota)
        db.font('LucidaGrande')
        quota -= TAB_LINE_HEIGHT
        return quota

    def _drawHeader(self, quota):
        titles = [('line', 0),
                  ('unicode', TAB_WIDTH*.8),
                  ('char', TAB_WIDTH*2),
                  ('glyph name', TAB_WIDTH*3),
                  ('template', TAB_WIDTH*5),
                  ('hairline', TAB_WIDTH*6),
                  ('medium', TAB_WIDTH*7),
                  ('black', TAB_WIDTH*8)]
        db.font('LucidaGrande-Bold')
        for eachTitle, eachX in titles:
            db.text(eachTitle, (PDF_MARGIN+eachX, quota))

    def _drawReport(self, referenceFont, someFonts, glyphNames, reportPath, caption):
        assert isinstance(reportPath, str) or isinstance(reportPath, unicode), 'this should be a string or unicode'
        assert isinstance(glyphNames, list), 'this should be a list of glyphnames'
        assert isinstance(someFonts, list), 'this should be a list of RFont'

        prog = ProgressWindow(text='{}: drawing glyphs...'.format(caption), tickCount=len(glyphNames))
        db.newDrawing()
        quota = self._initPage()
        for indexName, eachGlyphName in enumerate(glyphNames):
            db.save()
            db.translate(PDF_MARGIN, quota)

            # line number
            db.fill(*BLACK)
            db.text('{:0>4d}'.format(indexName), (0, 0))

            # unicode hex
            if eachGlyphName in referenceFont and referenceFont[eachGlyphName].unicode:
                uniIntValue = referenceFont[eachGlyphName].unicode
            elif eachGlyphName in someFonts[0] and someFonts[0][eachGlyphName].unicode:
                uniIntValue = someFonts[0][eachGlyphName].unicode
            else:
                uniIntValue = None

            db.translate(TAB_WIDTH*.8, 0)
            if uniIntValue:
                uniHexValue = 'U+{:04X}'.format(uniIntValue)
                db.fill(*BLACK)
                db.text(uniHexValue, (0, 0))

            # os char
            db.translate(TAB_WIDTH*1.2, 0)
            if uniIntValue:
                txt = db.FormattedString()
                txt.fontSize(BODY_SIZE_GLYPH)
                txt.fill(*GRAY)
                txt += 'H'
                txt.fill(*BLACK)
                txt += unichr(uniIntValue)
                txt.fill(*GRAY)
                txt += 'p'
                db.text(txt, (0, 0))

            # glyphname
            db.translate(TAB_WIDTH, 0)
            db.fontSize(BODY_SIZE_TEXT)
            db.text(eachGlyphName, (0, 0))

            # glyphs
            db.translate(TAB_WIDTH, 0)
            for eachFont in [referenceFont] + someFonts:
                db.translate(TAB_WIDTH, 0)
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
            db.restore()
            prog.update()

            quota -= TAB_LINE_HEIGHT
            if quota <= PDF_MARGIN:
                quota = self._initPage()

        prog.setTickCount(value=None)
        prog.update(text='{}: saving PDF...'.format(caption))

        db.saveImage(reportPath)
        db.endDrawing()
        prog.close()


if __name__ == '__main__':
    vr = VisualReporter()
