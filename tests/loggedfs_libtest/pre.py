# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	tests/loggedfs_libtest/pre.py: Stuff happening before test(s)

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
import shutil

from .const import (
	TEST_MOUNT_PATH,
	TEST_LOG_PATH,
	TEST_ROOT_PATH,
	TEST_LOGGEDFS_ERR_FN,
	TEST_LOGGEDFS_LOG_FN,
	TEST_LOGGEDFS_OUT_FN
	)
from .mount import (
	is_path_mountpoint,
	mount_loggedfs_python,
	umount
	)
from .lib import write_file


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: (1/3) PRE
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class fstest_pre_class():


	def init(self):

		self.__set_paths__()
		self.__cleanup_logfiles__()
		self.__cleanup_mountpoint__()
		self.__mount_fs__()


	def __cleanup_mountpoint__(self):

		if is_path_mountpoint(self.mount_abs_path):
			umount_status = umount(self.mount_abs_path, sudo = True, force = True)
			assert umount_status

		if os.path.isdir(self.mount_abs_path):
			shutil.rmtree(self.mount_abs_path, ignore_errors = True)
		assert not os.path.isdir(self.mount_abs_path)

		os.mkdir(self.mount_abs_path)
		assert os.path.isdir(self.mount_abs_path)


	def __cleanup_logfiles__(self):

		if os.path.isdir(self.logs_abs_path):
			shutil.rmtree(self.logs_abs_path, ignore_errors = True)

		os.mkdir(self.logs_abs_path)
		assert os.path.isdir(self.logs_abs_path)


	def __mount_fs__(self):

		loggedfs_status, loggedfs_out, loggedfs_err = mount_loggedfs_python(
			self.mount_abs_path, os.path.join(self.logs_abs_path, TEST_LOGGEDFS_LOG_FN)
			)

		write_file(os.path.join(self.root_abs_path, TEST_LOG_PATH, TEST_LOGGEDFS_OUT_FN), loggedfs_out)
		write_file(os.path.join(self.root_abs_path, TEST_LOG_PATH, TEST_LOGGEDFS_ERR_FN), loggedfs_err)

		assert loggedfs_status
		assert is_path_mountpoint(self.mount_abs_path)


	def __set_paths__(self):

		self.root_abs_path = os.path.abspath(os.path.join(os.getcwd(), TEST_ROOT_PATH))
		assert os.path.isdir(self.root_abs_path)

		self.logs_abs_path = os.path.join(self.root_abs_path, TEST_LOG_PATH)
		self.mount_abs_path = os.path.join(self.root_abs_path, TEST_MOUNT_PATH)
