#!/usr/bin/env python
# coding: utf-8

##########################################
# Check Smart Sets against template font #
##########################################

### Modules
import os
import codecs

### Constants
ERROR_MESSAGE_SET2TEMPLATE = '[WARNING] %(glyphName)s from %(smartSetName)s not in templateFont'
ERROR_MESSAGE_TEMPLATE2SET = '[WARNING] %(glyphName)s from templateFont not in smartSets'

### Functions & Procedures
def loadSmartSets(smartSetsFolder):
    smartSets = {}
    smartSetsPaths = [name for name in os.listdir(smartSetsFolder) if name.endswith('.txt')]
    for eachSmartSetName in smartSetsPaths:
        setContent = [item.strip() for item in codecs.open(os.path.join(smartSetsFolder, eachSmartSetName), 'r', 'utf-8').readlines() if item.strip()]
        smartSets[eachSmartSetName] = setContent
    return smartSets


### Variables
smartSetsFolder = os.path.join('..', '..', 'ttools', 'resources', 'smartSets')

### Instructions
templateFont = OpenFont(os.path.join('..', '..', 'ttools', 'resources', 'templates', 'templateFont.ufo'), showUI=False)
templateFontGlyphOrder = templateFont.glyphOrder

smartSets = loadSmartSets(smartSetsFolder)

# sets against templatefont
errors = []
for eachSetName, eachSetContent in smartSets.items():
    for eachGlyphName in eachSetContent:
        if eachGlyphName not in templateFontGlyphOrder:
            errors.append(ERROR_MESSAGE_SET2TEMPLATE % {'glyphName': eachGlyphName, 'smartSetName': eachSetName})
errorsFile = codecs.open('checkSmartSetsAgainstTemplateFont.txt', 'w', 'utf-8')
errorsFile.write('\n'.join(errors))
errorsFile.close()

# template font against sets
errors = []
allGlyphNamesInSets = []
for eachSetName, eachSetContent in smartSets.items():
    for eachGlyphName in eachSetContent:
        if eachGlyphName not in allGlyphNamesInSets:
            allGlyphNamesInSets.append(eachGlyphName)
        else:
            print '%s occurs more than once' % eachGlyphName

for eachGlyphName in templateFontGlyphOrder:
    if eachGlyphName not in allGlyphNamesInSets:
        errors.append(ERROR_MESSAGE_TEMPLATE2SET % {'glyphName': eachGlyphName})

errorsFile = codecs.open('checkTemplateFontAgainstSmartSets.txt', 'w', 'utf-8')
errorsFile.write('\n'.join(errors))
errorsFile.close()


print 'done'




