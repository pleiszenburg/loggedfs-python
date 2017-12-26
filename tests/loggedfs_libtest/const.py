# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	tests/loggedfs_libtest/const.py: Const items

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
# URLs & SOURCES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

TEST_FSTEST_GITREPO = 'https://github.com/pjd/pjdfstest.git'


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# FOLDER & FILE NAMES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

TEST_ROOT_PATH = 'tests'

TEST_FSTEST_PATH = 'test_suite'
TEST_MOUNT_PARENT_PATH = 'test_mount'
TEST_MOUNT_CHILD_PATH = 'test_child'
TEST_LOG_PATH = 'test_logs'

TEST_FSTEST_TESTS_SUBPATH = 'tests'
TEST_FSTEST_CONF_SUBPATH = 'tests/conf'

TEST_IMAGE_FN = 'test_image.bin'

TEST_LOGGEDFS_CFG_FN = 'test_loggedfs_cfg.xml'
TEST_LOGGEDFS_LOG_FN = 'loggedfs.log'
TEST_LOGGEDFS_OUT_FN = 'loggedfs_out.log'
TEST_LOGGEDFS_ERR_FN = 'loggedfs_err.log'

TEST_RESULTS_FN = 'test_fstest_results.log'
TEST_ERRORS_FN = 'test_fstest_errors.log'
TEST_STATUS_CURRENT_FN = 'test_status_current.yaml'
TEST_STATUS_DIFF_FN = 'test_status_diff.yaml'
TEST_STATUS_FROZEN_FN = 'test_status_frozen.yaml'


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MODES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

TEST_FS_EXT4 = 'ext4'
TEST_FS_LOGGEDFS = 'logggedfs'
TEST_IMAGE_SIZE_MB = 50


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SNIPPETS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

TEST_LOG_HEAD = """
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# %s
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

"""

TEST_LOG_STATS = 'Stats: expected %d | %d passed | %d failed'
