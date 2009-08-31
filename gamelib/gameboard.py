import pygame
from pygame.locals import MOUSEBUTTONDOWN, KEYDOWN, K_UP, K_DOWN, K_LEFT, K_RIGHT
from pgu import gui

import data
import tiles
import constants
import buildings


class OpaqueLabel(gui.Label):
    def paint(self, s):
        s.fill(self.style.background)
        gui.Label.paint(self, s)

    def update_value(self, value):
        self.value = value
        self.style.width, self.style.height = self.font.size(self.value)
        self.repaint()


class ToolBar(gui.Table):
    def __init__(self, gameboard, **params):
        gui.Table.__init__(self, **params)
        self.gameboard = gameboard
        self.cash_counter = OpaqueLabel("Groats:                ", color=constants.FG_COLOR)
        self.tr()
        self.add(self.cash_counter)
        self.add_tool_button("Sell chicken", constants.TOOL_SELL_CHICKEN)
        self.add_tool_button("Sell egg", constants.TOOL_SELL_EGG)
        self.add_tool_button("Sell building", constants.TOOL_SELL_BUILDING)
        self.add_tool_button("Buy fence", constants.TOOL_BUY_FENCE)
        for building_cls in buildings.BUILDINGS:
            self.add_tool_button("Buy %s" % (building_cls.NAME,), building_cls)

    def update_cash_counter(self, amount):
        self.cash_counter.update_value("Groats: %s" % amount)
        self.repaint()

    def add_tool_button(self, text, tool):
        button = gui.Button(text)
        button.connect(gui.CLICK, lambda: self.gameboard.set_selected_tool(tool))
        self.tr()
        self.add(button)


class VidWidget(gui.Widget):
    def __init__(self, gameboard, vid, **params):
        gui.Widget.__init__(self, **params)
        self.gameboard = gameboard
        vid.bounds = pygame.Rect((0, 0), vid.tile_to_view(vid.size))
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

    def move_view(self, x, y):
        self.vid.view.move_ip((x, y))

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
        self.create_disp()

        self.selected_tool = None
        self.chickens = []
        self.foxes = []
        self.buildings = []
        self.cash = 0
        self.add_cash(constants.STARTING_CASH)

    def create_disp(self):
        width, height = pygame.display.get_surface().get_size()
        tbl = gui.Table()
        tbl.tr()
        self.toolbar = ToolBar(self)
        tbl.td(self.toolbar, width=self.TOOLBAR_WIDTH)
        self.tvw = VidWidget(self, self.tv, width=width-self.TOOLBAR_WIDTH, height=height)
        tbl.td(self.tvw)
        self.disp = gui.App()
        self.disp.init(tbl)

    def paint(self, screen):
        self.disp.paint(screen)

    def update(self, screen):
        self.tvw.reupdate()
        return self.disp.update(screen)

    def loop(self):
        self.tv.loop()

    def set_selected_tool(self, tool):
        self.selected_tool = tool

    def use_tool(self, e):
        if self.selected_tool == constants.TOOL_SELL_CHICKEN:
            self.sell_chicken(e.pos)
        elif self.selected_tool == constants.TOOL_SELL_EGG:
            pass
        elif self.selected_tool == constants.TOOL_BUY_FENCE:
            self.buy_fence(self.tv.screen_to_tile(e.pos))
        elif buildings.is_building(self.selected_tool):
            building_cls = self.selected_tool
            tile_pos = self.tv.screen_to_tile(e.pos)
            building = building_cls(tile_pos)
            self.buy_building(building)

    def get_chicken(self, pos):
        for chick in self.chickens:
            if chick.rect.collidepoint(pos):
                return chick
        return None

    def sell_chicken(self, pos):
        chick = self.get_chicken(pos)
        if chick is None:
            return
        if len(self.chickens) == 1:
            print "You can't sell your last chicken!"
            return
        self.add_cash(constants.SELL_PRICE_CHICKEN)
        self.remove_chicken(chick)

    def buy_fence(self, tile_pos):
        if self.tv.get(tile_pos) != tiles.REVERSE_TILE_MAP['grassland']:
            return
        if self.cash < constants.BUY_PRICE_FENCE:
            print "You can't afford a fence."
            return
        self.add_cash(-constants.BUY_PRICE_FENCE)
        self.tv.set(tile_pos, tiles.REVERSE_TILE_MAP['fence'])

    def buy_building(self, building):
        if self.cash < building.buy_price():
            return
        if building.place(self.tv):
            self.add_cash(-building.buy_price())
            self.add_building(building)

    def event(self, e):
        if e.type == KEYDOWN:
            if e.key == K_UP:
                self.tvw.move_view(0, -self.TILE_DIMENSIONS[1])
            if e.key == K_DOWN:
                self.tvw.move_view(0, self.TILE_DIMENSIONS[1])
            if e.key == K_LEFT:
                self.tvw.move_view(-self.TILE_DIMENSIONS[0], 0)
            if e.key == K_RIGHT:
                self.tvw.move_view(self.TILE_DIMENSIONS[0], 0)
        else:
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

    def add_building(self, building):
        self.buildings.append(building)
        self.tv.sprites.append(building)

    def remove_fox(self, fox):
        if fox in self.foxes:
            self.foxes.remove(fox)
            self.tv.sprites.remove(fox)

    def remove_chicken(self, chick):
        if chick in self.chickens:
            self.chickens.remove(chick)
            self.tv.sprites.remove(chick)

    def add_cash(self, amount):
        self.cash += amount
        self.toolbar.update_cash_counter(self.cash)
