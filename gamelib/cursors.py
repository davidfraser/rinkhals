"""Data for the in game cursors"""

import pygame

import data


cursors = {
        'arrow' : pygame.cursors.arrow,
        'select' : pygame.cursors.broken_x,
        }

for tag, filename in [
        ('chicken', 'cursors/chkn.xbm'),
        ('rifle', 'cursors/equip_rifle.xbm'),
        ('knife', 'cursors/equip_knife.xbm'),
        ]:
    path = data.filepath(filename)
    # pygame 1.8 needs the file twice to do the right thing
    # XXX: check behaviour with pygame 1.9
    cursors[tag] = pygame.cursors.load_xbm(path, path)


