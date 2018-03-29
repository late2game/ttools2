#!/usr/bin/env python
# coding: utf-8

############################################
# Check Current Font Against Template Font #
############################################

### Modules
import sys
import os
import unicodedata

### Variables
templateFont = OpenFont(os.path.join('..', 'ttools', 'resources', 'templates', 'templateFont.ufo'), showUI=False)
templateCharacterMap = templateFont.getCharacterMapping()
currentFont = CurrentFont()

### Instructions
# iter over current
print 'NOT IN TEMPLATE'
for currentGlyphName in currentFont.glyphOrder:
    currentGlyph = currentFont[currentGlyphName]

    if currentGlyphName not in templateFont:
        if currentGlyph.unicode:

            if currentGlyph.unicode in templateCharacterMap:
                print '{}\t{}'.format(currentGlyphName, templateCharacterMap[currentGlyph.unicode][0])
                # print('%X' % currentGlyph.unicode).zfill(4)
                # print('')

# iter over template
# print 'NOT IN CURRENT'
# for templateGlyphName in templateFont.glyphOrder:
#     templateGlyph = templateFont[templateGlyphName]

#     if templateGlyphName not in currentFont:
#         print templateGlyphName