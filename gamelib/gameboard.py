import random

from pgu import gui, tilevid

import data


class GameBoard(object):
    TILE_DIMENSIONS = (20, 20)

    def __init__(self):
        self.tv = tilevid.Tilevid()
        self.tv.tga_load_tiles(data.filepath('tiles.tga'), self.TILE_DIMENSIONS)
        self.tv.tga_load_level(data.filepath('level1.tga'))

        self.tools = tilevid.Tilevid()
        self.tools.tga_load_tiles(data.filepath('tiles.tga'), self.TILE_DIMENSIONS)
        self.tools.resize((1, 2))
        self.populate_toolbar()

    def populate_toolbar(self):
        self.tools.set((0,0), 2)
        self.tools.set((0,1), 3)

    def split_screen(self, screen):
        leftbar_rect = screen.get_rect()
        leftbar_rect.width = self.TILE_DIMENSIONS[0] + 2
        main_rect = screen.get_rect()
        main_rect.width -= leftbar_rect.width
        main_rect.left += leftbar_rect.width
        return screen.subsurface(leftbar_rect), screen.subsurface(main_rect)

    def paint(self, screen):
        leftbar, main = self.split_screen(screen)
        self.tools.paint(leftbar)
        self.tv.paint(main)

    def update_vid(self, vid, subsurface):
        offset = subsurface.get_offset()
        return [r.move(offset) for r in vid.update(subsurface)]

    def update(self, screen):
        leftbar, main = self.split_screen(screen)
        updates = []
        updates.extend(self.update_vid(self.tools, leftbar))
        updates.extend(self.update_vid(self.tv, main))
        return updates

    def loop(self):
        x = random.randint(0, self.tv.size[0]-1)
        y = random.randint(0, self.tv.size[1]-1)
        tile = random.randint(0, 4)
        self.tv.set((x, y), tile)

    def event(self, e):
        pass
