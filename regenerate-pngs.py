#!/usr/bin/env python

import cairo
import rsvg
import os

def svg_to_png(svg_name, png_name, w, h):
    """Convert an SVG file to a PNG file."""
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

def main(path, width, height):
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            basename, ext = os.path.splitext(filename)
            if ext == ".svg":
                svg_name = os.path.join(dirpath, basename + ".svg")
                png_name = os.path.join(dirpath, basename + ".png")
                print "Generating %s at %dx%d..." % (png_name, width, height)
                svg_to_png(svg_name, png_name, width, height)

if __name__ == "__main__":
    main("data", 20, 20)
