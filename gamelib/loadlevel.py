"""Help screen."""

from pgu import gui
import os
import pygame
from . import level
from . import data
from . import gameboard
from . import constants


class LoadLevelDialog(gui.Dialog):
    """Load level dialog."""

    def __init__(self, curr_level, load_func, cls="dialog"):
        self.value = None
        self.levels = self._populate_levels()

        self.main_style = {
            'width': 300, 'height': 350
        }

        td_style = {
            'padding_left': 4,
            'padding_right': 4,
            'padding_top': 2,
            'padding_bottom': 2,
        }

        self.level_list = gui.List(**self.main_style)
        level_names = list(self.levels.keys())
        level_names.sort()
        for name in level_names:
            self.level_list.add(name, value=name)
        self.level_list.set_vertical_scroll(0)
        self.level_list.connect(gui.CHANGE, self._level_list_change)

        self.image_container = gui.Container()

        button_ok = gui.Button("Load Level")
        button_ok.connect(gui.CLICK, self._click_ok)

        button_cancel = gui.Button("Cancel")
        button_cancel.connect(gui.CLICK, self._click_cancel)

        body = gui.Table()
        body.tr()
        list_style = dict(self.main_style)
        list_style.update(td_style)
        body.td(self.level_list, style=list_style, valign=-1, rowspan=2)
        body.td(self.image_container, style=td_style, colspan=2)
        body.tr()
        # putting in the extra spacer squashes the ok and cancel button
        # up nicely
        body.td(gui.Spacer(0, 0), style=td_style)
        body.td(button_ok, style=td_style, align=1)
        body.td(button_cancel, style=td_style, align=1)

        title = gui.Label("Load Level ...", cls=cls + ".title.label")
        gui.Dialog.__init__(self, title, body)

        if curr_level.level_name in self.levels:
            self.level_list.group.value = curr_level.level_name
        elif level_names:
            self.level_list.group.value = level_names[0]

        self.connect(gui.CHANGE, self._load_level, load_func)

    def _populate_levels(self):
        """Read list of levels from disk."""
        levels = {}
        for name in os.listdir(data.filepath('levels/')):
            if not name.endswith('.conf'):
                continue
            try:
                this_level = level.Level(name)
            except RuntimeError:
                # Skip levels that fail to load
                continue
            if not os.path.exists(this_level.map):
                # Skip level if we can't see the map
                continue
            levels[this_level.level_name] = (this_level, None)
        return levels

    def _create_image_widget(self, curr_level):
        """Create an image showing the contents of level file."""
        board = gameboard.GameBoard(None, curr_level)
        w, h = board.tv.size

        map_image = pygame.Surface((constants.TILE_DIMENSIONS[0] * w,
            constants.TILE_DIMENSIONS[1] * h))
        board.tv.loop()
        board.tv.paint(map_image)

        style = {
            'width' : min(300, 7*w),
            'height' : min(300, 7*h),
        }

        doc = gui.Document(style=self.main_style)
        space = doc.style.font.size(" ")

        doc.block(align=0)
        doc.add(gui.Image(map_image, style=style))

        doc.block(align=0)
        doc.add(gui.Label(curr_level.level_name, style={
            'border_bottom': 1,
            'margin_bottom': 5,
            'margin_top': 5,
        }))

        doc.block(align=0)
        for word in curr_level.goal.split():
            doc.add(gui.Label(word))
            doc.space(space)

        return doc

    def _level_list_change(self):
        for w in self.image_container.widgets:
            self.image_container.remove(w)

        name = self.level_list.value
        curr_level, widget = self.levels[name]
        if widget is None:
            widget = self._create_image_widget(curr_level)
            self.levels[name] = (curr_level, widget)

        self.image_container.add(widget, 0, 0)

    def _click_ok(self):
        self.value = self.level_list.value
        if self.value:
            self.send(gui.CHANGE)
            self.close()

    def _click_cancel(self):
        self.value = None
        self.send(gui.CHANGE)
        self.close()

    def _load_level(self, load_func):
        level = self.get_level()
        if level is not None:
            load_func(level)

    def get_level(self):
        if self.value is None:
            return None
        return self.levels[self.value][0]



