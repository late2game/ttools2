#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

sourceFont.glyphOrder = newGlyphOrder