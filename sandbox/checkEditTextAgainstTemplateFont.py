#!/usr/bin/env python
# -*- coding: utf-8 -*-

######################
# Python Boilerplate #
######################

### Modules
import os
from collections import OrderedDict
from itertools import chain

### Constants

### Function & procedures

### Variables
templateFont = OpenFont(os.path.join('..', 'ttools', 'resources', 'templates', 'templateFont.ufo'), showUI=False)
textsFolder = os.path.join('..', 'ttools', 'resources', 'spacingTexts')

### Instructions
txtDict = OrderedDict()
for eachTxtPath in [os.path.join(textsFolder, name) for name in os.listdir(textsFolder) if name.endswith('.txt') is True]:

    txtMatrix = [[cell.strip() for cell in row.split(' ')] for row in open(eachTxtPath, 'r').readlines()]

    usedGlyphs = []
    _ = [usedGlyphs.append(name) for name in chain.from_iterable(txtMatrix) if name not in usedGlyphs]
    
    for eachGlyphName in usedGlyphs:
        if templateFont.has_key(eachGlyphName) is False:
            print '%s uses this unsupported glyph: %s' % (os.path.basename(eachTxtPath), eachGlyphName)