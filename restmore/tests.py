from collections import namedtuple
from django.utils.datastructures import MultiValueDict
from django.test import TestCase
from django.contrib.auth.models import User

from restmore.forms import DjangoFormMixin
from restmore.normalizer import normalize_data, Normalizer, NormalizedPreparer, defaultTransmuters
from restmore.presentors import HybridSerializer
from restmore.permissions import Authorization, DjangoModelAuthorization, AuthorizationMixin, ModelAuthorizationMixin
from restmore.crud import DjangoModelResource

from restless.serializers import JSONSerializer

import json


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
        mixin = NormalizedPreparer()
        result = mixin.prepare('hello world')
        self.assertEqual(result, 'hello world')


class PermissionsTestCase(TestCase):
    def test_authorization_process_queryset(self):
        authorization = Authorization(None, None)
        result = authorization.process_queryset(['foo'])
        self.assertEqual(result, ['foo'])

    def test_authorization_is_authorized(self):
        authorization = Authorization(None, None)
        result = authorization.is_authorized()
        self.assertEqual(result, True)

    def test_authorization_mixin_make_authorization(self):
        mixin = AuthorizationMixin()
        auth = mixin.make_authorization('identity', 'list')
        self.assertTrue(isinstance(auth, Authorization))

    def test_authorization_mixin_get_identity_returns_user(self):
        mixin = AuthorizationMixin()
        mixin.request = namedtuple('UserRequest', 'user')('John Smith')
        user = mixin.get_identity()
        self.assertEqual(user, 'John Smith')

    def test_authorization_mixin_is_authenticated(self):
        mixin = AuthorizationMixin()
        mixin.authorization = mixin.make_authorization('identity', 'list')
        result = mixin.is_authenticated()
        self.assertEqual(result, True)

    def test_django_model_authorization_is_authorized(self):
        identity = User.objects.create(is_superuser=True, username='foo', email='foo@domain.com')
        authorization = DjangoModelAuthorization(identity, User, 'list')
        result = authorization.is_authorized()
        self.assertEqual(result, True)
        #TODO this is far less then enough


class SerizlierTestCase(TestCase):
    def test_serialize(self):
        serializer = HybridSerializer(serializer=JSONSerializer(), deserializer=JSONSerializer())
        data = serializer.serialize({"msg": "hello world"})
        self.assertEqual(data, '{"msg": "hello world"}')


class UserModelResource(DjangoModelResource):
    model = User
    fields = ['username', 'email']

    def is_debug(self):
        return True

    def is_authenticated(self):
        return super(UserModelResource, self).is_authenticated() or True


class ViewTestCase(TestCase):
    #test the entire stack
    urls = UserModelResource.urls()

    def setUp(self):
        self.userA = User.objects.create_superuser(username='foo',
            email='foobar@domain.com', password='foobar')
        #print(self.userA.is_active, self.userA.pk, self.userA.check_password('foobar'), len(User.objects.all()))
        self.loggedIn = self.client.login(
            username='foo',
            password='foobar',
        )
        #TODO figure out why login isn't working!
        #assert self.loggedIn, "Login Response: "+str(self.loggedIn)

    def tearDown(self):
        User.objects.all().delete()


    def test_list(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200, response.content)
        message = json.loads(response.content.decode("utf-8"))
        if 'error' in message:
            self.fail(message['error']+ ": " + message['traceback'])
        #print(message)
        self.assertEqual(len(message['objects']), 1)
        self.assertEqual(message['objects'][0]['username'], 'foo')

    def test_detail(self):
        response = self.client.get('/{0}/'.format(self.userA.pk))
        self.assertEqual(response.status_code, 200, response.content)
        #print(response.content)
        message = json.loads(response.content.decode("utf-8"))
        if 'error' in message:
            self.fail(message['error']+ ": " + message['traceback'])
        #print(message)
        self.assertEqual(message['username'], 'foo')

    def test_create(self):
        response = self.client.post('/', json.dumps({
            "username": "forshizzle",
            "email": "rockstar@domain.com",
        }), 'application/json')
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(User.objects.all().count(), 2)

    def test_update(self):
        response = self.client.put('/{0}/'.format(self.userA.pk), json.dumps({
            "username": "foo",
            "email": "rockstar@domain.com",
        }), 'application/json')
        self.assertEqual(response.status_code, 202, response.content)
        self.assertEqual(User.objects.all()[0].email, 'rockstar@domain.com')

    def test_delete(self):
        response = self.client.delete('/{0}/'.format(self.userA.pk))
        self.assertEqual(response.status_code, 204, response.content)
        self.assertEqual(User.objects.all().count(), 0)

    def test_list_bad_page_num(self):
        response = self.client.get('/?page=foobar')
        self.assertEqual(response.status_code, 400, response.content)

    def test_list_outofbound_page_num(self):
        response = self.client.get('/?page=10000')
        self.assertEqual(response.status_code, 410, response.content)

    def test_detail_404(self):
        response = self.client.get('/15700/')
        self.assertEqual(response.status_code, 404, response.content)

    def test_bad_create(self):
        response = self.client.post('/', json.dumps({
            "email": "rockstar@domain.com",
        }), 'application/json')
        self.assertEqual(response.status_code, 400, response.content)

    def test_bad_update(self):
        response = self.client.put('/{0}/'.format(self.userA.pk), json.dumps({
            "email": "rockstar@domain.com",
        }), 'application/json')
        self.assertEqual(response.status_code, 400, response.content)
