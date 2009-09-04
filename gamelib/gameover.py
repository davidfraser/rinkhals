"""The Game Over Screen"""
import tempfile

from pgu import gui
from pgu.high import High
import pygame

import engine
import constants
import imagecache

def ScoreTable():
    """Create and initialise a score table"""
    # We need a true file, so load will work, but, as we never save,
    # the deletion doesn't bother us.
    our_scores = High(tempfile.NamedTemporaryFile(), 4)
    for score in range(700,1000,100):
        our_scores.submit(score, 'No-one', None)
    return our_scores

def create_game_over(gameboard, scores):
    """Create a game over screen"""
    game_over = GameOver(gameboard, scores)
    return GameOverContainer(game_over, align=0, valign=0)

class GameOverContainer(gui.Container):
    def __init__(self, game_over, *args, **kwargs):
        gui.Container.__init__(self, *args, **kwargs)
        self.add(game_over, 0, 0)
        if game_over.survived:
            self.splash = imagecache.load_image("images/gameover_win.png", ["darken_center"])
        else:
            self.splash = imagecache.load_image("images/gameover_lose.png", ["darken_center"])

    def paint(self, s):
        pygame.display.set_caption('Game Over')
        pygame.display.get_surface().blit(self.splash, (0, 0))
        gui.Container.paint(self, s)

class GameOver(gui.Table):
    def __init__(self, gameboard, scoreboard, **params):
        gui.Table.__init__(self, **params)

        def return_pressed():
            pygame.event.post(engine.GO_MAIN_MENU)

        def quit_pressed():
            pygame.event.post(engine.QUIT)


        score = gameboard.cash + \
                constants.SELL_PRICE_CHICKEN * len(gameboard.chickens) + \
                constants.SELL_PRICE_EGG * gameboard.eggs

        self.tr()
        if len(gameboard.chickens) > 0:
            self.survived = True
            self.td(gui.Label("You Survived", color=constants.FG_COLOR),
                    colspan=3)
            scoreboard.submit(score, 'Player')
        else:
            self.survived = False
            self.td(gui.Label("You Lost", color=constants.FG_COLOR),
                    colspan=3)
        # show the scoreboard

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
        self.tr()
        self.td(gui.Label("Final score : %d" % score,
            color=constants.FG_COLOR), colspan=3)
        if scoreboard.check(score) is not None:
            self.tr()
            if self.survived:
                self.td(gui.Label("You made the high scores",
                    color=constants.FG_COLOR), colspan=3)
            else:
                self.td(gui.Label("Pity, you could have made the high scores",
                    color=constants.FG_COLOR), colspan=3)

        self.tr()
        self.td(gui.Spacer(0, 50), colspan=3)

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
