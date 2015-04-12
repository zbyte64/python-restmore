"""
Test support harness for doing setup.py test.
See http://ericholscher.com/blog/2009/jun/29/enable-setuppy-test-your-django-apps/.
"""
import sys
import unittest
import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settngs'
#os.environ['REUSE_DB'] = '1'

# Bootstrap Django's settings.
#from django.conf import settings
#settings.TEST_RUNNER = "django_nose.NoseTestSuiteRunner"
#settings.NOSE_PLUGINS = ['tests.noseplugins.TestDiscoveryPlugin']


class SetupTestSuite(unittest.TestSuite):
    pass


def runtests():
    """Test runner for setup.py test."""
    # Run you some tests.

    #from django.core.management import execute_from_command_line

    #args = [sys.argv[0], 'test', 'montage', '--noinput'] + sys.argv[2:]
    #execute_from_command_line(args)
    #return []

    from django.conf import settings
    from django.test.utils import get_runner
    
    options = {
        'verbosity': 1,
        'interactive': False,
    }

    TestRunner = get_runner(settings, options.get('testrunner'))
    options['verbosity'] = int(options.get('verbosity'))

    if options.get('liveserver') is not None:
        os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = options['liveserver']
        del options['liveserver']

    test_runner = TestRunner(**options)
    failures = test_runner.run_tests(['tests.cases'])

    if failures:
        sys.exit(bool(failures))
    return SetupTestSuite()

if __name__ == '__main__':
    runtests()
