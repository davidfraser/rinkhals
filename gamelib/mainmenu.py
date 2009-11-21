"""Main menu."""

from pgu import gui
import pygame
import constants
import engine
import imagecache

def make_main_menu(level):
    """Create a main menu"""
    main_menu = MainMenu(level)

    c = MenuContainer(align=0, valign=0)
    c.add(main_menu, 0, 0)

    return c

class MenuContainer(gui.Container):
    def paint(self, s):
        pygame.display.set_caption(constants.NAME)
        splash = imagecache.load_image("images/splash.png")
        pygame.display.get_surface().blit(splash, (0, 0))
        gui.Container.paint(self, s)

    def get_mode(self):
        return self.widgets[0].mode

class MainMenu(gui.Table):
    def __init__(self, level, **params):
        gui.Table.__init__(self, **params)
        self.mode = None

        def fullscreen_toggled():
            pygame.display.toggle_fullscreen()

        def quit_pressed():
            pygame.event.post(engine.QUIT)

        def start_game():
            pygame.event.post(engine.START_DAY)

        def choose_level():
            pygame.event.post(engine.GO_LEVEL_SCREEN)

        def help_pressed():
            pygame.event.post(engine.GO_HELP_SCREEN)

        style = {
            "padding_bottom": 15,
        }
        td_kwargs = {
            "align": 0,
            "style": style,
        }

        change_button = gui.Button('Choose level')
        change_button.connect(gui.CLICK, choose_level)
        self.tr()
        self.td(change_button, **td_kwargs)

        start_button = gui.Button(level.level_name)
        start_button.connect(gui.CLICK, start_game)
        self.tr()
        self.td(start_button, **td_kwargs)

        quit_button = gui.Button("Quit")
        quit_button.connect(gui.CLICK, quit_pressed)

        help_button = gui.Button("Instructions")
        help_button.connect(gui.CLICK, help_pressed)

        fullscreen_toggle = gui.Button("Toggle Fullscreen")
        fullscreen_toggle.connect(gui.CLICK, fullscreen_toggled)

        self.tr()
        self.td(help_button, **td_kwargs)

        # self.tr()
        # self.td(fullscreen_toggle, **td_kwargs)

        self.tr()
        self.td(quit_button, **td_kwargs)
