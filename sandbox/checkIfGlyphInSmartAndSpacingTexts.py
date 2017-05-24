#!/usr/bin/env python
# -*- coding: utf-8 -*-

###################################################
# Check if glyphs in smart sets and spacing texts #
###################################################

### Modules
import os
from itertools import chain

### Constants

### Function & procedures

### Variables
cedillasAndCommas = ['Ccedilla', 'ccedilla', 'Scedilla', 'scedilla', 'uni0122', 'uni0123', 'uni0136', 'uni0137', 'uni013B', 'uni013C', 'uni0145', 'uni0146', 'uni0156', 'uni0157', 'uni0162', 'uni0163', 'uni0218', 'uni0219', 'uni021A', 'uni021B']
spacingTextFolder = os.path.join('..', 'ttools', 'resources', 'glyphLists')
smartSetsFolder = os.path.join('..', 'ttools', 'resources', 'spacingTexts')

### Instructions
alreadyThere = []
for eachPath in [os.path.join(spacingTextFolder, name) for name in os.listdir(spacingTextFolder) if name.endswith('.txt')]:
    glyphList = [name.strip() for name in open(eachPath, 'r').readlines()]

    for eachCedilla in cedillasAndCommas:
        if eachCedilla in glyphList:
            if eachCedilla not in alreadyThere:
                alreadyThere.append(eachCedilla)

if len(alreadyThere) == len(cedillasAndCommas):
    print 'we are fine'


glyphsUnique = []
for eachPath in [os.path.join(smartSetsFolder, name) for name in os.listdir(smartSetsFolder) if name.endswith('.txt')]:
    spacingTable = [[cell.strip() for cell in name.split(' ')] for name in open(eachPath, 'r').readlines()]
    _ = [glyphsUnique.append(name) for name in chain.from_iterable(spacingTable) if name not in glyphsUnique]

for eachCedilla in cedillasAndCommas:
    if eachCedilla not in glyphsUnique:
        print 'shout!'






