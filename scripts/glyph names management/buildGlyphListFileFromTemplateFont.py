#!/usr/bin/env python
# coding: utf-8

###################################################################
# Build the glyphList.csv file starting from the templateFont.ufo #
###################################################################

### Modules
import sys
import os
import unicodedata2

sys.path.append('/usr/local/lib/python2.7/site-packages/unicodedata2')
import unicodedata2


### Constants

### Functions & Procedures

### Variables
templateFont = OpenFont(os.path.join('..', '..', 'ttools', 'resources', 'templates', 'templateFont.ufo'), showUI=False)

### Instructions
for eachGlyphName in templateFont.glyphOrder:
    eachGlyph = templateFont[eachGlyphName]

    if eachGlyph.unicode:
        hexUniValue = ('%X' % eachGlyph.unicode).zfill(4)
        print eachGlyphName
        row = '\t'.join([eachGlyphName, hexUniValue, unicodedata.name(unichr(eachGlyph.unicode))])
        print row

    else:
        print eachGlyphName