from django.utils.datastructures import MultiValueDict
from django.test import TestCase

from restmore.forms import DjangoFormMixin
from collections import namedtuple


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
