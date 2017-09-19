#!/usr/bin/env python
# coding: utf-8

#####################
# make spacing text #
#####################

### Modules

### Constants

### Functions & Procedures

### Variables
UCaccentedGroups = [('AE', 'AEacute'),
                    ('A', 'Aacute', 'Abreve', 'Acircumflex', 'Adieresis', 'AEacute', 'Agrave', 'Amacron', 'Aogonek', 'Aring', 'Atilde'),
                    ('C', 'Cacute', 'Ccaron', 'Ccedilla', 'Ccircumflex', 'Cdotaccent'),
                    ('D', 'Dcaron'),
                    ('E', 'Eacute', 'Ebreve', 'Ecaron', 'Ecircumflex', 'Edieresis', 'Edotaccent', 'Egrave', 'Emacron', 'Eogonek'),
                    ('G', 'Gbreve', 'uni0122', 'Gcircumflex', 'Gdotaccent', 'Hcircumflex'),
                    ('I', 'Iacute', 'Ibreve', 'Icircumflex', 'Idieresis', 'Idotaccent', 'Igrave', 'Imacron', 'Iogonek', 'Itilde'),
                    ('J', 'Jcircumflex'),
                    ('K', 'uni0136'),
                    ('L', 'Lacute', 'uni013B'),
                    ('N', 'Nacute', 'Ncaron', 'uni0145', 'Ntilde'),
                    ('O', 'Oacute', 'Obreve', 'Ocircumflex', 'Odieresis', 'Ograve', 'Ohungarumlaut', 'Omacron', 'Otilde' ),
                    ('Oslash', 'Oslashacute'),
                    ('R', 'Racute', 'Rcaron', 'uni0156'),
                    ('S', 'Sacute', 'Scaron', 'Scircumflex', 'uni0218', 'uni015E'),
                    ('T', 'Tcaron', 'uni0162', 'uni021A'),
                    ('U', 'Uacute', 'Ubreve', 'Ucircumflex', 'Udieresis', 'Ugrave', 'Uhungarumlaut', 'Umacron', 'Uogonek', 'Uring', 'Utilde'),
                    ('W', 'Wacute', 'Wcircumflex', 'Wdieresis', 'Wgrave'),
                    ('Y', 'Yacute', 'Ycircumflex', 'Ydieresis', 'Ygrave'),
                    ('Z', 'Zacute', 'Zcaron', 'Zdotaccent'),

                    ('acute', 'AEacute', 'Aacute', 'AEacute', 'Cacute', 'Eacute', 'Iacute', 'Lacute', 'Nacute', 'Oacute', 'Oslashacute', 'Racute', 'Sacute', 'Uacute', 'Wacute', 'Yacute', 'Zacute'),
                    ('breve', 'Abreve', 'Ebreve', 'Gbreve', 'Ibreve', 'Obreve', 'Ubreve'),
                    ('caron', 'Ccaron', 'Dcaron', 'Ecaron', 'Ncaron', 'Rcaron', 'Scaron', 'Tcaron', 'Zcaron'),
                    ('cedilla', 'Ccedilla', 'uni0162'),
                    ('circumflex', 'Acircumflex', 'Ccircumflex', 'Ecircumflex', 'Gcircumflex', 'Hcircumflex', 'Icircumflex', 'Jcircumflex', 'Ocircumflex', 'Scircumflex', 'Ucircumflex', 'Wcircumflex', 'Ycircumflex'),
                    ('dieresis', 'Adieresis', 'Edieresis', 'Idieresis', 'Odieresis', 'Udieresis', 'Wdieresis', 'Ydieresis'),
                    ('dotaccent', 'Cdotaccent', 'Edotaccent', 'Gdotaccent', 'Idotaccent', 'Zdotaccent'),
                    ('hungarumlaut', 'Ohungarumlaut', 'Uhungarumlaut'),
                    ('grave', 'Agrave', 'Egrave', 'Igrave', 'Ograve', 'Ugrave', 'Wgrave', 'Ygrave'),
                    ('macron', 'Amacron', 'Emacron', 'Imacron', 'Omacron', 'Umacron'),
                    ('ogonek', 'Aogonek', 'Eogonek', 'Iogonek', 'Uogonek'),
                    ('ring', 'Aring', 'Uring'),
                    ('tilde', 'Atilde', 'Itilde', 'Ntilde', 'Otilde', 'Utilde'),
                    ('uni0326', 'uni0145', 'uni021A', 'uni0218', 'uni0136', 'uni0122', 'uni0156', 'uni013B'),
                    ]

### Instructions
for eachGroup in UCaccentedGroups:
    print 'H %s H O %s O' % (' H '.join(eachGroup), ' O '.join(eachGroup))


