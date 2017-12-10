# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	tests/libtest/__init__.py: Test library module init

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

from pprint import pprint as pp


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CONST
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

TEST_LOG_FN = 'test.log'
TEST_RESULTS_FN = 'test_results.log'
TEST_ERRORS_FN = 'test_errors.log'


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES: FSTEST ANALYSIS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def compile_stats(in_dict):

	tests_total = 0
	tests_failed = 0

	for item_key in in_dict.keys():
		tests_total += 1
		if not in_dict[item_key]:
			tests_failed += 1

	return {
		'int_tests': tests_total,
		'int_failed': tests_failed
		}


def get_results():

	test_results_raw_log = __read_file__(TEST_RESULTS_FN)
	return __process_raw_results__(test_results_raw_log)


def __process_raw_results__(in_str):

	lines = in_str.split('\n')
	ret_dict = {}

	for line in lines:

		line = line.strip()
		if line == '':
			break

		if line.startswith('Failed') or line == 'ok':
			continue

		if line.startswith('/'):
			current_path = line.split('fstest/tests/')[1].split(' ')[0]
			continue

		if '..' in line:
			index = 1
			continue

		if line.startswith('ok '):
			res = True
		elif line.startswith('not ok '):
			res = False
		else:
			print(current_path, index, line)
			raise

		if not line.endswith(str(index)):
			raise

		ret_dict.update({'%s:%d' % (current_path, index): res})
		index += 1

	return ret_dict


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES: I/O
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def __read_file__(filename):

	f = open(filename, 'r')
	data = f.read()
	f.close()
	return data
