#!/usr/bin/env python
# coding: utf-8

######################
# Python Boilerplate #
######################

### Modules
import os

### Constants

### Function & procedures

### Variables
sourceFont = CurrentFont()
glyphListFolder = os.path.join('..', 'ttools', 'resources', 'glyphLists')

### Instructions
allGLs = []
for eachPath in [os.path.join(glyphListFolder, name) for name in os.listdir(glyphListFolder) if name.endswith('.txt') is True]:
    _ = [allGLs.append(name.strip()) for name in open(eachPath, 'r').readlines() if name.strip() not in allGLs]

newGlyphOrder = []
for eachGlyphName in allGLs:
    if eachGlyphName in sourceFont.glyphOrder:
        newGlyphOrder.append(eachGlyphName)

for eachGlyphName in sourceFont.glyphOrder:
    if eachGlyphName not in newGlyphOrder:
        newGlyphOrder.append(eachGlyphName)

if len(sourceFont.glyphOrder) == len(newGlyphOrder):
    sourceFont.glyphOrder = newGlyphOrder
else:
    print len(sourceFont.glyphOrder)
    print len(newGlyphOrder)
