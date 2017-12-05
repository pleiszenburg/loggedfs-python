# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	setup.py: Used for package distribution

	Copyright (C) 2017 Sebastian M. Ernst <ernst@pleiszenburg.de>

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


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SETUP
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


# Bump version HERE!
_version_ = '0.0.0'


# List all versions of Python which are supported
confirmed_python_versions = [
	('Programming Language :: Python :: %s' % x)
	for x in '3.6'.split(' ')
	]


# Fetch readme file
with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
	long_description = f.read()


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
	dependency_links = [],
	install_requires = [
		'click',
		'fusepy',
		'xmltodict'
		],
	extras_require = {'dev': [
		'pytest',
		'python-language-server',
		'setuptools',
		'Sphinx',
		'sphinx_rtd_theme',
		'twine',
		'wheel'
		]},
	entry_points = '''
		[console_scripts]
		loggedfs = loggedfs:cli_entry
		''',
	zip_safe = False,
	classifiers = [
		'Development Status :: 3 - Alpha',
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
