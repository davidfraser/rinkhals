"""Extension to pgu's tilevid."""

import random
import os

from pgu import tilevid, vid
from . import data
from . import imagecache
from . import serializer

class TileMap(object):
    """Helper class for describing all the game tiles."""

    # number -> (name, image file name)
    DEFAULT_TILES = {
        0: ("woodland", "woodland.png"),
        1: ("grassland", "grassland.png"),
        2: ("fence", "fence.png"),
        3: ("henhouse", "grassland.png"),
        4: ("watchtower", "grassland.png"),
        5: ("broken fence", "broken_fence.png"),
        6: ("hendominium", "grassland.png"),
        7: ("trap", "trap.png"),
        8: ("barracks", "grassland.png"),
    }

    ALTERNATE_TILES = {
        255: ("woodland", "woodland.png"),
        254: ("woodland", "woodland2.png"),
        253: ("woodland", "woodland3.png"),
        }        

    def __init__(self, tiles=None, alternate_tiles=None):
        if tiles is None:
            tiles = self.DEFAULT_TILES.copy()
        if alternate_tiles is None:
            alternate_tiles = self.ALTERNATE_TILES.copy()
        self._alternate_tiles = alternate_tiles
        self._tiles = tiles
        self._reverse_map = dict((v[0], k) for k, v in list(self._tiles.items()))
        self._tiles.update(alternate_tiles)

    def __getitem__(self, n):
        """Get the string name of tile n."""
        return self._tiles[n][0]

    def tiles_for_image(self, image_name):
        """Return tile numbers associated with the given image name."""
        for n, (name, image) in list(self._tiles.items()):
            if image_name == image:
                yield n

    def random_alternate(self, n):
        alts = [a for a, (name, image) in list(self._alternate_tiles.items()) if name == self[n]]
        if alts:
            return random.choice(alts)
        return n

TILE_MAP = TileMap()
REVERSE_TILE_MAP = TILE_MAP._reverse_map


class LayeredSprites(object):
    # This is as small a subset of list behaviour as we can get away with.
    # WARNING: It makes assumptions that may not be justified in the general case.
    # Caveat utilitor and all the rest.

    def __init__(self, layers=None, default_layer=None):
        # Layers are ordered from bottom to top.
        if layers is None:
            layers = ['default']
        self.layers = layers
        if default_layer is None:
            default_layer = layers[0]
        self.default_layer = default_layer
        self._sprites = {}
        for layer in layers:
            self._sprites[layer] = []
        self.removed = []

    def append(self, sprite, layer=None):
        if layer is None:
            layer = self.default_layer
        self._sprites[layer].append(sprite)
        sprite.updated = 1

    def remove(self, sprite, layer=None):
        if layer is None:
            layer = self.default_layer
        self._sprites[layer].remove(sprite)
        sprite.updated = 1
        self.removed.append(sprite)

    def __getitem__(self, key):
        # vid.py uses sprites[:] to get a mutation-safe list copy, so we need this.
        # No other indexing or slicing operations make sense.
        if not isinstance(key, slice):
            raise IndexError('[:] is the only supported slice/index operation.')
        return iter(self)

    def __iter__(self):
        # We iterate over all sprites in layer order.
        for layer in self.layers:
            for sprite in self._sprites[layer]:
                yield sprite


class FarmVid(tilevid.Tilevid, serializer.Simplifiable):
    """Extension of pgu's TileVid class to handle the complications
       of raising chickens.
       """

    SIMPLIFY = [
        'size',
        'layers',
        'tlayer',
        'alayer',
        'blayer',
        'clayer',
    ]

    def __init__(self):
        tilevid.Tilevid.__init__(self)
        self.sprites = LayeredSprites(['buildings', 'animals', 'animations', 'cursor'], 'animals')

    @classmethod
    def make(cls):
        """Override default Simplifiable object creation."""
        return cls()

    @classmethod
    def unsimplify(cls, *args, **kwargs):
        """Override default Simplifiable unsimplification."""
        obj = serializer.Simplifiable.unsimplify(*args, **kwargs)

        obj.view.x, obj.view.y = 0,0
        obj._view.x, obj._view.y = 0,0
        obj.bounds = None
        obj.updates = []

        return obj

    def tga_load_level(self, level_map):
        tilevid.Tilevid.tga_load_level(self, level_map)
        for xy in [(x, y) for x in range(self.size[0]) for y in range(self.size[1])]:
            self.set(xy, TILE_MAP.random_alternate(self.get(xy)))

    def png_folder_load_tiles(self, path):
        """Load tiles from a folder of PNG files."""
        full_path = data.filepath(path)
        for dirpath, dirnames, filenames in os.walk(full_path):
            relative_path = dirpath[len(full_path):]
            relative_path = "/".join(relative_path.split(os.path.sep))
            for filename in filenames:
                image_name = "/".join([path, relative_path, filename])
                for tile_no in TILE_MAP.tiles_for_image(filename):
                    tile_name = TILE_MAP[tile_no]
                    self.tiles[tile_no] = FarmTile(tile_no, tile_name, image_name)

    def sun(self, sun_on):
        """Make it night."""
        for tile in self.tiles:
            if hasattr(tile, "sun"):
                tile.sun(sun_on)
        for sprite in self.sprites:
            if hasattr(sprite, "sun"):
                sprite.sun(sun_on)

class FarmTile(vid.Tile):

    def __init__(self, tile_no, tile_name, image_name):
        self.tile_no = tile_no
        self.tile_name = tile_name
        self.day_image = imagecache.load_image(image_name)
        self.night_image = imagecache.load_image(image_name, ("night",))
        vid.Tile.__init__(self, self.day_image)

    def sun(self, sun_on):
        if sun_on:
            self.image = self.day_image
        else:
            self.image = self.night_image
