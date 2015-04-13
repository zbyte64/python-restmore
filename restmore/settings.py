from django.conf import settings
from django.utils.module_loading import import_string

PRESENTORS = getattr(settings, 'RESTMORE_PRESENTORS',
    {'application/json': 'restmore.presentors.Presentor'})

NORMALIZER = getattr(settings, 'RESTMORE_NORMALIZER', 'restmore.normalizer.Normalizer')

for key, value in PRESENTORS.items():
    PRESENTORS[key] = import_string(value)

NORMALIZER = import_string(NORMALIZER)
