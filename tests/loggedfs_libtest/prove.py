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

from .const import (
	TEST_LOG_HEAD,
	TEST_LOG_STATS
	)
from .mount import is_path_mountpoint
from .lib import (
	format_yaml,
	read_file,
	run_command,
	write_file
	)

import tap.parser


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: (2/3) PROVE
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class fstest_prove_class:


	def prove(self, test_path):
		"""Called from mountpoint!
		"""

		assert is_path_mountpoint(self.mount_abs_path)

		status, out, err = self.__run_fstest__(test_path)
		len_expected, len_passed, len_failed, res_dict = self.__process_raw_results__(out)

		pass_condition = len_failed == 0 and len_expected == (len_passed + len_failed) and len_expected != 0 and err.strip() == ''

		if pass_condition:
			self.__clear_loggedfs_log__()
			assert True # Test is good, nothing more to do
			return # Get out of here ...

		grp_dir, grp_nr = self.__get_group_id_from_path__(test_path)
		grp_code = read_file(test_path)
		grp_log = read_file(self.loggedfs_log_abs_path)

		report = []

		report.append(TEST_LOG_HEAD % 'TEST SUITE LOG')
		report.append(test_path)
		report.append(TEST_LOG_STATS % (len_expected, len_passed, len_failed))
		report.append(format_yaml(res_dict))

		if err.strip() != '':
			report.append(TEST_LOG_HEAD % 'TEST SUITE ERR')
			report.append(err)

		report.append(TEST_LOG_HEAD % 'TEST SUITE CODE')
		report.append(grp_code)

		report.append(TEST_LOG_HEAD % 'LOGGEDFS LOG')
		report.append(grp_log)

		write_file(os.path.join(
			self.logs_abs_path,
			'test_%s_%02d_err.log' % (grp_dir, grp_nr)
			), '\n'.join(report))

		self.__clear_loggedfs_log__()

		# will always fail at this point
		assert pass_condition


	def __clear_loggedfs_log__(self):

		run_command(['truncate', '-s', '0', self.loggedfs_log_abs_path], sudo = self.with_sudo)


	def __get_group_id_from_path__(self, in_path):

		group_path, group_nr = os.path.split(in_path)
		_, group_dir = os.path.split(group_path)

		return (group_dir, int(group_nr.split('.')[0]))


	def __process_raw_results__(self, in_str):

		ret_dict = {}
		tap_parser = tap.parser.Parser()
		tap_lines_generator = tap_parser.parse_text(in_str)

		len_passed = 0
		len_failed = 0
		len_expected = 0
		for line in tap_lines_generator:
			if line.category == 'plan':
				len_expected = line.expected_tests
				continue
			if not hasattr(line, 'ok'):
				continue
			if line.number is None:
				continue
			if line.ok:
				len_passed += 1
			else:
				len_failed += 1
			ret_dict.update({line.number: {
				'ok': line.ok,
				'description' : line.description
				}})

		return len_expected, len_passed, len_failed, ret_dict


	def __run_fstest__(self, abs_test_path):

		return run_command(
			['prove', '-v', abs_test_path], return_output = True, sudo = self.with_sudo, timeout = 39, setsid = True
			)
