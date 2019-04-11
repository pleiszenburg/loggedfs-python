# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	tests/conftest.py: Configures the tests

	Copyright (C) 2017-2019 Sebastian M. Ernst <ernst@pleiszenburg.de>

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

import argparse
import os

from .lib import (
	fstest_parameters,
	TEST_ROOT_PATH,
	TEST_FSTEST_PATH,
	TEST_FSTEST_TESTS_SUBPATH
	)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES: PYTEST API
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def pytest_addoption(parser):

	parser.addoption(
		'-T',
		action = 'append',
		help = 'run specified test file',
		nargs = 1,
		type = __arg_type_testfile__
		)
	parser.addoption(
		'-M',
		action = 'store',
		default = 'loggedfs',
		help = 'specify tested filesystem'
		)


def pytest_generate_tests(metafunc):

	if 'fstest_group_path' in metafunc.fixturenames:
		if metafunc.config.getoption('T'):
			test_list = [a[0] for a in metafunc.config.getoption('T')]
		else:
			test_list = fstest_parameters()
		metafunc.parametrize('fstest_group_path', test_list)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES: HELPER
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def __arg_type_testfile__(filename):

	file_path = os.path.join(
		TEST_ROOT_PATH,
		TEST_FSTEST_PATH,
		TEST_FSTEST_TESTS_SUBPATH,
		filename
		)

	if os.path.isfile(file_path) and file_path.endswith('.t'):
		return os.path.abspath(file_path)

	raise argparse.ArgumentTypeError('No testfile: "%s"' % filename)
