"""Stuff for animals to use."""

import random
import sound
import imagecache
import animations

class Equipment(object):
    IS_EQUIPMENT = True
    DRAW_LAYER = 0
    UNDER_LIMB = False
    UNDER_EYE = False

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

    def images(self, eq_image_attr):
        eq_image_file = getattr(self, eq_image_attr, None)
        if not eq_image_file:
            return None
        eq_image_left = imagecache.load_image(eq_image_file)
        eq_image_right = imagecache.load_image(eq_image_file, ("right_facing",))
        if eq_image_attr == "CHICKEN_IMAGE_FILE":
            # a bit hacky; eventually the chicken should have a stack of images and layering should take care of everything
            if self.UNDER_LIMB:
                wing_left = imagecache.load_image("sprites/wing.png")
                wing_right = imagecache.load_image("sprites/wing.png", ("right_facing",))
                eq_image_left.blit(wing_left, (0,0))
                eq_image_right.blit(wing_right, (0,0))
            if self.UNDER_EYE:
                eye_left = imagecache.load_image("sprites/eye.png")
                eye_right = imagecache.load_image("sprites/eye.png", ("right_facing",))
                eq_image_left.blit(eye_left, (0,0))
                eq_image_right.blit(eye_right, (0,0))
        return eq_image_left, eq_image_right, self.DRAW_LAYER

class Weapon(Equipment):
    IS_WEAPON = True
    DRAW_LAYER = 10
    UNDER_LIMB = True

    def _get_parameter(self, parameter, wielder):
        param = getattr(self, parameter)
        if wielder.abode:
            mod_attr = 'MODIFY_%s_%s' % (self.TYPE, parameter)
            modifier = getattr(wielder.abode.building, mod_attr, lambda r: r)
            param = modifier(param)
        return param

    def in_range(self, gameboard, wielder, target):
        """Can the lucky wielder hit the potentially unlucky target with this?"""
        return wielder.pos.dist(target.pos) <= self._get_parameter('RANGE', wielder)

    def hit(self, gameboard, wielder, target):
        """Is the potentially unlucky target actually unlucky?"""
        if hasattr(self, 'HIT_SOUND'):
            sound.play_sound(self.HIT_SOUND)
        if hasattr(self, 'ANIMATION'):
            self.ANIMATION(gameboard.tv, wielder)
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
    NAME = "Rifle"
    BUY_PRICE = 100
    SELL_PRICE = 75

    RANGE = 3
    BASE_HIT = 55
    RANGE_PENALTY = 15
    HIT_SOUND = "fire-rifle.ogg"

    CHICKEN_IMAGE_FILE = 'sprites/equip_rifle.png'

    ANIMATION = animations.MuzzleFlash

class Knife(Weapon):
    TYPE = "KNIFE"
    NAME = "Knife"
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
    NAME = "Helmet"
    BUY_PRICE = 25
    SELL_PRICE = 15
    DRAW_LAYER = 6

    STARTING_HITPOINTS = 1

    CHICKEN_IMAGE_FILE = 'sprites/equip_helmet.png'
    UNDER_EYE = True

class Kevlar(Armour):
    NAME = "Kevlar"
    BUY_PRICE = 100
    SELL_PRICE = 75

    STARTING_HITPOINTS = 2

    CHICKEN_IMAGE_FILE = 'sprites/equip_kevlar.png'

class Accoutrement(Equipment):
    """Things which are not equipment, but are displayed in the same way"""
    IS_EQUIPMENT = False
    IS_ACCOUTREMENT = True
    BUY_PRICE = 0
    SELL_PRICE = 0

    def place(self, animal):
        for eq in animal.accoutrements:
            if eq.NAME == self.NAME:
                return False
        return True

class Spotlight(Accoutrement):
    NAME = "Spotlight"
    CHICKEN_IMAGE_FILE = 'sprites/select_chkn.png'
    DRAW_LAYER = -5

class Nest(Accoutrement):
    NAME = "Nest"
    CHICKEN_IMAGE_FILE = 'sprites/nest.png'
    DRAW_LAYER = 15

class NestEgg(Accoutrement):
    NAME = "Nestegg"
    CHICKEN_IMAGE_FILE = 'sprites/equip_egg.png'
    DRAW_LAYER = 14

def is_equipment(obj):
    """Return true if obj is a build class."""
    return getattr(obj, "IS_EQUIPMENT", False) and hasattr(obj, "NAME")

def is_weapon(obj):
    return is_equipment(obj) and getattr(obj, 'IS_WEAPON', False)

def is_armour(obj):
    return is_equipment(obj) and getattr(obj, 'IS_ARMOUR', False)

def is_accoutrement(obj):
    return not getattr(obj, "IS_EQUIPMENT", False) and hasattr(obj, "NAME") and getattr(obj, 'IS_ACCOUTREMENT', False)

EQUIPMENT = []
for name in dir():
    obj = eval(name)
    try:
        if is_equipment(obj):
            EQUIPMENT.append(obj)
    except TypeError:
        pass


EQUIP_MAP = { # Map chicken level codes to equipment
        1  : [],
        2  : [Helmet],
        3  : [Kevlar],
        4  : [Knife],
        5  : [Rifle],
        6  : [Kevlar, Helmet],
        7  : [Helmet, Knife],
        8  : [Kevlar, Knife],
        9  : [Kevlar, Helmet, Knife],
        10 : [Helmet, Rifle],
        11 : [Kevlar, Rifle],
        12 : [Kevlar, Helmet, Rifle],
        }
