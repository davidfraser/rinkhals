"""Stuff for animals to use."""

import random
from . import sound
from . import imagecache
from . import animations
from . import serializer


class Equipment(serializer.Simplifiable):
    IS_EQUIPMENT = True
    DRAW_LAYER = 0
    UNDER_LIMB = False
    UNDER_EYE = False
    AMMUNITION = None

    SIMPLIFY = [
        '_buy_price',
        '_sell_price',
        '_name',
        'ammunition',
    ]

    def __init__(self):
        self._buy_price = self.BUY_PRICE
        self._sell_price = self.SELL_PRICE
        self._name = self.NAME
        self.refresh_ammo()

    @classmethod
    def make(cls):
        """Override default Simplifiable object creation."""
        return cls()

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
        if eq_image_attr == "ANIMAL_IMAGE_FILE":
            # a bit hacky; eventually the horse should have a stack of images and layering should take care of everything
            if self.UNDER_EYE:
                eye_left = imagecache.load_image("sprites/eye.png")
                eye_right = imagecache.load_image("sprites/eye.png", ("right_facing",))
                eq_image_left.blit(eye_left, (0,0))
                eq_image_right.blit(eye_right, (0,0))
        return eq_image_left, eq_image_right, self.DRAW_LAYER

    def refresh_ammo(self):
        self.ammunition = getattr(self, 'AMMUNITION', None)

class Weapon(Equipment):
    IS_WEAPON = True
    DRAW_LAYER = 10
    UNDER_LIMB = True
    DAMAGE_RANGE = 1

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
        if self.ammunition is not None:
            if self.ammunition <= 0:
                # Out of ammunition, so we don't get to shoot.
                return
            else:
                self.ammunition -= 1
        if hasattr(self, 'HIT_SOUND'):
            sound.play_sound(self.HIT_SOUND)
        if hasattr(self, 'ANIMATION'):
            self.ANIMATION(gameboard.tv, wielder)
        training_bonus = getattr(wielder, 'TRAINING', 0)*10
        roll = random.randint(training_bonus + 1, 100)
        base_hit = self._get_parameter('BASE_HIT', wielder)
        range_penalty = self._get_parameter('RANGE_PENALTY', wielder)
        return roll > (100-base_hit) + range_penalty*wielder.pos.dist(target.pos)

    def damage_in_area(self, gameboard, wielder, target_pos):
        """For explosive weapons, affect foxes close to the target position"""
        if self.ammunition is not None:
            if self.ammunition <= 0:
                # Out of ammunition, so we don't get to shoot.
                return
            else:
                self.ammunition -= 1
        if hasattr(self, 'HIT_SOUND'):
            sound.play_sound(self.HIT_SOUND)
        if hasattr(self, 'ANIMATION'):
            self.ANIMATION(gameboard.tv, wielder)
        base_hit = self._get_parameter('BASE_HIT', wielder)
        range_penalty = self._get_parameter('RANGE_PENALTY', wielder)
        training_bonus = getattr(wielder, 'TRAINING', 0)*10
        roll = random.randint(training_bonus + 1, 100)
        damaged_foxes = set()
        for fox in gameboard.foxes:
            if target_pos.dist(fox.pos) <= self.DAMAGE_RANGE:
                damage_penalty = self.DAMAGE_RANGE_PENALTY * fox.pos.dist(target_pos)
                if roll > (100-base_hit) + range_penalty*(wielder.pos.dist(target_pos) + damage_penalty):
                    damaged_foxes.add(fox)
        for fox in damaged_foxes:
            fox.damage()

    def place(self, animal):
        for eq in animal.equipment:
            if is_weapon(eq):
                return False
        return True

class Knife(Weapon):
    TYPE = "KNIFE"
    NAME = "Knife"
    BUY_PRICE = 25
    SELL_PRICE = 15

    RANGE = 1
    BASE_HIT = 70
    RANGE_PENALTY = 0

    ANIMAL_IMAGE_FILE = 'sprites/equip_knife.png'


class Club(Weapon):
    TYPE = "CLUB"
    NAME = "Club"
    BUY_PRICE = 20
    SELL_PRICE = 12

    RANGE = 1
    BASE_HIT = 50
    RANGE_PENALTY = 0

    ANIMAL_IMAGE_FILE = 'sprites/equip_club.png'

class Axe(Weapon):
    TYPE = "AXE"
    NAME = "Axe"
    BUY_PRICE = 50
    SELL_PRICE = 30

    RANGE = 1
    BASE_HIT = 35
    RANGE_PENALTY = 0

    ANIMAL_IMAGE_FILE = 'sprites/equip_axe.png'

class Uniform(Equipment):
    IS_UNIFORM = True
    BUY_PRICE = 0
    SELL_PRICE = 0

    def place(self, animal):
        for eq in animal.equipment:
            if is_uniform(eq):
                return False
        return True

class LanceCorporalUniform(Uniform):
    NAME = "LanceCorporalUniform"
    ANIMAL_IMAGE_FILE = 'sprites/uniform_lance_corporal.png'

class CorporalUniform(Uniform):
    NAME = "CorporalUniform"
    ANIMAL_IMAGE_FILE = 'sprites/uniform_corporal.png'

class SergeantUniform(Uniform):
    NAME = "SergeantUniform"
    ANIMAL_IMAGE_FILE = 'sprites/uniform_sergeant.png'

class Disguise(Equipment):
    IS_DISGUISE = True

    def place(self, animal):
        for eq in animal.equipment:
            if is_disguise(eq):
                return False
        return True

class Cloak(Disguise):
    NAME = "Cloak"
    BUY_PRICE = 25
    SELL_PRICE = 15
    STEALTH_BONUS = 40

    ANIMAL_IMAGE_FILE = 'sprites/equip_cloak.png'

class FoxDisguise(Disguise):
    NAME = "Fox Disguise"
    BUY_PRICE = 60
    SELL_PRICE = 45
    STEALTH_BONUS = 70

    ANIMAL_IMAGE_FILE = 'sprites/equip_foxdisguise.png'

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

    ANIMAL_IMAGE_FILE = 'sprites/equip_helmet.png'
    UNDER_EYE = True

class Kevlar(Armour):
    NAME = "Kevlar"
    BUY_PRICE = 100
    SELL_PRICE = 75

    STARTING_HITPOINTS = 3

    ANIMAL_IMAGE_FILE = 'sprites/equip_kevlar.png'

class Shield(Armour):
    NAME = "Shield"
    BUY_PRICE = 50
    SELL_PRICE = 40
    STARTING_HITPOINTS = 2

    ANIMAL_IMAGE_FILE = 'sprites/equip_shield.png'

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
    ANIMAL_IMAGE_FILE = 'sprites/select_horse.png'
    DRAW_LAYER = -5

class Nest(Accoutrement):
    NAME = "Nest"
    ANIMAL_IMAGE_FILE = 'sprites/nest.png'
    DRAW_LAYER = 15

class NestEgg(Accoutrement):
    NAME = "Nestegg"
    ANIMAL_IMAGE_FILE = 'sprites/equip_egg.png'
    DRAW_LAYER = 14

def is_equipment(obj):
    """Return true if obj is an equipment class."""
    return getattr(obj, "IS_EQUIPMENT", False) and hasattr(obj, "NAME")

def is_weapon(obj):
    return is_equipment(obj) and getattr(obj, 'IS_WEAPON', False)

def is_uniform(obj):
    return is_equipment(obj) and getattr(obj, 'IS_UNIFORM', False)

def is_disguise(obj):
    return is_equipment(obj) and getattr(obj, 'IS_DISGUISE', False)

def is_armour(obj):
    return is_equipment(obj) and getattr(obj, 'IS_ARMOUR', False)

def is_accoutrement(obj):
    return not getattr(obj, "IS_EQUIPMENT", False) and hasattr(obj, "NAME") and getattr(obj, 'IS_ACCOUTREMENT', False)

EQUIPMENT = []
for name in dir():
    obj = eval(name)
    try:
        if is_equipment(obj) and obj.BUY_PRICE != 0:
            EQUIPMENT.append(obj)
    except TypeError:
        pass


EQUIP_MAP = { # Map horse level codes to equipment
        1  : [],
        2  : [Helmet],
        3  : [Kevlar],
        4  : [Knife],
        5  : [], # TODO: Add in Sword
        6  : [Kevlar, Helmet],
        7  : [Helmet, Knife],
        8  : [Kevlar, Knife],
        9  : [Kevlar, Helmet, Knife],
        10 : [Helmet], # TODO: Add in Sword
        11 : [Kevlar], # TODO: Add in Sword
        12 : [Kevlar, Helmet], # TODO: Add in Sword
        13 : [Axe],
        14 : [Helmet, Axe],
        15 : [Kevlar, Axe],
        16 : [Kevlar, Helmet, Axe],
        }

from . import eegg
if eegg.is_eggday():
    NestEgg.ANIMAL_IMAGE_FILE = 'sprites/equip_easter_egg.png'
