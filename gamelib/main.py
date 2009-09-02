'''Game main module.

Contains the entry point used by the run_game.py script.

Feel free to put all your game code here, or in other modules in this "gamelib"
package.
'''

import pygame
from pgu import gui
from pygame.locals import SWSURFACE

from mainmenu import MenuContainer, MainMenu
from engine import Engine, MainMenuState
from sound import init_sound
import constants



def create_app():
    """Create the app."""
    app = gui.App()
    return app

def main():
    """Main script."""
    init_sound()
    screen = pygame.display.set_mode(constants.SCREEN, SWSURFACE)
    main_app = create_app()
    engine = Engine(main_app)
    try:
        engine.run(MainMenuState(engine), screen)
    except KeyboardInterrupt:
        pass
