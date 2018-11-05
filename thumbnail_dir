#!/usr/bin/python3
# -*- coding: utf-8 -*-

from __future__ import print_function, division

import os
import struct
import sys

from PIL import Image
import piexif


# TODO: delete thumbnails of removed source images.
# TODO: multithreading
# TODO: add a --include option with a list a files to include, relative to the
#         source directory. Other files are ignored.
# TODO: add a --exclude option with a list of files to exclude.


def thumbnail_dir(srcdir, destdir, size):
    if os.path.samefile(srcdir, destdir):
        print('Source and destination directories must differ',
              file=sys.stderr)
        exit(1)
    if not os.path.exists(srcdir):
        print('Inexisting source directory', file=sys.stderr)
        exit(1)
    if not os.path.exists(destdir):
        print('Inexisting destination directory', file=sys.stderr)
        exit(1)

    len_str_srcdir = len(srcdir)
    dest_directory_checked = False
    for root, _, files in os.walk(srcdir):
        reldir = root[len_str_srcdir:]
        # Do not use os.path.join because reldir starts with '/'.
        full_src_dir = srcdir + reldir
        full_dest_dir = destdir + reldir
        for name in files:
            if not dest_directory_checked:
                ok_to_write = check_destination(
                    srcdir, destdir, os.path.join(reldir, name))
                if (ok_to_write is not None) and not ok_to_write:
                    exit(0)
                else:
                    dest_directory_checked = True
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
        if 'exif' in im.info.keys():
            # From https://stackoverflow.com/a/33885893.
            try:
                exif_dict = piexif.load(im.info['exif'])
                exif_bytes = piexif.dump(exif_dict)
            except (ValueError, struct.error):
                im.save(dest_file)
            else:
                im.save(dest_file, exif=exif_bytes)
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
    orientation = get_orientation(image)
    if orientation in [90, 270]:
        src_size = (image.size[1], image.size[0])
    else:
        src_size = image.size
    new_size = get_new_size(src_size, size)
    if orientation in [90, 270]:
        new_size = (new_size[1], new_size[0])
        size = (size[1], size[0])
    resized_image = image.resize(new_size, Image.ANTIALIAS)
    black = Image.new(mode='RGB', size=size)
    box = get_paste_box(new_size, size)
    black.paste(resized_image, box)
    black.info = image.info
    return black


def get_orientation(image):
    """Return the image orientation from EXIF data"""
    try:
        exif_dict = piexif.load(image.info['exif'])
    except (KeyError, struct.error):
        print('Cannot get EXIF for {}'.format(image.filename),
              file=sys.stderr)
        return 0
    try:
        orientation = exif_dict['0th'].pop(piexif.ImageIFD.Orientation)
    except KeyError:
        print('Cannot get orientation for {}'.format(image.filename),
              file=sys.stderr)
        return 0

    if orientation == 3:
        return 180
    if orientation == 6:
        return 270
    if orientation == 8:
        return 90
    return 0


def get_new_size(src_size, dest_size):
    """Return the size so that it fits into dest_size

    Use this function to compute the size of an image you want to paste into a
    destination image with size dest_size. If the source image is smaller than
    the destination image, returns src_size. Otherwise, returns the size so
    that the aspect ratio is respected and either the returned width or the
    height is equal to the width or the height of the destination image.
    """
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

    Return the position of the upper left corner of a source image, so that
    when pasted into the destination image, it will be centered.
    """
    src_width, src_height = src_size
    dest_width, dest_height = dest_size
    src_left = int((dest_width - src_width) / 2)
    src_top = int((dest_height - src_height) / 2)
    return src_left, src_top


def check_destination(srcdir, destdir, relname):
    """Ask the user to confirm overwriting the destination

    Returns True (can overwrite), False (must not overwrite), or None in the
    case that the destination file doesn't exist.
    """
    if not os.path.exists(os.path.join(destdir, relname)):
        return
    full_src_path = os.path.join(srcdir, relname)
    full_dest_path = os.path.join(destdir, relname)
    src_size = human_bytes_format(os.stat(full_src_path).st_size)
    dest_size = human_bytes_format(os.stat(full_dest_path).st_size)
    warn = 'About to overwrite "{}" in "{}", source size: {}, dest_size: {}'.format(
        relname, destdir, src_size, dest_size)
    print(warn)
    while True:
        reply = input('Are you sure, yes or no? ')
        if reply in ['yes', 'no']:
            break
    return reply == 'yes'


def human_bytes_format(size):
    """Return a number of bytes into n {B, kB, ...}"""
    power = 2 ** 10
    n = 0
    dict_power_n = {0: '', 1: 'kB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size //= power
        n += 1
    return '{} {}'.format(size, dict_power_n[n])


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
