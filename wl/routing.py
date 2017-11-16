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
# Created: 2017-11-02 00:10

import datetime

try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree

from flotils import Loadable
from floscraper import WebScraper
from requests.compat import urljoin
from dateutil.parser import parse as dt_parse

from .models.routing import ItdRequest, ItdResponse, ItdDMResponse,\
    Line, Departure, Stop
from .errors import RequestException
from .utils import local_to_utc, utc_to_local


class WLRouting(Loadable):
    """ Wienerlinien routing API """

    def __init__(self, settings=None):
        if settings is None:
            settings = {}
        super(WLRouting, self).__init__(settings)
        self.base_url = "https://www.wienerlinien.at/ogd_routing/"
        self.session = WebScraper(settings.get('web', {}))

    def _parse_datetime_st(self, st):
        if not st:
            return st
        return local_to_utc(dt_parse(st))

    def _parse_response(self, data):
        """

        :param data:
        :type data:
        :return:
        :rtype: wl.models.routing.ItdResponse
        """
        try:
            root = etree.fromstring(data)
        except ValueError:
            root = etree.fromstring(
                data.encode("utf-8"),
                parser=etree.XMLParser(encoding="utf-8")
            )
        if root is None or root.tag != "itdRequest":
            raise ValueError("Wrong root tag")
        res = ItdResponse()
        attr = {}
        if root.attrib:
            attr = root.attrib
        if 'serverID' in attr:
            res.server_id = attr['serverID']
        if 'version' in attr:
            res.version = attr['version']
        if 'language' in attr:
            res.language = attr['language']
        if 'lengthUnit' in attr:
            res.length_unit = attr['lengthUnit']
        if 'sessionID' in attr:
            res.session_id = attr['sessionID']
        if 'client' in attr:
            res.client = attr['client']
        if 'virtDir' in attr:
            res.virt_dir = attr['virtDir']
        if 'clientIP' in attr:
            res.client_ip = attr['clientIP']
        if 'now' in attr:
            res.now = self._parse_datetime_st(attr['now'])
        if 'nowWD' in attr:
            res.now_wd = attr['nowWD']
        res.children = list(root)
        return res

    def _make_req(self, url_part, req):
        """

        :param url_part: What service of routing api to use
        :type url_part: str | unicode
        :param req:
        :type req: wl.models.routing.ItdRequest
        :return: Response root element
        :rtype: wl.models.routing.ItdResponse
        """
        url = urljoin(self.base_url, url_part)
        try:
            resp = self.session.get(url, params=req.to_get_params())
        except:
            self.exception(
                "Failed to load on {}:\n{}".format(url, req.to_get_params())
            )
            raise RequestException("Request failed")
        try:
            if resp.html and resp.html.startswith("<!DOCTYPE HTML"):
                raise RequestException("API send plain html")
            data = resp.raw
            if not data:
                self.warning("Defaulting to decoded response")
                data = resp.html
            res = self._parse_response(data)
        except:
            self.exception(
                "Failed to parse {}:\n{}".format(url, req.to_get_params())
            )
            raise RequestException("Parse failed")
        return res

    def _parse_line(self, root):
        """

        :param root:
        :type root: xml.etree.ElementTree.Element
        :return:
        :rtype: wl.models.routing.Line
        """
        if root.tag != "itdServingLine":
            raise ValueError("Expected line - {}".format(root.tag))
        #self.debug("\n" + etree.tostring(root, pretty_print=True))
        line_dict = root.attrib
        for ele in root:
            if ele.tag == "motDivaParams":
                line_dict['network'] = ele.attrib.get('network')
                line_dict['line'] = ele.attrib.get('line')
            elif ele.tag == "itdRouteDescText":
                line_dict['description'] = ele.text
        #self.debug(line_dict)
        return Line.from_dict(line_dict)

    def _parse_lines(self, root):
        """

        :param root:
        :type root: xml.etree.ElementTree.Element
        :return:
        :rtype: list[wl.models.routing.Line]
        """
        if root.tag != "itdServingLines":
            raise ValueError("Expected lines - {}".format(root.tag))

        lines = []
        for ele in root:
            lines.append(self._parse_line(ele))
        return lines

    def _parse_datetime_itd(self, root):
        """

        :param root:
        :type root: xml.etree.ElementTree.Element
        :return:
        :rtype: datetime.datetime
        """
        if root.tag != "itdDateTime":
            raise ValueError("Expected datetime - {}".format(root.tag))
        d = root.find("itdDate")
        t = root.find("itdTime")
        dt_dict = {}
        if d is None:
            raise ValueError("Expected date")
        if t is None:
            raise ValueError("Expected time")
        dt_dict.update(d.attrib)
        dt_dict.update(t.attrib)
        del dt_dict['weekday']
        dt_dict = {key: int(value) for key, value in dt_dict.items() if value}
        return local_to_utc(datetime.datetime(**dt_dict))

    def _parse_departure(self, root):
        """

        :param root:
        :type root: xml.etree.ElementTree.Element
        :return:
        :rtype: wl.models.routing.Depature
        """
        if root.tag != "itdDeparture":
            raise ValueError("Expected departure - {}".format(root.tag))
        d = root.attrib
        d.update({
            'stop_id': d['stopID'],
            'stop_name': d['stopName'],
            'platform_name': d['platformName']
        })
        res = Departure.from_dict(d)
        for ele in root:
            if ele.tag == "itdServingLine":
                res.line = self._parse_line(ele)
            elif ele.tag == "itdDateTime":
                res.datetime = self._parse_datetime_itd(ele)
            else:
                self.debug("{}".format(ele.tag))

        return res

    def _parse_departures(self, root):
        """

        :param root:
        :type root: xml.etree.ElementTree.Element
        :return:
        :rtype: list[wl.models.routing.Depature]
        """
        if root.tag != "itdDepartureList":
            raise ValueError("Expected departures - {}".format(root.tag))
        deps = []
        for ele in root:
            deps.append(self._parse_departure(ele))
        return deps

    def _parse_stop(self, root):
        """

        :param root:
        :type root: xml.etree.ElementTree.Element
        :return:
        :rtype: wl.models.routing.Stop
        """
        if root.tag != "itdOdvAssignedStop":
            raise ValueError("Expected stop - {}".format(root.tag))
        d = root.attrib
        d.update({
            'stop_id': d['stopID'],
            'distance_time': d['distanceTime']
        })
        res = Stop.from_dict(d)
        res.name = root.text
        return res

    def _parse_stops(self, root):
        """

        :param root:
        :type root: xml.etree.ElementTree.Element
        :return:
        :rtype: list[wl.models.routing.Stop]
        """
        if root.tag != "itdOdvAssignedStops":
            raise ValueError("Expected stops - {}".format(root.tag))
        stops = []
        for ele in root:
            stops.append(self._parse_stop(ele))
        return stops

    def _parse_odv_name_elem(self, root):
        if root.tag != "odvNameElem":
            raise ValueError("Expected odv name elem - {}".format(root.tag))
        res = Stop()
        res.stop_id = root.attrib.get('id', root.attrib.get('stopID'))
        res.name = root.text
        return res

    def _parse_odv_name(self, root):
        if root.tag != "itdOdvName":
            raise ValueError("Expected odv name - {}".format(root.tag))
        stops = []
        for ele in root:
            if ele.tag == "odvNameElem":
                stops.append(self._parse_odv_name_elem(ele))
        return stops

    def _parse_itd_odv(self, root, res):
        """

        :param root:
        :type root: xml.etree.ElementTree.Element
        :param res:
        :type res: wl.models.routing.ItdDMResponse
        :return:
        :rtype: wl.models.routing.ItdDMResponse
        """
        if root.tag != "itdOdv":
            raise ValueError("Expected odv - {}".format(root.tag))
        xml_stops = root.find("itdOdvAssignedStops")
        if xml_stops is not None:
            res.stops = self._parse_stops(xml_stops)
        else:
            # No stops -> select
            xml_names = root.find("itdOdvName")
            res.stops = self._parse_odv_name(xml_names)
        return res

    def _parse_response_dm(self, resp):
        """

        :param resp:
        :type resp: wl.models.routing.ItdResponse
        :return:
        :rtype: wl.models.routing.ItdDMResponse
        """
        if not resp.children or len(resp.children) != 0:
            ValueError("Invalid Subtype")
        mon = resp.children[0]
        """ :type : xml.etree.ElementTree.Element """
        if mon.tag != "itdDepartureMonitorRequest":
            ValueError("Exepected departure monitor - {}".format(mon.tag))
        res = ItdDMResponse.from_dict(resp.to_dict())
        res.children = None
        res.request_id = mon.get('requestID')
        for ele in mon:
            if ele.tag == "itdServingLines":
                res.lines = self._parse_lines(ele)
            elif ele.tag == "itdDateTime":
                res.datetime = self._parse_datetime_itd(ele)
            elif ele.tag == "itdDepartureList":
                res.departures = self._parse_departures(ele)
            elif ele.tag == "itdOdv":
                self._parse_itd_odv(ele, res)
        return res

    def _make_req_dm(self, req):
        """

        :param req:
        :type req: wl.models.routing.ItdRequest
        :return:
        :rtype: wl.models.routing.ItdDMResponse
        """
        itd_resp = self._make_req("XML_DM_REQUEST", req)
        #self.debug("\n" + etree.tostring(itd_resp.children[0], pretty_print=True))
        return self._parse_response_dm(itd_resp)

    def dm_search(self, location, dt=None, limit=40):
        req = ItdRequest()
        req.session_id = 0
        req.params.update({
            'locationServerActive': 1,
            'lsShowTrainsExplicit': 1,
            'type_dm': "any",
            'name_dm': location,
            'limit': limit
        })
        if dt:
            dt = utc_to_local(dt)
            req.params['itdDate'] = dt.strftime("%Y%m%d")
            req.params['itdTime'] = dt.strftime("%H%M")
        res = self._make_req_dm(req)
        return res

    def dm_select(self, resp, lines=None, dt=None, stops=None, limit=40):
        req = ItdRequest.from_dict(resp.to_dict())
        """ :type : wl.models.routing.ItdRequest """
        req.params = []
        if stops:
            req.params.append(("type_dm", "stopID"))
            for stop_id in stops:
                req.params.append(("name_dm", stop_id))

        if lines is None:
            req.params.append(("dmLineSelectionAll", 1))
        else:
            req.params = []
            for line in lines:
                if isinstance(line, Line):
                    req.params.append(("dmLineSelection", line.index))
                else:
                    req.params.append(("dmLineSelection", line))
        if dt:
            dt = utc_to_local(dt)
            req.params.append(("itdDate",dt.strftime("%Y%m%d")))
            req.params.append(("itdTime", dt.strftime("%H%M")))
        req.params.append(('limit', limit))
        res = self._make_req_dm(req)
        return res

    def dm_search_select(self, location, dt=None, limit=40):
        req = ItdRequest()
        req.session_id = 0
        req.params.update({
            'locationServerActive': 1,
            'lsShowTrainsExplicit': 1,
            'type_dm': "any",
            'name_dm': location,
            'limit': limit,
            'dmLineSelectionAll': 1
        })
        if dt:
            dt = utc_to_local(dt)
            req.params['itdDate'] = dt.strftime("%Y%m%d")
            req.params['itdTime'] = dt.strftime("%H%M")
        res = self._make_req_dm(req)
        return res
