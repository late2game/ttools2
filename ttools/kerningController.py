#!/usr/bin/env python
# coding: utf-8

#########################
# TT Kerning controller #
#########################

from __future__ import absolute_import
#!/usr/bin/env python
# coding: utf-8

#########################
# TT Kerning controller #
#########################

from . import kerningComponents.mainController
reload(kerningComponents.mainController)
from .kerningComponents.mainController import KerningController

if __name__ == '__main__':
    kc = KerningController()
