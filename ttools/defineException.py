
def whichGroup(targetGlyphName, aLocation, aFont):
    assert aLocation in ['lft', 'rgt']
    possibleLocations = {'lft': '@MMK_L_',
                         'rgt': '@MMK_R_'}
    filteredGroups = {name: content for name, content in aFont.groups.items() if name.startswith(possibleLocations[aLocation])}
    for eachGroupName, eachGroupContent in filteredGroups.items():
        if targetGlyphName in eachGroupContent:
            return eachGroupName
    return None

def searchCorrections(aPair, aFont):
    """
    aPair should be only glyphNames, right?
    """

    lftGlyphName, rgtGlyphName = aPair
    lftGroup = whichGroup(lftGlyphName, 'lft', aFont)
    rgtGroup = whichGroup(rgtGlyphName, 'rgt', aFont)

    correctionsOptions = ('group2group', 'group2glyph', 'glyph2group', 'glyph2glyph')
    corrections = {'group2group': ((lftGroup, rgtGroup), aFont.kerning.get((lftGroup, rgtGroup))),
                   'group2glyph': ((lftGroup, rgtGlyphName), aFont.kerning.get((lftGroup, rgtGlyphName))),
                   'glyph2group': ((lftGlyphName, rgtGroup), aFont.kerning.get((lftGlyphName, rgtGroup))),
                   'glyph2glyph': ((lftGlyphName, rgtGlyphName), aFont.kerning.get((lftGlyphName, rgtGlyphName)))}

    usedCorrections = {kind: corrections[kind] for kind in correctionsOptions if corrections[kind][1] is not None}
    if len(usedCorrections) > 2:
        print 'we have a conflict here'
        raise StandardError

    usedKeys = [name for name in correctionsOptions if name in usedCorrections.keys()]
    correctionsMap = {'standard': None,
                      'exception': None}

    if len(usedCorrections) == 2:
        kerningStandard, kerningException = usedCorrections[usedKeys[0]], usedCorrections[usedKeys[1]]
        correctionsMap['standard'] = kerningStandard
        correctionsMap['exception'] = kerningException

    elif len(usedCorrections) == 1:
        kerningStandard = usedCorrections[usedKeys[0]]
        correctionsMap['standard'] = kerningStandard

    return correctionsMap

myFont = CurrentFont()
print searchCorrections(('H', 'Odieresis'), myFont)