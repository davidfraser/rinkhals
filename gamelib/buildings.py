"""Classes for various buildings in the game."""

from pgu.vid import Sprite

import imagecache

class Building(Sprite):
    """Base class for buildings"""

    def __init__(self, image, pos):
        # Create the building somewhere far off screen
        Sprite.__init__(self, image, (-1000, -1000))
        self.pos = pos

    def loop(self, tv, _sprite):
        ppos = tv.tile_to_view(self.pos)
        self.rect.x = ppos[0]
        self.rect.y = ppos[1]

    def move(self, state):
        """Given the game state, return a new position for the object"""
        # Default is not to move
        return self.pos

class HenHouse(Building):
    """A HenHouse."""

    def __init__(self, pos):
        image = imagecache.load_image('sprites/henhouse.png')
        Building.__init__(self, image, pos)
