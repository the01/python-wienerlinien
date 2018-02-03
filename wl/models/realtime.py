# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2017-18, Florian JUNG"
__license__ = "MIT"
__version__ = "0.1.0"
__date__ = "2018-02-03"
# Created: 2017-11-03 12:00

from flotils import FromToDictBase, PrintableBase


class RTResponse(FromToDictBase, PrintableBase):
    CODE_OK = 1

    def __init__(self):
        super(RTResponse, self).__init__()
        self.message_code = None
        self.server_time = None
        self.message_value = None
        self.raw = None
        self.monitors = None
        """ :type : list[wl.models.realtime.Monitor] """


class Monitor(FromToDictBase, PrintableBase):

    def __init__(self):
        super(Monitor, self).__init__()
        self.stop = None
        """ :type : None | wl.models.realtime.Stop """
        self.lines = None
        """ :type : None | list[wl.models.realtime.Line] """

    @property
    def name(self):
        if not self.stop:
            return None
        return self.stop.title


class Stop(FromToDictBase, PrintableBase):

    def __init__(self):
        super(Stop, self).__init__()
        self.stop_type = None
        self.location = None
        """ :type : dict """
        self.stop_id = None
        self.title = None
        """ Monitor name
            :type : None | str | unicode """
        self.municipality = None
        self.municipality_id = None
        self.type = None
        self.rbl = None
        self.gate = None


class Line(FromToDictBase, PrintableBase):
    def __init__(self):
        super(Line, self).__init__()
        self.name = None
        self.towards = None
        self.direction_id = None
        self.barrier_free = None
        self.realtime_supported = None
        self.traffic_jam = None
        self.departures = None
        """ :type : None | list[wl.models.realtime.Departure] """
        self.type = None
        self.id = None


class Departure(FromToDictBase, PrintableBase):
    def __init__(self):
        super(Departure, self).__init__()
        self.planned = None
        """ :type : None | datetime.datetime """
        self.real = None
        """ :type : None | datetime.datetime """
        self.countdown = None
        """ :type : None | int """
        self.vehicle = None
        """ :type : dict """
