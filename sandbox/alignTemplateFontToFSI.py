#!/usr/bin/env python
# coding: utf-8

##############################
# Align to FSI naming scheme #
##############################

### Modules
import os

### Constants

### Functions & Procedures

### Variables
oldName2newName = {"uniFB01": "fi",
                   "uniFB02": "fl",
                   "filledbox": "uni25A0",
                   "H22073": "uni25A1",
                   "circle": "uni25CB",
                   "H18533": "uni25CF",
                   "H18543": "uni25AA",
                   "H18551": "uni25AB",
                   "uni00B9": "onesuperior",
                   "uni00B2": "twosuperior",
                   "uni00B3": "threesuperior",
                   "Scedilla": "uni015E",
                   "scedilla": "uni015F",
                   "scedilla.sc": "uni015F.sc"}

### Instructions
templateFont = OpenFont(os.path.join('..', 'ttools', 'resources', 'templates', 'templateFont.ufo'), showUI=True)

for eachOldName, eachNewName in oldName2newName.items():
      templateFont.renameGlyph(eachOldName, eachNewName, renameComponents=True, renameGroups=True, renameKerning=True)
      eachGlyph = templateFont[eachNewName]
      eachGlyph.mark = 0,0,1,.5

