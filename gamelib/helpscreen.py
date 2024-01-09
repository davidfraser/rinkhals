"""Help screen."""

from pgu import gui
import pygame
from . import constants
from . import imagecache

HELP = [
"""Welcome to %s!

INTRODUCTION:

The aim of the game is to make as much money as possible from your chicken
farm. The problem is that chickens are delicious and foxes want to eat them.
Since hiring guards is too expensive and too unreliable, the obvious solution
is to help the chickens defend themselves.

You lose if you end a night with no chickens left.

Check the in-game controls reference for information about keys and mouse buttons!

""" % constants.NAME,

"""BIOLOGY AND ECONOMICS:

Chickens only lay eggs in henhouses. An egg must be incubated for two days to
hatch. Chickens that hatch in already full henhouses are moved outside. If there
is no space left next to the henhouse, they die immediately from overcrowding.

Chickens have short attention spans, and will stray from where you put them at
the end of the day if they are out in the open.

You can sell chickens and eggs.  Only one egg per chicken will hatch; the excess
is sold automatically. The fox pelts your chickens acquire during their violent
nocturnal activities are also sold automatically.

Buildings require wood to construct. You can buy and sell wood. If you equip a 
chicken with an axe and place it next to some trees, it will chop some down at the
end of the day.

""",

"""EQUIPMENT:

AXE: For chopping down trees. Doubles as a weapon, but it's not very good. \\
HELMET: Cheap armour. \\
KEVLAR: More expensive and durable armour. \\
KNIFE: Easy to use, but only at melee range, \\
HANDGUN: Slightly longer range than a knife, \\
RIFLE: Ranged weapon; requires more skill. \\
SNIPER RIFLE: Longer range and better accuracy than the plain rifle, but less ammo per clip. \\
BAZOOKA: Even longer range, but less accuracy then rifles - will spread damage over an area.

You can sell equipment, but you don't get the full price back.

Guns use ammunition.  You have an unlimited supply, but chickens don't have pockets, so they
can only use one clip per night.

""",

"""
BUILDINGS:

HENHOUSE: The standard chicken dwelling. \\
HENDOMINIUM: A luxury double-storey chicken dwelling. \\
WATCHTOWER: A lookout post which helps chickens with rifles to see better and further away. \\
BARRACKS: A training facility for specialist chickens. Each night a chicken is here will increase their rank. \\
FENCE: A barrier to both foxes and chickens. \\
TRAP: A fox trap - there's a chance that a fox wandering through this will be caught.

You can repair broken fences and demolish buildings for their wood.  You won't get as
much as you started with -- chickens are bad tenants and peck holes in everything.

Chickens trained in a barracks can rise through the ranks of lance-corporal, corporal or sergeant.
Training increases both the ability to detect enemies, and accuracy in using weapons.
""",

"""
THE ENEMY:

FOX: One of the little furry gluttons who are gorging themselves on your chickens. \\
GREEDY FOX: Doesn't have the decency to stop at just one chicken. \\
NINJA FOX: Tries to sneak past your chicken guards. \\
SAPPER FOX: Blows up your fences with explosives. \\
RINKHALS: Not in fact a fox at all.  It has eclectic tastes. \\

""",
]

LEVEL_TEXT="""The currently selected level is '%(name)s'.

The goal is:
    '%(goal)s'.
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
            pygame.event.post(constants.GO_MAIN_MENU)

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
                if word == "\\":
                    self.br(space[1])
                else:
                    self.add(gui.Label(word))
                    self.space(space)
            self.br(space[1])
        _width, _height = self.resize()
        self.br(440 - _height)
        self.add(self.prev_button, align=-1)
        self.add(self.next_button, align=1)
        self.add(self.done_button, align=0)
