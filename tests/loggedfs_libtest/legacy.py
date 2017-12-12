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
