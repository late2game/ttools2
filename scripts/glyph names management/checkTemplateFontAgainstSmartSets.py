#!/usr/bin/env python
# coding: utf-8

######################
# Python Boilerplate #
######################

### Modules

### Constants

### Functions & Procedures
def loadSmartSets(smartSetsFolder):
    smartSets = {}
    smartSetsPaths = [name for name in os.listdir(smartSetsFolder) if name.endswith('.txt')]
    for eachSmartSetName in smartSetsPaths:
        setContent = [item.strip() for item in codecs.open(os.path.join(smartSetsFolder, eachSmartSetName), 'r', 'utf-8').readlines() if item.strip()]
        smartSets[eachSmartSetName] = setContent
    return smartSets

### Variables
smartSetsFolder = os.path.join('..', '..', 'ttools', 'resources', 'smartSets')

### Instructions
templateFont = OpenFont(os.path.join('..', '..', 'ttools', 'resources', 'templates', 'templateFont.ufo'), showUI=False)
templateFontGlyphOrder = templateFont.glyphOrder

smartSets = loadSmartSets(smartSetsFolder)

errors = []

for eachGlyphName in templateFontGlyphOrder:
    