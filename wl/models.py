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


class ItdBase(FromToDictBase):

    def __init__(self):
        super(ItdBase, self).__init__()
        self.session_id = None
        """ Session id
            :type : None | str | unicode """
        self.request_id = None
        """ Request id
            :type : None | str | unicode """
        self.language = None
        """ Used language code (de, en, ..)
            :type : None | str | unicode """
        self.app_params = {}
        """ Paramters to inlcude in the XML for the application (ignored by api)
            :type : dict[str | unicode, str | unicode] """
        self.params = {}
        """ Parameters to include in get params
            :type : dict[str | unicode, str | unicode] | list[(str | unicode, str | unicode)] """

    @classmethod
    def from_itd(cls, ele):
        """

        :param ele:
        :type ele: T <= wl.models.ItdBase
        :return:
        :rtype: T <= wl.models.ItdBase
        """
        res = cls()
        """ :type : wl.models.ItdBase """
        res.session_id = ele.session_id
        res.request_id = ele.request_id
        res.language = ele.language
        res.app_params = ele.app_params
        res.params = ele.params
        return res

    def __str__(self):
        return "<ItdBase>({})".format(format_vars(self))

    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return self.__str__()


class ItdRequest(ItdBase):
    EXEC_INST_NORMAL = "normal"
    EXEC_INST_VERIFY_ONLY = "verifyOnly"
    EXEC_INST_READ_ONLY = "readOnly"

    def __init__(self):
        super(ItdRequest, self).__init__()

    def to_get_params(self):
        """
        Convert ItdRequest to HTTP GET parameter dictionary

        :return: GET parameters as dict
        :rtype: dict
        """
        res = {}
        if self.session_id is not None:
            res['sessionID'] = self.session_id
        if self.request_id is not None:
            res['requestID'] = self.request_id
        if self.language is not None:
            res['language'] = self.language
        for key, value in self.app_params.items():
            res['itdLPxx_{}'.format(key)] = value
        res.update(self.params)
        return res


class ItdResponse(ItdBase):

    def __init__(self):
        super(ItdResponse, self).__init__()
        self.client = None
        self.server_id = None
        self.client_ip = None
        self.version = None
        self.virt_dir = None
        self.now = None
        self.now_wd = None
        self.length_unit = None
        self.children = None
        """ :type : list[xml.etree.ElementTree.Element] """

    def __str__(self):
        return "<ItdResponse>({})".format(format_vars(self))


class ItdDMResponse(ItdResponse):

    def __init__(self):
        super(ItdDMResponse, self).__init__()
        self.lines = None
        """ :type : None | list[wl.models.Line] """
        self.places = None
        self.departures = None
        self.stops = None
        self.datetime = None

    def __str__(self):
        return "<ItdDMResponse>({})".format(format_vars(self))


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
