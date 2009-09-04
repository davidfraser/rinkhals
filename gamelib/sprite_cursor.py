"""In-game sprite cursors for the gameboard.

   Currently mostly used when placing buildings.
   """

import imagecache
from pgu.vid import Sprite

class SpriteCursor(Sprite):
    """A Sprite used as an on-board cursor."""

    def __init__(self, image_name, tv):
        image = imagecache.load_image(image_name, ["sprite_cursor"])
        # Create the sprite somewhere far off screen
        Sprite.__init__(self, image, (-1000, -1000))
        self._tv = tv

    def set_pos(self, tile_pos):
        """Set the cursor position on the gameboard."""
        self.rect.x, self.rect.y = self._tv.tile_to_view(tile_pos)
