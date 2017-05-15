#!/usr/bin/env python
# -*- coding: utf-8 -*-

###################
# load aglfn list #
###################

### Function & procedures
def loadAGLFN():
    aglfn = [item.strip().split(';') for item in open('aglfn.txt', 'r').readlines() if item.startswith('#') is False]
    aglfn = {item[0]: {'glyphName': item[1], 'description': item[2]} for item in aglfn}
    return aglfn