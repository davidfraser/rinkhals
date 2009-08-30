"""Main menu."""

from pgu import gui
import pygame
import constants

class MainMenu(gui.Table):
    def __init__(self,**params):
        gui.Table.__init__(self,**params)

        def fullscreen_changed(btn):
            pygame.display.toggle_fullscreen()

        fg = (255,255,255)

        self.tr()
        self.td(gui.Label(constants.NAME, color=fg), colspan=2)

        self.tr()
        self.td(gui.Label("Start", color=fg), align=1)

        btn = gui.Switch(value=False,name='fullscreen')
        btn.connect(gui.CHANGE, fullscreen_changed, btn)

        self.tr()
        self.td(gui.Label("Full Screen: ",color=fg),align=1)
        self.td(btn)

        self.tr()
        self.td(gui.Label("Quit", color=fg), align=1)
