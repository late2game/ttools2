#!/usr/bin/env python
# coding: utf-8

#####################
# make spacing text #
#####################

### Modules

### Constants

### Functions & Procedures

### Variables
SCaccentedGroups = [('a.sc', 'aacute.sc', 'abreve.sc', 'acircumflex.sc', 'adieresis.sc', 'agrave.sc', 'amacron.sc', 'aring.sc', 'atilde.sc'),
                    ('c.sc', 'cacute.sc', 'ccaron.sc', 'ccircumflex.sc', 'cdotaccent.sc'),
                    ('d.sc', 'dcaron.sc'),
                    ('e.sc', 'eacute.sc', 'ebreve.sc', 'ecaron.sc', 'ecircumflex.sc', 'edieresis.sc', 'edotaccent.sc', 'egrave.sc', 'emacron.sc'),
                    ('g.sc', 'gbreve.sc', 'gcircumflex.sc', 'gdotaccent.sc', 'uni0123.sc'),
                    ('h.sc', 'hcircumflex.sc'),
                    ('i.sc', 'Idotaccent.sc', 'i.latn_TRK.sc', 'iacute.sc', 'ibreve.sc', 'icircumflex.sc', 'idieresis.sc', 'igrave.sc', 'imacron.sc', 'itilde.sc'),
                    ('j.sc', 'jcircumflex.sc'),
                    ('k.sc', 'uni0137.sc'),
                    ('l.sc', 'lacute.sc', 'ldot.latn_CAT.sc', 'ldot.sc', 'uni013C.sc'),
                    ('n.sc', 'nacute.sc', 'ncaron.sc', 'ntilde.sc', 'uni0146.sc'),
                    ('o.sc', 'oacute.sc', 'obreve.sc', 'ocircumflex.sc', 'odieresis.sc', 'ograve.sc', 'ohungarumlaut.sc', 'omacron.sc', 'otilde.sc'),
                    ('r.sc', 'racute.sc', 'rcaron.sc', 'uni0157.sc'),
                    ('s.sc', 'sacute.sc', 'scaron.sc', 'scircumflex.sc', 'uni0219.sc'),
                    ('t.sc', 'tcaron.sc', 'uni0163.sc', 'uni021B.sc'),
                    ('u.sc', 'uacute.sc', 'ubreve.sc', 'ucircumflex.sc', 'udieresis.sc', 'ugrave.sc', 'uhungarumlaut.sc', 'umacron.sc', 'uring.sc', 'utilde.sc'),
                    ('w.sc', 'wacute.sc', 'wcircumflex.sc', 'wdieresis.sc', 'wgrave.sc'),
                    ('y.sc', 'yacute.sc', 'ycircumflex.sc', 'ydieresis.sc', 'ygrave.sc'),
                    ('z.sc', 'zacute.sc', 'zcaron.sc', 'zdotaccent.sc'),
                    ('acute', 'aacute.sc', 'aeacute.sc', 'cacute.sc', 'eacute.sc', 'iacute.sc', 'lacute.sc', 'nacute.sc', 'oacute.sc', 'oslashacute.sc', 'racute.sc', 'sacute.sc', 'uacute.sc', 'wacute.sc', 'yacute.sc', 'zacute.sc'),
                    ('breve', 'abreve.sc', 'ebreve.sc', 'gbreve.sc', 'ibreve.sc', 'obreve.sc', 'ubreve.sc'),
                    ('caron', 'ccaron.sc', 'dcaron.sc', 'ecaron.sc', 'ncaron.sc', 'rcaron.sc', 'scaron.sc', 'tcaron.sc', 'zcaron.sc'),
                    ('cedilla', 'uni0163.sc'),
                    ('circumflex', 'acircumflex.sc', 'ccircumflex.sc', 'ecircumflex.sc', 'gcircumflex.sc', 'hcircumflex.sc', 'icircumflex.sc', 'jcircumflex.sc', 'ocircumflex.sc', 'scircumflex.sc', 'ucircumflex.sc', 'wcircumflex.sc', 'ycircumflex.sc'),
                    ('dieresis', 'adieresis.sc', 'edieresis.sc', 'idieresis.sc', 'odieresis.sc', 'udieresis.sc', 'wdieresis.sc', 'ydieresis.sc'),
                    ('dotaccent', 'Idotaccent.sc', 'cdotaccent.sc', 'edotaccent.sc', 'gdotaccent.sc', 'i.latn_TRK.sc', 'ldot.latn_CAT.sc', 'ldot.sc', 'zdotaccent.sc'),
                    ('grave', 'agrave.sc', 'egrave.sc', 'igrave.sc', 'ograve.sc', 'ugrave.sc', 'wgrave.sc', 'ygrave.sc'),
                    ('hungarumlaut', 'ohungarumlaut.sc', 'uhungarumlaut.sc'),
                    ('macron', 'amacron.sc', 'emacron.sc', 'imacron.sc', 'omacron.sc', 'umacron.sc'),
                    ('tilde', 'atilde.sc', 'itilde.sc', 'ntilde.sc', 'otilde.sc', 'utilde.sc'),
                    ('ring', 'aring.sc', 'uring.sc'),
                    ('uni0326', 'uni0123.sc', 'uni0137.sc', 'uni013C.sc', 'uni0146.sc', 'uni0157.sc', 'uni0219.sc', 'uni021B.sc'),
                    ]

### Instructions
for eachGroup in SCaccentedGroups:
    print 'h.sc %s h.sc o.sc %s o.sc' % (' h.sc '.join(eachGroup), ' o.sc '.join(eachGroup))