"""The Game Over Screen"""

from pgu import gui
import pygame

import engine
import constants
import imagecache

def create_game_over(gameboard):
    """Create a game over screen"""
    game_over = GameOver(gameboard)

    c = GameOverContainer(align=0, valign=0)
    c.add(game_over, 0, 0)

    return c

class GameOverContainer(gui.Container):
    def paint(self, s):
        pygame.display.set_caption('Game Over')
        #splash = imagecache.load_image("images/splash.png")
        #pygame.display.get_surface().blit(splash, (0, 0))
        gui.Container.paint(self, s)

class GameOver(gui.Table):
    def __init__(self, gameboard, **params):
        gui.Table.__init__(self, **params)

        def return_pressed():
            pygame.event.post(engine.GO_MAIN_MENU)

        def quit_pressed():
            pygame.event.post(engine.QUIT)

        if len(gameboard.chickens) > 0:
            self.td(gui.Label("You Survived", color=constants.FG_COLOR),
                    colspan=3)
        else:
            self.td(gui.Label("You Lost", color=constants.FG_COLOR),
                    colspan=3)

        self.tr()
        self.td(gui.Label("Groats : %d" % gameboard.cash,
            color=constants.FG_COLOR))
        self.td(gui.Label("   Chickens : %d " % len(gameboard.chickens),
            color=constants.FG_COLOR))
        self.td(gui.Label("   Eggs : %d" % gameboard.eggs,
            color=constants.FG_COLOR))
        self.tr()
        self.td(gui.Label("Final score : %d" % (gameboard.cash +
            constants.SELL_PRICE_CHICKEN * len(gameboard.chickens) +
            constants.SELL_PRICE_EGG * gameboard.eggs),
            color=constants.FG_COLOR), colspan=3)

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
