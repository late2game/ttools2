#!/usr/bin/env python
# coding: utf-8

######################
# Python Boilerplate #
######################

### Modules
import os
from itertools import chain

### Constants

### Function & procedures
def catchFilesExtension(folderPath, extension):
    filePaths = [os.path.join(folderPath, name) for name in os.listdir(folderPath) if name.endswith(extension)]
    return filePaths

### Variables
sourceFont = CurrentFont()
setsFolder = os.path.join('..', 'ttools', 'resources', 'glyphLists')

### Instructions
setsFilePaths = catchFilesExtension(setsFolder, '.txt')
setsOrder = [os.path.basename(name).replace('.txt', '') for name in setsFilePaths]

setsDictionary = {}
for eachSetPath in setsFilePaths:
    glyphNames = open(eachSetPath, 'r').read().split('\n')
    setsDictionary[os.path.basename(eachSetPath).replace('.txt', '')] = glyphNames

allNames = [name for name in chain.from_iterable(setsDictionary.values())]
for eachGlyph in sourceFont:
    if eachGlyph.name not in allNames:
        print eachGlyph.name

print '-'*30

for eachSetName in setsOrder:
    glyphNames = setsDictionary[eachSetName]

    for eachName in glyphNames:
        if sourceFont.has_key(eachName) is False:
            print eachName
