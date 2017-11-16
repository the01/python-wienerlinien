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


class PrintableBase(object):

    def __str__(self):
        return "<{}>({})".format(self.__class__.__name__, format_vars(self))

    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return self.__str__()


class Request(FromToDictBase, PrintableBase):

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


class Response(FromToDictBase, PrintableBase):

    def __init__(self):
        super(Response, self).__init__()
        self.id = None
        self.stops = None
        """ :type : list[wl.models.general.Stop] """
        self.departures = None
        """ :type : list[wl.models.general.Departure] """


class Location(FromToDictBase, PrintableBase):

    def __init__(self, latitude=None, longitude=None):
        super(Location, self).__init__()
        self.latitude = latitude
        self.longitude = longitude


class Stop(PrintableBase, FromToDictBase):

    def __init__(self):
        super(Stop, self).__init__()
        # TODO: value for select
        self.id = None
        """ DIVA / routing.stop_id """
        self.name = None
        """ routing.name """
        #self.rbl = None
        """ realtime.rbl """
        self.distance = None
        """ routing.distance """
        self.distance_time = None
        """ routing.distance_time """
        self.location = None
        """ :type : wl.models.general.Location """

    @classmethod
    def from_dict(cls, d):
        new = super(Stop, Stop).from_dict(d)
        if new.location:
            new.location = Location.from_dict(new.location)
        return new


class Line(PrintableBase, FromToDictBase):

    def __init__(self):
        super(Line, self).__init__()
        self.id = None
        """ routing.index(5:0) """
        self.name = None
        """ routing.symbol(40) """
        self.direction = None
        """ routing.direction(Pötzleinsdorf) """
        self.realtime = None
        """ routing.realtime(1) """


class Departure(PrintableBase, FromToDictBase):

    def __init__(self):
        self.stop_id = None
        """ routing.stop_id """
        self.stop_name = None
        self.line_name = None
        self.datetime = None
        self.countdown = None
        self.direction = None
