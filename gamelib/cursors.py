"""Data for the in game cursors"""

import pygame

from . import data


cursors = {
        'arrow' : pygame.cursors.arrow,
        'select' : pygame.cursors.broken_x,
        'ball': pygame.cursors.ball,
        }

for tag, filename in [
        ('chicken', 'cursors/chkn.xbm'),
        ('sell', 'cursors/sell_cursor.xbm'),
        ('repair', 'cursors/repair_cursor.xbm'),
        ]:
    path = data.filepath(filename)
    # pygame 1.8 needs the file twice to do the right thing
    # XXX: check behaviour with pygame 1.9
    cursors[tag] = pygame.cursors.load_xbm(path, path)


