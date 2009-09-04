"""Help screen."""

from pgu import gui
import pygame
import constants
import engine
import imagecache

HELP="""Welcome to %s

Introduction:

The aim of the game is to make as much money as possible from your chicken
farm. The problem is the foxes, which want to eat your chickens.  Since hiring
guards is both too expensive and unreliable, the obvious solution is to help
the chickens defend themselves.

Game mechanics:

You lose if you end a night with no chickens left.

You win if you survive 14 nights.

Chickens only lay eggs in henhouses, and must stay on the egg for 2 days to
hatch a new chicken. Chickens that hatch in already full henhouses are
moved to just outside. If there is no space outside, they die immediately
from overcrowding.
""" % constants.NAME

def make_help_screen():
    """Create a main menu"""
    help_screen = HelpScreen(width=600)

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
    def __init__(self, **params):
        gui.Document.__init__(self, **params)

        def done_pressed():
            pygame.event.post(engine.GO_MAIN_MENU)

        done_button = gui.Button("Return to Main Menu")
        done_button.connect(gui.CLICK, done_pressed)

        space = self.style.font.size(" ")

        for paragraph in HELP.split('\n\n'):
            self.block(align=-1)
            for word in paragraph.split():
                self.add(gui.Label(word))
                self.space(space)
            self.br(space[1])
        self.br(space[1])
        self.block(align=0)
        self.add(done_button, align=0)
