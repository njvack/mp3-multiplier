#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from setuptools import setup, find_packages
import os

packages = find_packages()


def get_locals(filename):
    with open(filename) as f:
        l = {}
        code = compile(f.read(), filename, 'exec')
        exec(code, {}, l)
        return l

metadata = get_locals(os.path.join('mp3mux', 'metadata.py'))

setup(
    name="mp3mux",
    version=metadata['version'],
    author=metadata['author'],
    author_email=metadata['author_email'],
    license=metadata['license'],
    url=metadata['url'],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'mp3mux = mp3mux.scripts.mp3mux_cmd:main',
        ]
    }
)
