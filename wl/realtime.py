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
# Created: 2017-11-03 10:42

from flotils import Loadable
from flotils.loadable import load_json
from floscraper import WebScraper
from requests.compat import urljoin
from dateutil.parser import parse as dt_parse

from .errors import RequestException, ProtocolViolation
from .models import Request
from .models.realtime import RTResponse, Monitor, Stop, Line, Departure
from .utils import to_utc


class WLRealtime(Loadable):
    """ Wienerlinien realtime API """

    def __init__(self, settings=None):
        if settings is None:
            settings = {}
        super(WLRealtime, self).__init__(settings)
        self.api_key = settings['api_key']
        self.base_url = "https://www.wienerlinien.at/ogd_realtime/"
        self.session = WebScraper(settings.get('web', {}))

    def _parse_datetime(self, dt_str):
        """
        Parse datetime string to object

        :param dt_str: Datetime string to parse
        :type dt_str: str | unicode
        :return: Naive datetime in utc
        :rtype: None | datetime.datetime
        """
        if not dt_str:
            return None
        return to_utc(dt_parse(dt_str))

    def _is_present(
            self, element, field, required=False, type=None, exception_msg=None
    ):
        present = field in element
        # print field

        if not exception_msg:
            exception_msg = "field '{}' is required".format(field)

        if not present and required:
            self.debug(element)
            raise ProtocolViolation(exception_msg)

        return present

    def _get_field(
            self, element, field, required=False, type=None, exception_msg=None
    ):
        """
        Get field on element

        :param element:
        :type element: dict[str | unicode, T]
        :param field:
        :type field: str | unicode
        :param required:
        :type required: bool
        :param type:
        :type type:
        :param exception_msg:
        :type exception_msg: str | unicode | None
        :return:
        :rtype: T
        """
        present = field in element
        # print field

        if not exception_msg:
            exception_msg = "field '{}' is required".format(field)

        if not present:
            if required:
                self.debug(element)
                raise ProtocolViolation(exception_msg)
            return None

        return element[field]

    def _parse_stop(self, stop):
        """

        :param stop:
        :type stop: dict
        :return:
        :rtype: wl.models.realtime.Stop
        """
        if not stop:
            return None
        res = Stop()

        #   Filter            |   Val   | req |   Discr
        # .locationStop       | element |  y  | Informationen über die abgefragte Haltestelle (siehe JSON Geometry Object Definition)
        # ..type              | str     |  y  | Typ des JSON Geometry Objects
        # ..geometry          | element |  y  | Koordinaten Informationen der Haltestelle
        # ...type             | str     |  y  | Typ des Geometry Elements (hier immer 'Point')
        # ...coordinates      | double, |  y  | long,lat Koordinaten der Haltestelle im WGS84 Format
        #                     | double  |     |
        # ..properties        | element |  y  | Detail Informationen über den abgefragten Ort
        # ...name             | str     |  y  | DIVA Nummer der Haltestelle (= Haltestellennummer der el. Fahrplanauskunft)
        # ...title            | str     |  y  | Name der Haltestelle
        # ...municipality     | str     |  y  | Name der Stadt/des Ortes
        # ...municipalityId   | str     |  y  | ID der Stadt/des Ortes
        # ...type             | str     |  y  | Typ des Ortes (hier nur 'stop')
        # ...coordName        | str     |  y  | Verwendetes Koordinatensystem (hier nur 'WGS84')
        # ...gate             | str     |  n  | Gleis oder Steig des Fahrzeugs
        # ...attributes       | element |  y  | beliebige Attribute
        # ....rbl             | str     |  y  | Haltepunkt ID (RBL Nummer)
        res.stop_type = self._get_field(stop, 'type', True)
        self._is_present(stop, 'geometry', True)
        try:
            res.location = {
                'type': self._get_field(stop['geometry'], 'type', True),
                'lat': self._get_field(stop['geometry'], 'coordinates', True)[0],
                'lng': self._get_field(stop['geometry'], 'coordinates', True)[1]
            }
        except IndexError:
            raise ProtocolViolation("No lat/lng")

        self._is_present(stop, 'properties', True)
        self._is_present(stop['properties'], 'name', True)
        res.title = self._get_field(stop['properties'], 'title', True)
        res.municipality = self._get_field(
            stop['properties'], 'municipality', True
        )
        res.municipality_id = self._get_field(
            stop['properties'], 'municipalityId', True
        )
        res.type = self._get_field(stop['properties'], 'type', True)
        res.gate = self._get_field(stop['properties'], 'gate')
        self._is_present(stop['properties'], 'attributes', True)
        res.rbl = self._get_field(stop['properties']['attributes'], 'rbl', True)
        return res

    def _parse_departure(self, departure):
        """

        :param departure:
        :type departure: dict
        :return:
        :rtype: wl.models.realtime.Departure
        """
        res = Departure()
        #   Filter                |   Val   | req |   Discr
        # ....departureTime       | element |  y  | Wrapper für die Abfahrtszeiten
        # .....timePlanned        | datetime|  y  | Abfahrtszeit laut Fahrplan
        # .....timeReal           | datetime|  n  | Prognostizierte Abfahrtszeit (Echtzeit)
        # .....countdown          | int     |  y  | Verbleibende Minuten bis zur Abfahrt
        # ....vehicle             | element |  n  | Informationen über das Fahrzeug (nur wenn abweichend von der Linie)
        # .....name               | str     |  y  | Linienname (e.g.: 13A)
        # .....direction          | str     |  y  | Fahrtrichtung ('H' - hin oder 'R' - retour)
        # .....richtungsId        | str     |  y  | Eindeutige ID der Richtung
        # .....barrierFree        | boolean |  y  | Service Merkmal für das Fahrzeug gibt an, ob das Fahrzeug für mobilitätseingeschränkte Fahrgäste geeignet ist. (true - barrierefreies oder false - kein barrierefreiese Fahrzeug)
        # .....realtimeSupported  | boolean |  y  | Gibt an, ob für die Linie grundsätzlich Echtzeitdaten verfügbar sind (kann die Werte true oder false enthalten)
        # .....trafficjam         | boolean |  y  | Gibt an, ob Stau in der Zufahrt ist. (true - Stau, false - kein Stau)
        # .....type               | str     |  y  | Fahrzeugtyp (ptTram, ..)
        self._is_present(departure, 'departureTime', True)
        res.planned = self._parse_datetime(self._get_field(
            departure['departureTime'], 'timePlanned', True
        ))
        res.real = self._parse_datetime(self._get_field(
            departure['departureTime'], 'timeReal'
        ))
        res.countdown = self._get_field(
            departure['departureTime'], 'countdown', True
        )
        vehicle = departure.get('vehicle')
        if vehicle:
            res.vehicle = {
                'name': self._get_field(vehicle, 'name', True),
                'direction': self._get_field(vehicle, 'direction', True),
                'direction_id': self._get_field(vehicle, 'richtungsId', True),
                'barrier_free': self._get_field(vehicle, 'barrierFree', True),
                'realtime_supported': self._get_field(vehicle, 'realtimeSupported', True),
                'traffic_jam': self._get_field(vehicle, 'trafficjam', True),
                'type': self._get_field(vehicle, 'type', True)
            }
        return res

    def _parse_line(self, line):
        """

        :param line:
        :type line: dict
        :return:
        :rtype: wl.models.realtime.Line
        """
        res = Line()
        # ..name                  | str     |  y  | Name der Linie (e.g.: 13A)
        # ..towards               | str     |  y  | Name des Ziels (e.g.: Burggasse, Stadthalle U)
        # ..direction             | str     |  y  | Richtung ('H' - hin oder 'R' - retour)
        # ..richtungsId           | str     |  y  | Eindeutige ID der Richtung
        # ..barrierFree           | boolean |  n  | Service Merkmal für das Fahrzeug; gibt an, ob das Fahrzeug für mobilitätseingeschränkte Fahrgäste geeignet is. (true - barrierefreies oder false - kein barrierefreies Fahrzeug)
        # ..realtimeSupported     | boolean |  n  | Gibt an, ob für die Linie grundsätzlich Echtzeitdaten verfügbar sind (kann die Werte true oder false enthalten)
        # ..trafficjam            | boolean |  n  | Gibt an, ob Stau in der Zufahrt ist. (true - Stau, false - kein Stau)
        # ..type                  | str     |  y  | Fahrzeugtyp (ptTram, ..)
        # ..lineId                | int     |  n  | Eindeutige Linien ID
        # ..depatures             | element |  y  | Wrapper für die Abfahrten
        # ...departure            |[element]|  n  | Liste der Abfahrten (enthält 1-n Elemente).
        res.name = self._get_field(line, 'name', True)
        res.towards = self._get_field(line, 'towards', True)
        res.direction = self._get_field(line, 'direction', True)
        res.direction_id = self._get_field(line, 'richtungsId', True)
        res.barrier_free = self._get_field(line, 'barrierFree')
        res.realtime_supported = self._get_field(line, 'realtimeSupported')
        res.traffic_jam = self._get_field(line, 'trafficjam')
        res.type = self._get_field(line, 'type', True)
        res.id = self._get_field(line, 'lineId')
        self._is_present(line, 'departures', True)
        deps = line['departures'].get('departure')

        if deps:
            res.departures = []
            for dep in deps:
                res.departures.append(self._parse_departure(dep))
        else:
            # None or empty list
            res.departures = deps

        return res

    def _parse_lines(self, lines):
        """

        :param line:
        :type line: None | list[dict]
        :return:
        :rtype: None | list[wl.models.realtime.Line]
        """
        if not lines:
            return lines
        res = []

        for line in lines:
            res.append(self._parse_line(line))

        return res

    def _parse_monitor(self, monitor):
        """

        :param monitor:
        :type monitor: dict
        :return:
        :rtype: wl.models.realtime.Model
        """
        res = Monitor()

        res.stop = self._parse_stop(
            self._get_field(monitor, 'locationStop', True)
        )

        #   Filter                |   Val   | req |   Discr
        # .lines                  |[element]|  n  | Liste der Linien (enthält 1-n Elemente)
        res.lines = self._parse_lines(self._get_field(monitor, 'lines'))
        return res

    def _parse_monitors(self, monitors):
        """

        :param monitors:
        :type monitors: None | list[dict]
        :return:
        :rtype: None | list[wl.models.realtime.Model]
        """
        if not monitors:
            return monitors
        res = []
        for mon in monitors:
            res.append(self._parse_monitor(mon))
        return res

    def _parse_response(self, data):
        res = RTResponse()
        json = load_json(data)
        res.raw = json
        if not json:
            raise Exception("Empty response")
        if not isinstance(json, dict):
            raise ProtocolViolation("Expected object")

        msg = json.get('message')

        if not msg or not isinstance(msg, dict):
            raise ProtocolViolation("Expected object")

        res.message_code = msg.get('messageCode')
        res.message_value = msg.get('value')

        if res.message_value is None or res.message_code is None:
            raise ProtocolViolation("Value or Code unset")
        server_time = msg.get('serverTime')
        if server_time:
            res.server_time = self._parse_datetime(server_time)
        data = json.get('data')
        """ :type : dict """
        if not data:
            self.warning("No data")
            return res
        res.monitors = self._parse_monitors(data.get('monitors'))
        return res

    def _make_req(self, url_part, req):
        """

        :param url_part: What service of realtime api to use
        :type url_part: str | unicode
        :param req:
        :type req: wl.models.Request
        :return: Parsed response
        :rtype: wl.models.RTResponse
        """
        url = urljoin(self.base_url, url_part)
        params = req.params
        if isinstance(params, dict):
            params = dict(params)
            params.setdefault('sender', self.api_key)
        elif isinstance(params, list):
            params = list(params)
            if not [a for a in params if a[0] == 'sender']:
                params.append(('sender', self.api_key))
        else:
            self.warning("Unknown parameters - cannot add api key")
        try:
            resp = self.session.get(url, params=params)
        except:
            self.exception(
                "Failed to load on {}:\n{}".format(url, params)
            )
            raise RequestException("Request failed")
        if not resp.html:
            self.error(
                "No data {}:\n{}".format(url, params)
            )
            raise RequestException("Empty response")
        try:
            res = self._parse_response(resp.html)
        except:
            self.exception(
                "Failed to parse {}:\n{}".format(url, params)
            )
            raise RequestException("Parse failed")
        return res

    def _parse_traffic(self, data):
        """

        :param data:
        :type data: dict
        :return:
        :rtype:
        """
        self.debug("()")

        #   Filter                  |   Val   | req |   Discr
        # trafficInfoCategoryGroups |[element]|  n  | Wrapper für die StörungsKategorie Gruppen (enthält 1-n Elemente). Wird nur angezeigt, wenn es Störungen für die Abfrage gibt.
        # .id                       | int     |  y  | Eindeutige ID der Gruppe
        # .name                     | str     |  y  | Name der Gruppe (hier immer "pt")
        for cat in data.get('trafficInfoCategoryGroups', []):
            if self._is_present(cat, 'id', True):
                pass
            if self._is_present(cat, 'name', True):
                pass

        #   Filter                        |   Val   | req |   Discr
        # trafficInfoCategories           |[element]|  n  | Wrapper für die StörungsKategorie (enthält 1-n Elemente). Wird nur angezeigt, wenn es Störungen für die Abfrage gibt.
        # .id                             | int     |  y  | Eindeutige ID der Kategorie
        # .refTrafficInfoCategoryGroupId  | int     |  y  | Referenzierung auf die Kategorie ID der Gruppe
        # .name                           | str     |  y  | Name der Kategorie (stoerunglang, stoerungkurz, aufzugsinfo)
        # .trafficInfoNameList            | str     |  y  | Enthält die mit dem Monitor verknüpften Störungen der jeweiligen Kategorie mit Beistrich getrennt (Bsp.: v41_2,v41_1)
        # .title                          | str     |  y  | Titel der Kategorie
        for cat in data.get('trafficInfoCategories', []):
            if self._is_present(cat, 'id', True):
                pass
            if self._is_present(cat, 'refTrafficInfoCategoryGroupId', True):
                pass
            if self._is_present(cat, 'name', True):
                pass
            if self._is_present(cat, 'trafficInfoNameList', True):
                pass
            if self._is_present(cat, 'title', True):
                pass

        # Filter                  |   Val   | req |   Discr
        # trafficInfos              |[element]|  n  | Wrapper für die Störungen (enthält 1-n Elemente)
        # .refTrafficInfoCategoryId | int     |  y  | Referenzierung auf die Kategorie ID
        # .name                     | str     |  y  | Eindeutiger Name der Störung
        # .priority                 | str     |  n  | Priorität der Störung
        # .owner                    | str     |  n  | Datenlieferant
        # .title                    | str     |  y  | Titel der Störung
        # .description              | str     |  y  | Beschreibung der Störung
        # .relatedLines             | str     |  n  | Liste der Linien, die mit dieser Störung verknüpft sind. Trennzeichen Komma
        # .relatedStops             | str     |  n  | Liste der Haltepunkte (=RBL-Nummern), die mit dieser Störung verknüpft sind. Trennzeichen Komma
        # .time                     | element |  n  | Beinhaltet Start- und Endzeit der Störung
        # ..start                   | datetime|  n  | Startzeit der Störung
        # ..end                     | datetime|  n  | Endzeit der Störung
        # ..resume                  | datetime|  n  | Wiederaufnahme des Fahrtbetriebs innerhalb der Störung
        # .attributes               | element |  n  | Wrapper für Zusatzinformation
        # ..status                  | str     |  n  | Zusatzinformation bei Aufzugsstörung (z.B. außer Betrieb)
        # ..station                 | str     |  n  | Zusatzinformation bei Aufzugsstörung. Welche Haltestelle ist betroffen
        # ..location                | str     |  n  | Zusatzinformation bei Aufzugsstörung. Ort des Aufzuges
        # ..reason                  | str     |  n  | Zusatzinformation bei Aufzugsstörung. Textuelle Ausgabe des Grunds der Störung
        # ..towards                 | str     |  n  | Zusatzinformation bei Aufzugsstörung. Richtung der Linie (wenn nur eine Linie betroffen ist)
        # ..relatedLines            | str     |  n  | Zusatzinformation bei Aufzugsstörung. Liste der Linien, die mit dieser Störung verknüpft sind. Trennzeichen Komma
        # ..relatedStops            | str     |  n  | Zusatzinformation bei Aufzugsstörung. Liste der Haltestellen, die mit dieser Störung verknüpft sind. Trennzeichen Komma
        for info in data.get('trafficInfos',[]):
            if self._is_present(info, 'refTrafficInfoCategoryId', True):
                pass
            if self._is_present(info, 'name', True):
                pass
            if self._is_present(info, 'priority'):
                pass
            if self._is_present(info, 'owner'):
                pass
            if self._is_present(info, 'title', True):
                pass
            if self._is_present(info, 'description', True):
                pass
            if self._is_present(info, 'relatedLines'):
                pass
            if self._is_present(info, 'relatedStops'):
                pass
            if self._is_present(info, 'time'):
                if self._is_present(info, 'start'):
                    pass
                if self._is_present(info, 'end'):
                    pass
                if self._is_present(info, 'resume'):
                    pass
            if self._is_present(info, 'attributes'):
                if self._is_present(info['attributes'], 'status'):
                    pass
                if self._is_present(info['attributes'], 'station'):
                    pass
                if self._is_present(info['attributes'], 'location'):
                    pass
                if self._is_present(info['attributes'], 'reason'):
                    pass
                if self._is_present(info['attributes'], 'towards'):
                    pass
                if self._is_present(info['attributes'], 'relatedLines'):
                    pass
                if self._is_present(info['attributes'], 'relatedStops'):
                    pass

    def _parse_news(self, data):
        """

        :param data:
        :type data: dict
        :return:
        :rtype:
        """
        self.debug("()")

        #   Filter                  |   Val   | req |   Discr
        # poiCategoryGroups         |[element]|  y  | Gruppen-Wrapper
        # .id                       | int     |  y  | Eindeutige ID der Gruppe (-1 für Aufzugsservice)
        # .name                     | str     |  y  | Name der Gruppe
        if self._is_present(data, 'poiCategoryGroups', True):
            for cat in data['poiCategoryGroups']:
                if self._is_present(cat, 'id', True):
                    pass
                if self._is_present(cat, 'name', True):
                    pass

        # Filter                        |   Val   | req |   Discr
        # poiCategories                   |[element]|  y  | Kategorien-Wrapper
        # .id                             | int     |  y  | Eindeutige ID der Kategorie
        # .refPoiCategoryGroupId          | int     |  y  | Referenzierung auf ID der Grupp
        # .name                           | str     |  y  | Name der Kategorie
        # .title                          | str     |  y  | Titel der Kategorie
        if self._is_present(data, 'poiCategories', True):
            for cat in data['poiCategoryGroups']:
                if self._is_present(cat, 'id', True):
                    pass
                if self._is_present(cat, 'refPoiCategoryGroupId', True):
                    pass
                if self._is_present(cat, 'name', True):
                    pass
                if self._is_present(cat, 'trafficInfoNameList', True):
                    pass
                if self._is_present(cat, 'title', True):
                    pass

        # Filter                  |   Val   | req |   Discr
        # pois                      |[element]|  y  | Störungs-Wrapper
        # .refPoiCategoryId         | int     |  y  | Referenzierung auf die ID der Kategorie
        # .name                     | str     |  y  | Eindeutiger Name der News
        # .title                    | str     |  y  | Titel
        # .subtitle                 | str     |  n  | Sub-Titel
        # .description              | str     |  y  | Beschreibungstext
        # .relatedLines             | str     |  n  | Liste der Linien, die mit diesem Eintrag verknüpft sind. Trennzeichen Komma
        # .relatedStops             | str     |  n  | Liste der Haltepunkte, die mit diesem Eintrag verknüpft sind. Trennzeichen Komma
        # .time                     | element |  y  | Beinhaltet Start- und Endzeit der Gültigkeit
        # ..start                   | datetime|  y  | Startzeit der Gültigkeit
        # ..end                     | datetime|  y  | Endzeit der Gültigkeit
        # .attributes               | element |  n  | Wrapper für Zusatzinformation
        # ..status                  | str     |  n  | Zusatzinformation bei Aufzugswartung
        # ..station                 | str     |  n  | Zusatzinformation bei Aufzugswartung. Welche Haltestelle ist betroffen
        # ..location                | str     |  n  | Zusatzinformation bei Aufzugswartung. Ort des Aufzuges
        # ..towards                 | str     |  n  | Zusatzinformation bei Aufzugswartung. Textuelle Ausgabe der Richtungen der Linie
        # ..relatedLines            | str     |  n  | Zusatzinformation bei Aufzugswartung. Liste der Linien, die mit diesem Eintrag verknüpft sind. Trennzeichen Komma
        # ..relatedStops            | str     |  n  | Zusatzinformation bei Aufzugswartung. Liste der Haltestellen, die mit diesem Eintrag verknüpft sind. Trennzeichen Komma
        # ..ausVon                  | datetime|  n  | Startzeit der Wartung
        # ..ausBis                  | datetime|  n  | Endzeit der Wartung
        # ..rbls                    | str     |  n  | Zusatzinformation bei Aufzugswartung. Liste der Haltepunkte, die mit diesem Eintrag, verknüpft sind. Trennzeichen Komma
        for info in data.get('pois', []):
            if self._is_present(info, 'refPoiCategoryId', True):
                pass
            if self._is_present(info, 'name', True):
                pass
            if self._is_present(info, 'title', True):
                pass
            if self._is_present(info, 'subtitle'):
                pass
            if self._is_present(info, 'description', True):
                pass
            if self._is_present(info, 'relatedStops'):
                pass
            if self._is_present(info, 'relatedLines'):
                pass
            if self._is_present(info, 'time', True):
                if self._is_present(info, 'start', True):
                    pass
                if self._is_present(info, 'end', True):
                    pass
            if self._is_present(info, 'attributes'):
                if self._is_present(info['attributes'], 'status'):
                    pass
                if self._is_present(info['attributes'], 'station'):
                    pass
                if self._is_present(info['attributes'], 'location'):
                    pass
                if self._is_present(info['attributes'], 'towards'):
                    pass
                if self._is_present(info['attributes'], 'relatedLines'):
                    pass
                if self._is_present(info['attributes'], 'relatedStops'):
                    pass
                if self._is_present(info['attributes'], 'ausVon'):
                    pass
                if self._is_present(info['attributes'], 'ausBis'):
                    pass
                if self._is_present(info['attributes'], 'rbls'):
                    pass

    def monitor(self, rbls, traffic_info=None):
        """
        Get departure monitor for stop

        :param rbls: One or more rbls
        :type rbls: str | unicode | list[str | unicode]
        :param traffic_info: One or more of
            'stoerunglang', 'stoerungkurz', 'aufzugsinfo'
        :type traffic_info: str | unicode | list[str | unicode]
        :return: Monitor information
        :rtype:
        """
        if not isinstance(rbls, list):
            rbls = [rbls]
        req = Request()
        req.params = [("rbl", rbl) for rbl in rbls]
        if traffic_info:
            if not isinstance(traffic_info):
                traffic_info = [traffic_info]
            req.params.extend([("activateTrafficInfo", t) for t in traffic_info])
        resp = self._make_req("monitor", req)
        if resp.message_code != RTResponse.CODE_OK:
            raise RequestException("Error response {} ({})".format(
                resp.message_code, resp.message_value)
            )

        if resp.monitors is None:
            raise RequestException("No monitors parsed")
        return resp
