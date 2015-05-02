'''
Request (set serializer in `handle`) -> Resource -> Data
    -> Presentor (set response type in `build_response`, inject hypermedia in `serialize`)
    -> Normalizer (globalized preparer) -> Serializer
'''
from collections import namedtuple
from django.http import HttpResponse
from restless.serializers import JSONSerializer

from .normalizer import NormalizedPreparer


HybridSerializer = namedtuple('HybridSerializer', 'serialize deserialize')


class Presentor(object):
    '''
    A passthrough presentor
    '''
    def __init__(self, content_type):
        self.content_type = content_type

    def inject(self, method, endpoint, data):
        '''
        Inject hypermedia data
        '''
        return data

    def get_response_type(self):
        return self.content_type


class PresentorResourceMixin(object):
    preparer = NormalizedPreparer()

    def handle(self, endpoint, *args, **kwargs):
        #why the extra layer of indirection? so we can dynamically switch serializers and hypermedia
        try:
            self.serializer = self.make_serializer()
        except KeyError as error:
            msg = error.args[0]
            if msg == 'Invalid Request Type':
                return HttpResponse(msg, status=415)
            return HttpResponse(msg, status=406)

        try:
            self.presentor = self.get_presentor()
        except KeyError:
            #406 = Bad Accept, 415 = Bad Content Type
            return HttpResponse('Invalid Accepts', status=406)

        return super(PresentorResourceMixin, self).handle(endpoint, *args, **kwargs)

    def build_status_response(self, data, status=200):
        '''
        Like build response but serializes the data for you
        '''
        return self.build_response(self.prepare(data), status=status)

    def make_serializer(self):
        '''
        Constructs the serializers to be used based on HTTP Headers
        settable with django setting: `RESTMORE_SERIALIZERS`
        '''
        from .settings import SERIALIZERS
        rt = self.request.META.get('ContentType') #request type
        at = self.request.META.get('Accepts') #accept type
        rt = rt or at or 'application/json'
        at = at or rt
        try:
            rt_serializer = SERIALIZERS[rt]
        except KeyError:
            raise KeyError('Invalid Request Type')
        try:
            at_serializer = SERIALIZERS[at]
        except KeyError:
            raise KeyError('Invalid Accept Type')
        return HybridSerializer(serialize=at_serializer(), deserialize=rt_serializer())

    def get_presentor(self):
        '''
        Constructs the presentor to be used based on HTTP Headers
        settable with django setting: `RESTMORE_PRESENTORS`
        '''
        from .settings import PRESENTORS
        #TODO proper meta keys?
        ct = self.request.META.get('Accepts') or self.request.META.get('ContentType') or 'application/json'
        return PRESENTORS[ct](ct)

    def build_response(self, data, status=200):
        resp = HttpResponse(data, content_type=self.presentor.get_response_type())
        resp.status_code = status
        return resp

    def serialize(self, method, endpoint, data):
        hyperdata = self.presentor.inject(method, endpoint, data)
        return super(PresentorResourceMixin, self).serialize(method, endpoint, hyperdata)
