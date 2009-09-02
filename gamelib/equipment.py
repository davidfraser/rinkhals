"""Stuff for animals to use."""

import random
import sound

class Equipment(object):
    is_weapon = False

class Weapon(Equipment):
    is_weapon = True

    def in_range(self, gameboard, wielder, target):
        """Can the lucky wielder hit the potentially unlucky target with this?"""
        return False

    def hit(self, gameboard, wielder, target):
        """Is the potentially unlucky target actually unlucky?"""
        return False

class Rifle(Weapon):
    def in_range(self, gameboard, wielder, target):
        """For now, we ignore terrain and just assume we can hit
        anything that isn't too far away."""
        return wielder.pos.dist(target.pos) <= 3

    def hit(self, gameboard, wielder, target):
        """Closer is more accurate."""
        sound.play_sound("fire-rifle.ogg")
        return random.randint(1, 100) > 60 + 10*wielder.pos.dist(target.pos)

