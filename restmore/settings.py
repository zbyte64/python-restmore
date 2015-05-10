from django.conf import settings
from django.utils.module_loading import import_string

PRESENTORS = getattr(settings, 'RESTMORE_PRESENTORS',
    {'application/json': 'restmore.presentors.Presentor'})

SERIALIZERS = getattr(settings, 'RESTMORE_SERIALIZERS',
    {'application/json': 'restless.serializers.JSONSerializer',
     'multipart/form-data': 'restmore.serializers.MultipartFormSerializer',
     'application/x-www-form-urlencoded': 'restmore.serializers.UrlSerializer',
     'text/html': 'restmore.serializers.HTMLSerializer',
     'application/xhtml+xml': 'restmore.serializers.HTMLSerializer',
     'application/text-html': 'restmore.serializers.HTMLSerializer',
     'text/plain': 'restmore.serializers.HTMLSerializer',})

NORMALIZER = getattr(settings, 'RESTMORE_NORMALIZER', 'restmore.normalizer.Normalizer')

for key, value in PRESENTORS.items():
    PRESENTORS[key] = import_string(value)

for key, value in SERIALIZERS.items():
    SERIALIZERS[key] = import_string(value)

NORMALIZER = import_string(NORMALIZER)
