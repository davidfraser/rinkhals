"""Extension to pgu's tilevid."""

from pgu import tilevid, vid
import os
import imagecache

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
            abstract_dirpath = "/".join(dirpath.split(os.path.sep))
            for filename in filenames:
                basename, ext = os.path.splitext(filename)
                if ext != ".png":
                    continue
                if basename in REVERSE_TILE_MAP:
                    n = REVERSE_TILE_MAP[basename]
                    self.tiles[n] = FarmTile(abstract_dirpath + "/" + filename)

    def sun(self, sun_on):
        """Make it night."""
        for tile in self.tiles:
            if hasattr(tile, "sun"):
                tile.sun(sun_on)
        for sprite in self.sprites:
            if hasattr(sprite, "sun"):
                sprite.sun(sun_on)

class FarmTile(vid.Tile):

    def __init__(self, image_name):
        self.day_image = imagecache.load_image(image_name)
        self.night_image = imagecache.load_image(image_name, ("night",))
        vid.Tile.__init__(self, self.day_image)

    def sun(self, sun_on):
        if sun_on:
            self.image = self.day_image
        else:
            self.image = self.night_image
