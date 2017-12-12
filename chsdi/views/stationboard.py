# -*- coding: utf-8 -*-


from sqlalchemy.exc import OperationalError
from pyramid.httpexceptions import HTTPInternalServerError, HTTPBadRequest
from pyramid.view import view_config, view_defaults
from chsdi.lib.opentransapi import opentransapi


@view_defaults(renderer='jsonp', route_name='stationboard')
class TransportView(object):

    DEFAULT_LIMIT = 5

    MAX_LIMT = 20

    def __init__(self, request):
        self.ot_api = opentransapi.OpenTrans()
        self.request = request
        if request.matched_route.name == 'stationboard':
            id = request.matchdict['id']
            if id.isdigit() is False:
                raise HTTPBadRequest('The id must be an integer.')
            else:
                self.id = int(id)

            self.destination = request.params.get('destination', 'all')

            limit = request.params.get('limit')
            if limit:
                if limit.isdigit():
                    self.limit = min(int(limit), self.MAX_LIMT)
                else:
                    raise HTTPBadRequest('The limit parameter must be an integer.')
            else:
                self.limit = self.DEFAULT_LIMIT

    @view_config(request_method='GET')
    def get_departures(self):
        try:
            results = self.ot_api.get_departures(self.id, self.limit)
            if len(results) == 0:
                results = None
        except OperationalError as e:  # pragma: no cover
            raise HTTPInternalServerError(e)

        if not results:
            return [{'destination': 'nodata'}]
        return results
