#!/usr/bin/env python3

#built for python3 now

import os
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

VERSION = '0.1.0'
PATH = os.path.dirname(os.path.abspath(__file__))
try:
    LONG_DESC = '\n===='+open(os.path.join(PATH, 'README.rst'), 'r').read().split('====', 1)[-1]
except IOError: #happens when using tox
    LONG_DESC = ''
DESCRIPTION = 'The missing django batteries for restless to help you get more sleep.'


setup(name='restmore',
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESC,
      classifiers=[
          'Programming Language :: Python',
          'Environment :: Web Environment',
          'Framework :: Django',
          'Operating System :: OS Independent',
          'Natural Language :: English',
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          #'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ],
      keywords='API Framework',
      author = 'Jason Kraus',
      author_email = 'zbyte64@gmail.com',
      url='https://github.com/zbyte64/python-restmore',
      packages=find_packages(exclude=['tests']),
      test_suite='tests.runtests.runtests',
      tests_require=(
        #'pep8',
        #'coverage',
        'django',
        'restless',
      ),
      include_package_data = True,
      zip_safe = False,
  )
