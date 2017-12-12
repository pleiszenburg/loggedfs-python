# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	tests/loggedfs_libtest/param.py: Generate parameter tuple for tests

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

from .const import (
	TEST_ROOT_PATH,
	TEST_FSTEST_PATH,
	TEST_FSTEST_TESTS_SUBPATH
	)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def fstest_parameters():
	"""Can be called from anywhere in project tree ...
	"""

	fstests_root_abs_path = os.path.join(
		__find_root_path__(os.getcwd()),
		TEST_ROOT_PATH,
		TEST_FSTEST_PATH,
		TEST_FSTEST_TESTS_SUBPATH
		)

	test_group_list = []
	__get_recursive_inventory_list__(fstests_root_abs_path, fstests_root_abs_path, test_group_list)

	return test_group_list


def __find_root_path__(in_path):

	if os.path.isfile(os.path.join(in_path, 'setup.py')):
		return in_path

	while True:

		# Go one up
		new_path = os.path.abspath(os.path.join(in_path, '..'))
		# Can't go futher up
		if new_path == in_path:
			break
		# Set path
		in_path = new_path

		# Check for repo folder
		if os.path.isfile(os.path.join(in_path, 'setup.py')):
			return in_path

	# Nothing found
	raise


def __get_recursive_inventory_list__(root_path, scan_root_path, test_group_list):

	relative_path = os.path.relpath(scan_root_path, root_path)
	for item in os.scandir(scan_root_path):
		if item.is_file():
			if not item.name.endswith('.t'):
				continue
			test_group_list.append((item.path, item.name))
		elif item.is_dir():
			__get_recursive_inventory_list__(root_path, item.path, test_group_list)
		elif item.is_symlink():
			pass
		else:
			raise # TODO
