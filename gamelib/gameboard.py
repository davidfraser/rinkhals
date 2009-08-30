import random

from pygame.locals import MOUSEBUTTONDOWN

import data
import tiles


class GameBoard(object):
    TILE_DIMENSIONS = (20, 20)
    TOOLBAR_WIDTH = 22

    def __init__(self):
        self.tv = tiles.FarmVid()
        self.tv.tga_load_tiles(data.filepath('tiles.tga'), self.TILE_DIMENSIONS)
        self.tv.png_folder_load_tiles(data.filepath('tiles'))
        self.tv.tga_load_level(data.filepath('level1.tga'))

        self.tools = tiles.FarmVid()
        self.tools.tga_load_tiles(data.filepath('tiles.tga'), self.TILE_DIMENSIONS)
        self.tools.png_folder_load_tiles(data.filepath('tiles'))
        self.populate_toolbar()
        self.chickens = []
        self.foxes = []

        self.selected_tool = None

    def populate_toolbar(self):
        self.tools.resize((1, 2))
        self.tools.set((0,0), 2)
        self.tools.set((0,1), 3)

    def split_screen(self, screen):
        leftbar_rect = screen.get_rect()
        leftbar_rect.width = self.TOOLBAR_WIDTH
        main_rect = screen.get_rect()
        main_rect.width -= leftbar_rect.width
        main_rect.left += leftbar_rect.width
        return screen.subsurface(leftbar_rect), screen.subsurface(main_rect)

    def paint(self, screen):
        leftbar, main = self.split_screen(screen)
        self.tools.paint(leftbar)
        self.tv.paint(main)

    def update_vid(self, vid, subsurface):
        offset = subsurface.get_offset()
        return [r.move(offset) for r in vid.update(subsurface)]

    def update(self, screen):
        leftbar, main = self.split_screen(screen)
        updates = []
        updates.extend(self.update_vid(self.tools, leftbar))
        updates.extend(self.update_vid(self.tv, main))
        return updates

    def loop(self):
        self.tv.loop()

    def select_tool(self, e):
        tool_pos = self.tools.screen_to_tile(e.pos)
        if tool_pos[1] < 2:
            self.selected_tool = self.tools.get(tool_pos)
        else:
            self.selected_tool = None

    def use_tool(self, e):
        if self.selected_tool is None:
            return
        pos = self.tv.screen_to_tile((e.pos[0] - self.TOOLBAR_WIDTH, e.pos[1]))
        self.tv.set(pos, self.selected_tool)

    def event(self, e):
        if e.type == MOUSEBUTTONDOWN:
            if e.pos[0] < self.TOOLBAR_WIDTH:
                self.select_tool(e)
            else:
                self.use_tool(e)

    def clear_foxes(self):
        for fox in self.foxes:
            self.tv.sprites.remove(fox)
        self.foxes = [] # Remove all the foxes

    def add_chicken(self, chicken):
        self.chickens.append(chicken)
        self.tv.sprites.append(chicken)

    def add_fox(self, fox):
        self.foxes.append(fox)
        self.tv.sprites.append(fox)
