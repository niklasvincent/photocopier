import datetime

from photocopier import database


def test():
    ts = database.Database._datetime_from_core_data_timestamp(
        1,
        0
    )
    assert ts == datetime.datetime(2001, 1, 1, 0, 0, 1)
