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
       # In the current implementation, sequences longer than 4 frames
       # will cause issues as this will overrun the next move loop.
       # (assuming all animations are triggered by the move loop, of course)

    def __init__(self, tile_pos, sequence=None):
        # Create the first frame
        if sequence is None:
            sequence = self.SEQUENCE
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

    FLASH_LEFT = imagecache.load_image('sprites/muzzle_flash.png')
    FLASH_RIGHT = imagecache.load_image('sprites/muzzle_flash.png',
            ("right_facing",))

    SEQUENCE_LEFT = [FLASH_LEFT, FLASH_LEFT]
    SEQUENCE_RIGHT = [FLASH_RIGHT, FLASH_RIGHT]

    def __init__(self, chicken):
        if chicken.facing == 'right':
            Animation.__init__(self, chicken.pos, self.SEQUENCE_RIGHT)
        else:
            Animation.__init__(self, chicken.pos, self.SEQUENCE_LEFT)

class FenceExplosion(Animation):
    FLASH_LEFT = imagecache.load_image('sprites/muzzle_flash.png')
    FLASH_RIGHT = imagecache.load_image('sprites/muzzle_flash.png',
            ("right_facing",))
    SEQUENCE = [FLASH_LEFT, FLASH_RIGHT, FLASH_LEFT, FLASH_RIGHT]

class FoxDeath(Animation):
    BLOOD_SPLAT = imagecache.load_image('sprites/fox_death.png')
    SEQUENCE = [BLOOD_SPLAT, BLOOD_SPLAT]
    
class ChickenDeath(Animation):
    BLOOD_SPLAT = imagecache.load_image('sprites/fox_death.png')
    FEATHER_SPLAT = imagecache.load_image('sprites/chkn_death.png')
    SEQUENCE = [BLOOD_SPLAT, FEATHER_SPLAT, FEATHER_SPLAT]
