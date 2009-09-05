# Holder for misc useful classes

import random

from pygame.locals import KEYDOWN, K_ESCAPE
from pgu import gui

class Position(object):
    """2D position / vector"""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def to_tuple(self):
        return self.x, self.y

    def dist(self, b):
        """Gives the distance to another position"""

        return max(abs(self.x - b.x), abs(self.y - b.y))

    def __sub__(self, b):
        return Position(self.x - b.x, self.y - b.y)

    def __add__(self, b):
        return Position(self.x + b.x, self.y + b.y)

    def left_of(self, b):
        return self.x < b.x

    def right_of(self, b):
        return self.x > b.x

    def __eq__(self, b):
        return self.x == b.x and self.y == b.y

class WeightedSelection(object):
    def __init__(self, weightings=None):
        self.weightings = []
        self.total = 0
        if weightings:
            for item, weight in weightings:
                self.weightings.append((item, weight))
                self.total += weight
        
    def choose(self):
        roll = random.uniform(0, self.total)
        for item, weight in self.weightings:
            if roll < weight:
                return item
            roll -= weight

class CheckDialog(gui.Dialog):
    def __init__(self, **params):
        title = gui.Label('Are You sure')
        self.do_quit = False
        self.running = True
        tbl = gui.Table()
        tbl.tr()
        tbl.td(gui.Label("Do you REALLY want to exit this game?"), colspan=2)
        tbl.tr()
        tbl.td(gui.Spacer(0, 15), colspan=2)
        tbl.tr()
        yes_button = gui.Button('Yes')
        yes_button.connect(gui.CLICK, self.clicked, True)
        no_button = gui.Button('No')
        no_button.connect(gui.CLICK, self.clicked, False)
        tbl.td(no_button, align=-1)
        tbl.td(yes_button, align=1)
        gui.Dialog.__init__(self, title, tbl, **params)

    def clicked(self, val):
        self.do_quit = val
        self.running = False
        self.close()

    def event(self, e):
        if e.type == KEYDOWN and e.key == K_ESCAPE:
            self.clicked(True)
            return True
        return gui.Dialog.event(self, e)

def check_exit():
    dialog = CheckDialog()
    dialog.open()
    return dialog


