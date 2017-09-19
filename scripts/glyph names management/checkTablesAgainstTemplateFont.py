#!/usr/bin/env python
# coding: utf-8

#########################################
# Check tables against templateFont.ufo #
#########################################

### Modules
import os
import codecs

### Constants
ERROR_MESSAGE = '[WARNING] %(glyphName)s from %(tableName)s not in templateFont'

### Functions & Procedures
def loadTable(aPath):
    return [[cell.strip() for cell in row.split('\t') if not cell.startswith('*')] for row in codecs.open(aPath, 'r', 'utf-8').readlines()]

### Variables
tablesFolder = os.path.join('..', '..', 'ttools', 'resources', 'tables')
tablesNames = ['accentedLettersTable.csv', 'dnomNumrSubsSups.csv', 'fractions.csv', 'interpunctionFlippedSidebearings.csv', 'interpunctionGroups.csv', 'kerningPureSymmetricalGlyphs.csv', 'kerningSymmetricalCouples.csv', 'LCextrasTests.csv', 'LCligatures.csv', 'LCligaturesTests.csv', 'LigAndExtraSC.csv', 'mathCase.csv', 'mathSC.csv', 'tabularFigures.csv', 'UCextrasTests.csv', 'verticalGroups.csv']

### Instructions
templateFont = OpenFont(os.path.join('..', '..', 'ttools', 'resources', 'templates', 'templateFont.ufo'), showUI=False)
templateFontGlyphOrder = templateFont.glyphOrder

errors = []
for eachTableName in tablesNames:
    myTable = loadTable(os.path.join(tablesFolder, eachTableName))

    for eachRow in myTable:
        for eachCell in eachRow:
            if eachCell not in templateFontGlyphOrder and eachCell:
                errors.append(ERROR_MESSAGE % {'glyphName': eachCell, 'tableName': eachTableName})

errorsFile = codecs.open('checkTablesAgainstTemplateFontErrors.txt', 'w', 'utf-8')
errorsFile.write('\n'.join(errors))
errorsFile.close()
