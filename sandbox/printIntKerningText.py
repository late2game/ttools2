#!/usr/bin/env python
# -*- coding: utf-8 -*-

######################
# Python Boilerplate #
######################

### Modules
from string import uppercase, lowercase

### Constants

### Functions & Procedures

### Variables
interpunction = [u'(', u')', u'[', u']', u'{', u'}', u'/', u'\\', u'‹', u'›', u'-', u'‘', u'’', u'\'', u'.', u'•', u'·', u'*', u'°']
lcLetters = ['f', 'k', 'r', 't', 'v', 'w', 'x', 'y', 'z', u'&', u'ß']
theString = u"%(sep)s(%(gn)s)%(sep)s)%(gn)s(%(sep)s[%(gn)s]%(sep)s\n%(sep)s]%(gn)s[%(sep)s{%(gn)s}%(sep)s}%(gn)s{%(sep)s\n%(sep)s\%(gn)s//%(sep)s//%(gn)s\%(sep)s\n%(sep)s‹%(gn)s›%(sep)s›%(gn)s‹%(sep)s-%(gn)s-%(sep)s\n%(sep)s“%(gn)s”%(sep)s\"%(gn)s\"%(sep)s\n%(sep)s.%(gn)s.%(sep)s•%(gn)s•%(sep)s·%(gn)s·%(sep)s\n%(sep)s*%(gn)s*%(sep)s°%(gn)s°%(sep)s"

### Instructions
for eachLetter in interpunction:
    print theString % {'gn': eachLetter, 'sep': 'll'}