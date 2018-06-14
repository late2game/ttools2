#!/usr/bin/env python2
# coding: utf-8

import os, sys
import unittest

modulePath = os.path.abspath('../..')
if modulePath not in sys.path:
    sys.path.append(modulePath)

from ttools.sidebearingsLinker import SidebearingsLinker

class SidebearingLinkerTester(unittest.TestCase):

    def setUp(self):
        sl = SidebearingsLinker()

    def test_scenario1(self):
        pass

if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for obj in globals().values():
        if isinstance(obj, type) and issubclass(obj, unittest.TestCase):
            suite.addTest(loader.loadTestsFromTestCase(obj))
    unittest.TextTestRunner(verbosity=1).run(suite)
