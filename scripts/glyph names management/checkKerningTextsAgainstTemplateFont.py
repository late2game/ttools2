#!/usr/bin/env python
# coding: utf-8

################################################
# Check kerning texts against templateFont.ufo #
################################################

### Modules
import os
import codecs
from itertools import chain
from defconAppKit.tools.textSplitter import splitText

### Constants

### Functions & Procedures
def catchFilesAndFolders(path, extension):
    """Return all the files in a path with a specific extension"""
    items = [os.path.join(path, item) for item in os.listdir(path) if item.endswith(extension)]
    return items

def loadKerningTexts(aPath):
    kerningTextsPaths = catchFilesAndFolders(aPath, '.txt')
    kerningTextsUniqueNames = {}
    for eachPath in kerningTextsPaths:
        singleKerningText = [splitText(row.strip(), templateFont.naked().unicodeData) for row in codecs.open(eachPath, 'r', 'utf-8').readlines()]
        uniqueNames = []
        for eachRow in singleKerningText:
            for eachCell in eachRow:
                if eachCell not in uniqueNames:
                    uniqueNames.append(eachCell)
        kerningTextsUniqueNames[os.path.basename(eachPath)] = uniqueNames
    return kerningTextsUniqueNames

### Variables
templateFont = OpenFont(os.path.join('..', '..', 'ttools', 'resources', 'templates', 'templateFont.ufo'), showUI=False)
kerningTextsFolder = os.path.join('..', '..', 'ttools', 'resources', 'kerningTexts')

### Instructions

kerningTextsUniqueNames = loadKerningTexts(kerningTextsFolder)
for eachKey, eachValueGroup in kerningTextsUniqueNames.items():
    for eachName in eachValueGroup:
        if eachName not in templateFont.glyphOrder:
            print '%s from %s not in template font' % (eachName, eachKey)



