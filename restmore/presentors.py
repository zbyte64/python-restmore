'''
Request (set serializer in `handle`) -> Resource -> Data
    -> Presentor (set response type in `build_response`, inject hypermedia in `serialize`)
    -> Normalizer (globalized preparer) -> Serializer
'''
from django.http import HttpResponse
from restless.serializers import JSONSerializer

from .normalizer import NormalizedPreparer


class Presentor(object):
    '''
    A simple JSON presentor
    '''
    def get_serializer(self):
        return JSONSerializer

    def inject(self, method, endpoint, data):
        '''
        Inject hypermedia data
        '''
        return data

    def get_response_type(self):
        return 'application/json'


class PresentorResourceMixin(object):
    preparer = NormalizedPreparer()

    def handle(self, endpoint, *args, **kwargs):
        #why the extra layer of indirection? so we can dynamically switch serializers and hypermedia
        self.presentor = self.get_presentor()
        self.serializer = self.presentor.get_serializer()
        return super(PresentorResourceMixin, self).handle(endpoint, *args, **kwargs)

    def build_status_response(self, data, status=200):
        '''
        Like build response but serializes the data for you
        '''
        return self.build_response(self.prepare(data), status=status)

    def get_presentor(self):
        #TODO settable with django setting: `RESTMORE_PRESENTORS = {"contenttype": "python.path"}`
        return Presentor()

    def build_response(self, data, status=200):
        resp = HttpResponse(data, content_type=self.presentor.get_response_type())
        resp.status_code = status
        return resp

    def serialize(self, method, endpoint, data):
        hyperdata = self.presentor.inject(method, endpoint, data)
        return super(PresentorResourceMixin, self).serialize(method, endpoint, hyperdata)
