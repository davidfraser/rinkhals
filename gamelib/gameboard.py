import random

import pygame
from pygame.locals import MOUSEBUTTONDOWN, MOUSEMOTION, KEYDOWN, K_UP, K_DOWN, \
        K_LEFT, K_RIGHT, KMOD_SHIFT, K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, \
        K_8, K_9, K_ESCAPE, K_n, K_d, KMOD_CTRL, KMOD_ALT, KEYUP
from pgu import gui

import tiles
import icons
import constants
import buildings
import animal
import equipment
import sound
import cursors
import sprite_cursor
import misc
import toolbar
import serializer
import savegame

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
        elif e.type == gui.ENTER:
            self.gameboard.set_tool_cursor()
        elif e.type == gui.EXIT:
            self.gameboard.set_menu_cursor()
        else:
            return False


class AnimalPositionCache(object):
    def __init__(self, gameboard):
        self.gameboard = gameboard
        self.clear()

    def clear(self):
        self._cache = {'chicken': {}, 'fox': {}}

    def _in_bounds(self, pos):
        return self.gameboard.in_bounds(pos)

    def add(self, animal, animal_type):
        if animal and self._in_bounds(animal.pos):
            self._cache[animal_type][animal.pos] = animal

    def remove(self, pos, animal_type):
        if pos in self._cache[animal_type]:
            del self._cache[animal_type][pos]

    def update(self, old_pos, animal, animal_type):
        self.remove(old_pos, animal_type)
        self.add(animal, animal_type)

    def get(self, pos, animal_type):
        return self._cache[animal_type].get(pos, None)


class GameBoard(serializer.Simplifiable):

    GRASSLAND = tiles.REVERSE_TILE_MAP['grassland']
    FENCE = tiles.REVERSE_TILE_MAP['fence']
    BROKEN_FENCE = tiles.REVERSE_TILE_MAP['broken fence']

    SIMPLIFY = [
        'level',
        'tv',
        'max_foxes',
        #'selected_tool',
        #'sprite_cursor',
        'selected_chickens',
        'stored_selections',
        'chickens',
        'foxes',
        'buildings',
        #'_pos_cache',
        'cash',
        'wood',
        'eggs',
        'days',
        'killed_foxes',
        'day', 'night',
    ]

    def __init__(self, main_app, level):
        self.disp = main_app
        self.level = level
        self.tv = tiles.FarmVid()
        self.tv.png_folder_load_tiles('tiles')
        self.tv.tga_load_level(level.map)
        width, height = self.tv.size
        # Ensure we don't every try to create more foxes then is sane
        self.max_foxes = level.max_foxes
        self.calculate_wood_groat_exchange_rate()

        self.selected_tool = None
        self.sprite_cursor = None
        self.selected_chickens = []
        self.stored_selections = {}
        self.chickens = set()
        self.foxes = set()
        self.buildings = set()
        self._pos_cache = AnimalPositionCache(self)
        self.cash = 0
        self.wood = 0
        self.eggs = 0
        self.days = 0
        self.killed_foxes = 0
        self.day, self.night = True, False
        # For the level loading case
        if self.disp:
            self.toolbar = None
            self.create_display()
            self.add_cash(level.starting_cash)
            self.add_wood(level.starting_wood)

        self.fix_buildings()

        cdata = {}
        for tn in equipment.EQUIP_MAP:
            cdata[tn]  = (self.add_start_chickens, tn)

        self.tv.run_codes(cdata, (0,0,width,height))

    @classmethod
    def unsimplify(cls, *args, **kwargs):
        """Override default Simplifiable unsimplification."""
        obj = super(GameBoard, cls).unsimplify(*args, **kwargs)

        obj.tv.png_folder_load_tiles('tiles')
        obj.calculate_wood_groat_exchange_rate()

        obj._pos_cache = AnimalPositionCache(obj)
        obj._cache_animal_positions()

        obj.sprite_cursor = None
        obj.set_selected_tool(None, None)

        obj.disp = None

        # put chickens, foxes and buildings into sprite list

        existing_chickens = obj.chickens
        obj.chickens = set()
        for chicken in existing_chickens:
            obj.add_chicken(chicken)

        existing_foxes = obj.foxes
        obj.foxes = set()
        for fox in existing_foxes:
            obj.add_fox(fox)

        existing_buildings = obj.buildings
        obj.buildings = set()
        for building in existing_buildings:
            obj.add_building(building)

        # self.disp is not set properly here
        # whoever unsimplifies the gameboard needs to arrange for it to be
        # set and then call .create_display() and so create:
        #  - .toolbar
        #  - .tvw
        #  - .top_widget

        return obj

    def get_top_widget(self):
        return self.top_widget

    def create_display(self):
        width, height = self.disp.rect.w, self.disp.rect.h
        tbl = gui.Table()
        tbl.tr()
        self.toolbar = toolbar.DefaultToolBar(self, width=constants.TOOLBAR_WIDTH)
        tbl.td(self.toolbar, valign=-1)
        self.tvw = VidWidget(self, self.tv, width=width-constants.TOOLBAR_WIDTH, height=height)
        tbl.td(self.tvw)

        # we should probably create a custom widget to be the top widget
        # if we want to flow some events to the gameboard
        def event(e):
            if gui.Table.event(tbl, e):
                return True
            return self.event(e)
        tbl.event = event

        self.top_widget = tbl
        self.redraw_counters()

    def change_toolbar(self, new_toolbar):
        """Replace the toolbar"""
        td = self.toolbar.container
        td.remove(self.toolbar)
        td.add(new_toolbar, 0, 0)
        self.toolbar = new_toolbar
        self.toolbar.rect.size = self.toolbar.resize()
        self.redraw_counters()
        td.repaint()

        if new_toolbar.MOVE_SELECT_PERMITTED:
            if self.selected_tool not in [constants.TOOL_SELECT_CHICKENS, constants.TOOL_PLACE_ANIMALS]:
                self.set_selected_tool(None, None)
        else:
            self.set_selected_tool(None, None)
            self.unselect_all()

    def redraw_counters(self):
        self.toolbar.update_egg_counter(self.eggs)
        if self.level.is_last_day(self.days):
            self.toolbar.day_counter.style.color = (255, 0, 0)
        else:
            # can come back from last day when restoring a saved game
            self.toolbar.day_counter.style.color = (255, 255, 255)
        self.toolbar.update_day_counter("%s/%s" % (self.days,
            self.level.get_max_turns()))
        self.toolbar.update_chicken_counter(len(self.chickens))
        self.toolbar.update_cash_counter(self.cash)
        self.toolbar.update_wood_counter(self.wood)
        self.toolbar.update_fox_counter(self.killed_foxes)

    def update(self):
        self.tvw.reupdate()

    def loop(self):
        self.tv.loop()

    def set_selected_tool(self, tool, cursor):
        if not self.day:
            return False
        if tool is None:
            tool = constants.TOOL_SELECT_CHICKENS
            cursor = cursors.cursors['select']
        if self.apply_tool_to_selected(tool):
            return False # Using the tool on selected chickens is immediate
        self.selected_tool = tool
        sprite_curs = None
        if buildings.is_building(tool):
            sprite_curs = sprite_cursor.SpriteCursor(tool.IMAGE, self.tv, tool.BUY_PRICE)
        elif equipment.is_equipment(tool):
            sprite_curs = sprite_cursor.SpriteCursor(tool.CHICKEN_IMAGE_FILE, self.tv)
        elif tool == constants.TOOL_PLACE_ANIMALS and self.selected_chickens:
            cursor = cursors.cursors['chicken']
        self.current_cursor = (cursor, sprite_curs)
        self.set_tool_cursor((cursor, sprite_curs))
        return True

    def set_tool_cursor(self, current_cursor=None):
        if current_cursor:
            self.current_cursor = current_cursor
        if pygame.mouse.get_pos()[0] >= constants.TOOLBAR_WIDTH:
            self.set_cursor(*self.current_cursor)

    def set_menu_cursor(self):
        self.set_cursor()

    def apply_tool_to_selected(self, tool):
        if self.selected_chickens:
            # dispatch call to selected chickens if appropriate
            if tool == constants.TOOL_SELL_CHICKEN:
                self.sell_chicken(None)
                return True
            elif tool == constants.TOOL_SELL_EGG:
                self.sell_egg(None)
                return True
            elif toolbar.SellToolBar.is_equip_tool(tool):
                equipment_cls = toolbar.SellToolBar.get_equip_cls(tool)
                self.sell_equipment(None, equipment_cls)
                return True
            elif equipment.is_equipment(tool):
                self.buy_equipment(None, tool)
                return True
        return False

    def set_cursor(self, cursor=None, sprite_curs=None):
        if cursor:
            pygame.mouse.set_cursor(*cursor)
        else:
            pygame.mouse.set_cursor(*cursors.cursors['arrow'])
        if self.sprite_cursor is not None:
            self.tv.sprites.remove(self.sprite_cursor, layer='cursor')
        self.sprite_cursor = sprite_curs
        if self.sprite_cursor is not None:
            self.tv.sprites.append(self.sprite_cursor, layer='cursor')

    def reset_states(self):
        """Clear current states (highlights, etc.)"""
        self.set_selected_tool(None, None)
        self.toolbar.clear_tool()

    def update_sprite_cursor(self, e):
        tile_pos = self.tv.screen_to_tile(e.pos)
        self.sprite_cursor.set_pos(tile_pos)

    def start_night(self):
        self.day, self.night = False, True
        self.tv.sun(False)
        self.reset_states()
        self.selected_tool = None
        self.current_cursor = (cursors.cursors['arrow'],)
        self.set_menu_cursor()
        self.unselect_all()
        self.toolbar.start_night()
        self.spawn_foxes()
        self.eggs = 0
        for chicken in self.chickens.copy():
            chicken.start_night()
        self.toolbar.update_egg_counter(self.eggs)
        self._cache_animal_positions()
        self.chickens_chop_wood()
        self.chickens_scatter()

    def start_day(self):
        if hasattr(self, '_skip_start_day'):
            del self._skip_start_day
            return
        self.day, self.night = True, False
        self.tv.sun(True)
        self.reset_states()
        self.toolbar.start_day()
        self._pos_cache.clear()
        self.advance_day()
        self.clear_foxes()
        for chicken in self.chickens.copy():
            chicken.start_day()
        self.redraw_counters()

    def skip_next_start_day(self):
        # used to skip the start of the day triggered after
        # reloading a save game
        self._skip_start_day = True

    def in_bounds(self, pos):
        """Check if a position is within the game boundaries"""
        if pos.x < 0 or pos.y < 0:
            return False
        width, height = self.tv.size
        if pos.x >= width or pos.y >= height:
            return False
        return True

    def use_tool(self, e):
        if not self.day:
            return
        if e.button == 3: # Right button
            if self.selected_tool == constants.TOOL_SELECT_CHICKENS:
                self.place_animal(self.tv.screen_to_tile(e.pos))
            return
        elif e.button == 2: # Middle button
            self.reset_states()
            self.unselect_all()
            return
        elif e.button != 1: # Left button
            return
        mods = pygame.key.get_mods()
        if self.selected_tool == constants.TOOL_SELL_CHICKEN:
            self.sell_chicken(self.tv.screen_to_tile(e.pos))
        elif self.selected_tool == constants.TOOL_SELL_EGG:
            self.sell_egg(self.tv.screen_to_tile(e.pos))
        elif self.selected_tool == constants.TOOL_PLACE_ANIMALS:
            self.place_animal(self.tv.screen_to_tile(e.pos))
            self.set_selected_tool(constants.TOOL_SELECT_CHICKENS, cursors.cursors["select"])
            self.toolbar.unhighlight_move_button()
        elif self.selected_tool == constants.TOOL_SELECT_CHICKENS:
            # ctrl moves current selection without having to select move tool
            if (mods & KMOD_CTRL):
                self.place_animal(self.tv.screen_to_tile(e.pos))
            else:
                if not (mods & KMOD_SHIFT):
                    self.unselect_all()
                self.select_chicken(self.tv.screen_to_tile(e.pos))
        elif self.selected_tool == constants.TOOL_SELL_BUILDING:
            self.sell_building(self.tv.screen_to_tile(e.pos))
        elif self.selected_tool == constants.TOOL_REPAIR_BUILDING:
            self.repair_building(self.tv.screen_to_tile(e.pos))
        elif buildings.is_building(self.selected_tool):
            self.buy_building(self.tv.screen_to_tile(e.pos), self.selected_tool)
        elif toolbar.SellToolBar.is_equip_tool(self.selected_tool):
            equipment_cls = toolbar.SellToolBar.get_equip_cls(self.selected_tool)
            self.sell_equipment(self.tv.screen_to_tile(e.pos), equipment_cls)
        elif equipment.is_equipment(self.selected_tool):
            if not self.selected_chickens:
                # old selection behaviour
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

        def do_sell(chicken, update_button=None):
            if not chicken:
                return False # sanity check
            if len(self.chickens) == 1:
                msg = "You can't sell your last chicken!"
                TextDialog("Squuaaawwwwwk!", msg).open()
                return False
            for item in list(chicken.equipment):
                self.add_cash(item.sell_price())
                chicken.unequip(item)
            self.add_cash(self.level.sell_price_chicken)
            sound.play_sound("sell-chicken.ogg")
            if update_button:
                update_button(chicken, empty=True)
            self.remove_chicken(chicken)
            return True

        if tile_pos:
            chick = self.get_outside_chicken(tile_pos)
            if chick is None:
                building = self.get_building(tile_pos)
                if building and building.HENHOUSE:
                    self.open_building_dialog(building, False, do_sell)
                return
            do_sell(chick)
        else:
            def sure(val):
                if val:
                    for chick in self.selected_chickens[:]:
                        do_sell(chick)
            if self._check_dangerous_sale():
                dialog = misc.CheckDialog(sure,
                        "These chickens have equipment or eggs. Do you want to sell?",
                        "Yes, Sell Them", "No, Don't Sell", None)
                self.disp.open(dialog)
            else:
                sure(1)

    def sell_one_egg(self, chicken):
        if chicken.eggs:
            self.add_cash(self.level.sell_price_egg)
            chicken.remove_one_egg()
            return True
        return False

    def remove_eggs(self, num):
        self.eggs -= num
        self.toolbar.update_egg_counter(self.eggs)

    def sell_egg(self, tile_pos):
        def do_sell(chicken, update_button=None):
            # We try sell and egg
            if self.sell_one_egg(chicken):
                sound.play_sound("sell-chicken.ogg")
                # Force toolbar update
                self.toolbar.chsize()
                if update_button:
                    update_button(chicken)
            return False

        if tile_pos:
            building = self.get_building(tile_pos)
            if building and building.HENHOUSE:
                self.open_building_dialog(building, False, do_sell)
        else:
            for chicken in self.selected_chickens:
                do_sell(chicken)

    def _check_dangerous_sale(self):
        # Dangerous sales are: selling chickens with equipment & selling
        # chickens with eggs
        for chick in self.selected_chickens:
            if chick.eggs or chick.weapons() or chick.armour():
                return True
        return False

    def _check_dangerous_move(self, building=None):
        # Dangerous move involves moving chickens WITH eggs out of their
        # current building
        for chick in self.selected_chickens:
            if chick.eggs and chick.abode and \
                    chick.abode.building is not building:
                return True
        return False # safe move

    def select_animal(self, animal):
        self.selected_chickens.append(animal)
        if animal.abode:
            animal.abode.building.update_occupant_count()
        animal.equip(equipment.Spotlight())

    def unselect_all(self):
        # Clear any highlights
        old_sel = self.selected_chickens
        self.selected_chickens = []
        for chick in old_sel:
            chick.unequip_by_name("Spotlight")
            if chick.abode:
                chick.abode.building.update_occupant_count()

    def unselect_animal(self, animal):
        if animal in self.selected_chickens:
            self.selected_chickens.remove(animal)
            animal.unequip_by_name("Spotlight")
            if animal.abode:
                animal.abode.building.update_occupant_count()

    def get_chicken_at_pos(self, tile_pos):
        chicken = self.get_outside_chicken(tile_pos)
        if chicken:
            return chicken
        building = self.get_building(tile_pos)
        if building and building.ABODE:
            self.open_building_dialog(building, True)

    def select_chicken(self, tile_pos):
        """Handle a select chicken event"""
        # Get the chicken at this position
        chicken = self.get_chicken_at_pos(tile_pos)
        if not chicken:
            return # do nothing
        elif chicken in self.selected_chickens:
            self.unselect_animal(chicken)
        else:
            self.select_animal(chicken)

    def _do_move_selected(self, building, tile_pos):
        """Internal helper function for place_animal"""
        if building and building.ABODE:
            for chicken in self.selected_chickens[:]:
                try:
                    place = building.first_empty_place()
                    self.relocate_animal(chicken, place=place)
                    chicken.equip(equipment.Nest())
                    self.unselect_animal(chicken)
                except buildings.BuildingFullError:
                    pass
            try:
                # if there's a space left, open the building
                building.first_empty_place()
                self.open_building_dialog(building, True)
            except buildings.BuildingFullError:
                pass
            if not self.selected_chickens:
                # if we placed all the chickens, switch to select cursor
                self.set_tool_cursor((cursors.cursors['select'],))
        elif self.tv.get(tile_pos) == self.GRASSLAND:
            for chicken in self.selected_chickens:
                try_pos = tile_pos
                cur_chick = self.get_outside_chicken(try_pos)
                if cur_chick == chicken:
                    continue
                if cur_chick:
                    try_pos = None
                    # find a free square nearby
                    diff_pos = misc.Position(*tile_pos)
                    poss = [diff_pos + misc.Position(x, y)
                            for x in range(-2, 3)
                            for y in range(-2, 3)
                            if (x, y) != (0, 0)]
                    poss.sort(key=lambda p: p.dist(diff_pos))
                    for cand in poss:
                        if not self.in_bounds(cand):
                            continue
                        if self.tv.get(cand.to_tile_tuple()) == self.GRASSLAND and \
                               not self.get_outside_chicken(cand.to_tile_tuple()):
                            try_pos = cand.to_tile_tuple()
                            break
                if try_pos:
                    chicken.unequip_by_name("Nest")
                    self.relocate_animal(chicken, tile_pos=try_pos)
                    chicken.remove_eggs()


    def place_animal(self, tile_pos):
        """Handle an TOOL_PLACE_ANIMALS click.

           This will either select an animal or
           place a selected animal in a building.
           """
        if tile_pos and not self.selected_chickens:
            # Old behaviour
            chicken = self.get_chicken_at_pos(tile_pos)
            if chicken:
                self.select_animal(chicken)
                self.set_tool_cursor((cursors.cursors['chicken'],))
                return
        elif tile_pos:
            building = self.get_building(tile_pos)
            def sure(val):
                if val:
                    self._do_move_selected(building, tile_pos)

            if self._check_dangerous_move(building):
                dialog = misc.CheckDialog(sure,
                        "These chickens have eggs. Do you want to move them?",
                        "Yes, Move Them", "No, Don't Move", None)
                self.disp.open(dialog)
            else:
                sure(1)

    def relocate_animal(self, chicken, tile_pos=None, place=None):
        assert((tile_pos, place) != (None, None))
        if chicken.abode is not None:
            chicken.abode.clear_occupant()
        if tile_pos:
            chicken.set_pos(tile_pos)
        else:
            place.set_occupant(chicken)
            chicken.set_pos(place.get_pos())
        self.set_visibility(chicken)

    def set_visibility(self, animal):
        if animal.outside():
            if animal not in self.tv.sprites:
                self.tv.sprites.append(animal)
        else:
            if animal in self.tv.sprites:
                self.tv.sprites.remove(animal)

    def open_dialog(self, widget, x=None, y=None, close_callback=None):
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

        if x:
            offset = (self.disp.rect.center[0] +  x,
                    self.disp.rect.center[1] + y)
        else:
            offset = None
        self.disp.open(tbl, pos=offset)
        return tbl

    def open_building_dialog(self, building, fill_empty, sell_callback=None):
        """Create dialog for manipulating the contents of a building."""

        place_button_map = {}

        def update_button(animal, empty=False):
            """Update a button image (either to the animal, or to empty)."""
            if animal:
                button = place_button_map.get(id(animal.abode))
                if button:
                    if empty:
                        button.value = icons.EMPTY_NEST_ICON
                    else:
                        button.value = icons.animal_icon(animal)

        def nest_clicked(place, button):
            """Handle a nest being clicked."""
            if place.occupant:
                # there is an occupant, select or sell it
                if not sell_callback:
                    mods = pygame.key.get_mods()
                    if not (mods & KMOD_SHIFT):
                        chkns = self.selected_chickens
                        self.unselect_all()
                        for chkn in chkns:
                            update_button(chkn)
                    if place.occupant in self.selected_chickens:
                        self.unselect_animal(place.occupant)
                    else:
                        self.select_animal(place.occupant)
                    # select new animal (on button)
                    update_button(place.occupant)
                else:
                    # FIXME: This should really match the behaviour for
                    # outside buildings, but that requires using the toolbar
                    # while the dialog is open.
                    to_process = [place.occupant]
                    if place.occupant in self.selected_chickens:
                        # We do the same action for all the selected chickens
                        to_process = self.selected_chickens
                    for chick in to_process[:]:
                        sell_callback(chick, update_button)
            else:
                # there is no occupant, attempt to fill the space
                if self.selected_chickens and fill_empty:
                    # empty old nest (on button)
                    update_button(self.selected_chickens[0], empty=True)
                    self.relocate_animal(self.selected_chickens[0], place=place)
                    # populate the new nest (on button)
                    update_button(self.selected_chickens[0])

        tbl = gui.Table()
        columns = building.max_floor_width()
        kwargs = { 'style': { 'padding_left': 10, 'padding_bottom': 10 }}
        for floor in reversed(building.floors()):
            tbl.tr()
            tbl.td(gui.Button(floor.title), colspan=columns, align=-1, **kwargs)
            tbl.tr()
            for row in floor.rows():
                tbl.tr()
                for place in row:
                    if place.occupant is None:
                        button = gui.Button(icons.EMPTY_NEST_ICON)
                    else:
                        button = gui.Button(icons.animal_icon(place.occupant))
                    place_button_map[id(place)] = button
                    button.connect(gui.CLICK, nest_clicked, place, button)
                    tbl.td(button, **kwargs)

        building.selected(True)
        def close_callback():
            for floor in building.floors():
                for row in floor.rows():
                    for place in row:
                        if place.occupant is not None:
                            self.unselect_animal(place.occupant)
            building.selected(False)

        def select_all_callback():
            self.unselect_all()
            for chicken in building.occupants():
                self.select_animal(chicken)
                update_button(chicken)

        def evict_callback():
            if not self.selected_chickens:
                return
            for tile_pos in building.adjacent_tiles():
                if self.tv.get(tile_pos) != self.GRASSLAND:
                    continue
                if self.get_outside_chicken(tile_pos) is None:
                    for chicken in self.selected_chickens:
                        update_button(chicken, empty=True)
                    # this will place all the chickens
                    self.place_animal(tile_pos)
                    break

        def dlg_event(e):
            if e.type == MOUSEBUTTONDOWN and e.button == 2: # Middle
                self.unselect_all()
                for chicken in building.occupants():
                    update_button(chicken)
                return False
            return gui.Table.event(tbl, e)


        tbl.tr()
        select_button = gui.Button('Select All')
        select_button.connect(gui.CLICK, select_all_callback)
        tbl.td(select_button, colspan=2, **kwargs)
        if not sell_callback:
            evict_button = gui.Button('Evict')
            evict_button.connect(gui.CLICK, evict_callback)
            tbl.td(evict_button, colspan=2, **kwargs)

        tbl.event = dlg_event

        self.open_dialog(tbl, close_callback=close_callback)

    def buy_building(self, tile_pos, building_cls):
        building = building_cls(tile_pos, self)
        if self.wood < building.buy_price():
            return
        if any(building.covers((chicken.pos.x, chicken.pos.y)) for chicken in self.chickens):
            return
        if building.place():
            self.add_wood(-building.buy_price())
            self.add_building(building)

    def buy_equipment(self, tile_pos, equipment_cls):

        equipment = equipment_cls()

        def do_equip(chicken, update_button=None):
            # Try to equip the chicken
            if self.cash < equipment.buy_price():
                return False
            if equipment.place(chicken):
                self.add_cash(-equipment.buy_price())
                chicken.equip(equipment)
                if update_button:
                    update_button(chicken)
            return False

        if tile_pos:
            chicken = self.get_outside_chicken(tile_pos)
            if chicken is None:
                building = self.get_building(tile_pos)
                if not (building and building.ABODE):
                    return
                # Bounce through open dialog once more
                self.open_building_dialog(building, False, do_equip)
            else:
                do_equip(chicken)
        else:
            for chicken in self.selected_chickens:
                do_equip(chicken)

    def sell_building(self, tile_pos):
        building = self.get_building(tile_pos)
        if building is None:
            return
        if list(building.occupants()):
            warning = gui.Button("Occupied buildings may not be sold.")
            self.open_dialog(warning)
            return
        self.add_wood(building.sell_price())
        building.remove()
        self.remove_building(building)

    def repair_building(self, tile_pos):
        building = self.get_building(tile_pos)
        if not (building and building.broken()):
            return
        if self.wood < building.repair_price():
            return
        self.add_wood(-building.repair_price())
        building.repair()

    def sell_equipment(self, tile_pos, equipment_cls):
        x, y = 0, 0
        def do_sell(chicken, update_button=None):
            items = [item for item in chicken.equipment
                if isinstance(item, equipment_cls)]
            for item in items:
                self.add_cash(item.sell_price())
                chicken.unequip(item)
                if update_button:
                    update_button(chicken)
            return False
        if tile_pos:
            chicken = self.get_outside_chicken(tile_pos)
            if chicken is not None:
                do_sell(chicken)
            else:
                building = self.get_building(tile_pos)
                if building is None or not building.ABODE:
                    return
                x, y = 50, 0
                self.open_building_dialog(building, False, do_sell)
        else:
            for chicken in self.selected_chickens[:]:
                do_sell(chicken)

    def _do_quit(self):

        def saved(val):
            if val:
                pygame.event.post(constants.GO_GAME_OVER)

        def sure(val):
            if val == 2:
                savedialog = savegame.SaveDialog(self, saved)
                savedialog.open()
            elif val:
                pygame.event.post(constants.GO_GAME_OVER)

        dialog = misc.CheckDialog(sure,
                "Do you REALLY want to exit this game?",
                "Yes, Quit", "No, Don't Quit", "Save & Quit")
        self.disp.open(dialog)

    def event(self, e):
        if e.type == KEYDOWN and e.key == K_ESCAPE:
            self._do_quit()
            return True
        elif e.type == KEYDOWN and e.key == K_n and self.day:
            pygame.event.post(constants.START_NIGHT)
            return True
        elif e.type == KEYDOWN and e.key == K_d and self.night:
            pygame.event.post(constants.FAST_FORWARD)
            return True
        elif e.type == KEYDOWN and e.key in [K_UP, K_DOWN, K_LEFT, K_RIGHT]:
            if e.key == K_UP:
                self.tvw.move_view(0, -constants.TILE_DIMENSIONS[1])
            if e.key == K_DOWN:
                self.tvw.move_view(0, constants.TILE_DIMENSIONS[1])
            if e.key == K_LEFT:
                self.tvw.move_view(-constants.TILE_DIMENSIONS[0], 0)
            if e.key == K_RIGHT:
                self.tvw.move_view(constants.TILE_DIMENSIONS[0], 0)
            return True
        elif e.type == KEYDOWN and e.key in \
                [K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9]:
            mods = pygame.key.get_mods()
            if (mods & KMOD_CTRL) or (mods & KMOD_ALT):
                # store current selection
                self.stored_selections[e.key] = self.selected_chickens[:]
            else:
                additive = (mods & KMOD_SHIFT)
                self.restore_selection(self.stored_selections.get(e.key, []), additive)
            return True
        elif e.type == KEYDOWN:
            mods = pygame.key.get_mods()
            if mods & KMOD_CTRL and self.selected_tool == constants.TOOL_SELECT_CHICKENS and self.selected_chickens:
                self.set_tool_cursor((cursors.cursors['chicken'],))
        elif e.type == KEYUP:
            mods = pygame.key.get_mods()
            if not (mods & KMOD_CTRL) and self.selected_tool == constants.TOOL_SELECT_CHICKENS:
                self.set_tool_cursor((cursors.cursors['select'],))
        return False

    def restore_selection(self, selection, additive=False):
        if not additive:
            self.unselect_all()
        for chick in selection[:]:
            if chick in self.chickens:
                self.select_animal(chick)
            else:
                # Update stored selection
                selection.remove(chick)

    def advance_day(self):
        self.days += 1

    def is_woodland_tile(self, pos):
        return tiles.TILE_MAP[self.tv.get(pos.to_tile_tuple())] == 'woodland'

    def clear_foxes(self):
        for fox in self.foxes.copy():
            # Any foxes that didn't make it to the woods are automatically
            # killed
            if self.in_bounds(fox.pos) and not self.is_woodland_tile(fox.pos):
                self.kill_fox(fox)
            else:
                self.remove_fox(fox)
        self.foxes = set() # Remove all the foxes

    def clear_chickens(self):
        for chicken in self.chickens.copy():
            self.remove_chicken(chicken)

    def clear_buildings(self):
        for building in self.buildings.copy():
            self.remove_building(building)

    def do_night_step(self):
        """Handle the events of the night.

           We return True if there are no more foxes to move or all the
           foxes are safely back. This end's the night"""
        if not self.foxes:
            return True
        # Move all the foxes
        over = self.foxes_move()
        if not over:
            self.foxes_attack()
            self.chickens_attack()
        return over

    def _cache_animal_positions(self):
        """Cache the current set of fox positions for the avoiding checks"""
        self._pos_cache.clear()
        for fox in self.foxes:
            self._pos_cache.add(fox, 'fox')
        for chick in self.chickens:
            self._pos_cache.add(chick, 'chicken')

    def get_animal_at_pos(self, pos, animal_type):
        return self._pos_cache.get(pos, animal_type)

    def chickens_scatter(self):
        """Chickens outside move around randomly a bit"""
        for chicken in [chick for chick in self.chickens if chick.outside()]:
            old_pos = chicken.pos
            chicken.move()
            self._pos_cache.update(old_pos, chicken, 'chicken')

    def chickens_chop_wood(self):
        """Chickens with axes chop down trees near them"""
        for chicken in [chick for chick in self.chickens if chick.outside()]:
            chicken.chop()
        self.calculate_wood_groat_exchange_rate()

    def foxes_move(self):
        over = True
        for fox in self.foxes.copy():
            old_pos = fox.pos
            fox.move()
            if not fox.safe:
                over = False
                self._pos_cache.update(old_pos, fox, 'fox')
            else:
                # Avoid stale fox on board edge
                self.remove_fox(fox)
        return over

    def foxes_attack(self):
        for fox in self.foxes:
            fox.attack()

    def chickens_attack(self):
        for chicken in self.chickens:
            chicken.attack()

    def add_chicken(self, chicken):
        self.chickens.add(chicken)
        if chicken.outside():
            self.tv.sprites.append(chicken)
        if self.disp:
            self.toolbar.update_chicken_counter(len(self.chickens))

    def add_fox(self, fox):
        self.foxes.add(fox)
        self.tv.sprites.append(fox)

    def add_building(self, building):
        self.buildings.add(building)
        self.tv.sprites.append(building, layer='buildings')

    def place_hatched_chicken(self, new_chick, building):
        try:
            building.add_occupant(new_chick)
            self.add_chicken(new_chick)
            new_chick.equip(equipment.Nest())
            new_chick.set_pos(new_chick.abode.get_pos())
        except buildings.BuildingFullError:
            # No space in the hen house, look nearby
            for tile_pos in building.adjacent_tiles():
                if self.tv.get(tile_pos) != self.GRASSLAND:
                    continue
                if self.get_outside_chicken(tile_pos) is None:
                    self.add_chicken(new_chick)
                    self.relocate_animal(new_chick, tile_pos=tile_pos)
                    break
                # if there isn't a space for the
                # new chick it dies. :/ Farm life
                # is cruel.

    def kill_fox(self, fox):
        self.killed_foxes += 1
        self.toolbar.update_fox_counter(self.killed_foxes)
        self.add_cash(self.level.sell_price_dead_fox)
        self.remove_fox(fox)

    def remove_fox(self, fox):
        self._pos_cache.remove(fox.pos, 'fox')
        self.foxes.discard(fox)
        if fox.building:
            fox.building.remove_predator(fox)
        if fox in self.tv.sprites:
            self.tv.sprites.remove(fox)

    def remove_chicken(self, chick):
        if chick in self.selected_chickens:
            self.unselect_animal(chick)
        self.chickens.discard(chick)
        self.eggs -= chick.get_num_eggs()
        self.toolbar.update_egg_counter(self.eggs)
        if chick.abode:
            chick.abode.clear_occupant()
        self.toolbar.update_chicken_counter(len(self.chickens))
        if chick in self.tv.sprites and chick.outside():
            self.tv.sprites.remove(chick)
        self._pos_cache.remove(chick.pos, 'chicken')

    def remove_building(self, building):
        if building in self.buildings:
            self.buildings.discard(building)
            self.tv.sprites.remove(building, layer='buildings')

    def add_cash(self, amount):
        self.cash += amount
        self.toolbar.update_cash_counter(self.cash)

    def add_wood(self, planks):
        self.wood += planks
        self.toolbar.update_wood_counter(self.wood)

    def add_start_chickens(self, _map, tile, value):
        """Add chickens as specified by the code layer"""
        chick = random.choice([animal.Chicken, animal.Rooster])((tile.tx, tile.ty), self)
        for equip_cls in equipment.EQUIP_MAP[value]:
            item = equip_cls()
            chick.equip(item)
        self.add_chicken(chick)

    def _choose_fox(self, (x, y)):
        fox_cls = misc.WeightedSelection(self.level.fox_weightings).choose()
        return fox_cls((x, y), self)

    def spawn_foxes(self):
        """The foxes come at night, and this is where they come from."""
        # Foxes spawn just outside the map
        x, y = 0, 0
        width, height = self.tv.size
        min_foxes = max(self.level.min_foxes, (self.days+3)/2) # always more than one fox
        new_foxes = min(random.randint(min_foxes, min_foxes*2), self.max_foxes)
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
            self.add_fox(self._choose_fox((x, y)))

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
                building = building_cls(tile_pos, self)
                building.remove()
                building.place()
                self.add_building(building)

    def trees_left(self):
        width, height = self.tv.size
        return len([(x,y) for x in range(width) for y in range(height) if self.is_woodland_tile(misc.Position(x,y))])

    def calculate_wood_groat_exchange_rate(self):
        # per five planks
        width, height = self.tv.size
        treesleft = max(1, self.trees_left())
        sell_price = float(10*width*height)/treesleft
        buy_price = sell_price*(1.1)
        self.wood_sell_price, self.wood_buy_price = int(sell_price), int(buy_price)

    def snapshot(self, scale=0.25):
        """Return a snapshot of the gameboard."""
        w, h = self.disp.screen.get_size()
        snap_w, snap_h = int(w * scale), int(h * scale)
        dummy_screen = pygame.surface.Surface((w, h), 0, self.disp.screen)
        top_widget = self.get_top_widget()

        top_widget.paint(dummy_screen)
        snapshot = pygame.transform.smoothscale(dummy_screen, (snap_w, snap_h))
        return snapshot

    def save_game(self):
        # clear selected animals and tool states before saving
        self.reset_states()
        return serializer.simplify(self)

    @staticmethod
    def restore_game(gameboard):
        pygame.event.post(pygame.event.Event(constants.DO_LOAD_SAVEGAME, gameboard=gameboard))


class TextDialog(gui.Dialog):
    def __init__(self, title, text, **params):
        title_label = gui.Label(title)

        doc = gui.Document()

        space = doc.style.font.size(" ")

        for paragraph in text.split('\n\n'):
            doc.block(align=-1)
            for word in paragraph.split():
                doc.add(gui.Label(word))
                doc.space(space)
            doc.br(space[1])
        doc.br(space[1])

        done_button = gui.Button("Close")
        done_button.connect(gui.CLICK, self.close)

        tbl = gui.Table()
        tbl.tr()
        tbl.td(doc)
        tbl.tr()
        tbl.td(done_button, align=1)

        gui.Dialog.__init__(self, title_label, tbl, **params)


