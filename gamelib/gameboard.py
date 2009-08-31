import pygame
from pygame.locals import MOUSEBUTTONDOWN
from pgu import gui

import data
import tiles

# FIXME: These should probably be proper events of some kind.
SELL_CHICKEN = None
SELL_EGG = None
BUY_FENCE = 2
BUY_HENHOUSE = 3


class ToolBar(gui.Table):
    def __init__(self, gameboard, **params):
        gui.Table.__init__(self, **params)
        self.gameboard = gameboard
        self.add_tool_button("Sell chicken", SELL_CHICKEN)
        self.add_tool_button("Sell egg", SELL_EGG)
        self.add_tool_button("Buy fence", BUY_FENCE)
        self.add_tool_button("Buy henhouse", BUY_HENHOUSE)

    def add_tool_button(self, text, tool):
        button = gui.Button(text)
        button.connect(gui.CLICK, lambda: self.gameboard.set_selected_tool(tool))
        self.tr()
        self.add(button)


class VidWidget(gui.Widget):
    def __init__(self, gameboard, vid, **params):
        gui.Widget.__init__(self, **params)
        self.gameboard = gameboard
        self.vid = vid
        self.width = params.get('width', 0)
        self.height = params.get('height', 0)

    def paint(self, surface):
        self.vid.paint(surface)

    def update(self, surface):
        return self.vid.update(surface)

    def resize(self, width=0, height=0):
        if width is not None:
            self.width = width
        if height is not None:
            self.height = height
        return self.width, self.height

    def event(self, e):
        if e.type == MOUSEBUTTONDOWN:
            self.gameboard.use_tool(e)


class GameBoard(object):
    TILE_DIMENSIONS = (20, 20)
    TOOLBAR_WIDTH = 140

    def __init__(self):
        self.tv = tiles.FarmVid()
        self.tv.tga_load_tiles(data.filepath('tiles.tga'), self.TILE_DIMENSIONS)
        self.tv.png_folder_load_tiles(data.filepath('tiles'))
        self.tv.tga_load_level(data.filepath('level1.tga'))
        self.selected_tool = None
        self.chickens = []
        self.foxes = []
        self.create_disp()

    def create_disp(self):
        width, height = pygame.display.get_surface().get_size()
        tbl = gui.Table()
        tbl.tr()
        tbl.td(ToolBar(self), width=self.TOOLBAR_WIDTH)
        tbl.td(VidWidget(self, self.tv, width=width-self.TOOLBAR_WIDTH, height=height))
        self.disp = gui.App()
        self.disp.init(tbl)

    def paint(self, screen):
        self.disp.paint(screen)

    def update(self, screen):
        return self.disp.update(screen)

    def loop(self):
        self.tv.loop()

    def set_selected_tool(self, tool):
        self.selected_tool = tool

    def use_tool(self, e):
        if self.selected_tool is None:
            return
        pos = self.tv.screen_to_tile(e.pos)
        self.tv.set(pos, self.selected_tool)

    def event(self, e):
        self.disp.event(e)

    def clear_foxes(self):
        for fox in self.foxes:
            self.tv.sprites.remove(fox)
        self.foxes = [] # Remove all the foxes

    def move_foxes(self):
        for fox in self.foxes:
            fox.move(self)

    def add_chicken(self, chicken):
        self.chickens.append(chicken)
        self.tv.sprites.append(chicken)

    def add_fox(self, fox):
        self.foxes.append(fox)
        self.tv.sprites.append(fox)

    def remove_fox(self, fox):
        if fox in self.foxes:
            self.foxes.remove(fox)
            self.tv.sprites.remove(fox)

    def remove_chicken(self, chick):
        if chick in self.chickens:
            self.chickens.remove(chick)
            self.tv.sprites.remove(chick)
