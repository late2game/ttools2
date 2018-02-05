#!/usr/bin/env python
# coding: utf-8

######################
# Python Boilerplate #
######################

### Modules
import os
import shutil
import codecs

### Constants

### Functions & Procedures

### Variables
inputFolder = os.path.join('..', 'ttools', 'resources', 'spacingTexts')
fileNames = [name for name in os.listdir(inputFolder) if name.endswith('.txt')]
outputFolder = os.path.join('..', 'ttools', 'resources', 'spacingTexts_02')

### Instructions
myFont = CurrentFont()

if os.path.exists(outputFolder) is True:
    shutil.rmtree(outputFolder)
os.mkdir(outputFolder)

for eachFileName in fileNames:
    with codecs.open(os.path.join(inputFolder, eachFileName), 'r', 'utf-8') as textFile:
        myLines = [[glyph for glyph in row.strip().split(' ')] for row in textFile.readlines()]

    multipleLines = []
    for eachLine in myLines:
        newLine = []
        for eachGlyphName in eachLine:
            if eachGlyphName in myFont and myFont[eachGlyphName].unicode:
                eachChar = unichr(myFont[eachGlyphName].unicode)
            else:
                eachChar = '/{} '.format(eachGlyphName)
            newLine.append(eachChar)
        multipleLines.append(''.join(newLine))

    with codecs.open(os.path.join(outputFolder, eachFileName), 'w', 'utf-8') as textFile:
        for eachLine in multipleLines:
            textFile.write(eachLine)
            textFile.write('\n')





