import pygame
import xmlrpclib
from pgu import gui

import icons
import constants
import buildings
import equipment
import cursors
import engine

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
    params.setdefault('width', constants.TOOLBAR_WIDTH/2)
    return OpaqueLabel(text, **params)

def mkcountupdate(counter):
    def update_counter(self, value):
        getattr(self, counter).update_value("%s  " % value)
        self.repaint()
    return update_counter

class BaseToolBar(gui.Table):
    def __init__(self, gameboard, **params):
        gui.Table.__init__(self, **params)
        self.group = gui.Group(name='base_toolbar', value=None)
        self._next_tool_value = 0
        self.gameboard = gameboard
        self.cash_counter = mklabel(align=1)
        self.wood_counter = mklabel(align=1)
        self.chicken_counter = mklabel(align=1)
        self.egg_counter = mklabel(align=1)
        self.day_counter = mklabel(align=1)
        self.killed_foxes = mklabel(align=1)
        self.add_labels()

    def add_labels(self):
        self.tr()
        self.td(gui.Spacer(self.rect.w/2, 0))
        self.td(gui.Spacer(self.rect.w/2, 0))
        self.add_counter(mklabel("Day:"), self.day_counter)
        self.add_counter(mklabel("Groats:"), self.cash_counter)
        self.add_counter(mklabel("Planks:"), self.wood_counter)
        self.add_counter(mklabel("Eggs:"), self.egg_counter)
        self.add_counter(icons.CHKN_ICON, self.chicken_counter)
        self.add_counter(icons.KILLED_FOX, self.killed_foxes)
        self.add_spacer(5)

    def start_night(self):
        self.clear_tool()
        self._set_all_disabled(True)
        self.fin_tool.widget = gui.basic.Label('Fast Forward')
        self.fin_tool.resize()
        self.fin_tool.disabled = False # Can always select this
        self.fin_tool.focusable = True # Can always select this

    def start_day(self):
        self.clear_tool()
        self._set_all_disabled(False)
        self.fin_tool.widget = gui.basic.Label('Finished Day')
        self.fin_tool.resize()

    def _set_all_disabled(self, state):
        """Sets the disabled flag on all the buttons in the toolbar"""
        for td in self.widgets:
            for widget in td.widgets:
                if hasattr(widget, 'group'): # Tool
                    widget.disabled = state
                    widget.focusable = not state

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
        doc = gui.Document(width=510)
        space = doc.style.font.size(" ")
        for header in ['Item', 'Buy Price', 'Sell Price', 'Repair Price']:
            doc.add(make_box(header))
        doc.br(space[1])
        for building in buildings.BUILDINGS:
            doc.add(make_box(building.NAME))
            doc.add(make_box('%d planks' % building.BUY_PRICE))
            doc.add(make_box('%d planks' % building.SELL_PRICE))
            if building.BREAKABLE:
                doc.add(make_box('%d planks' % building.REPAIR_PRICE))
            else:
                doc.add(make_box('N/A'))
            doc.br(space[1])
        for equip in equipment.EQUIPMENT:
            doc.add(make_box(equip.NAME))
            doc.add(make_box('%d groats' % equip.BUY_PRICE))
            doc.add(make_box('%d groats' % equip.SELL_PRICE))
            doc.add(make_box('N/A'))
            doc.br(space[1])

        fix_widths(doc)
        for word in "Damaged equipment or buildings will be sold for" \
                " less than the sell price.".split():
            doc.add(gui.Label(word))
            doc.space(space)
        close_button = gui.Button("Close")
        tbl.td(doc)
        tbl.tr()
        tbl.td(close_button, align=1)
        dialog = gui.Dialog(gui.Label('Price Reference'), tbl)
        close_button.connect(gui.CLICK, dialog.close)
        dialog.open()

    def save_game(self):
        """Save game 'dialog'."""
        dialog = gui.FileDialog("Save game ...", button_txt="Save")

        def save():
            if dialog.value is None:
                return
            data = self.gameboard.save_game()
            xml = xmlrpclib.dumps((data,), "foxassault")
            try:
                open(dialog.value, "wb").write(xml)
            except Exception, e:
                print "Failed to save game: %s" % (e,)

        dialog.connect(gui.CHANGE, save)
        dialog.open()

    def load_game(self):
        """Load game 'dialog'."""
        dialog = gui.FileDialog("Load game ...", button_txt="Load")

        def restore():
            if dialog.value is None:
                return
            try:
                xml = open(dialog.value, "rb").read()
                params, methodname = xmlrpclib.loads(xml)
                if methodname != "foxassault":
                    raise ValueError("Bad XML save game.")
                data = params[0]
            except Exception, e:
                "Failed to load game: %s" % (e,)
                return

            self.gameboard.restore_game(data)

        dialog.connect(gui.CHANGE, restore)
        dialog.open()

    update_cash_counter = mkcountupdate('cash_counter')
    update_wood_counter = mkcountupdate('wood_counter')
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
        return tool

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
        width = constants.TOOLBAR_WIDTH
        return width, height

class DefaultToolBar(BaseToolBar):
    def __init__(self, gameboard, **params):
        BaseToolBar.__init__(self, gameboard, **params)
        self.group = gui.Group(name='default_toolbar', value=None)
        self.make_toolbar()

    def make_toolbar(self):
        self.add_tool_button("Select chicken", constants.TOOL_SELECT_CHICKENS,
                None, cursors.cursors['select'])

        self.add_spacer(5)

        self.add_tool('Sell stuff', self.add_sell_toolbar)

        self.add_heading(" ")

        self.add_tool('Buy building', self.add_building_toolbar)

        self.add_heading("For selection, ...")

        self.add_tool('Buy equipment', self.add_equipment_toolbar)

        self.add_tool_button("Move selected hen", constants.TOOL_PLACE_ANIMALS,
                None, cursors.cursors['select'])

        self.add_heading(" ")
        self.add_tool_button("Repair", constants.TOOL_REPAIR_BUILDING, None, cursors.cursors['repair'])

        self.add_heading("Help")
        self.add_tool("Price Reference", self.show_prices)

        self.add_spacer(5)
        self.add_tool("Save Game", self.save_game)
        self.add_tool("Load Game", self.load_game)

        self.add_heading(" ")
        self.add_spacer(10)
        self.fin_tool = self.add_tool("Finished Day", self.day_done)

    def add_building_toolbar(self):
        self.gameboard.change_toolbar(BuildingToolBar(self.gameboard,
                width=self.style.width))

    def add_sell_toolbar(self):
        self.gameboard.change_toolbar(SellToolBar(self.gameboard,
                width=self.style.width))

    def add_equipment_toolbar(self):
        self.gameboard.change_toolbar(EquipmentToolBar(self.gameboard,
                width=self.style.width))

    def day_done(self):
        if self.gameboard.day:
            pygame.event.post(engine.START_NIGHT)
        else:
            pygame.event.post(engine.FAST_FORWARD)

class BuildingToolBar(BaseToolBar):
    def __init__(self, gameboard, **params):
        BaseToolBar.__init__(self, gameboard, **params)
        self.group = gui.Group(name='building_toolbar', value=None)
        self.make_toolbar()

    def make_toolbar(self):
        self.gameboard.set_cursor(cursors.cursors['arrow'], None)
        for building_cls in buildings.BUILDINGS:
            self.add_tool_button(building_cls.NAME.title(), building_cls,
                    None, cursors.cursors.get('build', None))
        self.add_spacer(15)
        self.add_tool('Done', self.add_default_toolbar)

    def add_default_toolbar(self):
        self.gameboard.change_toolbar(DefaultToolBar(self.gameboard,
                width=self.style.width))

class EquipmentToolBar(BaseToolBar):
    def __init__(self, gameboard, **params):
        BaseToolBar.__init__(self, gameboard, **params)
        self.group = gui.Group(name='building_toolbar', value=None)
        self.make_toolbar()

    def make_toolbar(self):
        self.gameboard.set_cursor(cursors.cursors['arrow'], None)
        for equipment_cls in equipment.EQUIPMENT:
            self.add_tool_button(equipment_cls.NAME.title(),
                    equipment_cls,
                    equipment_cls.BUY_PRICE,
                    cursors.cursors.get('buy', None))
        self.add_spacer(15)
        self.add_tool('Done', self.add_default_toolbar)

    def add_default_toolbar(self):
        self.gameboard.change_toolbar(DefaultToolBar(self.gameboard,
                width=self.style.width))

class SellToolBar(BaseToolBar):
    def __init__(self, gameboard, **params):
        BaseToolBar.__init__(self, gameboard, **params)
        self.group = gui.Group(name='building_toolbar', value=None)
        self.make_toolbar()

    def make_toolbar(self):
        self.gameboard.set_cursor(cursors.cursors['arrow'], None)

        self.add_heading("Sell ...")
        self.add_tool_button("Chicken", constants.TOOL_SELL_CHICKEN,
                self.gameboard.level.sell_price_chicken, cursors.cursors['sell'])
        self.add_tool_button("Egg", constants.TOOL_SELL_EGG,
                self.gameboard.level.sell_price_egg, cursors.cursors['sell'])
        self.add_tool_button("Building", constants.TOOL_SELL_BUILDING,
                None, cursors.cursors['sell'])
        self.add_tool_button("Equipment", constants.TOOL_SELL_EQUIPMENT,
                None, cursors.cursors['sell'])
        self.add_spacer(15)
        self.add_tool('Done', self.add_default_toolbar)

    def add_default_toolbar(self):
        self.gameboard.change_toolbar(DefaultToolBar(self.gameboard,
                width=self.style.width))

