#######################
# make PDF glyph list #
#######################

### Modules
import os
import codecs
from datetime import datetime

### Constants
BLACK = (0,0,0)
GRAY = (.4,.4,.4)
FROM_MM_TO_PT = 2.834627813
MARGIN = 22*FROM_MM_TO_PT
AVAILABLE_MODES = ['Unicodes Only', 'No Small Caps', 'All Glyphs']

### Functions & Procedures
def initNewPage(mode):
    newPage('A4')
    stroke(None)
    fill(*BLACK)
    fontSize(9)
    font('FaktPro-Normal')
    # page number
    textBox('{:d}'.format(pageCount()), (0, 0, width(), leading*2), align='center')
    # page title
    justNow = datetime.now()
    textBox(u'TypeTailors standard glyph list – {}/{}/{} – {}'.format(justNow.day, justNow.month, justNow.year, mode), (0, 0, width(), height()-leading*2), align='center')
    # origin system arrangement
    translate(0, height()-MARGIN)
    return 0

def loadGlyphNamesTable(aPath):
    return [item.strip().split('\t') for item in codecs.open(aPath, 'r', 'utf-8')]

### Variables
templateFont = OpenFont(os.path.join('..', '..', 'ttools', 'resources', 'templates', 'templateFont.ufo'), showUI=False)
glyphListPath = os.path.join('..', '..', 'ttools', 'resources', 'tables', 'glyphList.csv')

col1_x = 18*FROM_MM_TO_PT
col2_x = 34*FROM_MM_TO_PT
col3_x = 54*FROM_MM_TO_PT
col4_x = 90*FROM_MM_TO_PT

glyphReprBodySize = 16
leading = 16 

### Instructions
glyphList = loadGlyphNamesTable(glyphListPath)

for eachMode in AVAILABLE_MODES:
    newDrawing()
    thisGlyphList = list(glyphList)

    jumpingY = initNewPage(eachMode)
    while thisGlyphList:
        eachLine = thisGlyphList.pop(0)
        glyphName = eachLine[0]

        if eachMode == 'Unicodes Only' and len(eachLine) == 1:
            continue
        if eachMode == 'No Small Caps' and '.sc' in glyphName:
            continue

        save()
        translate(0, -jumpingY)
        text(glyphName, (col3_x, 0))

        save()
        translate(col2_x, 0)
        scale(glyphReprBodySize/templateFont.info.unitsPerEm)
        referenceGlyph = templateFont['H']
        theGlyph = templateFont[glyphName]
        fill(*GRAY)
        drawGlyph(referenceGlyph)
        translate(referenceGlyph.width, 0)

        fill(*BLACK)
        drawGlyph(theGlyph)
        translate(theGlyph.width, 0)

        fill(*GRAY)
        drawGlyph(referenceGlyph)
        translate(referenceGlyph.width)
        restore()

        # when unicode...
        if len(eachLine) == 3:
            _, uniValue, description = eachLine
            text('U+{}'.format(uniValue), (col1_x, 0))
            text(description, (col4_x, 0))

        restore()

        jumpingY += leading
        if jumpingY >= height()-MARGIN*1.5:
            jumpingY = initNewPage(eachMode)

    justNow = datetime.now()
    fileName = '{0}{1}{2}_TypeT_standardGlyphList_{3}.pdf'.format(justNow.year, justNow.month, justNow.day, eachMode.replace(' ', ''))
    saveImage(fileName)
    endDrawing()


