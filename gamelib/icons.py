"""Constant definitions for the icons we use"""

from pgu.gui import Image

from . import imagecache

KILLED_FOX = Image(imagecache.load_image('icons/killed_fox.png'))
HORSE_ICON = Image(imagecache.load_image('icons/horse.png'))
EGG_ICON = Image(imagecache.load_image('icons/egg.png'))
WOOD_ICON = Image(imagecache.load_image('icons/wood.png'))
GROATS_ICON = Image(imagecache.load_image('icons/groats.png'))
EMPTY_NEST_ICON = Image(imagecache.load_image('sprites/nest.png'))
DAY_ICON = Image(imagecache.load_image('icons/sun.png'))

def animal_icon(animal):
    return Image(animal.image_left)

from . import eegg
if eegg.is_eggday():
    EGG_ICON = Image(imagecache.load_image('icons/easter_egg.png'))
