#!/usr/bin/env python
# coding: utf-8

#####################
# make spacing text #
#####################

### Modules

### Constants

### Functions & Procedures

### Variables
UCaccentedGroups = [('ae', 'aeacute'),
                    ('a', 'aacute', 'abreve', 'acircumflex', 'adieresis', 'agrave', 'amacron', 'aring', 'atilde'),
                    ('c', 'cacute', 'ccaron', 'ccircumflex', 'cdotaccent'),
                    ('e', 'eacute', 'ebreve', 'ecaron', 'ecircumflex', 'edieresis', 'edotaccent', 'egrave', 'emacron'),
                    ('g', 'gbreve', 'gcircumflex', 'gdotaccent'),
                    ('h', 'hcircumflex'),
                    ('k', 'uni0137'),
                    ('l', 'lacute', 'ldot', 'ldot.latn_CAT', 'uni013C'),
                    ('n', 'nacute', 'ncaron', 'ntilde', 'uni0146'),
                    ('o', 'oacute', 'obreve', 'ocircumflex', 'odieresis', 'ograve', 'ohungarumlaut', 'omacron', 'otilde'),
                    ('oslash', 'oslashacute'),
                    ('r', 'racute', 'rcaron', 'uni0157'),
                    ('s', 'sacute', 'scaron', 'scircumflex', 'uni0219'),
                    ('t', 'uni0163', 'uni021B'),
                    ('u', 'uacute', 'ubreve', 'ucircumflex', 'udieresis', 'ugrave', 'uhungarumlaut', 'umacron', 'uring', 'utilde'),
                    ('w', 'wacute', 'wcircumflex', 'wdieresis', 'wgrave'),
                    ('y', 'yacute', 'ycircumflex', 'ydieresis', 'ygrave'),
                    ('z', 'zacute', 'zcaron', 'zdotaccent'),
                    ('acute', 'aacute', 'aeacute', 'cacute', 'eacute', 'iacute', 'lacute', 'nacute', 'oacute', 'oslashacute', 'racute', 'sacute', 'uacute', 'wacute', 'yacute', 'zacute'),
                    ('breve', 'abreve', 'ebreve', 'gbreve', 'ibreve', 'obreve', 'ubreve'),
                    ('caron', 'ccaron', 'ecaron', 'ncaron', 'rcaron', 'scaron', 'zcaron'),
                    ('cedilla', 'uni0162', 'uni0163'),
                    ('circumflex', 'acircumflex', 'ccircumflex', 'ecircumflex', 'gcircumflex', 'hcircumflex', 'icircumflex', 'jcircumflex', 'ocircumflex', 'scircumflex', 'ucircumflex', 'wcircumflex', 'ycircumflex'),
                    ('dieresis', 'adieresis', 'edieresis', 'idieresis', 'odieresis', 'udieresis', 'wdieresis', 'ydieresis'),
                    ('dotaccent', 'cdotaccent', 'edotaccent', 'gdotaccent', 'ldot', 'ldot.latn_CAT', 'zdotaccent'),
                    ('grave', 'agrave', 'egrave', 'igrave', 'ograve', 'ugrave', 'wgrave', 'ygrave'),
                    ('hungarumlaut', 'ohungarumlaut', 'uhungarumlaut'),
                    ('macron', 'amacron', 'emacron', 'imacron', 'omacron', 'umacron', 'uni02C9'),
                    ('tilde', 'atilde', 'itilde', 'ntilde', 'otilde', 'utilde'),
                    ('ring', 'aring', 'uring'),
                    ('uni0326', 'uni0122', 'uni0136', 'uni0137', 'uni013B', 'uni013C', 'uni0145', 'uni0146', 'uni0156', 'uni0157', 'uni0218', 'uni0219', 'uni021A', 'uni021B')]

### Instructions
for eachGroup in UCaccentedGroups:
    print 'n %s n o %s o' % (' n '.join(eachGroup), ' o '.join(eachGroup))

