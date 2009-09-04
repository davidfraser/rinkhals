"""Stuff for animals to use."""

import random
import sound

class Equipment(object):
    IS_EQUIPMENT = True
    DRAW_LAYER = 0

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
    DRAW_LAYER = 10

    def _get_parameter(self, parameter, wielder):
        mod_attr = 'MODIFY_%s_%s' % (self.TYPE, parameter)
        param = getattr(self, parameter)
        return getattr(wielder.abode, mod_attr, lambda r: r)(param)

    def in_range(self, gameboard, wielder, target):
        """Can the lucky wielder hit the potentially unlucky target with this?"""
        return wielder.pos.dist(target.pos) <= self._get_parameter('RANGE', wielder)

    def hit(self, gameboard, wielder, target):
        """Is the potentially unlucky target actually unlucky?"""
        if hasattr(self, 'HIT_SOUND'):
            sound.play_sound(self.HIT_SOUND)
        roll = random.randint(1, 100)
        base_hit = self._get_parameter('BASE_HIT', wielder)
        range_penalty = self._get_parameter('RANGE_PENALTY', wielder)
        return roll > (100-base_hit) + range_penalty*wielder.pos.dist(target.pos)

    def place(self, animal):
        for eq in animal.equipment:
            if is_weapon(eq):
                return False
        return True

class Rifle(Weapon):
    TYPE = "GUN"
    NAME = "rifle"
    BUY_PRICE = 100
    SELL_PRICE = 75

    RANGE = 3
    BASE_HIT = 55
    RANGE_PENALTY = 15
    HIT_SOUND = "fire-rifle.ogg"

    CHICKEN_IMAGE_FILE = 'sprites/equip_rifle.png'

class Knife(Weapon):
    TYPE = "KNIFE"
    NAME = "knife"
    BUY_PRICE = 25
    SELL_PRICE = 15

    RANGE = 1
    BASE_HIT = 70
    RANGE_PENALTY = 0

    CHICKEN_IMAGE_FILE = 'sprites/equip_knife.png'

class Armour(Equipment):
    IS_ARMOUR = True
    DRAW_LAYER = 5

    def __init__(self):
        super(Armour, self).__init__()
        self.hitpoints = self.STARTING_HITPOINTS

    def place(self, animal):
        """Give additional lives"""
        for eq in animal.equipment:
            if eq.NAME == self.NAME:
                return False
        return True

    def survive_damage(self):
        self.hitpoints -= 1
        if self.hitpoints > 0:
            self._sell_price = int(self._sell_price*self.hitpoints/float(self.hitpoints+1))
            return True
        return False

class Helmet(Armour):
    NAME = "helmet"
    BUY_PRICE = 25
    SELL_PRICE = 15

    STARTING_HITPOINTS = 1

    CHICKEN_IMAGE_FILE = 'sprites/helmet.png'

class Kevlar(Armour):
    NAME = "kevlar"
    BUY_PRICE = 100
    SELL_PRICE = 75

    STARTING_HITPOINTS = 2

    CHICKEN_IMAGE_FILE = 'sprites/kevlar.png'

def is_equipment(obj):
    """Return true if obj is a build class."""
    return getattr(obj, "IS_EQUIPMENT", False) and hasattr(obj, "NAME")

def is_weapon(obj):
    return is_equipment(obj) and getattr(obj, 'IS_WEAPON', False)

def is_armour(obj):
    return is_equipment(obj) and getattr(obj, 'IS_ARMOUR', False)

EQUIPMENT = []
for name in dir():
    obj = eval(name)
    try:
        if is_equipment(obj):
            EQUIPMENT.append(obj)
    except TypeError:
        pass
