"""Classes for various buildings in the game."""

from pgu.vid import Sprite

import imagecache
import tiles

class Place(object):
    """Space within a building that can be occupied."""

    def __init__(self, building, offset):
        self.occupant = None
        self.building = building
        self.offset = offset

    def set_occupant(self, occupant):
        self.clear_occupant()
        self.occupant = occupant
        self.occupant.abode = self

    def clear_occupant(self):
        if self.occupant is not None:
            self.occupant.abode = None
            self.occupant = None

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

    def __init__(self, pos):
        """Initial image, tile vid position, size and tile number for building."""
        self.day_image = imagecache.load_image(self.IMAGE)
        self.night_image = imagecache.load_image(self.IMAGE, ('night',))
        self.pos = pos
        self.size = self.SIZE
        self.tile_no = self.TILE_NO
        self._buy_price = self.BUY_PRICE
        self._sell_price = self.SELL_PRICE

        self._floors = []
        for f in range(self.FLOORS):
            places = []
            for i in range(self.size[0]):
                row = []
                for j in range(self.size[1]):
                    row.append(Place(self, (i, j)))
                places.append(row)
            floor = Floor("Floor %s" % (f+1,), places)
            self._floors.append(floor)

        # Create the building somewhere far off screen
        Sprite.__init__(self, self.day_image, (-1000, -1000))

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

    def sun(self, sun_on):
        if sun_on:
            self.setimage(self.day_image)
        else:
            self.setimage(self.night_image)

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
    NAME = 'Hen House'
    FLOORS = 1

class DoubleStoryHenHouse(HenHouse):
    """A double story hen house."""
    BUY_PRICE = 300
    SELL_PRICE = 150
    NAME = 'Hendominium'
    FLOORS = 2

class GuardTower(Building):
    """A GuardTower."""

    TILE_NO = tiles.REVERSE_TILE_MAP['guardtower']
    BUY_PRICE = 200
    SELL_PRICE = 150
    SIZE = (2, 2)
    IMAGE = 'sprites/watchtower.png'
    NAME = 'Watch Tower'
    FLOORS = 1

def is_building(obj):
    """Return true if obj is a build class."""
    return getattr(obj, "IS_BUILDING", False) and hasattr(obj, "NAME")

BUILDINGS = []
for name in dir():
    obj = eval(name)
    try:
        if is_building(obj):
            BUILDINGS.append(obj)
    except TypeError:
        pass
