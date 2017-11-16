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
__date__ = "2017-11-06"
# Created: 2017-11-06 19:33

import os
import csv

from flotils import Loadable

from .models.db import Stop, Line, Platform


class WLDatabase(Loadable):

    def __init__(self, settings=None):
        if settings is None:
            settings = {}
        super(WLDatabase, self).__init__(settings)
        self.path_data = self.join_path_prefix(
            settings.get('path_data', "data")
        )
        self.path_csv_stops = self.join_path_prefix(os.path.join(
            self.path_data,
            settings.get('path_csv_stops', "wienerlinien-ogd-haltestellen.csv")
        ))
        self.path_csv_lines = self.join_path_prefix(os.path.join(
            self.path_data,
            settings.get('path_csv_lines', "wienerlinien-ogd-linien.csv")
        ))
        self.path_csv_platforms = self.join_path_prefix(os.path.join(
            self.path_data,
            settings.get(
                'path_csv_platforms', "wienerlinien-ogd-steige.csv"
            )
        ))
        self.stops = None
        """ :type : dict[int, wl.models.db.Stop] """
        self.platforms = None
        """ :type : dict[int, wl.models.db.Platform] """
        self.lines = None
        """ :type : dict[int, wl.models.db.Line] """

    def _csv_load(self , path , expected_keys, obj_cls):
        res = []

        with open(path, 'rb') as csvfile:
            dialect = csv.Sniffer().sniff( csvfile.read( 1024))
            csvfile.seek( 0)
            reader = csv.reader( csvfile, dialect)
            keys = reader.next()

            if len(expected_keys) != len(keys):
                raise IOError("csv error - unexpected number of keys")

            for i in range(len(keys)):
                if keys[i] != expected_keys[i]:
                    raise IOError("csv error - keys not matching")

            for row in reader:
                res.append(obj_cls.from_csv_row(*row))
        return res

    def csv_load_stops(self):
        res = self._csv_load(self.path_csv_stops, [
            "HALTESTELLEN_ID", "TYP", "DIVA", "NAME", "GEMEINDE", "GEMEINDE_ID",
            "WGS84_LAT", "WGS84_LON", "STAND"
        ], Stop)
        self.debug("Loaded {} stops".format(len(res)))
        return res

    def csv_load_lines(self):
        res = self._csv_load(self.path_csv_lines, [
            "LINIEN_ID","BEZEICHNUNG","REIHENFOLGE","ECHTZEIT",
            "VERKEHRSMITTEL","STAND"
        ], Line)
        self.debug("Loaded {} lines".format(len(res)))
        return res

    def csv_load_platforms(self):
        res = self._csv_load(self.path_csv_platforms, [
            "STEIG_ID","FK_LINIEN_ID","FK_HALTESTELLEN_ID","RICHTUNG",
            "REIHENFOLGE","RBL_NUMMER","BEREICH","STEIG",
            "STEIG_WGS84_LAT","STEIG_WGS84_LON","STAND"
        ], Platform)
        self.debug("Loaded {} platforms".format(len(res)))
        return res

    def find_stop(self, stop_id):
        """

        :param stop_id: Stop id (DIVA)
        :type stop_id: int
        :return:
        :rtype: wl.models.db.Stop
        """
        if not self.stops:
            return None
        val = 0
        for stop in self.stops.values():
            val += 1
            if stop.stop_id == stop_id:
                return stop
        return None

    def csv_load(self):
        self.debug("()")
        self.stops = {
            stop.id: stop for stop in self.csv_load_stops()
        }
        self.lines = {
            line.id: line for line in self.csv_load_lines()
        }
        for platform in self.csv_load_platforms():
            stop = self.stops[platform.stop_id]
            platform.stop = stop
            platform.line = self.lines[platform.line_id]
            if stop.platforms is None:
                stop.platforms = []
            stop.platforms.append(platform)
