#!/usr/bin/env python
# coding: utf-8

#########################
# TT Kerning controller #
#########################

from __future__ import absolute_import
import importlib

from .kerningComponents import mainController
importlib.reload(mainController)
from .kerningComponents.mainController import KerningController

if __name__ == '__main__':
    kc = KerningController()
