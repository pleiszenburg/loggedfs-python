# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	tests/lib/install.py: Install software required for tests

	Copyright (C) 2017-2020 Sebastian M. Ernst <ernst@pleiszenburg.de>

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
	TEST_FSTEST_GITREPO,
	TEST_FSTEST_PATH,
	TEST_FSTEST_CONF_FN,
	TEST_FSTEST_TESTS_SUBPATH,
	TEST_FSX_PATH,
	TEST_FSX_SOURCE_URL,
	TEST_ROOT_PATH
	)
from .procio import (
	download_file,
	read_file,
	run_command,
	write_file
	)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES: FSTEST
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def install_fstest():
	"""PUBLIC: Called from project root
	"""

	install_path = os.path.join(TEST_ROOT_PATH, TEST_FSTEST_PATH)
	if os.path.isdir(install_path):
		shutil.rmtree(install_path, ignore_errors = True)
	git_clone_result = run_command(['git', 'clone', TEST_FSTEST_GITREPO, install_path])
	assert git_clone_result
	__build_fstest__(install_path)


def install_fsx():
	"""PUBLIC: Called from project root
	"""

	install_path = os.path.join(TEST_ROOT_PATH, TEST_FSX_PATH)
	source_path = os.path.join(install_path, TEST_FSX_SOURCE_URL.split('/')[-1])

	if os.path.isfile(source_path):
		os.remove(source_path)
	write_file(source_path, download_file(TEST_FSX_SOURCE_URL).decode('utf-8'))

	old_path = os.getcwd()
	os.chdir(install_path)

	compile_status = run_command(['make', 'all'])
	assert compile_status
	install_status = run_command(['make', 'install'])
	assert install_status

	os.chdir(old_path)


def __build_fstest__(abs_in_path, filesystem = 'ext4'):

	old_path = os.getcwd()
	os.chdir(abs_in_path)

	# Fix filesystem in test config
	conf_rel_path = os.path.join(TEST_FSTEST_TESTS_SUBPATH, TEST_FSTEST_CONF_FN)
	fstest_conf = read_file(conf_rel_path).split('\n')
	for index, line in enumerate(fstest_conf):
		if line.startswith('fs=') or line.startswith('#fs='):
			fstest_conf[index] = 'fs="%s"' % filesystem
			break
	write_file(conf_rel_path, '\n'.join(fstest_conf))

	autoreconf_status = run_command(['autoreconf', '-ifs'])
	assert autoreconf_status
	configure_status = run_command(['./configure'])
	assert configure_status
	build_status, out, err = run_command(['make', 'pjdfstest'], return_output = True)
	assert build_status

	os.chdir(old_path)
