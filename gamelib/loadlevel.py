"""Help screen."""

from pgu import gui
import os
import pygame
import level
import engine
import data
import imagecache
import gameboard
import constants

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
        gui.Document.__init__(self, **params)

        self.levels = []
        self.cur_level = None
        for name in os.listdir(data.filepath('levels/')):
            if name.endswith('.conf'):
                try:
                    this_level = level.Level(name)
                except RuntimeError:
                    continue # Skip levels that fail to load
                if os.path.exists(this_level.map):
                    # Skip level if we can't see the map
                    self.levels.append(this_level)
                    if this_level.level_name == start_level.level_name:
                        self.cur_level = this_level

        if not self.cur_level:
            self.cur_level = self.levels[0]


        def done_pressed():
            pygame.event.post(engine.DO_LOAD_LEVEL)

        def cancel_pressed():
            pygame.event.post(engine.GO_MAIN_MENU)

        def next_pressed():
            self.next_level()

        def prev_pressed():
            self.prev_level()

        self.next_button = gui.Button("Next Level >>")
        self.next_button.connect(gui.CLICK, next_pressed)

        self.prev_button = gui.Button("<< Prev Level")
        self.prev_button.connect(gui.CLICK, prev_pressed)

        self.cancel_button = gui.Button("Cancel")
        self.cancel_button.connect(gui.CLICK, cancel_pressed)

        self.done_button = gui.Button("Load This Level")
        self.done_button.connect(gui.CLICK, done_pressed)

        self.render_level()


    def next_level(self):
        pos = self.levels.index(self.cur_level) + 1
        if pos == len(self.levels):
            pos = 0
        self.cur_level = self.levels[pos]
        self.render_level()

    def prev_level(self):
        pos = self.levels.index(self.cur_level) - 1
        if pos == -1:
            pos = len(self.levels) - 1
        self.cur_level = self.levels[pos]
        self.render_level()

    def render_level(self):
        self.clear()
        self.repaint()

        board = gameboard.GameBoard(None, self.cur_level)

        space = self.style.font.size(" ")
        w, h = board.tv.size

        map_image = pygame.Surface((constants.TILE_DIMENSIONS[0] * w,
            constants.TILE_DIMENSIONS[1] * h))
        board.tv.loop()
        board.tv.paint(map_image)

        style = {
                'width' : min(300, 7*w),
                'height' : min(300, 7*h),
                }

        image = gui.Image(map_image, style=style)

        self.block(align=0)
        self.add(image)

        self.block(align=-1)
        self.add(gui.Label(self.cur_level.level_name))
        self.block(align=-1)
        for word in self.cur_level.goal.split():
            self.add(gui.Label(word))
            self.space(space)

        self.block(align=0)
        # NB: pgu 's layout engine is sensitive to ordering here
        self.add(self.prev_button, align=-1)
        self.add(self.next_button, align=1)
        self.add(self.done_button)
        self.add(self.cancel_button)

    def clear(self):
        """Clear the document"""
        for widget in self.widgets[:]:
            self.remove(widget)
        self.layout._widgets = []
        self.layout.init()



