#!/usr/bin/env python
# coding: utf-8

from __future__ import absolute_import
#!/usr/bin/env python
# coding: utf-8

from . import multiMetricsComponents.mainController
reload(multiMetricsComponents.mainController)
from .multiMetricsComponents.mainController import MultiFontMetricsWindow

if __name__ == '__main__':
    mfmw = MultiFontMetricsWindow()