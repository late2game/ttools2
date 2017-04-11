from AppKit import NSWindow
from vanilla import *
from classnameincrementer import ClassNameIncrementer

class MyNSWindow(NSWindow):
    __metaclass__ = ClassNameIncrementer
    
    def keyDown_(self, event):
        print unicode(event)


class MyVanillaWindow(Window):
    __metaclass__ = ClassNameIncrementer
    nsWindowClass = MyNSWindow



w = MyVanillaWindow((400, 300))

w.open()
