# -*- coding:utf-8 -*-

import datetime

from photocopier import database


def test_core_data_timestamp_conversion():
    """Test core data to UNIX epoch timestamp conversion"""
    ts = database.Database._datetime_from_core_data_timestamp(
        1,
        0
    )
    assert ts == datetime.datetime(2001, 1, 1, 0, 0, 1)
