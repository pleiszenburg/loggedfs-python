# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	tests/loggedfs_libtest/prove.py: Stuff happening during test(s)

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

from .lib import run_command

import tap.parser


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: (2/3) PROVE
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class fstest_prove_class:


	def prove(self, test_path):
		"""Called from mountpoint!
		"""

		# prove_status, prove_out, prove_err = __run_fstest__(
		# 	os.path.join(test_root_abs_path, TEST_FSTEST_PATH), test_mount_abs_path
		# 	)
		# __write_file__(os.path.join(test_root_abs_path, TEST_RESULTS_FN), prove_out)
		# __write_file__(os.path.join(test_root_abs_path, TEST_ERRORS_FN), prove_err)

		status, out, err = self.__run_fstest__(test_path)

		len_passed, len_failed, res_dict = self.__process_raw_results__(out)

		assert len_failed == 0

		# processed_results = get_processed_results()
		# store_results(processed_results, TEST_STATUS_CURRENT_FN)
		# frozen_results = load_results(TEST_STATUS_FROZEN_FN)
		# result_diff = compare_results(frozen_results, processed_results)
		# store_results(result_diff, TEST_STATUS_DIFF_FN)
	    #
		# assert len(result_diff['ch_to_fail_set']) == 0
		# assert len(result_diff['dropped_dict'].keys()) == 0


	def __process_raw_results__(self, in_str):

		ret_dict = {}
		tap_parser = tap.parser.Parser()
		tap_lines_generator = tap_parser.parse_text(in_str)

		len_passed = 0
		len_failed = 0
		for line in tap_lines_generator:
			if not hasattr(line, 'ok'):
				continue
			if line.ok:
				len_passed += 1
			else:
				len_failed += 1
			ret_dict.update({line.number: (line.ok, line.description)})

		return len_passed, len_failed, ret_dict


	def __run_fstest__(self, abs_test_path):

		return run_command(
			['prove', '-v', abs_test_path], return_output = True
			)
