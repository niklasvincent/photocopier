# -*- coding:utf-8 -*-
from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import datetime
import os
import shutil
import sqlite3
import tempfile
from collections import namedtuple

from .exceptions import PhotosLibraryNotFoundException

Photo = namedtuple(
    "Photo",
    [
        "path",
        "created_date",
        "modified_date",
        "file_size",
        "albums",
        "checksum"
    ]
)
RKAlbumRow = namedtuple(
    "RKAlbumRow",
    [
        "name",
        "folderuuid"
    ]
)
RKMasterRow = namedtuple(
    "RKMasterRow",
    [
        "uuid",
        "modelId",
        "masterUuid",
        "lastmodifieddate",
        "imageDate",
        "hasAdjustments",
        "imagePath",
        "fileSize",
        "fileName",
        "createdDate"
    ]
)


class Database(object):

    def __init__(self, photos_full_dirname, photos_library_filename):
        self.photos_full_dirname = photos_full_dirname
        database_snapshot_filename = self._create_snapshot(
            database_filename=photos_library_filename
        )
        self.conn = sqlite3.connect(database_snapshot_filename)

    @staticmethod
    def _create_snapshot(database_filename):
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, 'photos.db')
        try:
            shutil.copy2(database_filename, temp_path)
            return temp_path
        except FileNotFoundError:
            raise PhotosLibraryNotFoundException(
                "No such file {database_filename}".format(
                    database_filename=database_filename
                )
            )

    def get_all_photos(self):
        photos = []
        for master in self._get_masters():
            albums = set([a.name for a in
                          self._get_albums_for_photo(master.modelId)
                          ])
            photos.append(
                Photo(
                    path=master.imagePath,
                    created_date=master.createdDate,
                    modified_date=master.lastmodifieddate,
                    file_size=master.fileSize,
                    albums=albums,
                    checksum=None
                )
            )
        return photos

    def _full_image_path(self, image_path):
        return os.path.join(self.photos_full_dirname, "Masters", image_path)

    @staticmethod
    def _datetime_from_core_data_timestamp(timestamp, timezone_offset=None):
        epoch_offset = 978307200  # Seconds between Jan 1, 1970 and Jan 1, 2001

        timezone_offset = timezone_offset if timezone_offset else 0
        unix_timestamp = timestamp if timestamp else 0

        return datetime.datetime.fromtimestamp(
            unix_timestamp + epoch_offset + timezone_offset
        )

    def _get_albums_for_photo(self, model_id):
        def _row_factory(cursor, row):
            return RKAlbumRow(
                name=row[0],
                folderuuid=row[1]
            )

        sql = """SELECT
            RKAlbum.name,
            RKAlbum.folderuuid
        FROM
            RKAlbum,
            RKVersion,
            RKAlbumVersion
        WHERE
            RKVersion.modelId = RKAlbumVersion.versionId AND
            RKAlbumVersion.albumId = RKAlbum.modelID AND
            RKAlbum.isInTrash = 0 AND
            RKAlbum.isHidden = 0 AND
            RKAlbum.isMagic = 0 AND
            RKVersion.modelID = ?"""
        self.conn.row_factory = _row_factory
        cursor = self.conn.cursor()
        cursor.execute(sql, (model_id,))
        rows = cursor.fetchall()
        self.conn.row_factory = None
        return rows

    def _get_masters(self):
        def _row_factory(cursor, row):
            timezone_offset = row[10]
            return RKMasterRow(
                uuid=row[0],
                modelId=row[1],
                masterUuid=row[2],
                lastmodifieddate=Database._datetime_from_core_data_timestamp(
                    timestamp=row[3],
                    timezone_offset=timezone_offset
                ),
                imageDate=Database._datetime_from_core_data_timestamp(
                    timestamp=row[4],
                    timezone_offset=timezone_offset
                ),
                hasAdjustments=row[5],
                imagePath=self._full_image_path(row[6]),
                fileSize=row[7],
                fileName=row[8],
                createdDate=Database._datetime_from_core_data_timestamp(
                    timestamp=row[9],
                    timezone_offset=timezone_offset
                )
            )

        sql = """SELECT
                RKVersion.uuid,
                RKVersion.modelId,
                RKVersion.masterUuid,
                RKVersion.lastmodifieddate,
                RKVersion.imageDate,
                RKVersion.hasAdjustments,
                RKMaster.imagePath,
                RKMaster.fileSize,
                RKMaster.fileName,
                RKMaster.createDate,
                RKVersion.imageTimeZoneOffsetSeconds
            FROM
                RKVersion,
                RKMaster
            WHERE
                RKVersion.isInTrash = 0 AND
                RKVersion.type = 2 AND
                RKVersion.masterUuid = RKMaster.uuid AND
                RKVersion.filename NOT LIKE '%.pdf'"""
        self.conn.row_factory = _row_factory
        cursor = self.conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        self.conn.row_factory = None
        return rows
