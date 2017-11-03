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
# Created: 2017-11-01 18:04

import abc


def format_vars(instance):
    attrs = vars(instance)
    return ", ".join("{}={}".format(key, value) for key, value in attrs.items())


class FromToDictBase(object):
    __metaclass__ = abc.ABCMeta

    @classmethod
    def from_dict(cls, d):
        new = cls()
        if not d:
            return new
        attrs = vars(new)
        for key in d:
            if key in attrs:
                # both in dict and this class
                setattr(new, key, d[key])
        return new

    def to_dict(self):
        attrs = vars(self)
        res = {}
        for key, value in attrs.items():
            if isinstance(value, FromToDictBase):
                res[key] = value.to_dict()
            else:
                res[key] = value
        return res

class Request(FromToDictBase):

    def __init__(self):
        super(Request, self).__init__()
        self.params = {}
        """ Parameters to include in get params
            :type : dict[str | unicode, str | unicode] | list[(str | unicode, str | unicode)] """

    def to_get_params(self):
        """
        Convert Paramters to HTTP GET parameter dictionary

        :return: GET parameters as dict
        :rtype: dict
        """
        res = {}
        res.update(self.params)
        return res

    def __str__(self):
        return "<Request>({})".format(format_vars(self))

    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return self.__str__()


class Line(FromToDictBase):

    def __init__(self):
        super(Line, self).__init__()
        self.index = None
        self.key = None
        self.code = None
        self.number = None
        self.symbol = None
        self.direction = None
        self.realtime = None
        self.selected = None
        self.network = None
        self.line = None
        self.description = None

    def __str__(self):
        return "<Line>({})".format(format_vars(self))

    def __repr__(self):
        return self.__str__()


class Departure(FromToDictBase):

    def __init__(self):
        super(Departure, self).__init__()
        self.stop_id = None
        self.stop_name = None
        self.platform = None
        self.platform_name = None
        self.datetime = None
        self.countdown = None
        self.line = None

    @classmethod
    def from_dict(cls, d):
        new = super(cls, cls).from_dict(d)
        if new.line:
            new.line = Line.from_dict(new.line)
        return new

    def __str__(self):
        return "<Departure>({})".format(format_vars(self))

    def __repr__(self):
        return self.__str__()


class Stop(FromToDictBase):

    def __init__(self):
        super(Stop, self).__init__()
        self.stop_id = None
        self.value = None
        self.distance = None
        self.distance_time = None
        self.name = None

    def __str__(self):
        return "<Stop>({})".format(format_vars(self))

    def __repr__(self):
        return self.__str__()
