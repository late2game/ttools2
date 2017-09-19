#!/usr/bin/env python
# coding: utf-8

####################################################
# Sort All fonts according to standard glyph lists #
####################################################

### Modules
import os

### Constants

### Function & procedures

### Variables
glyphListFolder = os.path.join('..', 'ttools', 'resources', 'glyphLists')

### Instructions
allGLs = []
for eachPath in [os.path.join(glyphListFolder, name) for name in os.listdir(glyphListFolder) if name.endswith('.txt') is True]:
    _ = [allGLs.append(name.strip()) for name in open(eachPath, 'r').readlines() if name.strip() not in allGLs]

for eachFont in AllFonts():
    newGlyphOrder = []
    for eachGlyphName in allGLs:
        if eachGlyphName in eachFont.glyphOrder:
            newGlyphOrder.append(eachGlyphName)

    for eachGlyphName in eachFont.glyphOrder:
        if eachGlyphName not in newGlyphOrder:
            newGlyphOrder.append(eachGlyphName)

    if len(eachFont.glyphOrder) == len(newGlyphOrder):
        eachFont.glyphOrder = newGlyphOrder
    else:
        print len(eachFont.glyphOrder)
        print len(newGlyphOrder)
