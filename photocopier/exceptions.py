# -*- coding:utf-8 -*-
from __future__ import (
    absolute_import, division, print_function, unicode_literals
)


class PhotosLibraryNotFoundException(Exception):
    """Exception indicating Photos library could not be found"""
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
