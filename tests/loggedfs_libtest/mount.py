# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	tests/loggedfs_libtest/mount.py: Mount & umount routines

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

from .lib import run_command


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def is_path_mountpoint(in_abs_path):

	return run_command(['mountpoint', '-q', in_abs_path])


def mount_loggedfs_python(in_abs_path, logfile, cfgfile):

	return run_command(
		['loggedfs', '-l', logfile, '-c', cfgfile, '-p', in_abs_path],
		return_output = True, sudo = True, sudo_env = True
		)


def umount(in_abs_path, sudo = False, force = False):

	cmd_list = []
	if sudo:
		cmd_list.append('sudo')
	cmd_list.append('umount')
	if force:
		cmd_list.append('-f')
	cmd_list.append(in_abs_path)

	return run_command(cmd_list)


def umount_fuse(in_abs_path):

	return run_command(['fusermount', '-u', in_abs_path])
