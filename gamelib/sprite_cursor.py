"""In-game sprite cursors for the gameboard.

   Currently mostly used when placing buildings.
   """

import pygame
from pygame.locals import SRCALPHA

from . import imagecache
from . import constants
from pgu.vid import Sprite

# ignore os.popen3 warning generated by pygame.font.SysFont
import warnings
warnings.filterwarnings("ignore", "os.popen3 is deprecated.")

class SpriteCursor(Sprite):
    """A Sprite used as an on-board cursor.
       """

    def __init__(self, image_name, tv, cost=None):
        self._font = pygame.font.SysFont('Vera', 20, bold=True)
        image = imagecache.load_image(image_name, ["sprite_cursor"])

        if cost is not None:
            image = self._apply_text(image, str(cost))

        # Create the sprite somewhere far off screen
        Sprite.__init__(self, image, (-1000, -1000))
        self._tv = tv

    def _apply_text(self, image, stext):
        """Apply the text to the image."""
        image = image.copy()
        text = self._font.render(stext, True, constants.FG_COLOR)
        w, h = image.get_size()
        x, y = text.get_size()
        image.blit(text, (w - x, h - y))
        return image

    def set_pos(self, tile_pos):
        """Set the cursor position on the gameboard."""
        self.rect.x, self.rect.y = self._tv.tile_to_view(tile_pos)

class SmallSpriteCursor(SpriteCursor):
    """A sprite cursor for use with images too small for the associated text."""

    def _apply_text(self, image, stext):
        text = self._font.render(stext, True, constants.FG_COLOR)
        w, h = image.get_size()
        x, y = text.get_size()

        new_w, new_h = w + x, max(h, y)

        new_image = pygame.Surface((new_w, new_h), SRCALPHA)
        new_image.blit(image, (0, 0))
        new_image.blit(text, (w, new_h - y))
        return new_image
