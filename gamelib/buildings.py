"""Classes for various buildings in the game."""

from pgu.vid import Sprite

import imagecache
import tiles

class Building(Sprite):
    """Base class for buildings"""

    GRASSLAND = tiles.REVERSE_TILE_MAP['grassland']

    def __init__(self, day_image, night_image, pos, size, tile_no):
        """Initial image, tile vid position, size and tile number for building."""
        # Create the building somewhere far off screen
        Sprite.__init__(self, day_image, (-1000, -1000))
        self.day_image = day_image
        self.night_image = night_image
        self.pos = pos
        self.size = size
        self.tile_no = tile_no

    def tile_positions(self):
        """Return pairs of (x, y) tile positions for each of the tile positions
           occupied by the building."""
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

    def sun(self, sun_on):
        if sun_on:
            self.setimage(self.day_image)
        else:
            self.setimage(self.night_image)

class HenHouse(Building):
    """A HenHouse."""

    HENHOUSE = tiles.REVERSE_TILE_MAP['henhouse']

    def __init__(self, pos):
        day_image = imagecache.load_image('sprites/henhouse.png')
        night_image = imagecache.load_image('sprites/henhouse.png', ('night',))
        size = (3, 2)
        Building.__init__(self, day_image, night_image, pos, size, self.HENHOUSE)


class GuardTower(Building):
    """A GuardTower."""

    GUARDTOWER = tiles.REVERSE_TILE_MAP['guardtower']

    def __init__(self, pos):
        day_image = imagecache.load_image('sprites/guardtower.png')
        night_image = imagecache.load_image('sprites/guardtower.png', ('night',))
        size = (1, 1)
        Building.__init__(self, day_image, night_image, pos, size, self.GUARDTOWER)
