#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from string import uppercase

DNOM_NUMR_SUBS_SUPS_PATH = os.path.join('..', 'ttools', 'resources', 'tables', 'dnomNumrSubsSups.csv')

LCacc = ('@MMK_L_yAcc',
         '@MMK_R_yAcc',
         '@MMK_L_zAcc',
         '@MMK_R_zAcc',
         '@MMK_L_sAcc',
         '@MMK_R_sAcc',
         '@MMK_L_rAcc',
         '@MMK_L_uAcc',
         '@MMK_R_uAcc',
         '@MMK_L_wAcc',
         '@MMK_R_wAcc',
         '@MMK_L_iAcc',
         '@MMK_R_iAcc',
         '@MMK_L_oAcc',
         '@MMK_R_oAcc',
         '@MMK_L_nAcc',
         '@MMK_R_nAcc',
         '@MMK_L_aAcc',
         '@MMK_R_aAcc',
         '@MMK_L_cAcc',
         '@MMK_L_eAcc',
         '@MMK_L_gAcc',
         '@MMK_R_gAcc')


def whichGroup(targetGlyphName, aLocation, aFont):
    assert aLocation in ['lft', 'rgt']

    locationPrefixes = {'lft': '@MMK_L_',
                        'rgt': '@MMK_R_'}

    filteredGroups = {name: content for name, content in aFont.groups.items() if name.startswith(locationPrefixes[aLocation])}
    for eachGroupName, eachGroupContent in filteredGroups.items():
        if targetGlyphName in eachGroupContent:
            return eachGroupName
    return None

def correct_f_sups_numr(aFont):
    """f followed by superior and numerator +60"""
    dnomNumrSubsSups = [line.strip().split('\t') for line in open(DNOM_NUMR_SUBS_SUPS_PATH, 'r').readlines() if line != '']

    aFont.group['@MMK_R_sups'] = []
    aFont.group['@MMK_R_subs'] = []
    for eachLine in dnomNumrSubsSups[1:]:
        aFont.group['@MMK_R_sups'].append(eachLine[2])
        aFont.group['@MMK_R_subs'].append(eachLine[4])

    fGroup = whichGroup('f', 'lft', aFont)
    if fGroup is None:
        aFont.kerning[('f', '@MMK_R_sups')] = 60
        aFont.kerning[('f', '@MMK_R_subs')] = 60
    else:
        aFont.kerning[(fGroup, '@MMK_R_sups')] = 60
        aFont.kerning[(fGroup, '@MMK_R_subs')] = 60


def collect_LCacc(aFont):
    """
    2) UC2LCAcc are 40% less than UC2LC corrections
    """

    locationDict = {
        "L": 'lft',
        "R": 'rgt'}

    UCreferences = list(uppercase)
    for eachChar in uppercase:
        lftGroup = whichGroup(eachChar, 'lft', aFont)
        if lftGroup is None:
            UCreferences.append(lftGroup)

        rgtGroup = whichGroup(eachChar, 'rgt', aFont)
        if rgtGroup is None:
            UCreferences.append(rgtGroup)

    for eachClassName in LCacc:
        location = locationDict[eachClassName[5]]
        glyphReference = eachClassName[7]
        referenceGroup = whichGroup(glyphReference, location, aFont)

        if referenceGroup is None:
            kerningParent = glyphReference
        else:
            kerningParent = referenceGroup

        if location == 'lft':
            pairsToExtend = aFont.kerning.getLeft(kerningParent)
        else:
            pairsToExtend = aFont.kerning.getRight(kerningParent)

        for eachPair, eachValue in pairsToExtend:
            lftName, rgtName = eachPair
            if location == 'lft':

                if rgtName in UCreferences:
                    extendedPair = (eachClassName, rgtName)
                else:
                    extendedPair = None
            else:
                if lftName in UCreferences:
                    extendedPair = (lftName, eachClassName)
                else:
                    extendedPair = None

            if extendedPair is not None:
                print
                print eachPair, eachValue
                print extendedPair, int(eachValue*.6)
                # aFont.kerning[extendedPair] = int(eachValue*.6)

"""
3) capital interpunction follow basic interpunction (maybe solved with classes?)
"""

if __name__ == '__main__':
    collect_LCacc(CurrentFont())
    # correct_f_sups_numr(CurrentFont())
