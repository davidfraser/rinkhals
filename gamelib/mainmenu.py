"""Main menu."""

from pgu import gui
import pygame
import constants

class MainMenu(gui.Table):
    def __init__(self, **params):
        gui.Table.__init__(self, **params)

        def fullscreen_toggled():
            pygame.display.toggle_fullscreen()

        def quit_pressed():
            pygame.event.post(pygame.event.Event(pygame.QUIT))

        def start_pressed():
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, event="<Our Start Event Class>"))

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
        self.td(gui.Label(constants.NAME, color=constants.FG_COLOR), **td_kwargs)

        self.tr()
        self.td(start_button, **td_kwargs)

        self.tr()
        self.td(fullscreen_toggle, **td_kwargs)

        self.tr()
        self.td(quit_button, **td_kwargs)
