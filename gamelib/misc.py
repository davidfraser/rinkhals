# Holder for misc useful classes

import random

from pygame.locals import KEYDOWN, K_ESCAPE
from pgu import gui
from pgu.algo import getline

import serializer

class Position(serializer.Simplifiable):
    """2D/3D position / vector. Assumed immutable."""

    SIMPLIFY = ['x', 'y', 'z']

    def __init__(self, x, y, z=0):
        self.x = x
        self.y = y
        self.z = z

    def to_tile_tuple(self):
        return self.x, self.y

    def to_3d_tuple(self):
        return self.x, self.y, self.z

    def dist(self, b):
        """Gives the distance to another position"""

        return max(abs(self.x - b.x), abs(self.y - b.y), abs(self.z - b.z))

    def __sub__(self, b):
        return Position(self.x - b.x, self.y - b.y, self.z - b.z)

    def __add__(self, b):
        return Position(self.x + b.x, self.y + b.y, self.z + b.z)

    def left_of(self, b):
        return self.x < b.x

    def right_of(self, b):
        return self.x > b.x

    def __hash__(self):
        return hash(self.to_3d_tuple())

    def __eq__(self, b):
        return self.to_3d_tuple() == b.to_3d_tuple()

    def __str__(self):
        return "<Position: %s>" % (self.to_3d_tuple(),)

    def intermediate_positions(self, b):
        """Only operates in two dimensions."""
        if max(abs(self.x - b.x), abs(self.y - b.y)) <= 1:
            # pgu gets this case wrong on occasion.
            return [b]
        start = self.to_tile_tuple()
        end = b.to_tile_tuple()
        points = getline(start, end)
        points.remove(start) # exclude start_pos
        if end not in points:
            # Rounding errors in getline cause this
            points.append(end)
        return [Position(p[0], p[1]) for p in points]

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
        title = gui.Label('Are You Sure?')
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
            self.clicked(False)
            return True
        return gui.Dialog.event(self, e)

def check_exit():
    dialog = CheckDialog()
    dialog.open()
    return dialog


