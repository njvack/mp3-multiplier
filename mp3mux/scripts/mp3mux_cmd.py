#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Part of mp3mux
#
# Copyright (c) 2016 Board of Regents of the University of Wisconsin System
# Licensed under the MIT License; see LICENSE at the root of the package.
#
# Written by Nate Vack <njvack@wisc.edu> at the Waisman Laboratory for Brain
# Imaging and Behavior

"""Make copies of MP3 files, changing ID3 tags based on a CSV file.

Usage:
  mp3mux [options] <csv_file> <out_base> <mp3_file>...
  mp3mux -h | --help
  mp3mux --version

Options:
  --filename-fields=<f>  The ID3 fields included in the filenames
                         [default: track,song]
  --filename-delim=<d>   The delimiter between filename fields [default: -]
  --csv-delim=<d>        The delimiter in the CSV input file [default: ,]
  --dry-run              Don't actually make changes
  -v, --verbose          Print extra debugging

The headings of the CSV file must be ID3 tag names -- so "artist", "album",
"song", "comment", "genre", "year" and/or "track". This is the same set of
values that can be used by the --filename-fields option; there must not be
overlap between the CSV headers and filename-fields option.

All ID3 tags not specified in either --filename-fields or the CSV headers will
be stripped.

Requires the id3v2 executable be in PATH.
"""

from __future__ import absolute_import, unicode_literals

import csv
import sys
import subprocess
import os
import shutil
import itertools

from mp3mux.vendor.docopt import docopt
from mp3mux import metadata

import logging
logger = logging.getLogger("mp3mux")
logger.setLevel(logging.ERROR)
log_handler = logging.StreamHandler()
log_handler.setLevel(logging.DEBUG)
log_handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(log_handler)


FIELDS = {
    'artist': '--artist',
    'album': '--album',
    'song': '--song',
    'track': '--track',
    'comment': '--comment',
    'genre': '--genre',
    'year': '--year'
}


def id3v2_args(tag_dict):
    nested = [
        [FIELDS[fname], val]
        for fname, val in tag_dict.items()
    ]
    return itertools.chain(*nested)


def parse_filename(filename, filename_delimiter, filename_fields):
    base_fname = os.path.basename(filename)
    main_part, _ = os.path.splitext(base_fname)
    fname_parts = [p.strip() for p in main_part.split(filename_delimiter)]
    part_dict = dict(zip(filename_fields, fname_parts))
    logger.debug("Parsed {0} as {1}".format(filename, part_dict))
    return (filename, base_fname, part_dict)


def single_mux(
        line,
        partified_files,
        out_path,
        make_changes):
    logger.info("Creating {0}".format(out_path))
    if make_changes:
        try:
            os.makedirs(out_path)
        except:
            logger.debug("Didn't make {0}".format(out_path))
    for mp3_file, mp3_base, part_dict in partified_files:
        devnull = open(os.devnull, 'w')
        target_file = os.path.join(out_path, mp3_base)
        logger.info('{0} -> {1}'.format(mp3_file, target_file))
        if make_changes:
            shutil.copyfile(mp3_file, target_file)
        cmd_args = ['id3v2', '-D', target_file]
        logger.info(' '.join(cmd_args))
        if make_changes:
            subprocess.check_call(cmd_args, stdout=devnull)
        id3_map = part_dict.copy()
        id3_map.update(line)
        cmd_args = ['id3v2'] + list(id3v2_args(id3_map)) + [target_file]
        logger.info(' '.join(cmd_args))
        if make_changes:
            subprocess.check_call(cmd_args, stdout=devnull)
    return 0


def multiplex_mp3s(
        mp3_files,
        csv_reader,
        filename_fields,
        filename_delimiter,
        base_dir,
        make_changes):

    partified = [
        parse_filename(f, filename_delimiter, filename_fields)
        for f in mp3_files]
    csv_fields = csv_reader.fieldnames
    for line in csv_reader:
        fields_ordered = [line.get(field) for field in csv_fields]
        out_dir = filename_delimiter.join(fields_ordered)
        out_path = os.path.join(base_dir, out_dir)

        single_mux(line, partified, out_path, make_changes)

    return 0


def main(argv=None):
    argv = argv or sys.argv[1:]
    pargs = docopt(__doc__, argv, version=metadata.version_description)
    if pargs['--verbose']:
        logger.setLevel(logging.DEBUG)
    logger.debug(pargs)
    filename_fields = [
        f.strip().lower() for f in pargs['--filename-fields'].split(",")]
    unmatched_fields = [f for f in filename_fields if f not in FIELDS]
    if len(unmatched_fields) > 0:
        logger.error("Unknown field: {0}".format(", ".join(unmatched_fields)))
        return 1
    with open(pargs['<csv_file>'], 'rU') as csv_in:
        reader = csv.DictReader(csv_in, delimiter=str(pargs['--csv-delim']))
        return multiplex_mp3s(
            pargs['<mp3_file>'],
            reader,
            filename_fields,
            pargs['--filename-delim'],
            pargs['<out_base>'],
            (not pargs['--dry-run'])
        )


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
