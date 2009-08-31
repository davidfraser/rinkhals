"""Class for the various animals in the game"""

import pygame
import random
from pgu.vid import Sprite

import data

class Animal(Sprite):
    """Base class for animals"""

    def __init__(self, image, pos):
        # Create the animal somewhere far off screen
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
        self.full = False
        Animal.__init__(self, image, pos)

    def move(self, gameboard):
        """Foxes will aim to move towards the closest henhouse or free
          chicken"""
        if self.full:
            return
        # Find the closest chicken
        min_dist = 999
        min_vec = None
        closest = None
        for chicken in gameboard.chickens:
            vec = (chicken.pos[0] - self.pos[0], chicken.pos[1] - self.pos[1])
            dist = abs(vec[0]) + abs(vec[1])
            if dist < min_dist:
                min_dist = dist
                min_vec = vec
                closest = chicken
        xpos, ypos = self.pos
        if min_vec[0] < 0:
            xpos -= 1
        elif min_vec[0] > 0:
            xpos += 1
        if min_vec[1] < 0:
            ypos -= 1
        elif min_vec[1] > 0:
            ypos += 1
        if closest.pos == self.pos:
            gameboard.remove_chicken(closest)
            self.full = True
        for fox in gameboard.foxes:
            if fox is not self:
                if fox.pos[0] == xpos and fox.pos[1] == ypos:
                    if xpos != self.pos[0]:
                        xpos = self.pos[0]
                    elif ypos != self.pos[1]:
                        ypos = self.pos[1]
                    else: # We move a step away
                        xpos += 1
        self.pos = (xpos, ypos)
        
            
