#!/usr/bin/env python

import cairosvg
import os
from gamelib import constants

def svg_to_png(svg_name, png_name, w, h):
    """Convert an SVG file to a PNG file."""
    print("Generating %s at %dx%d..." % (png_name, w, h))
    cairosvg.svg2png(url=svg_name, output_width=w, output_height=h, write_to=png_name)

def process_svg_folder(path, width, height):
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            basename, ext = os.path.splitext(filename)
            if ext == ".svg":
                svg_name = os.path.join(dirpath, basename + ".svg")
                png_name = os.path.join(dirpath, basename + ".png")
                svg_to_png(svg_name, png_name, width, height)

def process_sprite(name, width, height, sprite_path):
    svg_name = os.path.join(sprite_path, name) + ".svg"
    png_name = os.path.join(sprite_path, name) + ".png"
    svg_to_png(svg_name, png_name, width, height)

TILE_PATH = "data/tiles"
SPRITE_PATH = "data/sprites"
IMAGE_PATH = "data/images"

BASE_X, BASE_Y = constants.TILE_DIMENSIONS
SPRITES = [
    # horse bits
    ("horse", BASE_X, BASE_Y),
    ("stallion", BASE_X, BASE_Y),
    ("stealth_horse", BASE_X, BASE_Y),
    ("furry_stallion", BASE_X, BASE_Y),
    ("eye", BASE_X, BASE_Y),
    ("equip_club", BASE_X, BASE_Y),
    ("equip_knife", BASE_X, BASE_Y),
    ("uniform_lance_corporal", BASE_X, BASE_Y),
    ("uniform_corporal", BASE_X, BASE_Y),
    ("uniform_sergeant", BASE_X, BASE_Y),
    ("equip_cloak", BASE_X, BASE_Y),
    ("equip_orcdisguise", BASE_X, BASE_Y),
    ("equip_kevlar", BASE_X, BASE_Y),
    ("equip_helmet", BASE_X, BASE_Y),
    ("equip_axe", BASE_X, BASE_Y),
    ("equip_shield", BASE_X, BASE_Y),
    ("select_horse", BASE_X, BASE_Y),
    ("nest", BASE_X, BASE_Y),
    ("equip_egg", BASE_X, BASE_Y),
    ("equip_easter_egg", BASE_X, BASE_Y),
    ("equip_stealth_egg", BASE_X, BASE_Y),
    ("equip_furry_egg", BASE_X, BASE_Y),
    # orc bits
    ("orc", BASE_X, BASE_Y),
    ("greedy_orc", BASE_X, BASE_Y),
    ("ninja_orc", BASE_X, BASE_Y),
    ("sapper_orc", BASE_X, BASE_Y),
    ("robber_orc", BASE_X, BASE_Y),
    ("rinkhals", BASE_X, BASE_Y),
    ("mongoose", BASE_X, BASE_Y),
    # buildings
    ("henhouse", BASE_X*3, BASE_Y*2),
    ("select_henhouse", BASE_X*3, BASE_Y*2),
    ("hendominium", BASE_X*2, BASE_Y*3),
    ("select_hendominium", BASE_X*2, BASE_Y*3),
    ("watchtower", BASE_X*2, BASE_Y*2),
    ("select_watchtower", BASE_X*2, BASE_Y*2),
    ("barracks", BASE_X*3, BASE_Y*3),
    ("select_barracks", BASE_X*3, BASE_Y*3),
    # special effects
    ("muzzle_flash", BASE_X, BASE_Y),
    ("horse_death", BASE_X, BASE_Y),
    ("orc_death", BASE_X, BASE_Y),
    ("boom1", BASE_X, BASE_Y),
    ("boom2", BASE_X, BASE_Y),
    ("boom3", BASE_X, BASE_Y),
    ("boom4", BASE_X, BASE_Y),
]

if __name__ == "__main__":
    process_svg_folder("data/tiles", BASE_X, BASE_Y)
    process_svg_folder("data/icons", BASE_X*2, BASE_Y*2)
    for name, width, height in SPRITES:
        process_sprite(name, width, height, SPRITE_PATH)
    process_sprite("splash", constants.SCREEN[0], constants.SCREEN[1], IMAGE_PATH)
    process_sprite("gameover_win", constants.SCREEN[0], constants.SCREEN[1], IMAGE_PATH)
    process_sprite("gameover_lose", constants.SCREEN[0], constants.SCREEN[1], IMAGE_PATH)

