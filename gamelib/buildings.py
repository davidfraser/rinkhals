"""Classes for various buildings in the game."""

from pgu.vid import Sprite

import imagecache
import tiles

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
        self._occupants = set()

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

    def occupants(self):
        """Return list of buildings occupants."""
        return list(self._occupants)

    def add_occupant(self, occupant):
        if occupant.abode is not None:
            occupant.abode.remove_occupant(occupant)
        occupant.abode = self
        self._occupants.add(occupant)

    def remove_occupant(self, occupant):
        if occupant in self._occupants:
            self._occupants.remove(occupant)
            occupant.abode = None

class HenHouse(Building):
    """A HenHouse."""

    TILE_NO = tiles.REVERSE_TILE_MAP['henhouse']
    BUY_PRICE = 100
    SELL_PRICE = 90
    SIZE = (3, 2)
    IMAGE = 'sprites/henhouse.png'
    NAME = 'Hen House'


class GuardTower(Building):
    """A GuardTower."""

    TILE_NO = tiles.REVERSE_TILE_MAP['guardtower']
    BUY_PRICE = 200
    SELL_PRICE = 150
    SIZE = (2, 2)
    IMAGE = 'sprites/watchtower.png'
    NAME = 'Watch Tower'

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
