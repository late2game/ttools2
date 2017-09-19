#!/usr/bin/env python
# coding: utf-8

#################################
# Adding smart sets from source #
#################################

### Modules
import os
from mojo.UI import SmartSet, addSmartSet

### Functions, procedures, constants
def catchFilesAndFolders(path, extension):
    items = [item for item in os.listdir(path) if item.endswith(extension) is True]
    return items

### Variables
inputFolder = os.path.join('..', 'ttools', 'resources', 'smartSets')

### Instructions
txtPaths = catchFilesAndFolders(inputFolder, '.txt')
for eachPath in txtPaths:
    setName = os.path.splitext(eachPath)[0][3:]

    glyphs = open(inputFolder + os.sep + eachPath, 'r').readlines()
    glyphs = [item.replace('\n', '') for item in glyphs]

    smartSet = SmartSet()
    smartSet.name = setName
    smartSet.glyphNames = glyphs
    addSmartSet(smartSet)
