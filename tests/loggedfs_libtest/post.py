# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	tests/loggedfs_libtest/post.py: Stuff happening after test(s)

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
import time

from .const import (
	TEST_FS_LOGGEDFS,
	TEST_FSCK_FN,
	TEST_LOG_HEAD
	)
from .mount import (
	detach_loop_device,
	find_loop_devices,
	is_path_mountpoint,
	umount,
	umount_fuse
	)
from .lib import (
	ck_filesystem,
	write_file
	)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: (3/3) POST
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class fstest_post_class:


	def postproc(self):
		"""Called from project root after tests!
		"""

		os.chdir(self.prj_abs_path)

		if self.fs_type == TEST_FS_LOGGEDFS:
			umount_child_status = umount_fuse(self.mount_child_abs_path, sudo = self.with_sudo)
			assert umount_child_status
			assert not is_path_mountpoint(self.mount_child_abs_path)

		if self.travis:
			return

		time.sleep(0.1) # HACK ... otherwise parent will be busy

		umount_parent_status = umount(self.mount_parent_abs_path, sudo = True)
		assert umount_parent_status
		assert not is_path_mountpoint(self.mount_parent_abs_path)

		loop_device_list = find_loop_devices(self.image_abs_path)
		assert isinstance(loop_device_list, list)
		assert len(loop_device_list) == 1
		loop_device_path = loop_device_list[0]

		ck_status_code, ck_out, ck_err = ck_filesystem(loop_device_path)
		write_file(
			os.path.join(self.logs_abs_path, TEST_FSCK_FN),
			''.join([
				TEST_LOG_HEAD % 'EXIT STATUS',
				'%d\n' % ck_status_code,
				TEST_LOG_HEAD % 'OUT',
				ck_out,
				TEST_LOG_HEAD % 'ERR',
				ck_err
				])
			)

		detach_status = detach_loop_device(loop_device_path)
		assert detach_status

		assert not bool(ck_status_code) # not 0 for just about any type of error! Therefore asserting at the very end.
