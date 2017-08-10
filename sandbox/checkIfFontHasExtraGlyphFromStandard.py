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
    GL = [name.strip() for name in open(eachPath, 'r').readlines()]
    allGLs += GL

for eachGlyph in sourceFont:
    if eachGlyph.name not in allGLs:
        print eachGlyph.name