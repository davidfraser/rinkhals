'''Game main module.

Contains the entry point used by the run_game.py script.

Feel free to put all your game code here, or in other modules in this "gamelib"
package.
'''

import sys

import pygame
from pgu import gui
from pygame.locals import SWSURFACE, SRCALPHA

from . import sound
from . import constants
from .config import config
from . import data
from .misc import WarnDialog

def create_main_app(screen):
    """Create an app with a background widget."""
    app = gui.App()
    background = pygame.Surface(screen.get_size())
    widget = gui.Image(background)
    app.init(widget, screen)
    return app

def complaint_dialog(message):
    """Create a complaint dialog"""
    app = gui.App()

    def close(_w):
        app.quit()

    app.close = close

    dialog = WarnDialog('Problem starting orc Assault',
            message)
    app.run(dialog)
    sys.exit(1)

def sanity_check():
    """Run some sanity checks, and complain if they fail"""
    try:
        pygame.Surface((100, 100), flags=SRCALPHA)
    except Exception as e:
        complaint_dialog("Unable to create a suitable screen, please check your display settings")
    if sound.SOUND_INITIALIZED:
        try:
            sound.play_sound('silence.ogg')
            sound.background_music('silence.ogg')
        except pygame.error:
            complaint_dialog('Error trying to play sound. Please run with --no-sound')
        sound.stop_background_music()

def main():
    """Main script."""
    config.configure(sys.argv[1:])
    sound.init_sound()
    sanity_check()
    if sys.platform == 'win32':
        # On Windows, the monitor scaling can be set to something besides normal 100%.
        import ctypes
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except AttributeError:
            pass  # Windows XP doesn't support monitor scaling, so just do nothing.
    screen = pygame.display.set_mode(constants.SCREEN, SWSURFACE)
    pygame.display.set_icon(pygame.image.load(
        data.filepath('icons/foxassault24x24.png')))
    main_app = create_main_app(screen)

    from .engine import Engine, MainMenuState

    engine = Engine(main_app, config.level_name)
    try:
        engine.run(MainMenuState(engine), screen)
    except KeyboardInterrupt:
        pass
