# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	setup.py: Used for package distribution

	Copyright (C) 2017-2020 Sebastian M. Ernst <ernst@pleiszenburg.de>

<LICENSE_BLOCK>
The contents of this file are subject to the Apache License
Version 2 ("License"). You may not use this file except in
compliance with the License. You may obtain a copy of the License at
https://www.apache.org/licenses/LICENSE-2.0
https://github.com/pleiszenburg/loggedfs-python/blob/master/LICENSE

Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
specific language governing rights and limitations under the License.
</LICENSE_BLOCK>

"""


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import os
from setuptools import (
	find_packages,
	setup
	)
import sys


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SETUP
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


# Bump version HERE!
_version_ = '0.0.6'


# List all versions of Python which are supported
python_minor_min = 5
python_minor_max = 8
confirmed_python_versions = [
    'Programming Language :: Python :: 3.{MINOR:d}'.format(MINOR = minor)
    for minor in range(python_minor_min, python_minor_max + 1)
    ]


# Fetch readme file
with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
	long_description = f.read()


# Development dependencies
development_deps_list = [
	'coverage',
	'psutil',
	'pytest',
	'python-language-server[all]',
	'PyYAML',
	'setuptools',
	'Sphinx',
	'sphinx_rtd_theme',
	'tap.py',
	'twine',
	'wheel'
	]


# Get Python interpreter version
py_gen, py_ver, *_ = sys.version_info
# Raise an error if this is running on Python 2 (legacy)
if py_gen < 3:
	raise NotImplementedError
# Handle CPython 3.4 and below extra dependency
if py_ver < 5:
	development_deps_list.append('scandir') # See https://github.com/benhoyt/scandir


setup(
	name = 'loggedfs',
	packages = find_packages('src'),
	package_dir = {'': 'src'},
	version = _version_,
	description = 'Filesystem monitoring with Fuse and Python',
	long_description = long_description,
	author = 'Sebastian M. Ernst',
	author_email = 'ernst@pleiszenburg.de',
	url = 'https://github.com/pleiszenburg/loggedfs-python',
	download_url = 'https://github.com/pleiszenburg/loggedfs-python/archive/v%s.tar.gz' % _version_,
	license = 'Apache License 2.0',
	keywords = ['filesystem', 'fuse', 'logging', 'monitoring'],
	include_package_data = True,
	python_requires = '>=3.{MINOR:d}'.format(MINOR = python_minor_min),
	install_requires = [
		'click>=7.0',
		'refuse==0.0.4',
		'xmltodict'
		],
	extras_require = {'dev': development_deps_list},
	entry_points = '''
		[console_scripts]
		loggedfs = loggedfs:cli_entry
		''',
	zip_safe = False,
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Console',
		'Intended Audience :: Developers',
		'Intended Audience :: Information Technology',
		'Intended Audience :: Science/Research',
		'Intended Audience :: System Administrators',
		'License :: OSI Approved :: Apache Software License',
		'Operating System :: POSIX :: Linux',
		'Operating System :: MacOS',
		'Programming Language :: Python :: 3'
		] + confirmed_python_versions + [
		'Programming Language :: Python :: 3 :: Only',
		'Programming Language :: Python :: Implementation :: CPython',
		'Topic :: Scientific/Engineering',
		'Topic :: Software Development :: Libraries',
		'Topic :: Software Development :: Testing',
		'Topic :: System :: Archiving',
		'Topic :: System :: Filesystems',
		'Topic :: System :: Logging',
		'Topic :: System :: Monitoring',
		'Topic :: System :: Systems Administration',
		'Topic :: Utilities'
		]
)
