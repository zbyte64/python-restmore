from collections import namedtuple
from django.utils.datastructures import MultiValueDict
from django.test import TestCase

from restmore.forms import DjangoFormMixin
from restmore.normalizer import normalize_data, Normalizer, NormalizedResourceMixin, defaultTransmuters


MockedRequest = namedtuple('Request', 'FILES')


class FormTestCase(TestCase):
    def test_get_form_class(self):
        target = DjangoFormMixin()
        target.form_class = 'return this'
        self.assertEqual(target.get_form_class(), 'return this')

    def test_make_form(self):
        target = DjangoFormMixin()
        target.data = {'message': 'hello world'}
        target.request = MockedRequest(FILES=MultiValueDict())
        target.form_class = lambda **kwargs: kwargs
        kwargs = target.make_form()
        self.assertTrue('data' in kwargs)
        self.assertTrue('files' in kwargs)
        self.assertEqual(kwargs['data'].get('message'), 'hello world')


MockedObject = namedtuple('MockedObject', 'message')
testTransmuters = dict(defaultTransmuters)
testTransmuters[MockedObject] = lambda x: x.message

class SecondaryMockedObject(MockedObject):
    pass

class NormalizerTestCase(TestCase):
    def test_normalize_data_handles_yeild(self):
        def yielder():
            for i in range(5):
                yield i
        result = normalize_data(yielder())
        self.assertEqual(result, [0,1,2,3,4])

    def test_normalize_data_handles_nested_dictionary(self):
        data = {MockedObject('hello world'): MockedObject('from sagan')}
        result = normalize_data(data, enc=testTransmuters)
        self.assertEqual(result, {'hello world': 'from sagan'})

    def test_normalize_data_handles_nested_list(self):
        data = [MockedObject('hello world')]
        result = normalize_data(data, enc=testTransmuters)
        self.assertEqual(result, ['hello world'])

    def test_normalize_data_handles_nested_set(self):
        data = set([MockedObject('hello world')])
        result = normalize_data(data, enc=testTransmuters)
        self.assertEqual(result, set(['hello world']))

    def test_normalize_data_handles_inheritance(self):
        data = SecondaryMockedObject('hello world')
        result = normalize_data(data, enc=testTransmuters)
        self.assertEqual(result, 'hello world')

    def test_normalizer_normalize(self):
        normalizer = Normalizer(identity=None, authorization=None)
        result = normalizer.normalize('hello world')
        self.assertEqual(result, 'hello world')

    def test_normalized_resource_mixin_prepare(self):
        mixin = NormalizedResourceMixin()
        mixin.identity = None
        mixin.authorization = None
        result = mixin.prepare('hello world')
        self.assertEqual(result, 'hello world')
