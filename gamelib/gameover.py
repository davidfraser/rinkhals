"""The Game Over Screen"""
import random
import os
import getpass

from pgu import gui
from pgu import html
from pgu.high import Highs
import pygame
from pygame.locals import KEYDOWN, K_ESCAPE

import constants
import imagecache
import config

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
    score_path = os.path.join(config.config.prefs_folder, "highscores.dat")
    all_scores = Highs(score_path, 4)
    all_scores.load()
    level_scores = all_scores[level.level_name]

    if not list(level_scores):
        authors = [auth[2] for auth in constants.AUTHORS]
        scores = [700+i*100 for i in range(len(authors))]
        random.shuffle(scores)

        for auth, score in zip(authors, scores):
            level_scores.submit(score, auth, None)

        level_scores.save()

    return level_scores

def create_game_over(gameboard, level):
    """Create a game over screen"""
    game_over = GameOver(gameboard, level)
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

    def __init__(self, gameboard, level, **params):
        gui.Table.__init__(self, **params)
        scoreboard = ScoreTable(level)

        def return_pressed():
            pygame.event.post(constants.GO_MAIN_MENU)

        def quit_pressed():
            pygame.event.post(constants.DO_QUIT)

        score = gameboard.cash + \
                level.sell_price_chicken * len(gameboard.chickens) + \
                level.sell_price_egg * gameboard.eggs

        made_list = scoreboard.check(score) is not None
        if level.is_game_over(gameboard):
            if len(gameboard.chickens) > 0:
                self.survived = WON
                try:
                    player = getpass.getuser()
                except Exception:
                    player = 'You'
                scoreboard.submit(score, player)
                message = random.choice(WON_MESSAGES)
            else:
                self.survived = LOST
                message = random.choice(LOST_MESSAGES)
        else:
            self.survived = LEFT
            message = random.choice(LEFT_MESSAGES)

        self.tr()
        self.td(gui.Label(message, color=constants.FG_COLOR),
                colspan=3)
        self.add_spacer()

        # heading options
        head_kwargs = {
            'color': constants.FG_COLOR,
            'style': {
                'padding_top': 10,
                'padding_bottom': 5,
            },
        }

        # show the scoreboard

        self.tr()
        self.td(html.HTML('<b>High Scores for Level<i>%s:</i></b>'
            % level.level_name, **head_kwargs),
            colspan=3)

        for highscore in scoreboard:
            self.tr()
            self.td(gui.Label(highscore.name, color=constants.FG_COLOR), colspan=2)
            self.td(gui.Label('%d' % highscore.score, color=constants.FG_COLOR))

        # show player score

        self.tr()
        self.td(html.HTML('<b>Your Score:</b>', **head_kwargs), colspan=3)

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
                msg = "You made the high scores!"
                scoreboard.save()
            else:
                msg = "Pity, you could have made the high scores."
            self.td(html.HTML("<b>%s</b>" % msg, **head_kwargs)
                , colspan=3)

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


class ScoreDialog(gui.Dialog):

    def __init__(self, level, **params):
        title = html.HTML("<b>High Scores for Level<i>%s</i></b>"
            % level.level_name)
        scoreboard = ScoreTable(level)

        tbl = gui.Table()
        for highscore in scoreboard:
            tbl.tr()
            tbl.td(gui.Label(highscore.name), colspan=2)
            tbl.td(gui.Label('%d' % highscore.score))

        gui.Dialog.__init__(self, title, tbl, **params)

    def event(self, e):
        if e.type == KEYDOWN and e.key == K_ESCAPE:
            self.close()
            return True
        return gui.Dialog.event(self, e)
