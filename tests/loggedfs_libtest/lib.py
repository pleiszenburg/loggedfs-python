# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	tests/loggedfs_libtest/lib.py: Library routines, I/O, ...

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
import signal
import subprocess

import psutil
from yaml import load, dump
try:
	from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
	from yaml import Loader, Dumper

from .const import TEST_FS_EXT4


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES: SHELL OUT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def kill_proc(pid, k_signal = signal.SIGINT, entire_group = False, sudo = False):

	if not sudo:
		if entire_group:
			os.killpg(os.getpgid(pid), k_signal)
		else:
			os.kill(pid, k_signal)
	else:
		if entire_group:
			run_command(['kill', '-%d' % k_signal, '--', '-%d' % os.getpgid(pid)], sudo = sudo)
		else:
			run_command(['kill', '-%d' % k_signal, '%d' % pid], sudo = sudo)


def run_command(
	cmd_list, return_output = False, sudo = False, sudo_env = False, timeout = None, setsid = False, return_status_code = False
	):

	cmd_prefix = []

	if sudo:
		cmd_prefix.append('sudo')
		if setsid:
			cmd_prefix.append('-b')
		if sudo_env:
			cmd_prefix.append('env')
			cmd_prefix.append('%s=%s' % ('VIRTUAL_ENV', os.environ['VIRTUAL_ENV']))
			cmd_prefix.append('%s=%s:%s' % ('PATH', os.path.join(os.environ['VIRTUAL_ENV'], 'bin'), os.environ['PATH']))
	elif setsid:
		cmd_prefix.append('setsid') # TODO untested codepath

	full_cmd = cmd_prefix + cmd_list

	proc = subprocess.Popen(
		full_cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE
		)

	timeout_alert = ''
	if timeout is not None:
		try:
			outs, errs = proc.communicate(timeout = timeout)
		except subprocess.TimeoutExpired:
			timeout_alert = '\n\nLIBTEST: COMMAND TIMED OUT AND WAS KILLED!'
			if setsid:
				kill_pid = __get_pid__(full_cmd) # proc.pid will deliver wrong pid!
			else:
				kill_pid = proc.pid
			kill_proc(kill_pid, k_signal = signal.SIGINT, entire_group = setsid, sudo = sudo)
			outs, errs = proc.communicate() # (proc.stdout.read(), proc.stderr.read())
	else:
		outs, errs = proc.communicate()

	status_value = proc.returncode if return_status_code else not bool(proc.returncode)

	if return_output:
		return (status_value, outs.decode('utf-8'), errs.decode('utf-8') + timeout_alert)
	return status_value


def __get_pid__(cmd_line_list):

	for pid in psutil.pids():
		proc = psutil.Process(pid)
		if cmd_line_list == proc.cmdline():
			return proc.pid
	return None


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES: FILESYSTEM
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def ck_filesystem(filename, file_system = TEST_FS_EXT4):

	assert file_system == TEST_FS_EXT4 # TODO add support for other filesystems?
	return run_command(
		['fsck.ext4', '-f', '-F', '-n', '-v', filename],
		return_output = True, sudo = True, return_status_code = True
		)


def create_zero_file(filename, size_in_mb):

	assert not os.path.isfile(filename)
	status = run_command(['dd', 'if=/dev/zero', 'of=%s' % filename, 'bs=1M', 'count=%d' % size_in_mb])
	assert status
	assert os.path.isfile(filename)


def mk_filesystem(filename, file_system = TEST_FS_EXT4):

	assert file_system == TEST_FS_EXT4 # TODO add support for other filesystems?
	# https://github.com/pjd/pjdfstest/issues/24
	# Block size must be equal or greater than PATH_MAX or symlink/03.t tests 1&2 fail
	status = run_command(
		['mke2fs', '-b', '4096', '-I', '256', '-t', file_system, '-E', 'lazy_itable_init=0', '-O', '^has_journal', filename],
		sudo = True
		)
	assert status


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES: I/O
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def append_to_file(filename, data):

	f = open(filename, 'a')
	f.write(data)
	f.close()


def format_yaml(data):

	return dump(data, Dumper = Dumper, default_flow_style = False)


def dump_yaml(filename, data):

	f = open(filename, 'w+')
	dump(data, f, Dumper = Dumper, default_flow_style = False)
	f.close()


def load_yaml(filename):

	f = open(filename, 'r')
	data = load(f)
	f.close()
	return data


def read_file(filename):

	f = open(filename, 'r')
	data = f.read()
	f.close()
	return data


def write_file(filename, data):

	f = open(filename, 'w+')
	f.write(data)
	f.close()
