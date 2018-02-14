#!/usr/bin/env python
# coding: utf-8

"""elements for the sidebar"""
from vanilla import Group, TextBox, ComboBox

class ComboBoxWithCaption(Group):

    # attrs
    choice = None

    def __init__(self, posSize, title, options, chosenOption, sizeStyle, callback):
        Group.__init__(self, posSize)
        self.callback = callback
        self.options = options
        width = posSize[2]
        height = posSize[3]

        self.caption = TextBox((0, 2, width*.5, height),
                               title,
                               sizeStyle=sizeStyle,
                               alignment='right')

        self.combo = ComboBox((width*.5, 0, width*.5-1, height),
                              options,
                              continuous=False,
                              sizeStyle=sizeStyle,
                              callback=self.comboCallback)
        self.combo.set(chosenOption)

    def get(self):
        return self.choice

    def comboCallback(self, sender):
        self.choice = str(sender.get())
        self.callback(self)
