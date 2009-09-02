"""Extension to pgu's tilevid."""

from pgu import tilevid, vid
import os
import imagecache

class TileMap(object):
    """Helper class for describing all the game tiles."""

    # number -> (name, image file name)
    DEFAULT_TILES = {
        0: ("woodland", "woodland.png"),
        1: ("grassland", "grassland.png"),
        2: ("fence", "fence.png"),
        3: ("henhouse", "grassland.png"),
        4: ("guardtower", "guardtower.png"),
        5: ("broken fence", "broken_fence.png"),
        6: ("hendominium", "grassland.png"),
    }

    def __init__(self, tiles=None):
        if tiles is None:
            tiles = self.DEFAULT_TILES.copy()
        self._tiles = tiles
        self._reverse_map = dict((v[0], k) for k, v in self._tiles.iteritems())

    def __getitem__(self, n):
        """Get the string name of tile n."""
        return self._tiles[n][0]

    def tile_number(self, name):
        """Return the tile number of the tile with the given name."""
        return self._reverse_map[name]

    def tiles_for_image(self, image_name):
        """Return tile numbers associated with the given image name."""
        for n, (name, image) in self._tiles.iteritems():
            if image_name == image:
                yield n

TILE_MAP = TileMap()
REVERSE_TILE_MAP = TILE_MAP._reverse_map


class FarmVid(tilevid.Tilevid):
    """Extension of pgu's TileVid class to handle the complications
       of raising chickens.
       """
    def __init__(self):
        tilevid.Tilevid.__init__(self)

    def png_folder_load_tiles(self, path):
        """Load tiles from a folder of PNG files."""
        for dirpath, dirnames, filenames in os.walk(path):
            abstract_dirpath = "/".join(dirpath.split(os.path.sep))
            for filename in filenames:
                image_name = abstract_dirpath + "/" + filename
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
