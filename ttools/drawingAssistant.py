#!/usr/bin/env python
# coding: utf-8

#####################
# Drawing Assistant #
#####################

import drawingAssistantComponents.mainController
reload(drawingAssistantComponents.mainController)
from drawingAssistantComponents.mainController import DrawingAssistant

if __name__ == '__main__':
    da = DrawingAssistant()
