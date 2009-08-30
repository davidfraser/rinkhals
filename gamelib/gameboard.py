import random

from pgu import tilevid

import data


class GameBoard(object):
    TILE_DIMENSIONS = (20, 20)

    def __init__(self):
        self.tv = tilevid.Tilevid()
        self.tv.tga_load_tiles(data.filepath('tiles.tga'), self.TILE_DIMENSIONS)
        self.tv.tga_load_level(data.filepath('level1.tga'))

    def paint(self, screen):
        self.tv.paint(screen)

    def update(self, screen):
        return self.tv.update(screen)

    def loop(self):
        x = random.randint(0, self.tv.size[0]-1)
        y = random.randint(0, self.tv.size[1]-1)
        tile = random.randint(0, 4)
        self.tv.set((x, y), tile)

