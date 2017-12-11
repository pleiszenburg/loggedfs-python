# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	tests/loggedfs_libtest/legacy.py: Test library module init (OLD)

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
from pprint import pprint as pp
import shutil

import pytest
import tap.parser as tp


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@pytest.fixture(scope = 'module')
def loggedfs_mountpoint():

	os.chdir(TEST_ROOT_PATH) # tests usually run from project root

	test_root_abs_path = os.path.abspath(os.getcwd())
	test_mount_abs_path = os.path.join(test_root_abs_path, TEST_MOUNT_PATH)

	__pre_test_cleanup_mountpoint__(test_mount_abs_path)
	__pre_test_cleanup_logfiles__(test_root_abs_path)
	os.mkdir(test_mount_abs_path)

	loggedfs_status, loggedfs_out, loggedfs_err = __mount_loggedfs_python__(
		test_mount_abs_path, os.path.join(test_root_abs_path, TEST_LOG_FN)
		)
	__write_file__(os.path.join(test_root_abs_path, TEST_LOGGEDFS_OUT_FN), loggedfs_out)
	__write_file__(os.path.join(test_root_abs_path, TEST_LOGGEDFS_ERR_FN), loggedfs_err)
	assert loggedfs_status
	assert __is_path_mountpoint__(test_mount_abs_path)

	loggedfs_object = [] # TODO provide actual object to FS
	yield loggedfs_object

	# prove_status, prove_out, prove_err = __run_fstest__(
	# 	os.path.join(test_root_abs_path, TEST_FSTEST_PATH), test_mount_abs_path
	# 	)
	# __write_file__(os.path.join(test_root_abs_path, TEST_RESULTS_FN), prove_out)
	# __write_file__(os.path.join(test_root_abs_path, TEST_ERRORS_FN), prove_err)

	umount_fuse_status = __umount_fuse__(test_mount_abs_path)
	assert umount_fuse_status
	assert not __is_path_mountpoint__(test_mount_abs_path)

	os.chdir('..') # return to project root


# def __run_fstest__(abs_test_path, abs_mountpoint_path):
#
# 	old_cwd = os.getcwd()
# 	os.chdir(abs_mountpoint_path)
#
# 	ret_tuple = __run_command__(
# 		['prove', '-v', '-r', abs_test_path], return_output = True
# 		)
#
# 	os.chdir(old_cwd)
# 	return ret_tuple


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES: FSTEST ANALYSIS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def compare_results(old_results, new_results):

	old_results_keys = set(old_results.keys())
	new_results_keys = set(new_results.keys())
	common_keys = old_results_keys & new_results_keys

	dropped_keys = old_results_keys - common_keys
	new_keys = new_results_keys - common_keys

	ch_to_fail = {}
	ch_to_pass = {}
	for key in common_keys:
		if old_results[key][0] == new_results[key][0]:
			continue
		if new_results[key]:
			ch_to_pass.update({key: new_results[key][1]})
		else:
			ch_to_fail.update({key: new_results[key][1]})

	return {
		'ch_to_fail_set': ch_to_fail,
		'ch_to_pass_set': ch_to_pass,
		'dropped_dict': {key: old_results_keys[val] for key in dropped_keys},
		'new_dict': {key: old_results_keys[val] for key in new_keys}
		}


def compile_stats(in_dict):

	tests_total = 0
	tests_failed = 0

	for item_key in in_dict.keys():
		tests_total += 1
		if not in_dict[item_key][0]:
			tests_failed += 1

	return {
		'int_tests': tests_total,
		'int_failed': tests_failed
		}


def get_processed_results():

	test_results_raw_log = __read_file__(os.path.join(TEST_ROOT_PATH, TEST_RESULTS_FN))
	return __process_raw_results__(test_results_raw_log)


def freeze_results(auto_commit = False):

	current_path = os.path.join(TEST_ROOT_PATH, TEST_STATUS_CURRENT_FN)
	frozen_path = os.path.join(TEST_ROOT_PATH, TEST_STATUS_FROZEN_FN)

	if not os.path.isfile(current_path):
		raise
	if os.path.isfile(frozen_path):
		os.remove(frozen_path)
	shutil.copyfile(current_path, frozen_path)

	if auto_commit:
		commit_status = __run_command__(['git', 'commit', '-am', 'TEST_FREEZE'])
		assert commit_status


# def load_results(filename):
#
# 	return __load_yaml__(os.path.join(TEST_ROOT_PATH, filename))
#
#
# def store_results(in_dict, filename):
#
# 	__dump_yaml__(os.path.join(TEST_ROOT_PATH, filename), in_dict)


def __process_raw_results__(in_str):

	ret_dict = {}
	tap_parser = tp.Parser()
	tap_lines_generator = tap_parser.parse_text(data)

	for line in tap_lines_generator:
		if not hasattr(line, 'ok'):
			continue
		ret_dict.update({line.number: (line.ok, line.description)})

	return ret_dict
