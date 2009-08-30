"""Extension to pgu's tilevid."""

from pgu import tilevid, vid
import pygame
from pygame.locals import BLEND_RGBA_MULT
import os

TILE_MAP = {
    0: "woodland",
    1: "grassland",
    2: "fence",
    3: "henhouse",
    4: "chicken",
}

REVERSE_TILE_MAP = dict((v, k) for k, v in TILE_MAP.iteritems())

class FarmVid(tilevid.Tilevid):
    """Extension of pgu's TileVid class to handle the complications
       of raising chickens.
       """
    def __init__(self):
        tilevid.Tilevid.__init__(self)

    def png_folder_load_tiles(self, path):
        """Load tiles from a folder of PNG files."""
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                basename, ext = os.path.splitext(filename)
                if ext != ".png":
                    continue
                if basename in REVERSE_TILE_MAP:
                    n = REVERSE_TILE_MAP[basename]
                    img = pygame.image.load(os.path.join(dirpath, filename)).convert_alpha()
                    self.tiles[n] = FarmTile(img)

    def sun(self, sun_on):
        """Make it night."""
        for tile in self.tiles:
            if hasattr(tile, "sun"):
                tile.sun(sun_on)
        for sprite in self.sprites:
            if hasattr(sprite, "sun"):
                sprite.sun(sun_on)

class FarmTile(vid.Tile):

    NIGHT_COLOUR = (100.0, 100.0, 200.0, 255.0)

    def __init__(self, image):
        self.day_image = image
        self.night_image = image.copy()
        self.night_image.fill(self.NIGHT_COLOUR, None, BLEND_RGBA_MULT)
        self.image = self.day_image

    def sun(self, sun_on):
        if sun_on:
            self.image = self.day_image
        else:
            self.image = self.night_image
