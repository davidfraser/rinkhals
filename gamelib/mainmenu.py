"""Main menu."""

from pgu import gui
import pygame
import constants
import engine
import imagecache

def make_main_menu():
    """Create a main menu"""
    main_menu = MainMenu()

    c = MenuContainer(align=0, valign=0)
    c.add(main_menu, 0, 0)

    return c

class MenuContainer(gui.Container):
    def paint(self, s):
        pygame.display.set_caption(constants.NAME)
        splash = imagecache.load_image("images/splash.png")
        pygame.display.get_surface().blit(splash, (0, 0))
        gui.Container.paint(self, s)

class MainMenu(gui.Table):
    def __init__(self, **params):
        gui.Table.__init__(self, **params)

        def fullscreen_toggled():
            pygame.display.toggle_fullscreen()

        def quit_pressed():
            pygame.event.post(engine.QUIT)

        def start_pressed():
            pygame.event.post(engine.START_DAY)

        start_button = gui.Button("Start")
        start_button.connect(gui.CLICK, start_pressed)

        quit_button = gui.Button("Quit")
        quit_button.connect(gui.CLICK, quit_pressed)

        fullscreen_toggle = gui.Button("Toggle Fullscreen")
        fullscreen_toggle.connect(gui.CLICK, fullscreen_toggled)

        style = {
            "padding_bottom": 15,
        }
        td_kwargs = {
            "align": 0,
            "style": style,
        }

        self.tr()
        self.td(start_button, **td_kwargs)

        self.tr()
        self.td(fullscreen_toggle, **td_kwargs)

        self.tr()
        self.td(quit_button, **td_kwargs)
