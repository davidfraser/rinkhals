"""Class for the various animals in the game"""

import pygame
from pgu.vid import Sprite

import data

class Animal(Sprite):
    """Base class for animals"""

    def __init__(self, image, pos):
        Sprite.__init__(self, image, pos)
        self.pos = pos

    def loop(self, tv, _sprite):
        ppos = tv.tile_to_view(self.pos)
        self.rect.x = ppos[0]
        self.rect.y = ppos[1]

    def move(self, state):
        """Given the game state, return a new position for the object"""
        # Default is not to move
        return self.pos

class Chicken(Animal):
    """A chicken"""

    def __init__(self, pos):
        image = pygame.image.load(data.filepath('sprites/chkn.png'))
        Animal.__init__(self, image, pos)

    def move(self, gameboard):
        """A free chicken will move away from other free chickens"""
        return self.pos

class Egg(Animal):
    """An egg"""

    # Eggs don't move

class Fox(Animal):
    """A fox"""

    def __init__(self, pos):
        image = pygame.image.load(data.filepath('sprites/fox.png'))
        Animal.__init__(self, image, pos)

    def move(self, gameboard):
        """Foxes will aim to move towards the closest henhouse or free
          chicken"""
        return self.pos
