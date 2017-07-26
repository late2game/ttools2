#!/usr/bin/env python
# -*- coding: utf-8 -*-

####
#  #
####

### Modules

### Constants
SYMMETRICAL_GLYPHS = list(u'AHIOTUVWXY.:-•·!¡|¦†‡"\'_*°…')
SYMMETRICAL_COUPLES_POS = {u"‹": u"›",
                           u"«": u"»",
                           u"(": u")",
                           u"[": u"]",
                           u"{": u"}",
                           u"/": u"\\",
                           u"‘": u"’"}
SYMMETRICAL_COUPLES_NEG = {value: key for (key, value) in SYMMETRICAL_COUPLES_POS.items()}

### Functions & Procedures
def findSymmetricalPair(aPair):
    lftGlyph, rgtGlyph = aPair

    if lftGlyph == rgtGlyph:
        return None

    # only symmetrical
    elif lftGlyph in SYMMETRICAL_GLYPHS and rgtGlyph in SYMMETRICAL_GLYPHS:
        symmetricalPair = rgtGlyph, lftGlyph

    # symmetrical glyphs + couples
    elif lftGlyph in SYMMETRICAL_GLYPHS and rgtGlyph in SYMMETRICAL_COUPLES_POS:
        symmetricalPair = SYMMETRICAL_COUPLES_POS[rgtGlyph], lftGlyph

    elif lftGlyph in SYMMETRICAL_GLYPHS and rgtGlyph in SYMMETRICAL_COUPLES_NEG:
        symmetricalPair = SYMMETRICAL_COUPLES_NEG[rgtGlyph], lftGlyph

    elif lftGlyph in SYMMETRICAL_COUPLES_POS and rgtGlyph in SYMMETRICAL_GLYPHS:
        symmetricalPair = rgtGlyph, SYMMETRICAL_COUPLES_POS[lftGlyph]

    elif lftGlyph in SYMMETRICAL_COUPLES_NEG and rgtGlyph in SYMMETRICAL_GLYPHS:
        symmetricalPair = rgtGlyph, SYMMETRICAL_COUPLES_NEG[lftGlyph]

    # only from the couples
        # straight
    elif lftGlyph in SYMMETRICAL_COUPLES_POS and rgtGlyph in SYMMETRICAL_COUPLES_POS:
        symmetricalPair = SYMMETRICAL_COUPLES_POS[rgtGlyph], SYMMETRICAL_COUPLES_POS[lftGlyph]

    elif lftGlyph in SYMMETRICAL_COUPLES_NEG and rgtGlyph in SYMMETRICAL_COUPLES_NEG:
        symmetricalPair = SYMMETRICAL_COUPLES_NEG[rgtGlyph], SYMMETRICAL_COUPLES_NEG[lftGlyph]

        # crossed
    elif lftGlyph in SYMMETRICAL_COUPLES_POS and rgtGlyph in SYMMETRICAL_COUPLES_NEG:
        symmetricalPair = SYMMETRICAL_COUPLES_NEG[rgtGlyph], SYMMETRICAL_COUPLES_POS[lftGlyph]

    elif lftGlyph in SYMMETRICAL_COUPLES_NEG and rgtGlyph in SYMMETRICAL_COUPLES_POS:
        symmetricalPair = SYMMETRICAL_COUPLES_POS[rgtGlyph], SYMMETRICAL_COUPLES_NEG[lftGlyph]

    if symmetricalPair:
        if symmetricalPair != (lftGlyph, rgtGlyph):
            return symmetricalPair

    return None

### Variables

### Instructions
print findSymmetricalPair(u'}{')


