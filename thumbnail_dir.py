#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function, division

import os
import sys

from PIL import Image


# TODO: add a protection against overwriting source image by exchanging srcdir and destdir!!!
# TODO: delete thumbnails of removed source images.


def thumbnail_dir(srcdir, destdir, size):
    if os.path.samefile(srcdir, destdir):
        print('Source and destination directories must differ',
                file=sys.stderr)
        exit(1)
    if not os.path.exists(destdir):
        print('Inexisting destination directory', file=sys.stderr)
        exit(1)

    len_str_srcdir = len(srcdir)
    for root, _, files in os.walk(srcdir):
        reldir = root[len_str_srcdir:]
        full_src_dir = srcdir + reldir
        full_dest_dir = destdir + reldir
        for name in files:
            thumbnail_file(full_src_dir, full_dest_dir, name, size)


def thumbnail_file(full_src_dir, full_dest_dir, name, size):
    if not name.lower().endswith('.jpg'):
        return
    if not os.path.exists(full_dest_dir):
        print('Creating {}'.format(full_dest_dir))
        os.makedirs(full_dest_dir)
    src_file = os.path.join(full_src_dir, name)
    dest_file = os.path.join(full_dest_dir, name)
    if (not os.path.exists(dest_file)
            or (os.path.exists(dest_file)
                and os.path.getmtime(src_file) > os.path.getmtime(dest_file))):
        im = get_thumb(src_file, size)
        if im is None:
            return
        if 'exit' in im.info.keys():
            im.save(dest_file, exif=im.info['exif'])
        else:
            im.save(dest_file)


def get_thumb(src_file, size):
    """Return a resized PIL.Image
    
    On the opposite to most thumbnailers, the returned image has exactly the
    size (width, height). Black pixels will be added so that the image is not
    resized up and that the original aspect ratio is respected.
    """
    try:
        image = Image.open(src_file)
    except IOError:
        print('Cannot read ' + src_file, file=sys.stderr)
        return
    new_size = get_new_size(image.size, size)
    resized_image = image.resize(new_size, Image.ANTIALIAS)
    black = Image.new(mode='RGB', size=size)
    box = get_paste_box(new_size, size)
    black.paste(resized_image, box)
    black.info = image.info
    return black


def get_new_size(src_size, dest_size):
    out_width, out_height = src_size
    dest_width, dest_height = dest_size
    src_ratio = out_width / out_height
    if out_width > dest_width:
        out_width = dest_width
        out_height = dest_width / src_ratio
    if out_height > dest_height:
        out_width = dest_height * src_ratio
        out_height = dest_height
    return int(out_width), int(out_height)


def get_paste_box(src_size, dest_size):
    """Return the position of the left-top corner of src in dest

    Return the position of the upper left corner of a source image, so that when
    pasted into the destination image, it will be centered.
    """
    src_width, src_height = src_size
    dest_width, dest_height = dest_size
    src_left = int((dest_width - src_width) / 2)
    src_top = int((dest_height - src_height) / 2)
    return src_left, src_top


if __name__ == '__main__':
    try:
        srcdir = sys.argv[1]
        destdir = sys.argv[2]
        width = int(sys.argv[3])
        height = int(sys.argv[4])
    except IndexError:
        print('Usage: {} srcdir destdir width height'.format(sys.argv[0]), file=sys.stderr)
        exit(1)
    except ValueError:
        print('Width and height must be integers')
    thumbnail_dir(srcdir, destdir, (width, height))
