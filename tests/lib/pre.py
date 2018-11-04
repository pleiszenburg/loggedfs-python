# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	tests/lib/pre.py: Stuff happening before test(s)

	Copyright (C) 2017-2018 Sebastian M. Ernst <ernst@pleiszenburg.de>

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

from .const import TEST_FS_LOGGEDFS


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: (1/3) PRE
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class fstest_pre_class:


	def init(self, fs_type = TEST_FS_LOGGEDFS):

		self.init_a_members(fs_type)
		self.init_b_cleanup()
		self.init_c_parentfs()
		self.init_d_childfs()

		os.chdir(self.mount_child_abs_path)
