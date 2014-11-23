#!/usr/bin/env python

import os.path

import pygame
from pygame.locals import SWSURFACE, SRCALPHA

from gamelib import tiles, buildings, equipment
import regenerate_pngs

LEVEL_PATH = "data/levels"
TILE_WIDTH = 20
TILE_HEIGHT = 20
TILES_X = 8
TILES_Y = 8
WIDTH = TILES_X * TILE_WIDTH
HEIGHT = TILES_Y * TILE_HEIGHT

def generate_image(name, basepath):
    fn, _ = os.path.splitext(os.path.basename(name))
    svg_name = os.path.join(basepath, fn+".svg")
    if not os.path.exists(svg_name):
        print 'Skipping %s, as it seems to be missing' % svg_name
        return None
    png_name = os.path.join(LEVEL_PATH, fn+".png")
    regenerate_pngs.svg_to_png(svg_name, png_name, TILE_WIDTH, TILE_HEIGHT)
    return pygame.image.load(png_name)

def get_tile_mappings():
    tile_map = {}
    for building in buildings.BUILDINGS:
        tn = building.TILE_NO
        image = generate_image(building.IMAGE, regenerate_pngs.SPRITE_PATH)
        if image:
            tile_map[tn] = image
    for tn, (_, tile_png) in tiles.TileMap.DEFAULT_TILES.items():
        if tn not in tile_map:
            tile_map[tn] = generate_image(tile_png, regenerate_pngs.TILE_PATH)
    return tile_map

def get_code_mappings():
    code_map = {}
    # Needs better handling of wings
    for tn, sprites in equipment.EQUIP_MAP.iteritems():
        image = generate_image('chkn', regenerate_pngs.SPRITE_PATH)
        need_wing = False
        for equip in sprites:
            sub_image = generate_image(equip.ANIMAL_IMAGE_FILE,
                    regenerate_pngs.SPRITE_PATH)
            image.blit(sub_image, (0, 0))
            if equip.UNDER_LIMB:
                need_wing = True
        if need_wing:
            sub_image = generate_image('wing', regenerate_pngs.SPRITE_PATH)
            image.blit(sub_image, (0, 0))
        if image:
            code_map[tn] = image
    return code_map

if __name__ == '__main__':
    s = pygame.Surface((WIDTH, HEIGHT), SWSURFACE|SRCALPHA, 32)
    s.fill((0,0,0,0))
    for n, img in get_tile_mappings().items():
        rect = (TILE_WIDTH*(n % TILES_X), TILE_HEIGHT*(n / TILES_X), TILE_WIDTH, TILE_HEIGHT)
        print n, rect
        s.blit(img, rect)
    pygame.image.save(s, os.path.join(LEVEL_PATH, "tiles.tga"))
    s.fill((0,0,0,0))
    for n, img in get_code_mappings().items():
        rect = (TILE_WIDTH*(n % TILES_X), TILE_HEIGHT*(n / TILES_X), TILE_WIDTH, TILE_HEIGHT)
        print n, rect
        s.blit(img, rect)
    pygame.image.save(s, os.path.join(LEVEL_PATH, "codes.tga"))
