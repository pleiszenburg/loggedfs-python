# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	tests/loggedfs_libtest/lib.py: Library routines, I/O, ...

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
import subprocess

from yaml import load, dump
try:
	from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
	from yaml import Loader, Dumper


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES: SHELL OUT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def run_command(cmd_list, return_output = False, sudo = False, sudo_env = False, timeout = None):

	sudo_cmd = []
	if sudo:
		sudo_cmd.append('sudo')
		if sudo_env:
			sudo_cmd.append('env')
			sudo_cmd.append('%s=%s' % ('VIRTUAL_ENV', os.environ['VIRTUAL_ENV']))
			sudo_cmd.append('%s=%s:%s' % ('PATH', os.path.join(os.environ['VIRTUAL_ENV'], 'bin'), os.environ['PATH']))

	proc = subprocess.Popen(
		sudo_cmd + cmd_list, stdout = subprocess.PIPE, stderr = subprocess.PIPE
		)

	timeout_alert = ''
	try:
		outs, errs = proc.communicate(timeout = timeout)
	except TimeoutExpired:
		proc.kill()
		outs, errs = proc.communicate()
		timeout_alert = '\n\nLIBTEST: COMMAND TIMED OUT AND WAS KILLED!'

	if return_output:
		return (not bool(proc.returncode), outs.decode('utf-8'), errs.decode('utf-8') + timeout_alert)
	return not bool(proc.returncode)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES: I/O
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

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
