# -*- coding:utf-8 -*-
import datetime
import json
import os

import photocopier
from photocopier.database import Photo

test_matrix = [
    {
        "OS X": "10.12.6",
        "Photos": "2.0 3161.4.140"
    }
]


def json_object_pairs_hook(pairs, date_format="%Y-%m-%dT%H:%M:%S.%f"):
    """JSON parser hook for properly converting datetime strings and sets"""
    d = {}
    for k, v in pairs:
        if k in ["created_date", "modified_date"]:
            d[k] = datetime.datetime.strptime(v, date_format)
        elif k == "albums":
            d[k] = set(v)
        else:
            d[k] = v
    return d


def test_real_databases():
    """Test real databases"""
    for test_database in test_matrix:
        data_directory = "tests/data/OS_X_{osx_version}_Photos_" \
                         "{photos_version}" \
            .format(
                    osx_version=test_database["OS X"],
                    photos_version=test_database["Photos"].replace(" ", "_")
            )
        print("{osx_version} {photos_version}".format(
            osx_version=test_database["OS X"],
            photos_version=test_database["Photos"]
        ))
        actual_photos = photocopier.get_all_photos(
            photos_dirname=os.path.join(
                data_directory,
                "Photos Library.photoslibrary"
            ),
            calculate_checksum=True
        )
        expected_photos_json_filename = os.path.join(
            data_directory,
            "expected.json"
        )
        with open(expected_photos_json_filename, "r") as f:
            expected_photos = [Photo(**p) for p in json.load(
                f,
                object_pairs_hook=json_object_pairs_hook
            )["photos"]]
        assert expected_photos == actual_photos
