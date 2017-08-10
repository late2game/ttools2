#!/usr/bin/env python
# coding: utf-8

#################################
# Check if every glyph is AGLFN #
#################################

### Modules
import os
from loadAGLFN import loadAGLFN

### Constants

### Function & procedures

### Variables
sourceFont = CurrentFont()

### Instructions
AGLFN = loadAGLFN()
for eachGlyph in sourceFont:
    if eachGlyph.unicode:
        uniHex = ('%X' % eachGlyph.unicode).zfill(4)
        if uniHex in AGLFN:
            if AGLFN[uniHex]['glyphName'] != eachGlyph.name:
                print
                print sourceFont.info.familyName, sourceFont.info.styleName
                print uniHex
                print 'AGLFN name: %s' % AGLFN[uniHex]['glyphName']
                print 'actual name: %s' % eachGlyph.name
                print '-'*30
        else:
            print '%s not in aglfn, you should change name in uni%s' % (eachGlyph.name, uniHex)

    else:
        print '%s glyph does not have any unicode value, i cannot tell, sorry' % eachGlyph.name
