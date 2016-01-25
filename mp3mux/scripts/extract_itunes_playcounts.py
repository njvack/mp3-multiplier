#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Part of mp3mux
#
# Copyright (c) 2016 Board of Regents of the University of Wisconsin System
# Licensed under the MIT License; see LICENSE at the root of the package.
#
# Written by Nate Vack <njvack@wisc.edu> at the Waisman Laboratory for Brain
# Imaging and Behavior

"""Extracts the play counts from an iTunes library for some tracks.

Usage:
  extract_itunes_playcounts [options] <itunes_file>
  extract_itunes_playcounts -h | --help
  extract_itunes_playcounts --version

Options:
  -v, --verbose     Print more debugging

Requires lxml.
"""

from __future__ import absolute_import, unicode_literals

import csv
import sys

from lxml import etree

from mp3mux.vendor.docopt import docopt
from mp3mux import metadata

import logging
logger = logging.getLogger("mp3mux")
logger.setLevel(logging.ERROR)
log_handler = logging.StreamHandler()
log_handler.setLevel(logging.DEBUG)
log_handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(log_handler)


FIELDS_TO_EXTRACT = [
    'Track ID',
    'Artist',
    'Album',
    'Track Number',
    'Name',
    'Play Count',
    'Comments',
]


def extract(track, field_name):
    content = track.xpath(
        "key[.=$field]/following-sibling::*[1]/text()", field=field_name)
    logger.debug(repr(content))
    if len(content) > 1:
        logger.warn("content has more than one thing! {0}".format(content))
    return ''.join(content)  # empty list should return empty string


def extract_all_fields(track):
    return [
        extract(track, field).encode('utf-8')
        for field in FIELDS_TO_EXTRACT]


def extract_playcounts(itunes_file):
    doc = etree.parse(itunes_file)
    all_tracks = doc.xpath("./dict/dict/dict[key=$field]", field='Track Type')
    writer = csv.writer(sys.stdout, delimiter=str("\t"))
    writer.writerow(FIELDS_TO_EXTRACT)
    for track in all_tracks:
        writer.writerow(extract_all_fields(track))
    return 0


def main(argv=None):
    argv = argv or sys.argv[1:]
    pargs = docopt(__doc__, argv, version=metadata.version_description)
    if pargs['--verbose']:
        logger.setLevel(logging.DEBUG)
    logger.debug(pargs)
    return extract_playcounts(pargs['<itunes_file>'])

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
