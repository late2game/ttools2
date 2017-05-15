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

root = '/Users/robertoarista/Documents/Work/TypeTailors/TTools/ttools/resources'
glyphListFolder = os.path.join(root, 'glyphLists')
spacingTextsFolder = os.path.join(root, 'spacingTexts')

renameDict = {'Kcedilla': 'uni0136',
              'twosuperior': 'uni00B2',
              'Lcedilla': 'uni013B',
              'lcedilla': 'uni013C',
              'Rcedilla': 'uni0156',
              'dotlessj': 'uni0237',
              'gcedilla': 'uni0123',
              'rcedilla': 'uni0157',
              'mu': 'uni03BC',
              'litre': 'uni2113',
              'fi': 'uniFB01',
              'fl': 'uniFB02',
              'Ncedilla': 'uni0145',
              'Gcedilla': 'uni0122',
              'arrowNW': 'uni2196',
              'figurespace': 'uni2007',
              'numero': 'uni2116',
              'onesuperior': 'uni00B9',
              'starblack': 'uni2605',
              'arrowSW': 'uni2199',
              'ncedilla': 'uni0146',
              'arrowSE': 'uni2198',
              'threesuperior': 'uni00B3',
              'arrowNE': 'uni2197',
              'kcedilla': 'uni0137'}

### Instructions
# glyph lists
for eachPath in [os.path.join(glyphListFolder, name) for name in os.listdir(glyphListFolder) if name.endswith('.txt')]:
    glyphList = [name.strip() for name in open(eachPath, 'r').readlines()]
    glyphList = [renameDict[n] if n in renameDict else n for n in glyphList]

    myGLfile = open(eachPath.replace('glyphLists', 'glyphListsNew'), 'w')
    myGLfile.write('\n'.join(glyphList))
    myGLfile.write('\n')
    myGLfile.close()

# spacingTexts
for eachPath in [os.path.join(spacingTextsFolder, name) for name in os.listdir(spacingTextsFolder) if name.endswith('.txt')]:
    spacingText = [[cell.strip() for cell in row.split(' ')] for row in open(eachPath, 'r').readlines()]

    mySpacingFile = open(eachPath.replace('spacingTexts', 'spacingTextsNew'), 'w')
    for eachRow in spacingText:
        newRow = [renameDict[n] if n in renameDict else n for n in eachRow]
        mySpacingFile.write(' '.join(newRow))
        mySpacingFile.write('\n')

    mySpacingFile.close()







