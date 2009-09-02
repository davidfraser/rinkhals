'''Game main module.

Contains the entry point used by the run_game.py script.

Feel free to put all your game code here, or in other modules in this "gamelib"
package.
'''

import pygame
from pgu import gui
from pygame.locals import SWSURFACE

from mainmenu import MainMenu
from engine import Engine, MainMenuState
from sound import init_sound
import constants

def create_menu_app():
    """Create the menu app."""
    app = gui.App()
    main_menu = MainMenu()

    c = gui.Container(align=0, valign=0)
    c.add(main_menu, 0, 0)

    app.init(c)
    return app

def main():
    """Main script."""
    init_sound()
    screen = pygame.display.set_mode(constants.SCREEN, SWSURFACE)
    main_menu_app = create_menu_app()
    engine = Engine(main_menu_app)
    try:
        engine.run(MainMenuState(engine), screen)
    except KeyboardInterrupt:
        pass
