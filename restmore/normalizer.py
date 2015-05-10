import decimal
import types
from django.core.files import File
from django.utils.encoding import force_text
from django.utils.functional import Promise
from django.core.paginator import Page
from django.core.serializers.python import Serializer
from django.db.models import Model, QuerySet
from restless.preparers import Preparer


def normalize_queryset(queryset):
    for entry in queryset:
        yield entry


def normalize_model_instance(instance):
    serializer = Serializer()
    flat_obj = serializer.serialize([instance], use_natural_keys=True)[0]
    #print("normalized result:", flat_obj)
    data = flat_obj.fields
    if 'pk' in flat_obj:
        data['pk'] = flat_obj['pk']
    return data

#default transmuters
#TODO form.errors
defaultTransmuters = {
    File: lambda obj: obj.url if hasattr(obj, 'url') else obj.name,
    Promise: force_text,
    types.GeneratorType: list,
    Page: lambda obj: obj.object_list,
    QuerySet: normalize_queryset,
    Model: normalize_model_instance,
}

def normalize_data(obj, notfound=lambda x: x, enc=defaultTransmuters):
    '''
    Recursively normalizes an object into python primitives
    '''
    #print("normalize_dat:", obj)
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
    elif isinstance(obj, bytes):
        #TODO this is not proper
        return obj.decode('utf8')
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
    defaultTransmuter = lambda self, x: x
    transmuters = defaultTransmuters

    def __init__(self, identity, authorization):
        self.identity = identity
        self.authorization = authorization

    def normalize(self, obj):
        #TODO factor in identity & authorization to widdle down acceptable fields
        return normalize_data(obj, self.defaultTransmuter, self.transmuters)


class NormalizedPreparer(Preparer):
    '''
    Resource mixin that normalizes your data against a "globally" defined normalizer
    '''
    def get_normalizer(self, identity, authorization):
        from .settings import NORMALIZER
        #settable with django setting: `RESTMORE_NORMALIZER = "python.path"`
        #TODO transmuters should be directly registerable or settingsable
        return NORMALIZER(identity, authorization)

    def prepare(self, data, identity=None, authorization=None):
        #TODO how will identity & authorization get passed in from view?
        return self.get_normalizer(identity, authorization).normalize(data)
