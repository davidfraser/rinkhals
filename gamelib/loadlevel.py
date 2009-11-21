"""Help screen."""

from pgu import gui
import os
import pygame
import constants
import level
import engine
import data
import imagecache

def make_load_screen(level):
    """Create a screen for selecting the levels"""
    load_screen = LoadScreen(level, width=600)

    c = LoadContainer(align=0, valign=0)
    c.add(load_screen, 0, 0)

    return c, load_screen

class LoadContainer(gui.Container):
    def paint(self, s):
        pygame.display.set_caption('Load Level')
        splash = imagecache.load_image("images/splash.png", ["lighten_most"])
        pygame.display.get_surface().blit(splash, (0, 0))
        gui.Container.paint(self, s)

class LoadScreen(gui.Document):
    def __init__(self, start_level, **params):
        self.levels = {}
        self.cur_level = start_level
        for name in os.listdir(data.filepath('levels/')):
            if name.endswith('.conf'):
                try:
                    this_level = level.Level(name)
                except RuntimeError:
                    continue # Skip levels that fail to load
                if os.path.exists(this_level.map):
                    # Skip level if we can't see the map
                    self.levels[this_level.level_name] = this_level
        if not start_level.level_name in self.levels:
            print 'Start level not found'

        self.cur_level = self.levels.values()[0]

        gui.Document.__init__(self, **params)

        def done_pressed():
            pygame.event.post(engine.DO_LOAD_LEVEL)

        def cancel_pressed():
            pygame.event.post(engine.GO_MAIN_MENU)

        done_button = gui.Button("Load This Level")
        done_button.connect(gui.CLICK, done_pressed)

        cancel_button = gui.Button("Cancel & return to main menu")
        cancel_button.connect(gui.CLICK, cancel_pressed)

        self.add(done_button, align=0)
        self.add(cancel_button, align=0)

    def get_level(self):
        return self.cur_level_name

