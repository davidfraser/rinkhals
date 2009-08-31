"""Central image cache to avoid loading images multiple times."""

import pygame
import data

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

from pygame.locals import BLEND_RGBA_MULT
NIGHT_COLOUR = (100.0, 100.0, 200.0, 255.0)

def convert_to_night(image):
    """Convert a day tile to a night tile."""
    night_image = image.copy()
    night_image.fill(NIGHT_COLOUR, None, BLEND_RGBA_MULT)
    return night_image

# globals

cache = ImageCache()
cache.register_modifier("night", convert_to_night)
load_image = cache.load_image
