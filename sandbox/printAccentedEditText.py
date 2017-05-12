#!/usr/bin/env python
# -*- coding: utf-8 -*-

######################
# Python Boilerplate #
######################

### Modules
from collections import OrderedDict

### Constants

### Function & procedures

### Variables
accents = ['grave', 'acute', 'hungarumlaut', 'dotaccent', 'dieresis', 'circumflex', 'caron', 'macron', 'tilde', 'breve', 'ring', 'cedilla', 'ogonek', 'uni0312', 'uni0313', 'uni0326']

### Instructions
uppercaseStrings = OrderedDict()
lowercaseStrings = OrderedDict()

componentMapping = CurrentFont().getReverseComponentMapping()
for eachAccentName in accents:
    eachGroup = list(componentMapping[eachAccentName])
    eachGroup.sort()

    upperGlyphs = []
    lowerGlyphs = []
    for eachGlyphName in eachGroup:
        if eachGlyphName[0].isupper() is True:
            upperGlyphs.append(eachGlyphName)
        else:
            lowerGlyphs.append(eachGlyphName)

    uppercaseStrings[eachAccentName] = upperGlyphs
    lowercaseStrings[eachAccentName] = lowerGlyphs

for eachAccentName in accents:
    print ' '.join(uppercaseStrings[eachAccentName])

print '-'*30

for eachAccentName in accents:
    print ' '.join(lowercaseStrings[eachAccentName])
