#!/usr/bin/env python

import cairo
import rsvg
import os
from Image import open

def svg_to_png(svg_name, png_name, w, h):
    """Convert an SVG file to a PNG file."""
    print "Generating %s at %dx%d..." % (png_name, w, h)
    r = rsvg.Handle(svg_name)

    scale = max(float(r.props.width) / w, float(r.props.height) / h)
    scale = 1.0 / scale

    r.props.dpi_x = r.props.dpi_x / scale
    r.props.dpi_y = r.props.dpi_y / scale

    cs = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(cs)
    ctx.scale(scale, scale)
    r.render_cairo(ctx)
    cs.write_to_png(png_name)

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

SPRITES = [
    # chicken bits
    ("chkn", 20, 20),
    ("wing", 20, 20),
    ("eye", 20, 20),
    ("equip_rifle", 20, 20),
    ("equip_sniper_rifle", 20, 20),
    ("equip_knife", 20, 20),
    ("equip_kevlar", 20, 20),
    ("equip_helmet", 20, 20),
    ("equip_axe", 20, 20),
    ("select_chkn", 20, 20),
    ("nest", 20, 20),
    ("equip_egg", 20, 20),
    # fox bits
    ("fox", 20, 20),
    ("ninja_fox", 20, 20),
    ("sapper_fox", 20, 20),
    ("rinkhals", 20, 20),
    # buildings
    ("henhouse", 60, 40),
    ("select_henhouse", 60, 40),
    ("hendominium", 40, 60),
    ("select_hendominium", 40, 60),
    ("watchtower", 40, 40),
    ("select_watchtower", 40, 40),
    # special effects
    ("muzzle_flash", 20, 20),
    ("chkn_death", 20, 20),
    ("fox_death", 20, 20),
    ("boom1", 20, 20),
    ("boom2", 20, 20),
    ("boom3", 20, 20),
    ("boom4", 20, 20),
]

if __name__ == "__main__":
    process_svg_folder("data/tiles", 20, 20)
    process_svg_folder("data/icons", 40, 40)
    for name, width, height in SPRITES:
        process_sprite(name, width, height, SPRITE_PATH)
    process_sprite("splash", 800, 600, IMAGE_PATH)
    process_sprite("gameover_win", 800, 600, IMAGE_PATH)
    process_sprite("gameover_lose", 800, 600, IMAGE_PATH)
