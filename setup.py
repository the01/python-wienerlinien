#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
# from __future__ import unicode_literals

__author__ = "d01 <Florian Jung>"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2017, Florian JUNG"
__license__ = "MIT"
__version__ = "0.1.3"
__date__ = "2017-11-01"
# Created: ?

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import sys
import os
import re
from setuptools import find_packages


if sys.argv[-1] == "build":
    os.system("python setup.py clean sdist bdist bdist_egg bdist_wheel")


def get_version():
    """
    Parse the version information from the init file
    """
    version_file = os.path.join("wl", "__init__.py")
    initfile_lines = open(version_file, "rt").readlines()
    version_reg = r"^__version__ = ['\"]([^'\"]*)['\"]"
    for line in initfile_lines:
        mo = re.search(version_reg, line, re.M)
        if mo:
            return mo.group(1)
    raise RuntimeError(
        u"Unable to find version string in {}".format(version_file)
    )


def get_file(path):
    with open(path, "r") as f:
        return f.read()


version = get_version()
# readme = get_file("README.rst")
# history = get_file("HISTORY.rst")
requirements = get_file("requirements.txt").split("\n")

assert version is not None
# assert readme is not None
# assert history is not None
assert requirements is not None

setup(
    name="wl",
    version=version,
    description="",
    # long_description=readme + "\n\n" + history,
    author="the01",
    author_email="jungflor@gmail.com",
    url="https://github.com/the01/python-wienerlinien",
    packages=[
        "wl",
        "wl.models",
    ],
    install_requires=requirements,
    license="MIT License",
    keywords="",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
    ]
)
