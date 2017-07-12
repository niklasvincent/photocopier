# -*- coding:utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import os
import sqlite3
from collections import namedtuple


Photo = namedtuple('Photo', ['x'])
RKMasterRow = namedtuple(
    'RKMasterRow',
    [
        'uuid',
        'modelId',
        'masterUuid',
        'lastmodifieddate',
        'imageDate',
        'hasAdjustments',
        'imagePath',
        'fileSize',
        'fileName',
        'createdDate'
    ]
)


class Database(object):

    def __init__(self, photos_full_dirname):
        self.photos_full_dirname = photos_full_dirname
        database_filename = os.path.join(photos_full_dirname, 'database', 'photos.db')
        self.conn = sqlite3.connect(database_filename)

    def get_all_photos(self):
        return self._get_masters()

    def _full_image_path(self, image_path):
        return os.path.join(self.photos_full_dirname, "Masters", image_path)

    @staticmethod
    def _datetime_from_core_data_timestamp(timestamp, timezone_offset):
        epoch_offset = 978307200  # Seconds between Jan 1, 1970 and Jan 1, 2001
        return datetime.datetime.fromtimestamp(timestamp + epoch_offset + timezone_offset)

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
