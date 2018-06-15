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

# standard library
import os

### Constants
PLUGIN_WIDTH = 250
PLUGIN_TITLE = 'TTools Visual Reporter'

FROM_MM_TO_PT = 2.834627813
PDF_MARGIN = 10*FROM_MM_TO_PT

GRAY = (.4, .4, .4)
BLACK = (0, 0, 0)
RED = (1, 0, 0)

### Drawing routines
def initPage():
    db.newPage('A4')
    db.fontSize(bodySizeText)
    quota = db.height() -MARGIN
    drawHeader(quota)
    db.font('LucidaGrande')
    quota -= tabLineHeight
    return quota

def drawHeader(quota):
    titles = [('line', 0),
              ('unicode', tabWidth*.8),
              ('char', tabWidth*2),
              ('glyph name', tabWidth*3),
              ('template', tabWidth*5),
              ('hairline', tabWidth*6),
              ('medium', tabWidth*7),
              ('black', tabWidth*8)]
    db.font('LucidaGrande-Bold')
    for eachTitle, eachX in titles:
        db.text(eachTitle, (MARGIN+eachX, quota))

"""


### Functions & Procedures


### Variables
bodySizeGlyph = 18
bodySizeText  = 11
tabWidth = 21*FROM_MM_TO_PT
tabLineHeight = 24

IRA_hairline = OpenFont(os.path.join('..', '00_repository', 'IRA Hairline.ufo'), showUI=False)
IRA_medium =   OpenFont(os.path.join('..', '00_repository', 'IRA Medium.ufo'), showUI=False)
IRA_black =    OpenFont(os.path.join('..', '00_repository', 'IRA Black.ufo'), showUI=False)

templateFont = OpenFont('/Users/robertoarista/Documents/Work/TypeTailors/TTools/ttools/resources/templates/templateFont.ufo', showUI=False)
templateCharacterMap = templateFont.getCharacterMapping()

### Instructions
quota = initPage()

index = 1
IRA_leftovers = [gl for gl in IRA_hairline.glyphOrder if gl not in templateFont.glyphOrder]
for eachGlyphName in templateFont.glyphOrder + [None] + IRA_leftovers:

    if eachGlyphName is None:
        saveImage('templateComplaint.pdf')
        newDrawing()
        index = 1
        quota = initPage()
        continue

    save()
    translate(MARGIN, quota)

    # line number
    fill(*BLACK)
    text('{:0>4d}'.format(index), (0, 0))

    # unicode hex
    if eachGlyphName in templateFont and templateFont[eachGlyphName].unicode:
        uniIntValue = templateFont[eachGlyphName].unicode
    elif eachGlyphName in IRA_hairline and IRA_hairline[eachGlyphName].unicode:
        uniIntValue = IRA_hairline[eachGlyphName].unicode
    else:
        uniIntValue = None

    translate(tabWidth*.8, 0)
    if uniIntValue:
        uniHexValue = 'U+{:04X}'.format(uniIntValue)
        fill(*BLACK)
        text(uniHexValue, (0, 0))

    # os char
    translate(tabWidth*1.2, 0)
    if uniIntValue:
        txt = FormattedString()
        txt.fontSize(bodySizeGlyph)
        txt.fill(*GRAY)
        txt += 'H'
        txt.fill(*BLACK)
        txt += unichr(uniIntValue)
        txt.fill(*GRAY)
        txt += 'p'
        text(txt, (0, 0))

    # glyphname
    translate(tabWidth, 0)
    fontSize(bodySizeText)
    text(eachGlyphName, (0, 0))

    # glyphs
    translate(tabWidth, 0)
    for eachFont in [templateFont, IRA_hairline, IRA_medium, IRA_black]:
        translate(tabWidth, 0)
        if eachGlyphName in eachFont:
            eachGlyph = eachFont[eachGlyphName]
            lftRefGL = eachFont['H']
            rgtRefGL = eachFont['p']

            save()
            scale(bodySizeGlyph/eachFont.info.unitsPerEm)
            fill(*GRAY)
            drawGlyph(lftRefGL)
            translate(lftRefGL.width, 0)
            fill(*BLACK)
            drawGlyph(eachGlyph)
            translate(eachGlyph.width, 0)
            fill(*GRAY)
            drawGlyph(rgtRefGL)
            restore()
    restore()

    quota -= tabLineHeight
    if quota <= MARGIN:
        quota = initPage()

    index +=1

saveImage('nonTemplateComplaint.pdf')


"""

def drawReport(someFonts, aFolder)
    templateFont = OpenFont('/Users/robertoarista/Documents/Work/TypeTailors/TTools/ttools/resources/templates/templateFont.ufo', showUI=False)
    templateCharacterMap = templateFont.getCharacterMapping()

### Plugin
class VisualReporter(BaseWindowController):

    fontNames = []

    def __init__(self):
        super(VisualReporter, self).__init__()

        self.allFonts = AllFonts()
        self.collectFontNames()

        self.w = Window((0, 0, PLUGIN_WIDTH, 1),
                        PLUGIN_TITLE)

        jumpingY = MARGIN
        self.w.fontsPopUp = PopUpButton((MARGIN, jumpingY, NET_WIDTH, vanillaControlsSize['PopUpButtonRegularHeight']),
                                        self.fontNames,
                                        callback=None)

        self.w.reportButton = SquareButton((),
                                           'Generate PDF Report',
                                           callback=self.reportButtonCallback)

        self.setUpBaseWindowBehavior()
        addObserver(self, 'updateFontOptions', "newFontDidOpen")
        addObserver(self, 'updateFontOptions', "fontDidOpen")
        addObserver(self, 'updateFontOptions', "fontWillClose")
        self.w.bind("close", self.windowCloseCallback)
        self.w.resize()
        self.w.open()

    def collectFontNames(self):
        self.fontNames = ['All Fonts']+[os.path.basename(item.path) for item in self.allFonts]

    def updateFontOptions(self):
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

        PDF_folder = getFolder('Choose a folder...')
        drawReport(someFonts=fontsToProcess, aFolder=PDF_folder)

    def windowCloseCallback(self, sender):
        removeObserver(self, "newFontDidOpen")
        removeObserver(self, "fontDidOpen")
        removeObserver(self, "fontWillClose")
        super(VisualReporter, self).windowCloseCallback(sender)

if __name__ == '__main__':
    vr = VisualReporter()