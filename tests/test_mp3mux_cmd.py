# -*- coding: utf-8 -*-
# Part of mp3mux
#
# Copyright (c) 2016 Board of Regents of the University of Wisconsin System
# Licensed under the MIT License; see LICENSE at the root of the package.
#
# Written by Nate Vack <njvack@wisc.edu> at the Waisman Laboratory for Brain
# Imaging and Behavior


from mp3mux.scripts import mp3mux_cmd as cmd
from mp3mux.scripts.mp3mux_cmd import logger
import logging
logger.setLevel(logging.DEBUG)


def test_filename_mapping():
    fname = '/tmp/01 - Something.mp3'
    _, _, mapped = cmd.parse_filename(fname, '-', ['track', 'song'])
    assert mapped == {'track': '01', 'song': 'Something'}


def test_id3v2_args():
    d = {
        'artist': 'Bert',
        'song': 'Bertsong',
        'album': 'albumin',
        'track': '10',
        'comment': 'commenty',
        'genre': '10',
        'year': '2016'
    }
    args = cmd.id3v2_args(d)
    assert set(args) == {
        '--artist', 'Bert', '--album', 'albumin', '--song', 'Bertsong',
        '--track', '10', '--comment', 'commenty', '--genre', '10', '--year',
        '2016'}
