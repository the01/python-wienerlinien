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
__date__ = "2017-11-07"
# Created: 2017-11-07 01:34

from flotils import Loadable

from .realtime import WLRealtime
from .routing import WLRouting
from .db import WLDatabase
from .models.general import Response, Stop, Line, Location, Departure
from .models.routing import ItdRequest


class WL(Loadable):
    """ Wienerlinien client """

    def __init__(self, settings=None):
        if settings is None:
            settings = {}
        super(WL, self).__init__(settings)
        self.realtime = WLRealtime(settings['realtime'])
        self.routing = WLRouting(settings.get('routing', {}))
        self.database = WLDatabase(settings.get('database', {}))

        self.database.csv_load()

    def _print(self, req):
        if req.stops:
            self.debug("stops:")
            for stop in req.stops:
                self.debug("{} ({}m)".format(stop.name, stop.distance))
        if req.lines:
            self.debug("lines:")
            for line in req.lines:
                self.debug("{}: {} ({})".format(
                    line.symbol, line.direction, line.description)
                )
        if req.departures:
            self.debug("departures:")
            for dep in req.departures:
                line_st = ""
                if dep.line:
                    line_st = "{}-{}: ".format(
                        dep.line.symbol, dep.line.direction
                    )
                self.debug("{}{}-{}: {} ({})".format(
                    line_st,
                    dep.stop_name, dep.platform_name, dep.datetime,
                    dep.countdown
                ))

    def _from_itd_dm_response(self, itd):
        """

        :param itd:
        :type itd: wl.models.routing.ItdDMResponse
        :return:
        :rtype: wl.models.general.Response
        """
        res = Response()
        if not itd:
            return None
        res.id = ":"
        if itd.session_id:
            res.id = itd.session_id + res.id
        if itd.request_id:
            res.id = res.id + itd.request_id
        if itd.stops:
            res.stops = []
            for stop in itd.stops:
                new = Stop()
                new.id = stop.stop_id
                new.name = stop.name
                new.distance = stop.distance
                new.distance_time = stop.distance_time
                db_stop = self.database.find_stop(new.id)
                if db_stop:
                    new.location = Location(db_stop.lat, db_stop.lng)
                    if not(new.location.latitude and new.location.longitude):
                        new.location = None
                res.stops.append(new)
        if itd.departures:
            res.departures = []

            for dep in itd.departures:
                new = Departure()
                new.datetime = dep.datetime
                new.countdown = dep.countdown
                new.stop_id = dep.stop_id
                new.stop_name = dep.stop_name
                if dep.line:
                    new.direction = dep.line.direction
                    new.line_name = dep.line.symbol
                res.departures.append(new)
        return res

    def find_by(self, address, dt=None):
        self.debug("({}, {})".format(address, dt))
        res = self.routing.dm_search(address, dt)
        self._print(res)
        if res.departures:
            return None
        return self._from_itd_dm_response(res)

    def select(self, session, stops=None, lines=None, dt=None, limit=20):
        req = ItdRequest()
        parts =[""]
        if session:
            parts = session.split(":")
        if parts[0]:
            req.session_id = parts[0]
        if len(parts) > 1 and parts[1]:
            req.request_id = parts[1]

        selected = self.routing.dm_select(
            req, stops=stops, lines=lines, dt=dt, limit=limit
        )
        if stops:
            selected = self.routing.dm_select(
                selected, limit=limit
            )
        #self._print(selected)
        return self._from_itd_dm_response(selected)
