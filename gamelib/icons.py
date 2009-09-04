"""Constant definitions for the icons we use"""

from pgu.gui import Image

import imagecache

KILLED_FOX = Image(imagecache.load_image('icons/killed_fox.png'))
CHKN_ICON = Image(imagecache.load_image('icons/chkn.png'))
EMPTY_NEST_ICON = Image(imagecache.load_image('sprites/nest.png'))

def animal_icon(animal):
    return Image(animal.image_left)
