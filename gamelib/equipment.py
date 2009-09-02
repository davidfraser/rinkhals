"""Stuff for animals to use."""

import random
import sound

class Equipment(object):
    IS_EQUIPMENT = True

    def __init__(self):
        self._buy_price = self.BUY_PRICE
        self._sell_price = self.SELL_PRICE
        self._name = self.NAME

    def buy_price(self):
        return self._buy_price

    def sell_price(self):
        return self._sell_price

    def name(self):
        return self._name

class Weapon(Equipment):
    IS_WEAPON = True

    def in_range(self, gameboard, wielder, target):
        """Can the lucky wielder hit the potentially unlucky target with this?"""
        return wielder.pos.dist(target.pos) <= self.RANGE

    def hit(self, gameboard, wielder, target):
        """Is the potentially unlucky target actually unlucky?"""
        if hasattr(self, 'HIT_SOUND'):
            sound.play_sound(self.HIT_SOUND)
        roll = random.randint(1, 100)
        return roll > self.BASE_HIT + self.RANGE_MODIFIER*wielder.pos.dist(target.pos)

    def place(self, animal):
        for eq in animal.equipment:
            if self.NAME == eq.NAME:
                return False
        return True

class Rifle(Weapon):
    NAME = "rifle"
    BUY_PRICE = 20
    SELL_PRICE = 15

    RANGE = 3
    BASE_HIT = 50
    RANGE_MODIFIER = 15
    HIT_SOUND = "fire-rifle.ogg"

def is_equipment(obj):
    """Return true if obj is a build class."""
    return getattr(obj, "IS_EQUIPMENT", False) and hasattr(obj, "NAME")

def is_weapon(obj):
    return is_equipment(obj) and getattr(obj, 'IS_WEAPON', False)

EQUIPMENT = []
for name in dir():
    obj = eval(name)
    try:
        if is_equipment(obj):
            EQUIPMENT.append(obj)
    except TypeError:
        pass
