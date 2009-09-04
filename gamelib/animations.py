"""Animation Loops"""

from pgu.vid import Sprite

import imagecache
from misc import Position

class Animation(Sprite):
    """Animation loop.

       These are derived from sprites, since they behave similiary in most
       respects, but, to ensure draw ordering, we don't add them to
       the sprites list.
       
       Ideally, animations should be quite short."""

    def __init__(self, sequence, tile_pos):
        # Create the first frame
        self.iter = iter(sequence)
        Sprite.__init__(self, self.iter.next(), (-1000, -1000))
        if hasattr(tile_pos, 'to_tuple'):
            self.pos = tile_pos
        else:
            self.pos = Position(tile_pos[0], tile_pos[1])
        self.removed = False

    def fix_pos(self, tv):
        ppos = tv.tile_to_view(self.pos.to_tuple())
        self.rect.x = ppos[0]
        self.rect.y = ppos[1]

    def animate(self):
        """Step to the next frame.

           Set removed flag when we hit the end of the sequence"""
        try:
            self.setimage(self.iter.next())
        except StopIteration:
            self.removed = True

class MuzzleFlash(Animation):

    SEQUENCE_LEFT = [imagecache.load_image('sprites/muzzle_flash.png')]
    SEQUENCE_RIGHT = [imagecache.load_image('sprites/muzzle_flash.png',
        ("right_facing",))]

    def __init__(self, chicken):
        if chicken.facing == 'right':
            Animation.__init__(self, self.SEQUENCE_RIGHT, chicken.pos)
        else:
            Animation.__init__(self, self.SEQUENCE_LEFT, chicken.pos)

