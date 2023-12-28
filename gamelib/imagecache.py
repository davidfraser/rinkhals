"""Central image cache to avoid loading images multiple times."""

import pygame
from . import data

class ImageCache(object):
    """Create an image cache with a list of modifiers."""

    def __init__(self):
        # (image name, ordered modifiers tuple) -> pygame surface
        self._cache = {}
        self._modifiers = {}

    def register_modifier(self, name, function):
        """Register a post-load modifying function."""
        if name in self._modifiers:
            raise ValueError("Attempt to re-register and existing modifier function.")
        self._modifiers[name] = function

    def load_image(self, name, modifiers=None):
        """Load an image from disk or return a cached image.

           name: image name relative to data path.
           modifers: ordered list of modifiers to apply.
           """
        # convert lists to tuples
        if modifiers is not None:
            modifiers = tuple(modifiers)

        # convert empty tuples to None
        if not modifiers:
            modifiers = None

        # look for modified image
        key = (name, modifiers)
        if key in self._cache:
            return self._cache[key]

        # look for unmodified image
        base_key = (name, None)
        if base_key in self._cache:
            image = self._cache[base_key]
        else:
            image = pygame.image.load(data.filepath(name))
            self._cache[base_key] = image

        # handle unmodified case
        if modifiers is None:
            return image

        for mod in modifiers:
            image = self._modifiers[mod](image)

        self._cache[key] = image
        return image

# modifiers

from pygame.locals import BLEND_MULT, BLEND_ADD, BLEND_RGBA_MULT
NIGHT_COLOUR = (100.0, 100.0, 200.0, 255.0)
DARKEN_COLOUR = (100.0, 100.0, 100.0, 255.0)
LIGHTEN_COLOUR = (200.0, 200.0, 200.0, 225.0)

def convert_to_night(image):
    """Convert a day tile to a night tile."""
    night_image = image.copy()
    night_image.fill(NIGHT_COLOUR, None, BLEND_MULT)
    return night_image

def convert_to_right_facing(image):
    right_facing_image = image.copy()
    right_facing_image = pygame.transform.flip(right_facing_image, 1, 0)
    return right_facing_image

def darken_center(image):
    darkened = image.copy()
    w, h = darkened.get_size()
    fraction = 0.65
    offset = (1.0 - fraction) / 2.0
    over_w, over_h = int(w*fraction), int(h*fraction)
    over_x, over_y = int(w*offset), int(h*offset)
    overlay = pygame.Surface((over_w, over_h))
    overlay.fill(DARKEN_COLOUR)
    darkened.blit(overlay, (over_x, over_y), None, BLEND_MULT)
    return darkened

def lighten_most(image):
    lighten = image.copy()
    w, h = lighten.get_size()
    over_w, over_h = int(w*0.9), int(h*0.9)
    over_x, over_y = int(w*0.05), int(h*0.05)
    overlay = pygame.Surface((over_w, over_h))
    overlay.fill(LIGHTEN_COLOUR)
    lighten.blit(overlay, (over_x, over_y), None, BLEND_ADD)
    return lighten

def sprite_cursor(image):
    cursor = image.copy()
    cursor.fill((255, 255, 255, 100), None, BLEND_RGBA_MULT)
    return cursor

# globals

cache = ImageCache()
cache.register_modifier("night", convert_to_night)
cache.register_modifier("right_facing", convert_to_right_facing)
cache.register_modifier("darken_center", darken_center)
cache.register_modifier("lighten_most", lighten_most)
cache.register_modifier("sprite_cursor", sprite_cursor)
load_image = cache.load_image
