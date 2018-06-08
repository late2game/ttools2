# coding: utf-8

import unittest

def multiply(a, b):
    return a*b

class StandardFontTests(unittest.TestCase):

    def test_glyphIntoFont(self):
        from mojo.roboFont import CurrentFont
        self.assertIn('a', CurrentFont())
        
    def test_multiplication(self):
        self.assertEqual(multiply(2, 2), 4)

if __name__ == '__main__':
    unittest.main()
