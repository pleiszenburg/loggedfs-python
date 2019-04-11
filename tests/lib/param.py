# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	tests/lib/param.py: Generate parameter tuple for tests

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

import os

# Use the built-in version of scandir/walk if possible
# Otherwise: https://github.com/benhoyt/scandir
try:
	from os import scandir
except ImportError:
	from scandir import scandir

import pytest

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
	test_group_list = __ignore_tests__(test_group_list)

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
	for item in scandir(scan_root_path):
		if item.is_file():
			if not item.name.endswith('.t'):
				continue
			test_group_list.append(item.path)
		elif item.is_dir():
			__get_recursive_inventory_list__(root_path, item.path, test_group_list)
		elif item.is_symlink():
			pass
		else:
			raise # TODO


def __ignore_tests__(old_group_list):

	new_group_list = []

	ignore_group_list = []
		# [
		# ('truncate', 3),
		# ('open', 3),
		# ('mkdir', 3),
		# ('chmod', 3),
		# ('mknod', 3),
		# ('mkfifo', 3),
		# ('unlink', 3),
		# ('symlink', 3),
		# ('link', 3),
		# ('chown', 3),
		# ('ftruncate', 3),
		# ('rmdir', 3),
		# ('rename', 2)
		# ] # The original LoggedFS crashes when tested against those.
	xfail_group_list = []

	for group_path in old_group_list:

		group_path_segment, group_number_str = os.path.split(group_path)
		group_number = int(group_number_str.split('.')[0])
		_, group_folder = os.path.split(group_path_segment)

		if (group_folder, group_number) not in ignore_group_list and (group_folder, group_number) not in xfail_group_list:
			new_group_list.append(group_path)
		elif (group_folder, group_number) in xfail_group_list and (group_folder, group_number) not in ignore_group_list:
			new_group_list.append(pytest.param(group_path, marks = pytest.mark.xfail))

	return new_group_list
