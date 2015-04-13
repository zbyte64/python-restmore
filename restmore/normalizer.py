import decimal
import types
from django.core.files import File
from django.utils.encoding import force_text
from django.utils.functional import Promise


#default transmuters
#TODO form.errors
defaultTransmuters = {
    File: lambda obj: obj.url if hasattr(obj, 'url') else obj.name,
    Promise: force_text,
    types.GeneratorType: list,
}


def normalize_data(obj, notfound=lambda x: x, enc=defaultTransmuters):
    '''
    Recursively normalizes an object into python primitives
    '''
    cls = obj if hasattr(obj, '__mro__') else type(obj)
    mro = cls.__mro__
    for subcls in mro:
        encoder = enc.get(subcls) or enc.get(subcls.__name__)
        if encoder:
            while not callable(encoder):  # alias
                encoder = enc[encoder]
            return normalize_data(encoder(obj), notfound, enc)
    if isinstance(obj, (str, int, float, decimal.Decimal)):
        return obj
    elif isinstance(obj, list):
        obj = [normalize_data(item, notfound, enc) for item in obj]
    elif isinstance(obj, dict):
        obj = dict([(normalize_data(k, notfound, enc), normalize_data(v, notfound, enc))
            for k, v in obj.items()])
    elif isinstance(obj, set):
        obj = set([normalize_data(item, notfound, enc) for item in obj])
    elif hasattr(obj, '__iter__'):
        obj = [normalize_data(item, notfound, enc) for item in obj]
    return notfound(obj)


class Normalizer(object):
    defaultTransmuter = lambda x: x
    transmuters = defaultTransmuters

    def __init__(self, identity, authorization):
        self.identity = identity
        self.authorization = authorization

    def normalize(self, obj):
        #TODO factor in identity & authorization to widdle down acceptable fields
        return normalize_data(obj, self.defaultTransmuter, self.transmuters)


class NormalizedResourceMixin(object):
    '''
    Resource mixin that normalizes your data against a "globally" defined normalizer
    '''
    def get_normalizer(self):
        #TODO settable with django setting: `RESTMORE_NORMALIZER = "python.path"`
        return Normalizer(self.identity, self.authorization)

    def prepare(self, data):
        return self.get_normalizer().normalize(data)

    def build_status_response(self, data, status=200):
        '''
        Like build response but serializes the data for you
        '''
        return self.build_response(self.prepare(data), status=status)
