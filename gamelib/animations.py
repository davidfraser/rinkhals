"""Animation Loops"""

from pgu.vid import Sprite

from . import imagecache

class Animation(Sprite):
    """Animation loop.

       These are derived from sprites, since they behave similiary in most
       respects. Ideally, animations should be quite short."""
       # In the current implementation, sequences longer than 4 frames
       # will overrun the next move loop.
       # (assuming all animations are triggered by the move loop, of course)

    def __init__(self, tv, tile_pos, sequence=None, layer='animations'):
        # Create the first frame
        if sequence is None:
            sequence = self.SEQUENCE
        self.iter = iter(sequence)
        self.layer = layer
        Sprite.__init__(self, next(self.iter), tv.tile_to_view(tile_pos))
        tv.sprites.append(self, layer=self.layer)

    def loop(self, tv, s):
        """Step to the next frame, removing sprite when done."""
        try:
            self.setimage(next(self.iter))
        except StopIteration:
            tv.sprites.remove(self, layer=self.layer)

class WeaponAnimation(Animation):
    def __init__(self, tv, wielder, layer='animations'):
        if wielder.facing == 'right':
            Animation.__init__(self, tv, wielder.pos.to_tile_tuple(), self.SEQUENCE_RIGHT, layer=layer)
        else:
            Animation.__init__(self, tv, wielder.pos.to_tile_tuple(), self.SEQUENCE_LEFT, layer=layer)


class MuzzleFlash(WeaponAnimation):
    FLASH_LEFT = imagecache.load_image('sprites/muzzle_flash.png')
    FLASH_RIGHT = imagecache.load_image('sprites/muzzle_flash.png', ("right_facing",))
    SEQUENCE_LEFT = [FLASH_LEFT, FLASH_LEFT]
    SEQUENCE_RIGHT = [FLASH_RIGHT, FLASH_RIGHT]

class FenceExplosion(Animation):
    FLASH_1 = imagecache.load_image('sprites/boom1.png')
    FLASH_2 = imagecache.load_image('sprites/boom2.png')
    FLASH_3 = imagecache.load_image('sprites/boom3.png')
    FLASH_4 = imagecache.load_image('sprites/boom4.png')
    SEQUENCE = [FLASH_1, FLASH_2, FLASH_3, FLASH_4]

class FoxDeath(Animation):
    BLOOD_SPLAT = imagecache.load_image('sprites/fox_death.png')
    SEQUENCE = [BLOOD_SPLAT, BLOOD_SPLAT]
    
class ChickenDeath(Animation):
    BLOOD_SPLAT = imagecache.load_image('sprites/fox_death.png')
    FEATHER_SPLAT = imagecache.load_image('sprites/chkn_death.png')
    SEQUENCE = [BLOOD_SPLAT, FEATHER_SPLAT, FEATHER_SPLAT]
