"""The Game Over Screen"""
import tempfile
import random

from pgu import gui
from pgu.high import Highs
import pygame

import engine
import constants
import imagecache

WON, LOST, LEFT = range(3)

WON_MESSAGES = [
    "You won.",
    "You survived!",
    "Your chickens will one day rule the world.",
    ]

LOST_MESSAGES = [
    "You lost.",
    "You failed to protect your chickens.",
    "Unopposed, the foxes overrun the farm.",
    ]

LEFT_MESSAGES = [
    "You gave up.",
    "You sold your farm.",
    "Real life got in the way.",
    "Are you siding with the foxes?",
    "What will your chickens do now?",
    ]

def ScoreTable(level):
    """Create and initialise a score table"""
    # We need a true file, so load will work, but, as we never save,
    # the deletion doesn't bother us.
    our_scores = Highs(tempfile.NamedTemporaryFile(), 4)
    #for mode in constants.TURN_LIMITS:
    #    for score in range(700,1000,100):
    #        our_scores[mode].submit(score, 'No-one', None)
    for score in range(700,1000,100):
        our_scores[level.level_name].submit(score, 'No-one', None)
    return our_scores

def create_game_over(gameboard, scores, level):
    """Create a game over screen"""
    game_over = GameOver(gameboard, scores, level)
    return GameOverContainer(game_over, align=0, valign=0)

class GameOverContainer(gui.Container):
    def __init__(self, game_over, *args, **kwargs):
        gui.Container.__init__(self, *args, **kwargs)
        self.add(game_over, 0, 0)
        if game_over.survived == WON:
            self.splash = imagecache.load_image("images/gameover_win.png",
                    ["darken_center"])
        elif game_over.survived == LOST:
            self.splash = imagecache.load_image("images/gameover_lose.png",
                    ["darken_center"])
        else:
            self.splash = imagecache.load_image("images/splash.png",
                    ["darken_center"])

    def paint(self, s):
        pygame.display.set_caption('Game Over')
        pygame.display.get_surface().blit(self.splash, (0, 0))
        gui.Container.paint(self, s)

class GameOver(gui.Table):

    def __init__(self, gameboard, scoreboard, level, **params):
        gui.Table.__init__(self, **params)

        def return_pressed():
            pygame.event.post(engine.GO_MAIN_MENU)

        def quit_pressed():
            pygame.event.post(engine.QUIT)

        score = gameboard.cash + \
                level.sell_price_chicken * len(gameboard.chickens) + \
                level.sell_price_egg * gameboard.eggs

        self.tr()
        made_list = scoreboard.check(score) is not None
        if level.is_game_over(gameboard):
            if len(gameboard.chickens) > 0:
                self.survived = WON
                scoreboard.submit(score, 'Player')
                message = random.choice(WON_MESSAGES)
            else:
                self.survived = LOST
                message = random.choice(LOST_MESSAGES)
        else:
            self.survived = LEFT
            message = random.choice(LEFT_MESSAGES)
        self.td(gui.Label(message, color=constants.FG_COLOR),
                colspan=3)
        self.add_spacer()
        # show the scoreboard

        self.tr()
        self.td(gui.Label('Level: %s' % level.level_name, color=constants.FG_COLOR),
                colspan=3)

        for highscore in scoreboard:
            self.tr()
            self.td(gui.Label(highscore.name, color=constants.FG_COLOR), colspan=2)
            self.td(gui.Label('%d' % highscore.score, color=constants.FG_COLOR))

        self.tr()
        self.td(gui.Label("Groats : %d" % gameboard.cash,
            color=constants.FG_COLOR))
        self.td(gui.Label("   Chickens : %d " % len(gameboard.chickens),
            color=constants.FG_COLOR))
        self.td(gui.Label("   Eggs : %d" % gameboard.eggs,
            color=constants.FG_COLOR))
        self.add_spacer()
        self.tr()
        self.td(gui.Label("You killed %d foxes" % gameboard.killed_foxes,
            color=constants.FG_COLOR), colspan=3)
        self.add_spacer()
        self.tr()
        self.td(gui.Label("Final score : %d" % score,
            color=constants.FG_COLOR), colspan=3)
        if made_list:
            self.tr()
            if self.survived == WON:
                self.td(gui.Label("You made the high scores",
                    color=constants.FG_COLOR), colspan=3)
            else:
                self.td(gui.Label("Pity, you could have made the high scores",
                    color=constants.FG_COLOR), colspan=3)

        self.add_spacer(50)

        return_button = gui.Button("Return to Main Menu")
        return_button.connect(gui.CLICK, return_pressed)

        quit_button = gui.Button("Quit")
        quit_button.connect(gui.CLICK, quit_pressed)

        style = {
            "padding_bottom": 15,
        }
        td_kwargs = {
            "align": 0,
            "style": style,
            "colspan": 3,
        }

        self.tr()
        self.td(return_button, **td_kwargs)

        self.tr()
        self.td(quit_button, **td_kwargs)

    def add_spacer(self, height=5):
        self.tr()
        self.td(gui.Spacer(0, height), colspan=3)
