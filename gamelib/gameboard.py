import random

import pygame
from pygame.locals import MOUSEBUTTONDOWN, MOUSEMOTION, KEYDOWN, K_UP, K_DOWN, K_LEFT, K_RIGHT
from pgu import gui

import data
import tiles
import icons
import constants
import buildings
import animal
import equipment
import sound
import cursors
import sprite_cursor

class OpaqueLabel(gui.Label):
    def __init__(self, value, **params):
        gui.Label.__init__(self, value, **params)
        if 'width' in params:
            self._width = params['width']
        if 'height' in params:
            self._height = params['height']
        self._set_size()

    def _set_size(self):
        width, height = self.font.size(self.value)
        width = getattr(self, '_width', width)
        height = getattr(self, '_height', height)
        self.style.width, self.style.height = width, height

    def paint(self, s):
        s.fill(self.style.background)
        if self.style.align > 0:
            r = s.get_rect()
            w, _ = self.font.size(self.value)
            s = s.subsurface(r.move((r.w-w, 0)).clip(r))
        gui.Label.paint(self, s)

    def update_value(self, value):
        self.value = value
        self._set_size()
        self.repaint()

def mklabel(text="", **params):
    params.setdefault('color', constants.FG_COLOR)
    params.setdefault('width', GameBoard.TOOLBAR_WIDTH/2)
    return OpaqueLabel(text, **params)

def mkcountupdate(counter):
    def update_counter(self, value):
        getattr(self, counter).update_value("%s  " % value)
        self.repaint()
    return update_counter

class ToolBar(gui.Table):
    def __init__(self, gameboard, **params):
        gui.Table.__init__(self, **params)
        self.gameboard = gameboard
        self.cash_counter = mklabel(align=1)
        self.chicken_counter = mklabel(align=1)
        self.egg_counter = mklabel(align=1)
        self.day_counter = mklabel(align=1)
        self.killed_foxes = mklabel(align=1)

        self.tr()
        self.td(gui.Spacer(self.rect.w/2, 0))
        self.td(gui.Spacer(self.rect.w/2, 0))
        self.add_counter(mklabel("Day:"), self.day_counter)
        self.add_counter(mklabel("Groats:"), self.cash_counter)
        self.add_counter(mklabel("Eggs:"), self.egg_counter)
        self.add_counter(icons.CHKN_ICON, self.chicken_counter)
        self.add_counter(icons.KILLED_FOX, self.killed_foxes)
        self.add_spacer(20)

        self.add_tool_button("Move Hen", constants.TOOL_PLACE_ANIMALS,
                cursors.cursors['select'])
        self.add_tool_button("Cut Trees", constants.TOOL_LOGGING)
        self.add_spacer(20)

        self.add_heading("Sell ...")
        self.add_tool_button("Chicken", constants.TOOL_SELL_CHICKEN,
                cursors.cursors['select'])
        self.add_tool_button("Egg", constants.TOOL_SELL_EGG,
                cursors.cursors['select'])
        self.add_tool_button("Building", constants.TOOL_SELL_BUILDING,
                cursors.cursors['select'])
        self.add_tool_button("Equipment", constants.TOOL_SELL_EQUIPMENT)
        self.add_spacer(20)

        self.add_heading("Buy ...")
        self.add_tool_button("Fence", constants.TOOL_BUY_FENCE)
        for building_cls in buildings.BUILDINGS:
            self.add_tool_button(building_cls.NAME.title(), building_cls,
                    cursors.cursors.get('build', None))
        for equipment_cls in equipment.EQUIPMENT:
            self.add_tool_button(equipment_cls.NAME.title(), equipment_cls,
                    cursors.cursors.get(equipment_cls.NAME, None))
        self.add_spacer(30)

        self.add_button("Finished Day", self.day_done)

    def day_done(self):
        import engine
        pygame.event.post(engine.START_NIGHT)

    update_cash_counter = mkcountupdate('cash_counter')
    update_fox_counter = mkcountupdate('killed_foxes')
    update_chicken_counter = mkcountupdate('chicken_counter')
    update_egg_counter = mkcountupdate('egg_counter')
    update_day_counter = mkcountupdate('day_counter')

    def add_spacer(self, height):
        self.tr()
        self.td(gui.Spacer(0, height), colspan=2)

    def add_heading(self, text):
        self.tr()
        self.td(mklabel(text), colspan=2)

    def add_tool_button(self, text, tool, cursor=None):
        self.add_button(text, lambda: self.gameboard.set_selected_tool(tool,
            cursor))

    def add_button(self, text, func):
        button = gui.Button(text, width=self.rect.w, style={"padding_left": 0})
        button.connect(gui.CLICK, func)
        self.tr()
        self.td(button, align=-1, colspan=2)

    def add_counter(self, icon, label):
        self.tr()
        self.td(icon, width=self.rect.w/2)
        self.td(label, width=self.rect.w/2)

    def resize(self, width=None, height=None):
        width, height = gui.Table.resize(self, width, height)
        width = GameBoard.TOOLBAR_WIDTH
        return width, height


class VidWidget(gui.Widget):
    def __init__(self, gameboard, vid, **params):
        gui.Widget.__init__(self, **params)
        self.gameboard = gameboard
        self.vid = vid
        self.vid.bounds = pygame.Rect((0, 0), vid.tile_to_view(vid.size))

    def paint(self, surface):
        self.vid.paint(surface)

    def update(self, surface):
        return self.vid.update(surface)

    def move_view(self, x, y):
        self.vid.view.move_ip((x, y))

    def event(self, e):
        if e.type == MOUSEBUTTONDOWN:
            self.gameboard.use_tool(e)
        elif e.type == MOUSEMOTION and self.gameboard.sprite_cursor:
            self.gameboard.update_sprite_cursor(e)


class GameBoard(object):
    TILE_DIMENSIONS = (20, 20)
    TOOLBAR_WIDTH = 140

    GRASSLAND = tiles.REVERSE_TILE_MAP['grassland']
    FENCE = tiles.REVERSE_TILE_MAP['fence']
    WOODLAND = tiles.REVERSE_TILE_MAP['woodland']
    BROKEN_FENCE = tiles.REVERSE_TILE_MAP['broken fence']

    def __init__(self, main_app):
        self.disp = main_app
        self.tv = tiles.FarmVid()
        self.tv.tga_load_tiles(data.filepath('tiles.tga'), self.TILE_DIMENSIONS)
        self.tv.png_folder_load_tiles(data.filepath('tiles'))
        self.tv.tga_load_level(data.filepath('level1.tga'))
        self.create_display()

        self.selected_tool = None
        self.animal_to_place = None
        self.sprite_cursor = None
        self.chickens = set()
        self.foxes = set()
        self.buildings = []
        self.cash = 0
        self.eggs = 0
        self.days = 0
        self.killed_foxes = 0
        self.add_cash(constants.STARTING_CASH)

        self.fix_buildings()

        self.add_some_chickens()

    def get_top_widget(self):
        return self.top_widget

    def create_display(self):
        width, height = self.disp.rect.w, self.disp.rect.h
        tbl = gui.Table()
        tbl.tr()
        self.toolbar = ToolBar(self, width=self.TOOLBAR_WIDTH)
        tbl.td(self.toolbar, valign=-1)
        self.tvw = VidWidget(self, self.tv, width=width-self.TOOLBAR_WIDTH, height=height)
        tbl.td(self.tvw)
        self.top_widget = tbl

    def update(self):
        self.tvw.reupdate()

    def loop(self):
        self.tv.loop()

    def set_selected_tool(self, tool, cursor):
        self.selected_tool = tool
        self.animal_to_place = None
        if cursor:
            pygame.mouse.set_cursor(*cursor)
        else:
            pygame.mouse.set_cursor(*cursors.cursors['arrow'])
        if self.sprite_cursor:
            self.tv.sprites.remove(self.sprite_cursor)
            self.sprite_cursor = None
        if buildings.is_building(tool):
            self.sprite_cursor = sprite_cursor.SpriteCursor(tool.IMAGE, self.tv)
            self.tv.sprites.append(self.sprite_cursor)

    def reset_cursor(self):
        pygame.mouse.set_cursor(*cursors.cursors['arrow'])

    def update_sprite_cursor(self, e):
        tile_pos = self.tv.screen_to_tile(e.pos)
        self.sprite_cursor.set_pos(tile_pos)

    def in_bounds(self, pos):
        """Check if a position is within the game boundaries"""
        if pos.x < 0 or pos.y < 0:
            return False
        width, height = self.tv.size
        if pos.x >= width or pos.y >= height:
            return False
        return True

    def use_tool(self, e):
        if e.button == 3: # Right button
            self.selected_tool = None
            self.reset_cursor()
        elif e.button != 1: # Left button
            return
        if self.selected_tool == constants.TOOL_SELL_CHICKEN:
            self.sell_chicken(self.tv.screen_to_tile(e.pos))
        elif self.selected_tool == constants.TOOL_SELL_EGG:
            pass
        elif self.selected_tool == constants.TOOL_PLACE_ANIMALS:
            self.place_animal(self.tv.screen_to_tile(e.pos))
        elif self.selected_tool == constants.TOOL_BUY_FENCE:
            self.buy_fence(self.tv.screen_to_tile(e.pos))
        elif self.selected_tool == constants.TOOL_SELL_BUILDING:
            self.sell_building(self.tv.screen_to_tile(e.pos))
        elif self.selected_tool == constants.TOOL_SELL_EQUIPMENT:
            self.sell_equipment(self.tv.screen_to_tile(e.pos))
        elif self.selected_tool == constants.TOOL_LOGGING:
            self.logging_forest(self.tv.screen_to_tile(e.pos))
        elif buildings.is_building(self.selected_tool):
            self.buy_building(self.tv.screen_to_tile(e.pos), self.selected_tool)
        elif equipment.is_equipment(self.selected_tool):
            self.buy_equipment(self.tv.screen_to_tile(e.pos), self.selected_tool)

    def get_outside_chicken(self, tile_pos):
        for chick in self.chickens:
            if chick.covers(tile_pos) and chick.outside():
                return chick
        return None

    def get_building(self, tile_pos):
        for building in self.buildings:
            if building.covers(tile_pos):
                return building
        return None

    def sell_chicken(self, tile_pos):
        chick = self.get_outside_chicken(tile_pos)
        if chick is None:
            return
        if len(self.chickens) == 1:
            print "You can't sell your last chicken!"
            return
        self.add_cash(constants.SELL_PRICE_CHICKEN)
        sound.play_sound("sell-chicken.ogg")
        self.remove_chicken(chick)

    def place_animal(self, tile_pos):
        """Handle an TOOL_PLACE_ANIMALS click.

           This will either select an animal or
           place a selected animal in a building.
           """
        chicken = self.get_outside_chicken(tile_pos)
        if chicken:
            if chicken is self.animal_to_place:
                self.animal_to_place = None
                pygame.mouse.set_cursor(*cursors.cursors['select'])
            else:
                self.animal_to_place = chicken
                pygame.mouse.set_cursor(*cursors.cursors['chicken'])
            return
        building = self.get_building(tile_pos)
        if building:
            self.open_building_dialog(building)
            return
        if self.tv.get(tile_pos) == self.GRASSLAND:
            if self.animal_to_place is not None:
                occupant = self.animal_to_place
                if occupant.abode is not None:
                    occupant.abode.clear_occupant()
                occupant.set_pos(tile_pos)
                self.set_visibility(occupant)

    def set_visibility(self, chicken):
        if chicken.outside():
            if chicken not in self.tv.sprites:
                self.tv.sprites.append(chicken)
        else:
            if chicken in self.tv.sprites:
                self.tv.sprites.remove(chicken)

    def open_dialog(self, widget, close_callback=None):
        """Open a dialog for the given widget. Add close button."""
        tbl = gui.Table()

        def close_dialog():
            self.disp.close(tbl)
            if close_callback is not None:
                close_callback()

        close_button = gui.Button("Close")
        close_button.connect(gui.CLICK, close_dialog)

        tbl = gui.Table()
        tbl.tr()
        tbl.td(widget, colspan=2)
        tbl.tr()
        tbl.td(gui.Spacer(100, 0))
        tbl.td(close_button, align=1)

        self.disp.open(tbl)
        return tbl

    def open_building_dialog(self, building):
        """Create dialog for manipulating the contents of a building."""
        def select_occupant(place, button):
            """Select occupant in place."""
            self.animal_to_place = place.occupant
            pygame.mouse.set_cursor(*cursors.cursors['chicken'])

        def set_occupant(place, button):
            """Set occupant of a given place."""
            if self.animal_to_place is not None:
                button.value = icons.CHKN_NEST_ICON
                button.disconnect(gui.CLICK, set_occupant)
                button.connect(gui.CLICK, select_occupant, place, button)

                old_abode = self.animal_to_place.abode
                if old_abode is not None:
                    old_abode.clear_occupant()
                if id(old_abode) in place_button_map:
                    old_button = place_button_map[id(old_abode)]
                    old_button.value = icons.EMPTY_NEST_ICON
                    old_button.disconnect(gui.CLICK, select_occupant)
                    old_button.connect(gui.CLICK, set_occupant, place, button)

                chicken = self.animal_to_place
                place.set_occupant(chicken)
                chicken.set_pos(place.get_pos())
                self.set_visibility(self.animal_to_place)

        place_button_map = {}

        tbl = gui.Table()
        columns = building.max_floor_width()
        kwargs = { 'style': { 'padding_left': 10, 'padding_bottom': 10 }}
        for floor in building.floors():
            tbl.tr()
            tbl.td(gui.Button(floor.title), colspan=columns, align=-1, **kwargs)
            tbl.tr()
            for row in floor.rows():
                tbl.tr()
                for place in row:
                    if place.occupant is None:
                        button = gui.Button(icons.EMPTY_NEST_ICON)
                        button.connect(gui.CLICK, set_occupant, place, button)
                    else:
                        button = gui.Button(icons.CHKN_NEST_ICON)
                        button.connect(gui.CLICK, select_occupant, place, button)
                    place_button_map[id(place)] = button
                    tbl.td(button, **kwargs)

        building.selected(True)
        def close_callback():
            building.selected(False)

        self.open_dialog(tbl, close_callback=close_callback)

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

    def logging_forest(self, tile_pos):
        if self.tv.get(tile_pos) != self.WOODLAND:
            return
        if self.cash < constants.LOGGING_PRICE:
            return
        self.add_cash(-constants.LOGGING_PRICE)
        self.tv.set(tile_pos, self.GRASSLAND)

    def buy_building(self, tile_pos, building_cls):
        building = building_cls(tile_pos)
        if self.cash < building.buy_price():
            return
        if building.place(self.tv):
            self.add_cash(-building.buy_price())
            self.add_building(building)

    def buy_equipment(self, tile_pos, equipment_cls):
        chicken = self.get_outside_chicken(tile_pos)
        equipment = equipment_cls()
        if chicken is None or self.cash < equipment.buy_price():
            return
        if equipment.place(chicken):
            self.add_cash(-equipment.buy_price())
            chicken.equip(equipment)

    def sell_building(self, tile_pos):
        if self.tv.get(tile_pos) == self.FENCE:
            return self.sell_fence(tile_pos)
        building = self.get_building(tile_pos)
        if building is None:
            return
        if list(building.occupants()):
            warning = gui.Button("Occupied buildings may not be sold.")
            self.open_dialog(warning)
            return
        self.add_cash(building.sell_price())
        building.remove(self.tv)
        self.remove_building(building)

    def sell_equipment(self, tile_pos):
        chicken = self.get_outside_chicken(tile_pos)
        if chicken is None or not chicken.equipment:
            return
        if len(chicken.equipment) == 1:
            item = chicken.equipment[0]
            self.add_cash(item.sell_price())
            chicken.unequip(item)
        else:
            self.open_equipment_dialog(chicken)

    def open_equipment_dialog(self, chicken):
        tbl = gui.Table()

        def sell_item(item, button):
            """Select item of equipment."""
            self.add_cash(item.sell_price())
            chicken.unequip(item)
            self.disp.close(dialog)

        kwargs = { 'style': { 'padding_left': 10, 'padding_bottom': 10 }}

        tbl.tr()
        tbl.td(gui.Button("Sell ...     "), align=-1, **kwargs)

        for item in chicken.equipment:
            tbl.tr()
            button = gui.Button(item.name().title())
            button.connect(gui.CLICK, sell_item, item, button)
            tbl.td(button, align=1, **kwargs)

        dialog = self.open_dialog(tbl)

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

    def advance_day(self):
        self.days += 1
        self.toolbar.update_day_counter(self.days)

    def clear_foxes(self):
        for fox in self.foxes.copy():
            # Any foxes that didn't make it to the woods are automatically
            # killed
            if self.in_bounds(fox.pos) and self.tv.get(fox.pos.to_tuple()) \
                    != self.WOODLAND:
                self.kill_fox(fox)
            else:
                self.tv.sprites.remove(fox)
        self.foxes = set() # Remove all the foxes

    def move_foxes(self):
        """Move the foxes.
        
           We return True if there are no more foxes to move or all the
           foxes are safely back. This end's the night"""
        if not self.foxes:
            return True
        over = True
        for fox in self.foxes:
            fox.move(self)
            if not fox.safe:
                over = False
        for chicken in self.chickens:
            chicken.attack(self)
        return over

    def add_chicken(self, chicken):
        self.chickens.add(chicken)
        if chicken.outside():
            self.tv.sprites.append(chicken)
        self.toolbar.update_chicken_counter(len(self.chickens))

    def add_fox(self, fox):
        self.foxes.add(fox)
        self.tv.sprites.append(fox)

    def add_building(self, building):
        self.buildings.append(building)
        self.tv.sprites.append(building)

    def lay_eggs(self):
        self.eggs = 0
        for building in self.buildings:
            if building.NAME in buildings.HENHOUSES:
                for chicken in building.occupants():
                    chicken.lay()
                    if chicken.egg:
                        self.eggs += 1
        self.toolbar.update_egg_counter(self.eggs)

    def hatch_eggs(self):
        for building in self.buildings:
            if building.NAME in buildings.HENHOUSES:
                for chicken in building.occupants():
                    new_chick = chicken.hatch()
                    if new_chick:
                        self.eggs -= 1
                        try:
                            building.add_occupant(new_chick)
                            self.add_chicken(new_chick)
                        except buildings.BuildingFullError:
                            print "Building full."
        self.toolbar.update_egg_counter(self.eggs)

    def kill_fox(self, fox):
        if fox in self.foxes:
            if not fox.survive_damage():
                self.killed_foxes += 1
                self.toolbar.update_fox_counter(self.killed_foxes)
                self.add_cash(constants.SELL_PRICE_DEAD_FOX)
                self.remove_fox(fox)

    def remove_fox(self, fox):
        self.foxes.discard(fox)
        if fox in self.tv.sprites:
            self.tv.sprites.remove(fox)

    def remove_chicken(self, chick):
        self.chickens.discard(chick)
        if chick.egg:
            self.eggs -= 1
            self.toolbar.update_egg_counter(self.eggs)
        if chick.abode:
            chick.abode.clear_occupant()
        self.toolbar.update_chicken_counter(len(self.chickens))
        if chick in self.tv.sprites and chick.outside():
            self.tv.sprites.remove(chick)

    def remove_building(self, building):
        if building in self.buildings:
            self.buildings.remove(building)
            self.tv.sprites.remove(building)

    def add_cash(self, amount):
        self.cash += amount
        self.toolbar.update_cash_counter(self.cash)

    def add_some_chickens(self):
        """Add some random chickens to start the game"""
        x, y = 0, 0
        width, height = self.tv.size
        while len(self.chickens) < 10:
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
                roll = random.randint(0, 10)
                if roll < 8:
                    fox = animal.Fox((x, y))
                elif roll < 9:
                    fox = animal.NinjaFox((x, y))
                else:
                    fox = animal.GreedyFox((x, y))
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

    def is_game_over(self):
        """Return true if we're complete"""
        if self.days > constants.TURN_LIMIT:
            return True
        if len(self.chickens) == 0:
            return True
