===========
photocopier
===========

.. image:: https://travis-ci.org/nlindblad/photocopier.svg?branch=master
    :target: https://travis-ci.org/nlindblad/photocopier

A small Python library (with bundled CLI) for listing all photos contained in an OS X Photos library.

Since OS X 10.10.3, Photos has been the default photo management solution. The export options leave a lot to be desired, especially for larger collections.

This tools aims to be a starting point for making things like periodic backups and transfer to other photo management solutions easier.

Command line usage
==================

Usage: ``photocopier photocopier [-h] [--list] [--directory DIRECTORY] [--checksums]``

  -h, --help            show this help message and exit
  --list                list all photos
  --directory DIRECTORY
                        path to Photos directory
  --checksums           calculate SHA1 checksum

Example output:

.. code-block:: json

  {
      "photos": [
        {
            "albums": [
                "Nature"
            ],
            "checksum": "b7ca1f49ed9c82ef922df092cface3b25029c055",
            "created_date": "2017-10-29T16:59:57.448276",
            "file_size": 6082983,
            "modified_date": "2017-10-29T16:59:57.451486",
            "path": "tests/data/OS_X_10.12.6_Photos_2.0_3161.4.140/Photos Library.photoslibrary/Masters/2017/10/29/20171029-155957/pexels-photo-66181.jpeg"
        }
      ]
  }

Library usage
=============

To use ``photocopier`` in your own tools, simply import it:

.. code-block:: python

  import photocopier
  photos = photocopier.get_all_photos()
