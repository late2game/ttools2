from AppKit import NSView
from vanilla import *
from classnameincrementer import ClassNameIncrementer

class MyNSView(NSView):
    __metaclass__ = ClassNameIncrementer

    def canBecomeKeyView(self):
        return True

    def acceptsFirstResponder(self):
        return True

    def keyDown_(self, event):
        print event

    def mouseDown_(self, event):
        print "mouse", event


class MyVanillaGroup(Group):
    nsViewClass = MyNSView



w = Window((400, 300))
w.testGroup = MyVanillaGroup((10, 10, -10, -10))
# w.button = Button((10, 40, 150, 25), "Whatever")
w.open()
