#!/usr/bin/env python

import cairo
import rsvg
import os

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

if __name__ == "__main__":
    tile_path = "data/tiles"
    sprite_path = "data/sprites"
    image_path = "data/images"
    sprites = [
        ("chkn", 20, 20),
        ("select_chkn", 20, 20),
        ("chkn_death", 20, 20),
        ("egg", 20, 20),
        ("fox", 20, 20),
        ("fox_death", 20, 20),
        ("ninja_fox", 20, 20),
        ("equip_rifle", 20, 20),
        ("equip_knife", 20, 20),
        ("muzzle_flash", 20, 20),
        ("kevlar", 20, 20),
        ("helmet", 20, 20),
        ("henhouse", 60, 40),
        ("select_henhouse", 60, 40),
        ("hendominium", 40, 60),
        ("select_hendominium", 40, 60),
        ("watchtower", 40, 40),
        ("select_watchtower", 40, 40),
        ("chknnest", 20, 20),
        ("emptynest", 20, 20),
    ]

    process_svg_folder("data/tiles", 20, 20)
    process_svg_folder("data/icons", 40, 40)
    for name, width, height in sprites:
        process_sprite(name, width, height, sprite_path)
    process_sprite("splash", 800, 600, image_path)
    process_sprite("gameover_win", 800, 600, image_path)
    process_sprite("gameover_lose", 800, 600, image_path)
