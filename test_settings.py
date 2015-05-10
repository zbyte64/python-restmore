import os
import random
import string

SECRET_KEY = ''.join(random.sample(string.printable, 20))

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'restmore',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # os.path.join(PROJECT_ROOT, 'db.sqlite'),
        #'TEST_NAME': os.path.join(PROJECT_ROOT, 'test_db.sqlite'),
    }
}

MIDDLEWARE_CLASSES = [
     'django.contrib.sessions.middleware.SessionMiddleware',
     'django.contrib.auth.middleware.AuthenticationMiddleware',
     'django.contrib.messages.middleware.MessageMiddleware',
]

if os.environ.get('DATABASE_URL', False):
    import dj_database_url
    DATABASES = {'default': dj_database_url.config()}


#are we going to use nose?
#INSTALLED_APPS.append('django_nose')
#TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=montage',
    '--verbosity=3',
    #'--stop',
    #'--with-profile',
]

if os.environ.get('CIRCLECI'):
    NOSE_ARGS.extend([
        '--with-xunit',
        '--xunit-file=%s' % os.path.join(
            os.environ.get('CIRCLE_ARTIFACTS', PROJECT_ROOT),
            'nosetests.xml'),
        '--cover-xml',
        '--cover-xml-file=%s' % os.path.join(
            os.environ.get('CIRCLE_ARTIFACTS', PROJECT_ROOT),
            'coverage.xml'),
    ])
else:
    NOSE_ARGS.append('--with-progressive')


NOSE_PLUGINS = ['tests.noseplugins.TestDiscoveryPlugin']

ROOT_URLCONF = ''
