#!/usr/bin/python
# -*- coding: utf8 -*-

from setuptools import setup, find_packages

setup (
    name = "beancounter",
    version = "0.1",
    packages = find_packages(),
    scripts = ['beancounter.py'],

    author = "Reto Schüttel",
    author_email = "reto schuettel ch, add at and dot",
    description = "Beancounter counts the beans of your servers4you virtual server",
    license = "GPLv3",
    url = "http://github.com/retoo/beancounter"
)
