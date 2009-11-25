"""Help screen."""

from pgu import gui
import pygame
import constants
import engine
import imagecache

HELP = [
"""Welcome to %s

Introduction:

The aim of the game is to make as much money as possible from your chicken
farm. The problem is the foxes, which want to eat your chickens.  Since hiring
guards is both too expensive and unreliable, the obvious solution is to help
the chickens defend themselves.

You lose if you end a night with no chickens left.

""" % constants.NAME,

"""Important Game mechanics:

Chickens only lay eggs in henhouses, and must stay on the egg for 2 days to
hatch a new chicken. Chickens that hatch in already full henhouses are
moved to just outside. If there is no space outside, they die immediately
from overcrowding.

Buildings require wood to construct. You can either trade money for wood,
or, by equipping a chicken with an axes, and placing it near trees, your
chickens will chop down trees at the end of the day.

Chickens that aren't in buildings will move around at the end of the day.

"""
]

LEVEL_TEXT="""The currently selected level is %(name)s

The goal is:
    %(goal)s
"""

def make_help_screen(level):
    """Create a main menu"""
    help_screen = HelpScreen(level, width=600)

    c = HelpContainer(align=0, valign=0)
    c.add(help_screen, 0, 0)

    return c

class HelpContainer(gui.Container):
    def paint(self, s):
        pygame.display.set_caption('Instructions')
        splash = imagecache.load_image("images/splash.png", ["lighten_most"])
        pygame.display.get_surface().blit(splash, (0, 0))
        gui.Container.paint(self, s)

class HelpScreen(gui.Document):
    def __init__(self, level, **params):
        gui.Document.__init__(self, **params)

        self.cur_page = 0

        self.level = level

        def done_pressed():
            pygame.event.post(engine.GO_MAIN_MENU)

        def next_page():
            self.cur_page += 1
            if self.cur_page >= len(HELP):
                self.cur_page = 0
            self.redraw()

        def prev_page():
            self.cur_page -= 1
            if self.cur_page < 0:
                self.cur_page = len(HELP) - 1
            self.redraw()

        self.done_button = gui.Button("Return to Main Menu")
        self.done_button.connect(gui.CLICK, done_pressed)

        self.prev_button = gui.Button("Prev Page")
        self.prev_button.connect(gui.CLICK, prev_page)

        self.next_button = gui.Button("Next Page")
        self.next_button.connect(gui.CLICK, next_page)

        self.redraw()

    def redraw(self):
        for widget in self.widgets[:]:
            self.remove(widget)
        self.layout._widgets = []
        self.layout.init()

        space = self.style.font.size(" ")

        if self.cur_page == 0:
            full_text = "Page %d / %d\n\n" % (self.cur_page + 1, len(HELP)) + \
                    HELP[self.cur_page] + '\n\n' + LEVEL_TEXT % {
                            'name' : self.level.level_name,
                            'goal' : self.level.goal
                            }
        else:
            full_text = "Page %d / %d\n\n" % (self.cur_page + 1, len(HELP)) + \
                    HELP[self.cur_page]

        for paragraph in full_text.split('\n\n'):
            self.block(align=-1)
            for word in paragraph.split():
                self.add(gui.Label(word))
                self.space(space)
            self.br(space[1])
        self.br(space[1])
        self.add(self.prev_button, align=-1)
        self.add(self.next_button, align=1)
        self.add(self.done_button, align=0)
