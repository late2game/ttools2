#!/usr/bin/env python
# coding: utf-8

"""Here some values I use constantly across different plugins"""

from collections import OrderedDict

glyphCollectionColors = OrderedDict([('Light Violet', (0.84709999999999996, 0.84709999999999996, 1, 1)),
                                     ('Medium Violet', (0.74509999999999998, 0.74509999999999998, 1, 1)),
                                     ('Violet', (0.58819999999999995, 0.58819999999999995, 1, 1)),

                                     ('Light Cyan', (0.84309999999999996, 1, 1, 1)),
                                     ('Medium Cyan', (0.67449999999999999, 1, 1, 1)),
                                     ('Cyan', (0.502, 1, 1, 1)),

                                     ('Light Pink', (1, 0.84309999999999996, 0.84309999999999996, 1)),
                                     ('Medium Pink', (1, 0.64710000000000001, 0.64710000000000001, 1)),
                                     ('Pink', (1, 0.54120000000000001, 0.54120000000000001, 1)),

                                     ('Light Yellow', (1, 1, 0.84709999999999996, 1)),
                                     ('Medium Yellow', (1, 1, 0.68240000000000001, 1)),
                                     ('Yellow', (1, 1, 0.502, 1)),
                                     ])


vanillaControlsSize = {
    'HorizontalLineThickness': 1,
    'VerticalLineThickness': 1,

    'ButtonRegularHeight': 20,
    'ButtonSmallHeight': 17,
    'ButtonMiniHeight': 14,

    'TextBoxRegularHeight': 17,
    'TextBoxSmallHeight': 14,
    'TextBoxMiniHeight': 12,

    'EditTextRegularHeight': 22,
    'EditTextSmallHeight': 19,
    'EditTextMiniHeight': 16,

    'CheckBoxRegularHeight': 22,
    'CheckBoxSmallHeight': 18,
    'CheckBoxMiniHeight': 10,

    'ComboBoxRegularHeight': 21,
    'ComboBoxSmallHeight': 17,
    'ComboBoxMiniHeight': 14,

    'PopUpButtonRegularHeight': 20,
    'PopUpButtonSmallHeight': 17,
    'PopUpButtonMiniHeight': 15,

    'SliderWithoutTicksRegularHeight': 15,
    'SliderWithoutTicksSmallHeight': 11,
    'SliderWithoutTicksMiniHeight': 10,

    'SliderWithTicksRegularHeight': 23,
    'SliderWithTicksSmallHeight': 17,
    'SliderWithTicksMiniHeight': 16,
    }
