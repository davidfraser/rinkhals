'''Game main module.

Contains the entry point used by the run_game.py script.

Feel free to put all your game code here, or in other modules in this "gamelib"
package.
'''

import pygame
from pgu import gui
from pygame.locals import SWSURFACE

#from engine import Engine, MainMenuState
from sound import init_sound
import constants
import data
import sys

def create_main_app(screen):
    """Create an app with a background widget."""
    app = gui.App()
    background = pygame.Surface(screen.get_size())
    widget = gui.Image(background)
    app.init(widget, screen)
    return app

def main():
    """Main script."""
    init_sound()
    screen = pygame.display.set_mode(constants.SCREEN, SWSURFACE)
    pygame.display.set_icon(pygame.image.load(
        data.filepath('icons/foxassault24x24.png')))
    main_app = create_main_app(screen)

    from engine import Engine, MainMenuState

    if len(sys.argv) > 1:
        level_name = sys.argv[1]
    else:
        level_name = 'two_weeks'

    engine = Engine(main_app, level_name)
    try:
        engine.run(MainMenuState(engine), screen)
    except KeyboardInterrupt:
        pass
