"""Classes for various buildings in the game."""

from pgu.vid import Sprite

import imagecache
import tiles

class Building(Sprite):
    """Base class for buildings"""

    GRASSLAND = tiles.REVERSE_TILE_MAP['grassland']

    def __init__(self, pos):
        """Initial image, tile vid position, size and tile number for building."""
        self.day_image = imagecache.load_image(self.IMAGE)
        self.night_image = imagecache.load_image(self.IMAGE, ('night',))
        self.pos = pos
        self.size = self.SIZE
        self.tile_no = self.TILE_NO
        self._buy_price = self.BUY_PRICE

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
        xpos, ypos = self.pos
        xsize, ysize = self.size

        # check that all spaces under the structure are grassland
        for tile_pos in self.tile_positions():
            if not tv.get(tile_pos) == self.GRASSLAND:
                return False

        # place tile
        for tile_pos in self.tile_positions():
            tv.set(tile_pos, self.tile_no)

        return True

    def buy_price(self):
        return self._buy_price

    def sun(self, sun_on):
        if sun_on:
            self.setimage(self.day_image)
        else:
            self.setimage(self.night_image)


class HenHouse(Building):
    """A HenHouse."""

    TILE_NO = tiles.REVERSE_TILE_MAP['henhouse']
    BUY_PRICE = 100
    SIZE = (3, 2)
    IMAGE = 'sprites/henhouse.png'
    NAME = 'Hen House'


class GuardTower(Building):
    """A GuardTower."""

    TILE_NO = tiles.REVERSE_TILE_MAP['guardtower']
    BUY_PRICE = 200
    SIZE = (2, 2)
    IMAGE = 'sprites/watchtower.png'
    NAME = 'Watch Tower'

def is_building(obj):
    """Return true if obj is a build class."""
    return hasattr(obj, "NAME")

BUILDINGS = []
for name in dir():
    obj = eval(name)
    try:
        if is_building(obj):
            BUILDINGS.append(obj)
    except TypeError:
        pass
