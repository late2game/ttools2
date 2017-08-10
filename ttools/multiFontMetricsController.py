#!/usr/bin/env python
# coding: utf-8

import multiMetricsComponents.mainController
reload(multiMetricsComponents.mainController)
from multiMetricsComponents.mainController import MultiFontMetricsWindow

if __name__ == '__main__':
    mfmw = MultiFontMetricsWindow()