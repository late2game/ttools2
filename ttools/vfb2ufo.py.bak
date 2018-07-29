#!/usr/bin/env python
# coding: utf-8

###########
# vfb2ufo #
###########

### Modules
# custom
import ui.userInterfaceValues
reload(ui.userInterfaceValues)
from ui.userInterfaceValues import vanillaControlsSize

import extraTools.miscFunctions
reload(extraTools.miscFunctions)
from extraTools.miscFunctions import catchFilesAndFolders

# standard
from mojo.compile import executeCommand
from vanilla import FloatingWindow, PopUpButton, Button, RadioGroup
from vanilla.dialogs import getFile, getFolder, message
from defconAppKit.windows.baseWindow import BaseWindowController

### Constants
PLUGIN_TITLE = 'VFB2UFO'

PLUGIN_WIDTH = 200
MARGIN_HOR = 10
MARGIN_VER = 8
NET_WIDTH = PLUGIN_WIDTH - MARGIN_HOR*2

### Tool
class VFB2UFO(BaseWindowController):

    inputOptions = ['Single File', 'Multiple files from a Folder']
    chosenMode = inputOptions[0]

    conversionOptions = ["From VFB to UFO", "From UFO to VFB"]
    suffix2conversionOption = {"From VFB to UFO": '.vfb',
                               "From UFO to VFB": '.ufo'}
    chosenSuffix = suffix2conversionOption[conversionOptions[0]]

    def __init__(self):
        super(VFB2UFO, self).__init__()
        self.w = FloatingWindow((PLUGIN_WIDTH, 2),
                                PLUGIN_TITLE)
        self.jumpingY = MARGIN_VER

        # options button
        self.w.optionsPopUp = PopUpButton((MARGIN_HOR, self.jumpingY, NET_WIDTH, vanillaControlsSize['PopUpButtonRegularHeight']),
                                          self.inputOptions,
                                          callback=self.optionsPopUpCallback)
        self.jumpingY += vanillaControlsSize['PopUpButtonRegularHeight'] + MARGIN_HOR

        # suffix option
        self.w.suffixRadio = RadioGroup((MARGIN_HOR, self.jumpingY, NET_WIDTH, vanillaControlsSize['ButtonRegularHeight']*2),
                                        ["From VFB to UFO", "From UFO to VFB"],
                                        callback=self.suffixRadioCallback)
        self.w.suffixRadio.set(0)
        self.w.suffixRadio.enable(False)
        self.jumpingY += vanillaControlsSize['ButtonRegularHeight']*2 + MARGIN_HOR

        # convert button
        self.w.convertButton = Button((MARGIN_HOR, self.jumpingY, NET_WIDTH, vanillaControlsSize['ButtonRegularHeight']),
                                      'Choose file and convert',
                                      callback=self.convertButtonCallback)
        self.jumpingY += vanillaControlsSize['ButtonRegularHeight'] + MARGIN_HOR

        self.w.resize(PLUGIN_WIDTH, self.jumpingY)
        self.w.open()

    def optionsPopUpCallback(self, sender):
        self.chosenMode = self.inputOptions[sender.get()]
        if self.chosenMode == 'Single File':
            self.w.suffixRadio.enable(False)
            self.w.convertButton.setTitle('Choose file and convert')
        else:
            self.w.suffixRadio.enable(True)
            self.w.convertButton.setTitle('Choose folder and convert')

    def suffixRadioCallback(self, sender):
        self.chosenSuffix = self.suffix2conversionOption[self.conversionOptions[sender.get()]]

    def convertButtonCallback(self, sender):
        if self.chosenMode == 'Single File':
            inputPath = getFile('Choose the file to convert')[0]
            if inputPath.endswith('.vfb') or inputPath.endswith('.ufo'):
                executeCommand(['vfb2ufo', '-fo', inputPath], shell=True)
            else:
                message('input file path is not correct')
        else:
            inputFolder = getFolder('Choose a folder with files to convert')[0]
            if inputFolder:
                for eachPath in catchFilesAndFolders(inputFolder, self.chosenSuffix):
                    executeCommand(['vfb2ufo', '-fo', eachPath], shell=True)
            else:
                message('input folder path is not correct')


### init tool
if __name__ == '__main__':
    vu = VFB2UFO()
