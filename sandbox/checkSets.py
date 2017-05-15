#!/usr/bin/env python
# -*- coding: utf-8 -*-

######################
# Python Boilerplate #
######################

### Modules
import os

### Constants

### Function & procedures
def catchFilesExtension(folderPath, extension):
    filePaths = [os.path.join(folderPath, name) for name in os.listdir(folderPath) if name.endswith(extension)]
    return filePaths

### Variables
setsFolder = os.path.join('..', 'ttools', 'resources', 'glyphLists')

### Instructions
setsFilePaths = catchFilesExtension(setsFolder, '.txt')
setsFilePaths.sort()
setsOrder = [os.path.basename(name).replace('.txt', '') for name in setsFilePaths]

setsDictionary = {}
for eachSetPath in setsFilePaths:
    glyphNames = [name.strip() for name in open(eachSetPath, 'r').readlines()]
    setsDictionary[os.path.basename(eachSetPath).replace('.txt', '')] = glyphNames

for eachSetIndex, eachSetName in enumerate(setsOrder):
    if eachSetIndex == 0:
        continue

    for eachCurrentGlyphName in setsDictionary[eachSetName]:
        for eachPreviousSet in setsOrder[0:eachSetIndex]:
            if eachCurrentGlyphName in setsDictionary[eachPreviousSet]:
                print '%s in %s and %s' % (eachCurrentGlyphName, eachSetName, eachPreviousSet)


