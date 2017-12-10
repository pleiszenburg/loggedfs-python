# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	tests/test_fstest.py: Runs the fstest-suite

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

from loggedfs_libtest import (
	TEST_STATUS_CURRENT_FN,
	TEST_STATUS_DIFF_FN,
	TEST_STATUS_FROZEN_FN,
	compare_results,
	get_processed_results,
	load_results,
	run_fstest,
	store_results
	)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TESTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def test_fstest_run():

	run_fstest()
	processed_results = get_processed_results()
	store_results(processed_results, TEST_STATUS_CURRENT_FN)
	frozen_results = load_results(TEST_STATUS_FROZEN_FN)
	result_diff = compare_results(frozen_results, processed_results)
	store_results(result_diff, TEST_STATUS_DIFF_FN)

	assert len(result_diff['ch_to_fail_set']) == 0
	assert len(result_diff['dropped_dict'].keys()) == 0
