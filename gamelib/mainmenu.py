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

        def fortnight_pressed():
            constants.TURN_LIMIT = 14
            pygame.event.post(engine.START_DAY)

        def quarter_pressed():
            constants.TURN_LIMIT = 90
            pygame.event.post(engine.START_DAY)

        def unlimited_pressed():
            constants.TURN_LIMIT = 0
            pygame.event.post(engine.START_DAY)

        def help_pressed():
            pygame.event.post(engine.GO_HELP_SCREEN)

        fortnight_button = gui.Button("Fortnight")
        fortnight_button.connect(gui.CLICK, fortnight_pressed)

        quarter_button = gui.Button("Quarter")
        quarter_button.connect(gui.CLICK, quarter_pressed)

        unlim_button = gui.Button("Unlimited")
        unlim_button.connect(gui.CLICK, unlimited_pressed)

        quit_button = gui.Button("Quit")
        quit_button.connect(gui.CLICK, quit_pressed)

        help_button = gui.Button("Instructions")
        help_button.connect(gui.CLICK, help_pressed)

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
        self.td(fortnight_button, **td_kwargs)

        self.tr()
        self.td(quarter_button, **td_kwargs)

        self.tr()
        self.td(unlim_button, **td_kwargs)

        self.tr()
        self.td(help_button, **td_kwargs)

        self.tr()
        self.td(fullscreen_toggle, **td_kwargs)

        self.tr()
        self.td(quit_button, **td_kwargs)
