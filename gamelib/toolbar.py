import pygame
from pgu import gui

import icons
import constants
import buildings
import equipment
import cursors
import engine
import savegame
import misc

class RinkhalsTool(gui.Tool):
    def __init__(self, group, label, value, func, **params):
        gui.Tool.__init__(self, group, label, value, **params)
        self.func = func

    def click(self):
        gui.Tool.click(self)
        if not self.func():
            # Don't hightlight if the function says so
            self.group.value = None

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

    IS_DEFAULT = False
    MOVE_SELECT_PERMITTED = True

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
        self.add_counter(icons.DAY_ICON, self.day_counter)
        self.add_counter(icons.GROATS_ICON, self.cash_counter)
        self.add_counter(icons.WOOD_ICON, self.wood_counter)
        self.add_counter(icons.EGG_ICON, self.egg_counter)
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

        tbl = gui.Table()
        tbl.tr()
        doc = gui.Document(width=510)
        space = doc.style.font.size(" ")
        for header in ['Item', 'Buy Price', 'Sell Price', 'Repair Price']:
            doc.add(misc.make_box("<b>%s</b>" % header, markup=True))
        doc.br(space[1])
        for building in buildings.BUILDINGS:
            doc.add(misc.make_box(building.NAME))
            doc.add(misc.make_box('%d planks' % building.BUY_PRICE))
            doc.add(misc.make_box('%d planks' % building.SELL_PRICE))
            if building.BREAKABLE:
                doc.add(misc.make_box('%d planks' % building.REPAIR_PRICE))
            else:
                doc.add(misc.make_box('N/A'))
            doc.br(space[1])
        for equip in equipment.EQUIPMENT:
            doc.add(misc.make_box(equip.NAME))
            doc.add(misc.make_box('%d groats' % equip.BUY_PRICE))
            doc.add(misc.make_box('%d groats' % equip.SELL_PRICE))
            doc.add(misc.make_box('N/A'))
            doc.br(space[1])
        doc.add(misc.make_box("5 planks"))
        doc.add(misc.make_box('%d groats' % self.gameboard.wood_buy_price))
        doc.add(misc.make_box('%d groats' % self.gameboard.wood_sell_price))
        doc.add(misc.make_box('N/A'))
        doc.br(space[1])

        misc.fix_widths(doc)
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

    def show_controls(self):
        """Popup dialog of controls"""

        COMBOS = [
            ('Select Multiple chickens', 'Shift & Left Click'),
            ('Move selected chickens', 'Ctrl & Left Click'),
            ('Toggle between select and move', 'Right Click'),
            ('Unselect current tool and chickens', 'Middle Click'),
            ('Save selection', 'Ctrl & 0 .. 9'),
            ('        or', 'Alt & 0 .. 9'),
            ('Recall saved selection', '0 .. 9'),
            ('Exit game', 'Esc'),
            ]

        tbl = gui.Table()
        tbl.tr()
        doc = gui.Document(width=610)
        space = doc.style.font.size(" ")
        for header in ['Action', 'Combination']:
            doc.add(misc.make_box("<b>%s</b>" % header, markup=True))
        doc.br(space[1])
        for command, combo in COMBOS:
            doc.add(misc.make_box(command))
            doc.add(misc.make_box(combo))
            doc.br(space[1])
        doc.br(space[1])

        misc.fix_widths(doc)
        close_button = gui.Button("Close")
        tbl.td(doc)
        tbl.tr()
        tbl.td(close_button, align=1)
        dialog = gui.Dialog(gui.Label('Command Reference'), tbl)
        close_button.connect(gui.CLICK, dialog.close)
        dialog.open()


    def save_game(self):
        """Save game 'dialog'."""
        savegame.SaveDialog(self.gameboard).open()

    def load_game(self):
        """Load game 'dialog'."""
        savegame.RestoreDialog(self.gameboard.restore_game).open()

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
        return self.add_tool(text, lambda: self.gameboard.set_selected_tool(tool,
            cursor))

    def add_tool(self, text, func):
        label = gui.basic.Label(text)
        value = self._next_tool_value
        self._next_tool_value += 1
        tool = RinkhalsTool(self.group, label, value, func, width=self.rect.w,
                style={"padding_left": 0})
        #tool.connect(gui.CLICK, func)
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

    def event(self, e):
        if not gui.Table.event(self, e):
            return self.gameboard.event(e)
        return True

class DefaultToolBar(BaseToolBar):

    IS_DEFAULT = True
    MOVE_SELECT_PERMITTED = True

    def __init__(self, gameboard, **params):
        BaseToolBar.__init__(self, gameboard, **params)
        self.group = gui.Group(name='default_toolbar', value=None)
        self.make_toolbar()

    def make_toolbar(self):
        self._select_tool = self.add_tool_button("Select / Move", constants.TOOL_SELECT_CHICKENS,
                None, cursors.cursors['select'])

        self.add_spacer(5)

        self.add_tool('Equip chickens', self.add_equipment_toolbar)

        self.add_tool('Sell stuff', self.add_sell_toolbar)

        self.add_tool('Trade wood', self.add_wood_toolbar)

        self.add_spacer(5)

        self.add_heading("Buildings")

        self.add_tool('Buy building', self.add_building_toolbar)

        self.add_tool_button("Sell building", constants.TOOL_SELL_BUILDING,
                None, cursors.cursors['sell'])

        self.add_tool_button("Repair", constants.TOOL_REPAIR_BUILDING, None, cursors.cursors['repair'])

        self.add_spacer(5)
        self.add_heading("Help")
        self.add_tool("Price Reference", self.show_prices)
        self.add_tool("Controls", self.show_controls)

        self.add_spacer(5)
        self.add_heading("Game")
        self.add_tool("Save Game", self.save_game)
        self.add_tool("Load Game", self.load_game)

        self.add_heading(" ")
        ## Dear pgu, is there a better way to get the current height?
        #_cur_width, cur_height = self.resize()
        #self.add_spacer(570-cur_height)
        self.fin_tool = self.add_tool("Finished Day", self.day_done)

        if self.gameboard.selected_tool in [constants.TOOL_PLACE_ANIMALS, constants.TOOL_SELECT_CHICKENS]:
            self.highlight_move_select_button()

    def highlight_move_select_button(self):
        self._select_tool.group.value = self._select_tool.value
        self._select_tool.pcls = "down"

    def add_building_toolbar(self):
        self.gameboard.change_toolbar(BuildingToolBar(self.gameboard,
                width=self.style.width))

    def add_sell_toolbar(self):
        self.gameboard.change_toolbar(SellToolBar(self.gameboard,
                width=self.style.width))

    def add_wood_toolbar(self):
        self.gameboard.change_toolbar(WoodToolBar(self.gameboard,
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
        self.group = gui.Group(name='equipment_toolbar', value=None)
        self.make_toolbar()

    def make_toolbar(self):
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
        self.group = gui.Group(name='sell_toolbar', value=None)
        self.make_toolbar()

    def make_toolbar(self):
        self.add_heading("Sell ...")
        self.add_tool_button("Chicken", constants.TOOL_SELL_CHICKEN,
                self.gameboard.level.sell_price_chicken, cursors.cursors['sell'])
        self.add_tool_button("Egg", constants.TOOL_SELL_EGG,
                self.gameboard.level.sell_price_egg, cursors.cursors['sell'])
        self.add_tool_button("Equipment", constants.TOOL_SELL_EQUIPMENT,
                None, cursors.cursors['sell'])
        self.add_spacer(15)
        self.add_tool('Done', self.add_default_toolbar)

    def add_default_toolbar(self):
        self.gameboard.change_toolbar(DefaultToolBar(self.gameboard,
                width=self.style.width))

class WoodToolBar(BaseToolBar):

    def __init__(self, gameboard, **params):
        BaseToolBar.__init__(self, gameboard, **params)
        self.group = gui.Group(name='wood_toolbar', value=None)
        self.make_toolbar()

    def make_toolbar(self):
        self.add_heading("Trade...")
        self.add_tool("Buy 5 planks (%s)" % self.gameboard.wood_buy_price, self.buy_wood)
        self.add_tool("Sell 5 planks (%s)" % self.gameboard.wood_sell_price, self.sell_wood)

        self.add_spacer(15)
        self.add_tool('Done', self.add_default_toolbar)

    def add_default_toolbar(self):
        self.gameboard.change_toolbar(DefaultToolBar(self.gameboard,
                width=self.style.width))

    def buy_wood(self):
        if self.gameboard.cash >= self.gameboard.wood_buy_price:
            self.gameboard.add_wood(5)
            self.gameboard.add_cash(-self.gameboard.wood_buy_price)

    def sell_wood(self):
        if self.gameboard.wood >= 5:
            self.gameboard.add_wood(-5)
            self.gameboard.add_cash(self.gameboard.wood_sell_price)
