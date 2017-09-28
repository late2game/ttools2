####################
# proofing kerning #
####################

### Modules
import os
import codecs
from collections import OrderedDict
from defconAppKit.tools.textSplitter import splitText

### Constants
FROM_MM_TO_PT = 2.834627813

### Functions & Procedures
def drawColumnTitles():
    fontPaths2colWidth = fontsPerDoc[weightToDisplay]
    for eachFontPath, eachColOffset in fontPaths2colWidth:
        font('Georgia')
        fontSize(16)
        text(dir2text[os.path.dirname(eachFontPath)], (horMargin+eachColOffset, 36))
        text(dir2text[os.path.dirname(eachFontPath)], (horMargin+eachColOffset, height()-36))

def loadKerningTexts(kerningTextFolder):
    """copied/modified from kerningMisc.py"""
    kerningWordDB = OrderedDict()
    kerningTextBaseNames = [pth for pth in os.listdir(kerningTextFolder) if pth.endswith('.txt')]
    kerningTextBaseNames.sort()
    for eachKerningTextBaseName in kerningTextBaseNames:
        kerningWordsDoc = codecs.open(os.path.join(kerningTextFolder, eachKerningTextBaseName), 'r', 'utf-8').readlines()

        kerningWords = []
        for rawWord in kerningWordsDoc:
            if '#' in rawWord:
                word = u'%s' % rawWord[:rawWord.index('#')].strip()
            else:
                word = u'%s' % rawWord.strip()

            if word:
                kerningWords.append(word)

        uniqueKerningWords = []
        _ = [uniqueKerningWords.append(word) for word in kerningWords if word not in uniqueKerningWords]
        
        kerningWordsList = [{'#': index, 'word': word} for (index, word) in enumerate(uniqueKerningWords)]
        kerningWordDB[eachKerningTextBaseName[3:]] = kerningWordsList
    return kerningWordDB

### Variables
fontsFolder = '/Users/robertoarista/Desktop/kerningTest'
weightToDisplay = 'bold'

dir2text = {
    'noKerning':   'not kerned',    
    'withKerning': 'kerned'    
    }

fontsPerDoc = {
    'light': [('noKerning/Dresden Light Condensed.otf', 35+15+5),
              ('withKerning/Dresden Light Condensed.otf', 200+15+5),

              ('noKerning/Dresden Light.otf', 400+15),
              ('withKerning/Dresden Light.otf', 600+15+30)
             ],

    'bold': [('noKerning/Dresden Bold Condensed.otf', 35+15+5),
             ('withKerning/Dresden Bold Condensed.otf', 240+15+5),

             ('noKerning/Dresden Bold.otf', 475+15+20),
             ('withKerning/Dresden Bold.otf', 720+15+30+40)
             ]
    }

lcTexts = ['02_UC2LC.txt', '03_UC2LCACC.txt', '06_LC2LC.txt', '07_LC2INT.txt']

debugMode = True
kerningTextsFolder = os.path.join('..', '..', 'ttools', 'resources', 'kerningTexts')

canvasWidth, canvasHeight = 420*FROM_MM_TO_PT, 297*FROM_MM_TO_PT
horMargin = 15*FROM_MM_TO_PT
netWidth = canvasWidth-horMargin*2
verMargin = 20*FROM_MM_TO_PT
netHeight = canvasHeight-verMargin*2

### Instructions
# choose which fonts
fontPaths2colWidth = fontsPerDoc[weightToDisplay]

# testInstall fonts
fontNames2colWidth = [('Georgia', 0)]
for eachPath, eachColWidth in fontPaths2colWidth:
    aName = installFont(os.path.join(fontsFolder, eachPath))
    fontNames2colWidth.append((aName, eachColWidth))

# start making proof
myKerningTexts = loadKerningTexts(kerningTextsFolder)
stringToDisplay = FormattedString()
stringToDisplay.fontSize(24)

# building tabs
kerningTabs = []
for _, eachColWidth in fontNames2colWidth:
    kerningTabs.append((eachColWidth, 'left'))
stringToDisplay.tabs(*kerningTabs)

# building formattedString
for eachKerningTextName, eachKerningTextData in myKerningTexts.items():

    # we only need UC
    if 'LC' not in eachKerningTextName:
        # init table
        stringToDisplay.tabs(None)
        stringToDisplay.append('%s\n' % eachKerningTextName, font='Georgia')
        stringToDisplay.tabs(*kerningTabs)

        # iterating over the kerning data
        for eachLine in eachKerningTextData:
            # unpacking data
            indexLine = eachLine['#']
            if 'UC2UC' in eachKerningTextName:
                word = eachLine['word'].replace('//', '/')
            else:
                word = eachLine['word'].replace('//', '/')
            # iterating over font names
            for indexFontName, eachFontData in enumerate(fontNames2colWidth):
                eachFontName, _ = eachFontData
                if eachFontName == 'Georgia':
                    stringToDisplay.append('%s' % indexLine, font=eachFontName)
                else:
                    stringToDisplay.append(word, font=eachFontName)
                # defining the limit character (cell or line)
                if indexFontName == len(fontNames2colWidth)-1:
                    stringToDisplay += '\n'
                else:
                    stringToDisplay += '\t'

        stringToDisplay += '\n'

# drawing the formatted string on the many canvases
overflow = stringToDisplay
while overflow:
    newPage(canvasWidth, canvasHeight)
    drawColumnTitles()
    overflow = textBox(overflow, (horMargin, verMargin, netWidth, netHeight))
