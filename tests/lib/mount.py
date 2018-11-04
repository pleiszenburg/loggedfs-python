# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	tests/loggedfs_libtest/mount.py: Mount & umount routines

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

from .lib import run_command


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def attach_loop_device(in_abs_path):

	return run_command(['losetup', '-f', in_abs_path], sudo = True)


def detach_loop_device(device_path):

	return run_command(['losetup', '-d', device_path], sudo = True)


def find_loop_devices(in_abs_path):

	status, out, err = run_command(['losetup', '-j', in_abs_path], return_output = True, sudo = True)
	if status:
		return [line.strip().split(':')[0] for line in out.split('\n') if line.strip() != '']
	else:
		return None


def is_path_mountpoint(in_abs_path):

	return run_command(['mountpoint', '-q', in_abs_path])


def mount(in_abs_path, device_path):

	return run_command(['mount', device_path, in_abs_path], sudo = True)


def mount_loggedfs_python(in_abs_path, logfile, cfgfile, sudo = False):

	return run_command(
		[
			'coverage', 'run',
			os.path.join(os.environ['VIRTUAL_ENV'], 'bin', 'loggedfs'),
			'-l', logfile,
			'-c', cfgfile,
			'-p', in_abs_path,
			'-s'
			],
		return_output = True, sudo = sudo, sudo_env = sudo
		)


def umount(in_abs_path, sudo = False, force = False):

	cmd_list = ['umount']
	if force:
		cmd_list.append('-f')
	cmd_list.append(in_abs_path)

	return run_command(cmd_list, sudo = sudo)


def umount_fuse(in_abs_path, sudo):

	return run_command(['fusermount', '-u', in_abs_path], sudo = sudo)
