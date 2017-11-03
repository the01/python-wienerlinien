# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2017, Florian JUNG"
__license__ = "MIT"
__version__ = "0.1.0"
__date__ = "2017-11-03"
# Created: 2017-11-03 12:27


from dateutil import tz
from dateutil.tz import tzutc


def to_utc(dt):
    dt = dt.astimezone(tzutc())
    return dt.replace(tzinfo=None)


def local_to_utc(dt):
    dt = dt.replace(tzinfo=tz.gettz("Europe/Vienna")).astimezone(tzutc())
    return dt.replace(tzinfo=None)


def utc_to_local(dt):
    dt = dt.replace(tzinfo=tzutc()).astimezone(tz.gettz("Europe/Vienna"))
    return dt.replace(tzinfo=None)
