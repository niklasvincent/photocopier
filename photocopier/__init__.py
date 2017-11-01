# -*- coding:utf-8 -*-
from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import argparse
import glob
import hashlib
import json
import os
import sys
from datetime import date, datetime

from .database import Database, Photo
from .exceptions import PhotosLibraryNotFoundException


def locate_photos_library_directory():
    """Get location of Photos library directory for the current user"""
    pictures_directory = os.path.expanduser(r"~/Pictures")
    candidates = glob.glob(pictures_directory + "/*.photoslibrary")
    if not candidates:
        return None
    return candidates[0]


def locate_photos_library_database_file(photos_full_dirname):
    """Get location of Photos SQLite database filename"""
    candidates = [
        os.path.join(
            photos_full_dirname,
            "database",
            "Library.apdb"
        ),
        os.path.join(
            photos_full_dirname,
            "database",
            "photos.db"
        )
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    return None


def get_all_photos(photos_dirname=None, calculate_checksum=False):
    """Get all photos in the specified Photos library"""

    def get_checksum(photo, block_size=65536):
        """Calculate SHA1 for a photo and update its attributes"""
        sha1 = hashlib.sha1()
        with open(photo.path, 'rb') as f:
            for block in iter(lambda: f.read(block_size), b''):
                sha1.update(block)
        checksum = sha1.hexdigest()
        return Photo(
            path=photo.path,
            created_date=photo.created_date,
            modified_date=photo.modified_date,
            file_size=photo.file_size,
            albums=photo.albums,
            checksum=checksum
        )

    if not photos_dirname:
        photos_full_dirname = locate_photos_library_directory()
    else:
        photos_full_dirname = os.path.expanduser(photos_dirname)

    if not photos_full_dirname:
        raise PhotosLibraryNotFoundException(
            "No Photos library found. Please provide one."
        )
    elif not os.path.exists(photos_full_dirname):
        raise PhotosLibraryNotFoundException(
            "No such Photos library: {}".format(photos_dirname)
        )

    photos_library_filename = locate_photos_library_database_file(
        photos_full_dirname
    )
    if not photos_library_filename:
        raise PhotosLibraryNotFoundException(
            "Could not find a compatible SQLite database in {}".format(
                photos_full_dirname
            )
        )

    db = Database(
        photos_full_dirname=photos_full_dirname,
        photos_library_filename=photos_library_filename
    )

    photos = db.get_all_photos()

    if not calculate_checksum:
        return photos

    return [get_checksum(p) for p in photos]


def main():
    """Entry point for the application script"""

    def json_serial(obj):
        """JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, set):
            return list(obj)
        return obj.__dict__

    parser = argparse.ArgumentParser(description='List OS X Photos photos.')
    parser.add_argument(
        '--list',
        required=False,
        action="store_true",
        help='list all photos'
    )
    parser.add_argument(
        '--directory',
        required=False,
        default=None,
        help='path to Photos directory'
    )

    parser.add_argument(
        '--checksums',
        required=False,
        action="store_true",
        default=False,
        help='calculate SHA1 checksum'
    )

    args = parser.parse_args()

    photos_dirname = None if not args.directory else args.directory

    try:
        if args.list:
            photos = get_all_photos(
                photos_dirname=photos_dirname,
                calculate_checksum=args.checksums
            )
            expanded_tuples = [p._asdict() for p in photos]

            print(json.dumps(
                {
                    "photos": expanded_tuples,
                },
                default=json_serial,
                sort_keys=True,
                indent=4
            ))
        elif not args.list:
            parser.print_help()
    except PhotosLibraryNotFoundException as e:
        print(e)
        sys.exit(1)
