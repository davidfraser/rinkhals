import random

import pygame
from pygame.locals import MOUSEBUTTONDOWN, MOUSEMOTION, KEYDOWN, K_UP, K_DOWN, \
        K_LEFT, K_RIGHT
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
import misc

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
        self.group = gui.Group(name='toolbar', value=None)
        self._next_tool_value = 0
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
                None, cursors.cursors['select'])
        self.add_tool_button("Cut Trees", constants.TOOL_LOGGING,
                constants.LOGGING_PRICE, cursors.cursors['ball'])
        self.add_spacer(20)

        self.add_heading("Sell ...")
        self.add_tool_button("Chicken", constants.TOOL_SELL_CHICKEN,
                constants.SELL_PRICE_CHICKEN, cursors.cursors['sell'])
        self.add_tool_button("Egg", constants.TOOL_SELL_EGG,
                constants.SELL_PRICE_EGG, cursors.cursors['sell'])
        self.add_tool_button("Building", constants.TOOL_SELL_BUILDING,
                None, cursors.cursors['sell'])
        self.add_tool_button("Equipment", constants.TOOL_SELL_EQUIPMENT,
                None, cursors.cursors['sell'])
        self.add_spacer(20)

        self.add_heading("Buy ...")

        self.add_tool_button("Fence", constants.TOOL_BUY_FENCE,
                "%s/%s" % (constants.BUY_PRICE_FENCE,
                           constants.REPAIR_PRICE_FENCE))

        for building_cls in buildings.BUILDINGS:
            self.add_tool_button(building_cls.NAME.title(), building_cls,
                    None, cursors.cursors.get('build', None))

        for equipment_cls in equipment.EQUIPMENT:
            self.add_tool_button(equipment_cls.NAME.title(),
                    equipment_cls,
                    equipment_cls.BUY_PRICE,
                    cursors.cursors.get('buy', None))

        self.add_tool("Price Reference", self.show_prices)
        self.add_spacer(30)

        self.add_tool("Finished Day", self.day_done)

    def day_done(self):
        import engine
        pygame.event.post(engine.START_NIGHT)

    def show_prices(self):
        """Popup dialog of prices"""
        def make_box(text):
            style = {
                    'border' : 1
                    }
            word = gui.Label(text, style=style)
            return word

        def fix_widths(doc):
            """Loop through all the widgets in the doc, and set the
               width of the labels to max + 10"""
            # We need to do this because of possible font issues
            max_width = 0
            for thing in doc.widgets:
                if hasattr(thing, 'style'):
                    # A label
                    if thing.style.width > max_width:
                        max_width = thing.style.width
            for thing in doc.widgets:
                if hasattr(thing, 'style'):
                    thing.style.width = max_width + 10

        tbl = gui.Table()
        tbl.tr()
        doc = gui.Document(width=400)
        space = doc.style.font.size(" ")
        for header in ['Item', 'Buy Price', 'Sell Price']:
            doc.add(make_box(header))
        doc.br(space[1])
        for building in buildings.BUILDINGS:
            doc.add(make_box(building.NAME))
            doc.add(make_box('%d' % building.BUY_PRICE))
            doc.add(make_box('%d' % building.SELL_PRICE))
            doc.br(space[1])
        for equip in equipment.EQUIPMENT:
            doc.add(make_box(equip.NAME))
            doc.add(make_box('%d' % equip.BUY_PRICE))
            doc.add(make_box('%d' % equip.SELL_PRICE))
            doc.br(space[1])
        fix_widths(doc)
        for word in "Damaged equipment will be sold for less than" \
                " the sell price.".split():
            doc.add(gui.Label(word))
            doc.space(space)
        close_button = gui.Button("Close")
        tbl.td(doc, colspan=3)
        tbl.tr()
        tbl.td(gui.Label(''))
        tbl.td(gui.Label(''))
        tbl.td(close_button)
        dialog = gui.Dialog(gui.Label('Price Reference'), tbl)
        close_button.connect(gui.CLICK, dialog.close)
        dialog.open()

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

    def add_tool_button(self, text, tool, price=None, cursor=None):
        if price is not None:
            text = "%s  (%s)" % (text, price)
        self.add_tool(text, lambda: self.gameboard.set_selected_tool(tool,
            cursor))

    def add_tool(self, text, func):
        label = gui.basic.Label(text)
        value = self._next_tool_value
        self._next_tool_value += 1
        tool = gui.Tool(self.group, label, value, width=self.rect.w, style={"padding_left": 0})
        tool.connect(gui.CLICK, func)
        self.tr()
        self.td(tool, align=-1, colspan=2)

    def clear_tool(self):
        self.group.value = None
        for item in self.group.widgets:
            item.pcls = ""

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
        # Blit animation frames on top of the drawing
        x, y = self.vid.view.x, self.vid.view.y
        for anim in self.gameboard.animations:
            anim.fix_pos(self.vid)
            anim.irect.x = anim.rect.x - anim.shape.x
            anim.irect.y = anim.rect.y - anim.shape.y
            surface.blit(anim.image, (anim.irect.x - x, anim.irect.y - y))
            # We don't store anim._irect, since we only update anims if the
            # image changes, which kills irect

    def update(self, surface):
        us = []
        x, y = self.vid.view.x, self.vid.view.y
        for anim in self.gameboard.animations[:]:
            if anim.updated or anim.removed:
                # We flag that we need to redraw stuff undeneath the animation
                us.append(pygame.Rect(anim.irect.x - x, anim.irect.y - y,
                    anim.irect.width, anim.irect.height))
                self.vid.alayer[anim.pos.y][anim.pos.x]=1
                self.vid.updates.append(anim.pos.to_tuple())
            if anim.removed:
                # Remove the animation from the draw loop
                self.gameboard.animations.remove(anim)
        us.extend(self.vid.update(surface))
        for anim in self.gameboard.animations:
            if anim.updated: 
                anim.fix_pos(self.vid)
                # setimage has happened, so redraw
                anim.irect.x = anim.rect.x - anim.shape.x
                anim.irect.y = anim.rect.y - anim.shape.y
                surface.blit(anim.image, (anim.irect.x - x, anim.irect.y - y))
                anim.updated = 0
                us.append(pygame.Rect(anim.irect.x - x, anim.irect.y - y,
                    anim.irect.width, anim.irect.height))
                # This is enough, because sprite changes happen disjoint
                # from the animation sequence, so we don't need to worry
                # other changes forcing us to redraw the animation frame.
        return us

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

    FOX_WEIGHTINGS = (
        (animal.Fox, 60),
        (animal.GreedyFox, 30),
        (animal.NinjaFox, 5),
        (animal.DemoFox, 5),
        )

    def __init__(self, main_app):
        self.disp = main_app
        self.tv = tiles.FarmVid()
        self.tv.png_folder_load_tiles(data.filepath('tiles'))
        self.tv.tga_load_level(data.filepath('levels/farm.tga'))
        self.create_display()

        self.selected_tool = None
        self.animal_to_place = None
        self.sprite_cursor = None
        self.chickens = set()
        self.foxes = set()
        self.buildings = []
        self.animations = []
        self.cash = 0
        self.eggs = 0
        self.days = 0
        self.killed_foxes = 0
        self.add_cash(constants.STARTING_CASH)
        self.day, self.night = True, False

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
        if not self.day:
            return
        self.selected_tool = tool
        if self.animal_to_place:
            # Clear any highlights
            self.animal_to_place.unequip_by_name("spotlight")
        self.select_animal_to_place(None)
        sprite_curs = None
        if buildings.is_building(tool):
            sprite_curs = sprite_cursor.SpriteCursor(tool.IMAGE, self.tv, tool.BUY_PRICE)
        elif equipment.is_equipment(tool):
            sprite_curs = sprite_cursor.SpriteCursor(tool.CHICKEN_IMAGE_FILE, self.tv)
        elif tool == constants.TOOL_BUY_FENCE:
            sprite_curs = sprite_cursor.SpriteCursor("tiles/fence.png", self.tv)
        self.set_cursor(cursor, sprite_curs)

    def set_cursor(self, cursor=None, sprite_curs=None):
        if cursor:
            pygame.mouse.set_cursor(*cursor)
        else:
            pygame.mouse.set_cursor(*cursors.cursors['arrow'])
        self.sprite_cursor = sprite_curs
        self.tv.sprites.set_cursor(sprite_curs)

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

    def start_day(self):
        self.day, self.night = True, False
        self.tv.sun(True)
        self.reset_states()

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
            self.set_selected_tool(None, None)
            self.toolbar.clear_tool()
        elif e.button != 1: # Left button
            return
        if self.selected_tool == constants.TOOL_SELL_CHICKEN:
            self.sell_chicken(self.tv.screen_to_tile(e.pos))
        elif self.selected_tool == constants.TOOL_SELL_EGG:
            self.sell_egg(self.tv.screen_to_tile(e.pos))
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

        def do_sell(chicken):
            if not chicken:
                return False # sanity check
            if len(self.chickens) == 1:
                print "You can't sell your last chicken!"
                return False
            for item in list(chicken.equipment):
                self.add_cash(item.sell_price())
                chicken.unequip(item)
            self.add_cash(constants.SELL_PRICE_CHICKEN)
            sound.play_sound("sell-chicken.ogg")
            return True

        chick = self.get_outside_chicken(tile_pos)
        if chick is None:
            building = self.get_building(tile_pos)
            if building and building.NAME in buildings.HENHOUSES:
                self.open_building_dialog(building, do_sell)
            return

        if do_sell(chick):
            self.remove_chicken(chick)

    def sell_one_egg(self, chicken):
        if chicken.eggs:
            self.add_cash(constants.SELL_PRICE_EGG)
            chicken.remove_one_egg()
            self.eggs -= 1
            self.toolbar.update_egg_counter(self.eggs)
            return True
        return False

    def sell_egg(self, tile_pos):
        def do_sell(chicken):
            # We try sell and egg
            if self.sell_one_egg(chicken):
                sound.play_sound("sell-chicken.ogg")
                # Force toolbar update
                self.toolbar.chsize()
            return False

        building = self.get_building(tile_pos)
        if building and building.NAME in buildings.HENHOUSES:
            self.open_building_dialog(building, do_sell)

    def select_animal_to_place(self, animal):
        if self.animal_to_place:
            self.animal_to_place.unequip_by_name("spotlight")
        self.animal_to_place = animal
        if self.animal_to_place:
            self.animal_to_place.equip(equipment.Spotlight())

    def place_animal(self, tile_pos):
        """Handle an TOOL_PLACE_ANIMALS click.

           This will either select an animal or
           place a selected animal in a building.
           """
        chicken = self.get_outside_chicken(tile_pos)
        if chicken:
            if chicken is self.animal_to_place:
                self.select_animal_to_place(None)
                pygame.mouse.set_cursor(*cursors.cursors['select'])
            else:
                self.select_animal_to_place(chicken)
                pygame.mouse.set_cursor(*cursors.cursors['chicken'])
            return
        building = self.get_building(tile_pos)
        if building:
            if self.animal_to_place:
                try:
                    place = building.first_empty_place()
                    self.relocate_animal(self.animal_to_place, place=place)
                    self.animal_to_place.equip(equipment.Nest())
                    self.select_animal_to_place(None)
                    pygame.mouse.set_cursor(*cursors.cursors['select'])
                except buildings.BuildingFullError:
                    pass
            else:
                self.open_building_dialog(building)
            return
        if self.tv.get(tile_pos) == self.GRASSLAND:
            if self.animal_to_place is not None:
                self.animal_to_place.unequip_by_name("nest")
                self.relocate_animal(self.animal_to_place, tile_pos=tile_pos)
                self.eggs -= self.animal_to_place.get_num_eggs()
                self.animal_to_place.remove_eggs()
                self.toolbar.update_egg_counter(self.eggs)

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

    def open_building_dialog(self, building, sell_callback=None):
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
            # sell_callback should return true if we need to remove the
            # occupant
            if place.occupant:
                # there is an occupant, select or sell it
                if not sell_callback:
                    old_animal = self.animal_to_place
                    self.select_animal_to_place(place.occupant)
                    # deselect old animal (on button)
                    update_button(old_animal)
                    # select new animal (on button)
                    update_button(self.animal_to_place)
                else:
                    # Attempt to sell the occupant
                    if sell_callback(place.occupant):
                        # empty the nest (on button)
                        update_button(place.occupant, empty=True)
                        self.remove_chicken(place.occupant)
                    else:
                        # Update for equipment changes, etc.
                        update_button(place.occupant)
            else:
                # there is no occupant, attempt to fill the space
                if self.animal_to_place is not None:
                    # empty old nest (on button)
                    update_button(self.animal_to_place, empty=True)
                    self.relocate_animal(self.animal_to_place, place=place)
                    # populate the new nest (on button)
                    update_button(self.animal_to_place)

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
                    else:
                        button = gui.Button(icons.animal_icon(place.occupant))
                    place_button_map[id(place)] = button
                    button.connect(gui.CLICK, nest_clicked, place, button)
                    tbl.td(button, **kwargs)

        building.selected(True)
        def close_callback():
            building.selected(False)

        def evict_callback():
            if not self.animal_to_place:
                return
            for tile_pos in building.adjacent_tiles():
                if self.tv.get(tile_pos) != self.GRASSLAND:
                    continue
                if self.get_outside_chicken(tile_pos) is None:
                    update_button(self.animal_to_place, empty=True)
                    self.place_animal(tile_pos)
                    break

        if not sell_callback:
            tbl.tr()
            button = gui.Button('Evict')
            button.connect(gui.CLICK, evict_callback)
            tbl.td(button, colspan=2, **kwargs)

        self.open_dialog(tbl, close_callback=close_callback)

    def buy_fence(self, tile_pos):
        this_tile = self.tv.get(tile_pos)
        if this_tile not in [self.GRASSLAND, self.BROKEN_FENCE]:
            return
        if this_tile == self.GRASSLAND:
            cost = constants.BUY_PRICE_FENCE
        else:
            cost = constants.REPAIR_PRICE_FENCE
        if any((chicken.pos.x, chicken.pos.y) == tile_pos for chicken in self.chickens):
            return

        if self.cash < cost:
            print "You can't afford a fence."
            return
        self.add_cash(-cost)
        self.tv.set(tile_pos, self.FENCE)

    def sell_fence(self, tile_pos):
        this_tile = self.tv.get(tile_pos)
        if this_tile not in [self.FENCE, self.BROKEN_FENCE]:
            return
        if this_tile == self.FENCE:
            self.add_cash(constants.SELL_PRICE_FENCE)
        elif this_tile == self.BROKEN_FENCE:
            self.add_cash(constants.SELL_PRICE_BROKEN_FENCE)
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
        if any(building.covers((chicken.pos.x, chicken.pos.y)) for chicken in self.chickens):
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
        if self.tv.get(tile_pos) in [self.FENCE, self.BROKEN_FENCE]:
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
        if e.type == KEYDOWN and e.key in [K_UP, K_DOWN, K_LEFT, K_RIGHT]:
            if e.key == K_UP:
                self.tvw.move_view(0, -self.TILE_DIMENSIONS[1])
            if e.key == K_DOWN:
                self.tvw.move_view(0, self.TILE_DIMENSIONS[1])
            if e.key == K_LEFT:
                self.tvw.move_view(-self.TILE_DIMENSIONS[0], 0)
            if e.key == K_RIGHT:
                self.tvw.move_view(self.TILE_DIMENSIONS[0], 0)
            return True
        return False

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

    def run_animations(self):
        for anim in self.animations:
            anim.animate()

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
                    self.eggs += chicken.get_num_eggs()
        self.toolbar.update_egg_counter(self.eggs)

    def hatch_eggs(self):
        for building in self.buildings:
            if building.NAME in buildings.HENHOUSES:
                for chicken in building.occupants():
                    new_chick = chicken.hatch(self)
                    if new_chick:
                        try:
                            building.add_occupant(new_chick)
                            self.add_chicken(new_chick)
                            new_chick.equip(equipment.Nest())
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
        self.toolbar.update_egg_counter(self.eggs)

    def kill_fox(self, fox):
        self.killed_foxes += 1
        self.toolbar.update_fox_counter(self.killed_foxes)
        self.add_cash(constants.SELL_PRICE_DEAD_FOX)
        self.remove_fox(fox)

    def remove_fox(self, fox):
        self.foxes.discard(fox)
        if fox in self.tv.sprites:
            self.tv.sprites.remove(fox)

    def remove_chicken(self, chick):
        if chick is self.animal_to_place:
            self.select_animal_to_place(None)
        self.chickens.discard(chick)
        self.eggs -= chick.get_num_eggs()
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
        tries = 0
        while len(self.chickens) < 10:
            if x < width:
                tile = self.tv.get((x, y))
            else:
                y += 1
                if y >= height:
                    y = 0
                    tries += 1
                    if tries > 3:
                        break # Things have gone wierd
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

    def _choose_fox(self, (x, y)):
        fox_cls = misc.WeightedSelection(self.FOX_WEIGHTINGS).choose()
        return fox_cls((x, y))

    def spawn_foxes(self):
        """The foxes come at night, and this is where they come from."""
        # Foxes spawn just outside the map
        x, y = 0, 0
        width, height = self.tv.size
        min_foxes = (self.days+3)/2 # always more than one fox
        new_foxes = random.randint(min_foxes, min_foxes*2)
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
