from AppKit import NSView, NSColor, NSRectFill
from vanilla import *

class DemoView03(NSView):

    def __init__(self):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.pop = PopUpButton((0,0,200,20),
                                ['a', 'b'],
                                callback=self.ciao)
        self.pop.show(True)

    def ciao(self, sender):
        print sender.get()


class ScrollViewDemo(object):

    def __init__(self):
        self.w = Window((200, 200))
        self.view = DemoView03.alloc().init()
        self.view.setFrame_(((0, 0), (300, 300)))
        self.w.scrollView = ScrollView((10, 10, -10, -10),
                                       self.view)
        self.w.open()

ScrollViewDemo()