#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import
import importlib

from .multiMetricsComponents import mainController
importlib.reload(mainController)
from .multiMetricsComponents.mainController import MultiFontMetricsWindow

if __name__ == '__main__':
    mfmw = MultiFontMetricsWindow()
