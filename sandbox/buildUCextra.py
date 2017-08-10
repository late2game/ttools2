#!/usr/bin/env python
# coding: utf-8

#####################################################
# let's put the right composites in the right place #
#####################################################

### Variables
UCextraDict = {'Eth'   : ['D'],
               'Dcroat': ['D'],
               'Hbar'  : ['H'],
               'IJ'    : ['I', 'J'],
               'Lslash': ['L'],
               'Ldot'  : ['L'],
               'Lcaron': ['L'],
               'Eng'   : ['N'],
               'Oslash': ['O'],
               'Tbar'  : ['T'],
               'Thorn' : ['P']
               }

### Instructions
for eachFont in AllFonts():
    for eachTargetName, eachSourceGroup in UCextraDict.items():
        targetGlyph = eachFont[eachTargetName]
        targetGlyph.clear()

        overallWidth = 0
        for eachSourceName in eachSourceGroup:
            sourceGlyph = eachFont[eachSourceName]
            targetGlyph.appendComponent(eachSourceName, (overallWidth, 0))
            overallWidth += sourceGlyph.width
        targetGlyph.width = overallWidth
