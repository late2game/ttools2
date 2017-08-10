#!/usr/bin/env python
# coding: utf-8

"""a few useful functions"""

from fontTools.agl import AGL2UV

def convertLineToPseudoUnicode(glyphNamesLine):
    pseudoUniString = u''
    for eachGlyphName in glyphNamesLine:
        if eachGlyphName in AGL2UV:
            pseudoUniString += unichr(AGL2UV[eachGlyphName])
        else:
            pseudoUniString += '\\%s ' % eachGlyphName
    return pseudoUniString