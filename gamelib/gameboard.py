import random

import pygame
from pygame.locals import MOUSEBUTTONDOWN, KEYDOWN, K_UP, K_DOWN, K_LEFT, K_RIGHT
from pgu import gui

import data
import tiles
import icons
import constants
import buildings
import animal

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
        self.chicken_counter = OpaqueLabel("         ", color=constants.FG_COLOR)
        self.killed_foxes = OpaqueLabel("         ", color=constants.FG_COLOR)
        self.tr()
        self.add(self.cash_counter)
        self.tr()
        self.td(icons.CHKN_ICON, align=-1)
        self.add(self.chicken_counter)
        self.tr()
        self.td(icons.KILLED_FOX, align=-1)
        self.add(self.killed_foxes)
        self.add_tool_button("Sell chicken", constants.TOOL_SELL_CHICKEN)
        self.add_tool_button("Sell egg", constants.TOOL_SELL_EGG)
        self.add_tool_button("Sell building", constants.TOOL_SELL_BUILDING)
        self.add_tool_button("Buy fence", constants.TOOL_BUY_FENCE)
        for building_cls in buildings.BUILDINGS:
            self.add_tool_button("Buy %s" % (building_cls.NAME,), building_cls)

        day_done_button = gui.Button("Finished Day")
        day_done_button.connect(gui.CLICK, self.day_done)
        self.tr()
        self.td(day_done_button, style={"padding_top": 30})

    def day_done(self):
        import engine
        pygame.event.post(engine.START_NIGHT)

    def update_cash_counter(self, amount):
        self.cash_counter.update_value("Groats: %s" % amount)
        self.repaint()

    def update_chicken_counter(self, number):
        self.chicken_counter.update_value("  %s" % number)
        self.repaint()

    def update_fox_counter(self, number):
        self.killed_foxes.update_value("  %s" % number)
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

    GRASSLAND = tiles.REVERSE_TILE_MAP['grassland']
    FENCE = tiles.REVERSE_TILE_MAP['fence']
    WOODLAND = tiles.REVERSE_TILE_MAP['woodland']
    BROKEN_FENCE = tiles.REVERSE_TILE_MAP['broken fence']

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
        self.killed_foxes = 0
        self.add_cash(constants.STARTING_CASH)

        self.fix_buildings()

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

    def in_bounds(self, pos):
        """Check if a position is within the game boundaries"""
        if pos.x < 0 or pos.y < 0:
            return False
        width, height = self.tv.size
        if pos.x >= width or pos.y >= height:
            return False
        return True

    def use_tool(self, e):
        if self.selected_tool == constants.TOOL_SELL_CHICKEN:
            self.sell_chicken(e.pos)
        elif self.selected_tool == constants.TOOL_SELL_EGG:
            pass
        elif self.selected_tool == constants.TOOL_BUY_FENCE:
            self.buy_fence(self.tv.screen_to_tile(e.pos))
        elif self.selected_tool == constants.TOOL_SELL_BUILDING:
            self.sell_building(self.tv.screen_to_tile(e.pos))
        elif buildings.is_building(self.selected_tool):
            self.buy_building(self.tv.screen_to_tile(e.pos), self.selected_tool)

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
        this_tile = self.tv.get(tile_pos)
        if this_tile not in [self.GRASSLAND, self.BROKEN_FENCE]:
            return
        if this_tile == self.GRASSLAND:
            cost = constants.BUY_PRICE_FENCE
        else:
            cost = constants.REPAIR_PRICE_FENCE
        if self.cash < cost:
            print "You can't afford a fence."
            return
        self.add_cash(-cost)
        self.tv.set(tile_pos, self.FENCE)

    def sell_fence(self, tile_pos):
        if self.tv.get(tile_pos) != self.FENCE:
            return
        self.add_cash(constants.SELL_PRICE_FENCE)
        self.tv.set(tile_pos, self.GRASSLAND)

    def buy_building(self, tile_pos, building_cls):
        building = building_cls(tile_pos)
        if self.cash < building.buy_price():
            return
        if building.place(self.tv):
            self.add_cash(-building.buy_price())
            self.add_building(building)

    def sell_building(self, tile_pos):
        if self.tv.get(tile_pos) == self.FENCE:
            return self.sell_fence(tile_pos)
        for building in self.buildings:
            if building.covers(tile_pos):
                self.add_cash(building.sell_price())
                building.remove(self.tv)
                self.remove_building(building)
                break

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
            # Any foxes that didn't make it to the woods are automatically
            # killed
            if self.in_bounds(fox.pos) and self.tv.get(fox.pos.to_tuple()) \
                    != self.WOODLAND:
                self.killed_foxes += 1
                self.toolbar.update_fox_counter(self.killed_foxes)
                self.add_cash(constants.SELL_PRICE_DEAD_FOX)
        self.foxes = [] # Remove all the foxes

    def move_foxes(self):
        for fox in self.foxes:
            fox.move(self)

    def add_chicken(self, chicken):
        self.chickens.append(chicken)
        self.tv.sprites.append(chicken)
        self.toolbar.update_chicken_counter(len(self.chickens))

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
            self.toolbar.update_chicken_counter(len(self.chickens))

    def remove_building(self, building):
        if building in self.buildings:
            self.buildings.remove(building)
            self.tv.sprites.remove(building)

    def add_cash(self, amount):
        self.cash += amount
        self.toolbar.update_cash_counter(self.cash)

    def update_chickens(self):
        """Update the chickens state at the start of the new day"""
        # Currently random chickens appear
        # Very simple, we walk around the tilemap, and, for each farm tile,
        # we randomly add a chicken (1 in 10 chance) until we have 5 chickens
        # or we run out of board
        x, y = 0, 0
        width, height = self.tv.size
        while len(self.chickens) < 5:
            if x < width:
                tile = self.tv.get((x, y))
            else:
                y += 1
                if y >= height:
                    break
                x = 0
                continue
            # See if we place a chicken
            if 'grassland' == tiles.TILE_MAP[tile]:
                # Farmland
                roll = random.randint(1, 20)
                # We don't place within a tile of the fence, this is to make things
                # easier
                for xx in range(x-1, x+2):
                    if xx >= width or xx < 0:
                        continue
                    for yy in range(y-1, y+2):
                        if yy >= height or yy < 0:
                            continue
                        neighbour = self.tv.get((xx, yy))
                        if 'fence' == tiles.TILE_MAP[neighbour]:
                            # Fence
                            roll = 10
                if roll == 1:
                    # Create a chicken
                    chick = animal.Chicken((x, y))
                    self.add_chicken(chick)
            x += 1

    def spawn_foxes(self):
        """The foxes come at night, and this is where they come from."""
        # Foxes spawn just outside the map
        x, y = 0, 0
        width, height = self.tv.size
        new_foxes = random.randint(3, 7)
        while len(self.foxes) < new_foxes:
            side = random.randint(0, 3)
            if side == 0:
                # top
                y = -1
                x = random.randint(-1, width)
            elif side == 1:
                # bottom
                y = height
                x = random.randint(-1, width)
            elif side == 2:
                # left
                x = -1
                y = random.randint(-1, height)
            else:
                x = width
                y = random.randint(-1, height)
            skip = False
            for other_fox in self.foxes:
                if other_fox.pos.x == x and other_fox.pos.y == y:
                    skip = True # Choose a new position
                    break
            if not skip:
                fox = animal.Fox((x, y))
                self.add_fox(fox)

    def fix_buildings(self):
        """Go through the level map looking for buildings that haven't
           been added to self.buildings and adding them.

           Where partial buildings exist (i.e. places where the building
           cannot fit on the available tiles) the building is added anyway
           to the top left corner.

           Could be a lot faster.
           """
        tile_to_building = dict((b.TILE_NO, b) for b in buildings.BUILDINGS)

        w, h = self.tv.size
        for x in xrange(w):
            for y in xrange(h):
                tile_pos = (x, y)
                tile_no = self.tv.get(tile_pos)
                if tile_no not in tile_to_building:
                    continue

                covered = False
                for building in self.buildings:
                    if building.covers(tile_pos):
                        covered = True
                        break

                if covered:
                    continue

                building_cls = tile_to_building[tile_no]
                building = building_cls(tile_pos)
                building.remove(self.tv)
                building.place(self.tv)
                self.add_building(building)
