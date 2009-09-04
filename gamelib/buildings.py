"""Classes for various buildings in the game."""

from pgu.vid import Sprite
from pygame.locals import SRCALPHA
import pygame
import pygame.font

import imagecache
import tiles
import constants

import warnings
warnings.filterwarnings("ignore", "os.popen3 is deprecated.")

class Place(object):
    """Space within a building that can be occupied."""

    def __init__(self, building, offset):
        self.occupant = None
        self.building = building
        self.offset = offset

    def set_occupant(self, occupant, _update=True):
        self.clear_occupant(_update=False)
        self.occupant = occupant
        self.occupant.abode = self
        if _update:
            self.building.update_occupant_count()

    def clear_occupant(self, _update=True):
        if self.occupant is not None:
            self.occupant.abode = None
            self.occupant = None
        if _update:
            self.building.update_occupant_count()

    def get_pos(self):
        bpos = self.building.pos
        return (bpos[0] + self.offset[0], bpos[1] + self.offset[1])

class Floor(object):
    """A set of places within a building. Places on a
       floor are organised into rows and columns.
       """

    def __init__(self, title, places):
        self.title = title # str
        self.places = places # list of lists of places

    def rows(self):
        for row in self.places:
            yield row

    def width(self):
        return max(len(row) for row in self.places)

class BuildingFullError(Exception):
    pass

class Building(Sprite):
    """Base class for buildings"""

    IS_BUILDING = True
    GRASSLAND = tiles.REVERSE_TILE_MAP['grassland']
    MODIFY_KNIFE_RANGE = lambda s, x: 0
    MODIFY_GUN_RANGE = lambda s, x: -1

    def __init__(self, pos):
        """Initial image, tile vid position, size and tile number for building."""
        self.day_image = imagecache.load_image(self.IMAGE)
        self.night_image = imagecache.load_image(self.IMAGE, ('night',))
        self.selected_image = imagecache.load_image(self.SELECTED_IMAGE)
        self.pos = pos
        self.size = self.SIZE
        self.tile_no = self.TILE_NO
        self._buy_price = self.BUY_PRICE
        self._sell_price = self.SELL_PRICE
        self._sun_on = True
        self._font = pygame.font.SysFont('Vera', 30, bold=True)
        self._font_image = pygame.Surface(self.day_image.get_size(), flags=SRCALPHA)
        self._font_image.fill((0, 0, 0, 0))

        self._floors = []
        for f in range(self.FLOORS):
            places = []
            for j in range(self.size[1]):
                row = []
                for i in range(self.size[0]):
                    row.append(Place(self, (i, j)))
                places.append(row)
            floor = Floor("Floor %s" % (f+1,), places)
            self._floors.append(floor)

        # 0: the main iamge
        # 1: above, -1: below
        self.draw_stack = {"main": (0, self.day_image)}

        # Create the building somewhere far off screen
        Sprite.__init__(self, self.day_image, (-1000, -1000))

    def _redraw(self):
        items = self.draw_stack.values()
        items.sort(key=lambda x: x[0])
        image = items.pop(0)[1].copy()
        for _lvl, overlay in items:
            image.blit(overlay, (0, 0))
        self.setimage(image)

    def _replace_main(self, new_main):
        self.draw_stack["main"] = (0, new_main)
        self._redraw()

    def tile_positions(self):
        """Return pairs of (x, y) tile positions for each of the tile positions
           occupied by the building.
           """
        xpos, ypos = self.pos
        xsize, ysize = self.size

        for dx in xrange(xsize):
            for dy in xrange(ysize):
                yield (xpos + dx, ypos + dy)

    def loop(self, tv, _sprite):
        ppos = tv.tile_to_view(self.pos)
        self.rect.x = ppos[0]
        self.rect.y = ppos[1]

    def move(self, state):
        """Given the game state, return a new position for the object"""
        # Default is not to move
        return self.pos

    def place(self, tv):
        """Check that the building can be placed at its current position
           and place it if possible.
           """
        # check that all spaces under the structure are grassland
        for tile_pos in self.tile_positions():
            if not tv.get(tile_pos) == self.GRASSLAND:
                return False

        # place tile
        for tile_pos in self.tile_positions():
            tv.set(tile_pos, self.tile_no)

        return True

    def covers(self, tile_pos):
        """Return True if build covers tile_pos, False otherwise."""
        xpos, ypos = self.pos
        xsize, ysize = self.size
        return (xpos <= tile_pos[0] < xpos + xsize) and \
            (ypos <= tile_pos[1] < ypos + ysize)

    def remove(self, tv):
        """Remove the building from its current position."""
        # remove tile
        for tile_pos in self.tile_positions():
            tv.set(tile_pos, self.GRASSLAND)

    def buy_price(self):
        return self._buy_price

    def sell_price(self):
        return self._sell_price

    def selected(self, selected):
        if selected:
            self._replace_main(self.selected_image)
        else:
            self.sun(self._sun_on)

    def sun(self, sun_on):
        self._sun_on = sun_on
        if sun_on:
            self._replace_main(self.day_image)
        else:
            self._replace_main(self.night_image)

    def update_occupant_count(self):
        count = len(list(self.occupants()))
        if count == 0:
            if "count" in self.draw_stack:
                del self.draw_stack["count"]
        else:
            image = self._font_image.copy()
            text = self._font.render(str(count), True, constants.FG_COLOR)
            w, h = image.get_size()
            x, y = text.get_size()
            image.blit(text, (w - x, h - y))
            self.draw_stack["count"] = (1, image)
        self._redraw()

    def floors(self):
        return self._floors

    def places(self):
        for floor in self._floors:
            for row in floor.rows():
                for place in row:
                    yield place

    def max_floor_width(self):
        return max(floor.width() for floor in self._floors)

    def first_empty_place(self):
        for place in self.places():
            if place.occupant is None:
                return place
        raise BuildingFullError()

    def add_occupant(self, occupant):
        place = self.first_empty_place()
        place.set_occupant(occupant)

    def occupants(self):
        for place in self.places():
            if place.occupant is not None:
                yield place.occupant

class HenHouse(Building):
    """A HenHouse."""

    TILE_NO = tiles.REVERSE_TILE_MAP['henhouse']
    BUY_PRICE = 100
    SELL_PRICE = 90
    SIZE = (3, 2)
    IMAGE = 'sprites/henhouse.png'
    SELECTED_IMAGE = 'sprites/select_henhouse.png'
    NAME = 'Henhouse'
    FLOORS = 1

class DoubleStoryHenHouse(HenHouse):
    """A double story hen house."""

    TILE_NO = tiles.REVERSE_TILE_MAP['hendominium']
    BUY_PRICE = 300
    SELL_PRICE = 150
    SIZE = (2, 3)
    IMAGE = 'sprites/hendominium.png'
    SELECTED_IMAGE = 'sprites/select_hendominium.png'
    NAME = 'Hendominium'
    FLOORS = 2

class GuardTower(Building):
    """A GuardTower."""

    TILE_NO = tiles.REVERSE_TILE_MAP['guardtower']
    BUY_PRICE = 200
    SELL_PRICE = 150
    SIZE = (2, 2)
    IMAGE = 'sprites/watchtower.png'
    SELECTED_IMAGE = 'sprites/select_watchtower.png'
    NAME = 'Watchtower'
    FLOORS = 1

    MODIFY_GUN_RANGE = lambda s, x: (3*x)/2
    MODIFY_GUN_BASE_HIT = lambda s, x: x-5
    MODIFY_GUN_RANGE_PENALTY = lambda s, x: x-1
    MODIFY_VISION_BONUS = lambda s, x: x+10
    MODIFY_VISION_RANGE_PENALTY = lambda s, x: x-2

def is_building(obj):
    """Return true if obj is a build class."""
    return getattr(obj, "IS_BUILDING", False) and hasattr(obj, "NAME")

# Building hens can lay eggs in
HENHOUSES = [HenHouse.NAME, DoubleStoryHenHouse.NAME]

BUILDINGS = []
for name in dir():
    obj = eval(name)
    try:
        if is_building(obj):
            BUILDINGS.append(obj)
    except TypeError:
        pass
