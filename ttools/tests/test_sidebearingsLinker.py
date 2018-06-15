#!/usr/bin/env python
# coding: utf-8

import os, sys
import unittest

modulePath = os.path.abspath('../..')
if modulePath not in sys.path:
    sys.path.append(modulePath)

import ttools
reload(ttools)
from ttools.sidebearingsLinker import SidebearingsLinker

class SidebearingLinkerTester(unittest.TestCase):

    def setUp(self):
        self.linker = SidebearingsLinker(willOpen=False)

    def tearDown(self):
        if self.linker is not None:
            self.linker.unsubscribeGlyphs()
            self.linker.unsubscribeDisplayedGlyphs()
        self.linker.w.close()

    def test_openPluginAfterFont(self):
        pass

    def test_switchToAnotherFont(self):
        pass

    def test_openPluginBeforeFont(self):
        pass

    def test_removedObservers(self):
        pass


    def test_workingOnMultipleFonts(self):
        pass


if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for obj in globals().values():
        if isinstance(obj, type) and issubclass(obj, unittest.TestCase):
            suite.addTest(loader.loadTestsFromTestCase(obj))
    unittest.TextTestRunner(verbosity=1).run(suite)
