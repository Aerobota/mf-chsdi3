# -*- coding: utf-8 -*-

import requests
import xml.etree.ElementTree as et
from pytz import timezone
from datetime import datetime, timedelta
from pyramid.threadlocal import get_current_registry


class OpenTrans:

    def __init__(self):
        self.open_trans_api_key = get_current_registry().settings['opentrans_api_key']  # Get API key from config .ini
        self.url = 'https://api.opentransportdata.swiss/trias'  # URL of API

    def get_departures(self, station_id, number_results=5, request_dt_time=False):
        if not request_dt_time:
            request_dt_time = datetime.now(timezone('Europe/Zurich')).strftime('%Y-%m-%dT%H:%M:%S')
        api_response_xml = self.send_post(station_id, request_dt_time, number_results)  # request_dt_time in format 2017-12-11T14:26:18Z
        results = self.xml_to_array(api_response_xml)
        return results

    def _format_time(self, str_date_time, only_time=False):
        formated_date_time = datetime.strptime(str_date_time, '%Y-%m-%dT%H:%M:%SZ')
        formated_date_time += timedelta(hours=1)  # time offset UTC +1
        if only_time:
            style_date_time = '%H:%M'
        else:
            style_date_time = '%d/%m/%Y %H:%M'
        return formated_date_time.strftime(style_date_time)

    def _calc_delay(self, el_timetable, el_estimated):
        if el_estimated == None:
            return 'nodata'
        else:
            timetable_time = datetime.strptime(el_timetable.text, '%Y-%m-%dT%H:%M:%SZ')
            estimated_time = datetime.strptime(el_estimated.text, '%Y-%m-%dT%H:%M:%SZ')
            time_diff = estimated_time - timetable_time
            hours, minutes, seconds = self._convert_timedelta(time_diff)
            return '%d:%02d' % (hours, minutes)

    def _convert_estimated_date(self, el_estimated):
        if el_estimated == None:
            return 'nodata'
        else:
            return self._format_time(el_estimated.text)

    def _convert_timedelta(self, duration):
        days, seconds = duration.days, duration.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = (seconds % 60)
        return hours, minutes, seconds

    def xml_to_array(self, xml_data):
        ns = {'trias': 'http://www.vdv.de/trias'}
        root = et.fromstring(xml_data)
        el_stop_events = root.findall('.//trias:StopEvent', ns)
        results = [{
            'id': el.find('./trias:ThisCall/trias:CallAtStop/trias:StopPointRef', ns).text,
            'time': self._format_time(el.find('./trias:ThisCall/trias:CallAtStop/trias:ServiceDeparture/trias:TimetabledTime', ns).text, True),
            'label': el.find('./trias:Service/trias:PublishedLineName/trias:Text', ns).text,
            'currentDate': self._format_time(root.find('.//{http://www.siri.org.uk/siri}ResponseTimestamp').text),
            'departureDate': self._format_time(el.find('./trias:ThisCall/trias:CallAtStop/trias:ServiceDeparture/trias:TimetabledTime', ns).text),
            'estimatedDate': self._convert_estimated_date(el.find('./trias:ThisCall/trias:CallAtStop/trias:ServiceDeparture/trias:EstimatedTime', ns)),
            'predictableDelay': self._calc_delay(el.find('./trias:ThisCall/trias:CallAtStop/trias:ServiceDeparture/trias:TimetabledTime', ns),
                                                el.find('./trias:ThisCall/trias:CallAtStop/trias:ServiceDeparture/trias:EstimatedTime', ns)),
            'destinationName': el.find('./trias:Service/trias:DestinationText/trias:Text', ns).text,
            'destinationId': el.find('./trias:Service/trias:DestinationStopPointRef', ns).text
        } for el in el_stop_events]
        return results

    def send_post(self, station_id, request_dt_time, number_results=5):
        self.headers = {
            'Authorization': self.open_trans_api_key,
            'Content-Type': 'application/xml'
        }
        self.xml_data = """
                    <?xml version="1.0" encoding="UTF-8"?>
                    <Trias version="1.1" xmlns="http://www.vdv.de/trias" xmlns:siri="http://www.siri.org.uk/siri" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                        <ServiceRequest>
                            <siri:RequestTimestamp>%s</siri:RequestTimestamp>
                            <siri:RequestorRef>EPSa</siri:RequestorRef>
                            <RequestPayload>
                                <StopEventRequest>
                                    <Location>
                                        <LocationRef>
                                            <StopPointRef>%s</StopPointRef>
                                        </LocationRef>
                                        <DepArrTime>%s</DepArrTime>
                                    </Location>
                                    <Params>
                                        <NumberOfResults>%s</NumberOfResults>
                                        <StopEventType>departure</StopEventType>
                                        <IncludePreviousCalls>false</IncludePreviousCalls>
                                        <IncludeOnwardCalls>true</IncludeOnwardCalls>
                                        <IncludeRealtimeData>true</IncludeRealtimeData>
                                    </Params>
                                </StopEventRequest>
                            </RequestPayload>
                        </ServiceRequest>
                    </Trias>
                    """ % (str(request_dt_time), str(station_id), str(request_dt_time), str(number_results))
        self.r = requests.post(self.url, self.xml_data, headers=self.headers)
        self.r.encoding = 'utf-8'
        return self.r.text.encode('utf-8')
