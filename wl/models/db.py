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
# Created: 2017-11-06 19:26

from .general import FromToDictBase, format_vars


class Stop(FromToDictBase):

    def __init__(self):
        super(Stop, self).__init__()
        self.id = None
        self.type = None
        self.stop_id = None
        self.name = None
        self.municipality = None
        self.municipality_id = None
        self.lat = None
        self.lng = None
        self.change_date = None

        self.platforms = None
        """ :type : None | list[wl.models.db.Platform] """

    @classmethod
    def from_csv_row(
            cls,
            entry_id, type, diva, name, municipality, municipality_id,
            lat, lng, change_date
    ):
        return cls.from_dict({
            'id': entry_id,
            'type': type,
            'stop_id': diva,
            'name': name,
            'municipality': municipality,
            'municipality_id': municipality_id,
            'lat': lat,
            'lng': lng,
            'change_date': change_date if change_date else None
        })

    def __str__(self):
        return "<Stop>({})".format(format_vars(self))

    def __repr__(self):
        return self.__str__()


class Line(FromToDictBase):

    def __init__(self):
        super(Line, self).__init__()
        self.id = None
        self.designation = None
        self.order = None
        self.realtime = None
        self.car_type = None
        self.change_date = None

    @classmethod
    def from_csv_row(
            cls,
            entry_id, designation, order, realtime, car_type, change_date
    ):
        return cls.from_dict({
            'id': entry_id,
            'designation': designation,
            'order': order,
            'realtime': realtime == 1,
            'car_type': car_type,
            'change_date': change_date if change_date else None
        })

    def __str__(self):
        return "<Line>({})".format(format_vars(self))

    def __repr__(self):
        return self.__str__()


class Platform(FromToDictBase):

    def __init__(self):
        super(Platform, self).__init__()
        self.id = None
        self.line_id = None
        self.stop_id = None
        self.direction = None
        self.order = None
        self.rbl = None
        self.area = None
        self.platform = None
        self.lat = None
        self.lng = None
        self.change_date = None

        self.line = None
        """ :type : wl.models.db.Line """
        self.stop = None
        """ :type : wl.models.db.Stop """

    @classmethod
    def from_csv_row(
            cls,
            entry_id, line_id, stop_id, direction, order, rbl, area, platform,
            lat, lng, change_date
    ):
        return cls.from_dict({
            'id': entry_id,
            'line_id': line_id,
            'stop_id': stop_id,
            'direction': direction,
            'order': order,
            'rbl': rbl,
            'area': area,
            'platform': platform,
            'lat': lat,
            'lng': lng,
            'change_date': change_date if change_date else None
        })

    def __str__(self):
        return "<Platform>({})".format(format_vars(self))

    def __repr__(self):
        return self.__str__()
