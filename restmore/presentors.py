'''
Request (set serializer in `handle`) -> Resource -> Data
    -> Presentor (set response type in `build_response`, inject hypermedia in `serialize`)
    -> Normalizer (globalized preparer) -> Serializer
'''
from collections import namedtuple
from django.http import HttpResponse
from restless.serializers import JSONSerializer

from .normalizer import NormalizedPreparer


class HybridSerializer(object):
    def __init__(self, serializer, deserializer):
        self.serializer = serializer
        self.deserializer = deserializer

    def serialize(self, data):
        return self.serializer.serialize(data)

    def deserialize(self, data):
        return self.deserializer.deserialize(data)


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


class StatusException(Exception):
    def __init__(self, message, status=400):
        super(StatusException, self).__init__(message)
        self.status = status


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

    def build_status_response(self, data, status=400):
        '''
        An event occurred preventing the request from being completed
        '''
        raise StatusException(data, status)

    def make_serializer(self):
        '''
        Constructs the serializers to be used based on HTTP Headers
        settable with django setting: `RESTMORE_SERIALIZERS`
        '''
        #print("make_serializer:", self.request.META)
        from .settings import SERIALIZERS
        rt = self.request.META.get('CONTENT_TYPE') #request type
        at = self.request.META.get('ACCEPTS', 'application/json') #accept type
        rt = rt or at
        #TODO intelligent mimetype matching
        try:
            rt_serializer = SERIALIZERS[rt]
        except KeyError:
            raise KeyError('Invalid Request Type')
        try:
            at_serializer = SERIALIZERS[at]
        except KeyError:
            raise KeyError('Invalid Accept Type')
        return HybridSerializer(serializer=at_serializer(), deserializer=rt_serializer())

    def get_presentor(self):
        '''
        Constructs the presentor to be used based on HTTP Headers
        settable with django setting: `RESTMORE_PRESENTORS`
        '''
        from .settings import PRESENTORS
        ct = self.request.META.get('ACCEPTS') or self.request.META.get('CONTENT_TYPE') or 'application/json'
        return PRESENTORS[ct](ct)

    def build_response(self, data, status=200):
        assert isinstance(data, (str, bytes)), "build_response only accepts serialized data"
        resp = HttpResponse(data, content_type=self.presentor.get_response_type())
        resp.status_code = status
        return resp

    def serialize(self, method, endpoint, data):
        hyperdata = self.presentor.inject(method, endpoint, data)
        return super(PresentorResourceMixin, self).serialize(method, endpoint, hyperdata)

    def prepare(self, data):
        """
        Given an item (``object`` or ``dict``), this will potentially go through
        & reshape the output based on ``self.prepare_with`` object.
        :param data: An item to prepare for serialization
        :type data: object or dict
        :returns: A potentially reshaped dict
        :rtype: dict
        """
        #pass along identity & authorization to the preparer so that fields may be properly masked
        return self.preparer.prepare(data, identity=self.identity, authorization=self.authorization)
