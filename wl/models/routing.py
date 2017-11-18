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
# Created: 2017-11-03 12:00

from .general import Request, FromToDictBase, PrintableBase


class ItdBase(Request):

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
        else:
            res['sessionID'] = "0"
        if self.request_id is not None:
            res['requestID'] = self.request_id
        if self.language is not None:
            res['language'] = self.language
        for key, value in self.app_params.items():
            res['itdLPxx_{}'.format(key)] = value
        res.update(super(ItdRequest, self).to_get_params())
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


class ItdDMResponse(ItdResponse):

    def __init__(self):
        super(ItdDMResponse, self).__init__()
        self.lines = None
        """ :type : None | list[wl.models.routing.Line] """
        self.places = None
        self.departures = None
        """ :type : None | list[wl.models.routing.Departure] """
        self.stops = None
        """ :type : None | list[wl.models.routing.Stop] """
        self.lines = None
        """ :type : None | list[wl.models.routing.Line] """
        self.datetime = None


class Line(FromToDictBase, PrintableBase):

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


class Departure(FromToDictBase, PrintableBase):

    def __init__(self):
        super(Departure, self).__init__()
        self.stop_id = None
        self.stop_name = None
        self.platform = None
        self.platform_name = None
        self.datetime = None
        self.countdown = None
        self.line = None
        """ :type : wl.models.routing.Line """

    @classmethod
    def from_dict(cls, d):
        new = super(cls, cls).from_dict(d)
        if new.line:
            new.line = Line.from_dict(new.line)
        return new


class Stop(FromToDictBase, PrintableBase):

    def __init__(self):
        super(Stop, self).__init__()
        self.stop_id = None
        self.value = None
        self.distance = None
        self.distance_time = None
        self.name = None

