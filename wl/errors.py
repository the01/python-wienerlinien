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
__date__ = "2017-11-01"
# Created: 2017-11-01 18:13

DATE_INVALID = -1
DATE_OFR_YEAR = -10
DATE_OFR_MONTH = -20
DATE_OFR_DAY = -30
DATE_OUT_OF_PLAN = -4001

TIME_INVALID = -1
TIME_OFR_HOUR = -10
TIME_OFR_MINUTE = -20


class WL_Exception(Exception):
    """ Base WL exception """


class RequestException(WL_Exception):
    """ Error while making request """
