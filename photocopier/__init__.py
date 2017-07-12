# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, \
    print_function, unicode_literals


import os
import sys


from .database import Database


def main():
    """Entry point for the application script"""

    photos_dirname = r"~/Pictures/Photos Library.photoslibrary"
    photos_full_dirname = os.path.expanduser(photos_dirname)

    if not os.path.exists(photos_full_dirname):
        print("Error: No such Photos library: {}".format(photos_dirname))
        sys.exit(1)

    db = Database(photos_full_dirname=photos_full_dirname)
    print(db.get_all_photos())
