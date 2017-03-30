#!/usr/bin/env python
# -*- coding: utf-8 -*-

######################
# Python Boilerplate #
######################

### Modules
from vanilla import Window
from defconAppKit.windows.baseWindow import BaseWindowController


### Constants


### Controllers
class KerningController(BaseWindowController):
    """docstring for KerningController"""
    def __init__(self):
        super(KerningController, self).__init__()

        self.w = Window((0,0,600,800))

        self.w.open()


kc = KerningController()