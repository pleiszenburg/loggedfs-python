# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	src/loggedfs/_core/notify.py: Notification backend - LoggedFS as a library

	Copyright (C) 2017-2019 Sebastian M. Ernst <ernst@pleiszenburg.de>

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

import inspect
import os
import subprocess
import sys
import threading

from .defaults import (
	FUSE_ALLOWOTHER_DEFAULT,
	LOG_BUFFERS_DEFAULT
	)
from .ipc import receive, end_of_transmission


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CONST
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# https://en.wikipedia.org/wiki/ANSI_escape_code
c = {
	'RESET': '\033[0;0m',
	'BOLD': '\033[;1m',
	'REVERSE': '\033[;7m',
	'GREY': '\033[1;30m',
	'RED': '\033[1;31m',
	'GREEN': '\033[1;32m',
	'YELLOW': '\033[1;33m',
	'BLUE': '\033[1;34m',
	'MAGENTA': '\033[1;35m',
	'CYAN': '\033[1;36m',
	'WHITE': '\033[1;37m'
	}


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: NOTIFY
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class notify_class:
	"""Simple wrapper for using LoggedFS-python as a library.
	Attach a method of your choice to filesystem events.
	"""


	def __init__(self,
		directory,
		consumer_func = None, # consumes signals
		post_exit_func = None, # called on exit
		log_buffers = LOG_BUFFERS_DEFAULT,
		fuse_allowother = FUSE_ALLOWOTHER_DEFAULT,
		background = False # thread in background
		):
		"""Creates a filesystem notifier object.

		- directory: Relative or absolute path as a string
		- consumer_func: None or callable, consumes events provided as a dictionary
		- post_exit_func: None or callable, called when notifier was terminated
		- log_buffers: Boolean, activates logging of read and write buffers
		- fuse_allowother: Boolean, allows other users to see the LoggedFS filesystem
		- background: Boolean, starts notifier in a thread
		"""

		if not isinstance(directory, str):
			raise TypeError('directory must be of type string')
		if not os.path.isdir(directory):
			raise ValueError('directory must be a path to an existing directory')
		if not os.access(directory, os.W_OK | os.R_OK):
			raise ValueError('not sufficient permissions on directory')

		if consumer_func is not None and not hasattr(consumer_func, '__call__'):
			raise ValueError('consumer_func must either be None or callable')
		if hasattr(consumer_func, '__call__'):
			if len(inspect.signature(consumer_func).parameters.keys()) != 1:
				raise ValueError('consumer_func must have one parameter')
		if post_exit_func is not None and not hasattr(post_exit_func, '__call__'):
			raise ValueError('post_exit_func must either be None or callable')
		if not isinstance(log_buffers, bool):
			raise TypeError('log_buffers must be of type bool')
		if not isinstance(fuse_allowother, bool):
			raise TypeError('fuse_allowother must be of type bool')
		if not isinstance(background, bool):
			raise TypeError('background must be of type bool')

		self._directory = os.path.abspath(directory)
		self._post_exit_func = post_exit_func if post_exit_func is not None else lambda: None
		self._consumer_func = consumer_func if consumer_func is not None else self._handle_stdout
		self._log_buffers = log_buffers
		self._fuse_allowother = fuse_allowother
		self._background = background

		self._up = True

		command = ['loggedfs',
			'-f', # foreground
			'-s', # no syslog
			'--lib' # "hidden" library mode
			]
		if self._log_buffers:
			command.append('-b') # also log read and write buffers
		if self._fuse_allowother:
			command.append('-p')
		command.append(self._directory)

		args = (command, self._consumer_func, self._handle_stderr, self._handle_exit)

		if self._background:
			self._t = threading.Thread(target = receive, args = args, daemon = False)
			self._t.start()
		else:
			receive(*args)


	def _handle_stderr(self, msg):

		sys.stdout.write(c['RED'] + str(msg).rstrip('\n') + c['RESET'] + '\n')
		sys.stdout.flush()


	def _handle_stdout(self, msg):

		sys.stdout.write(c['GREEN'] + str(msg) + c['RESET'] + '\n')
		sys.stdout.flush()


	def _handle_exit(self):

		if self._post_exit_func is not None:
			self._post_exit_func()


	def terminate(self):

		if not self._up:
			return

		self._up = False

		command = ['fusermount', '-u', self._directory]
		proc = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
		proc.wait()

		if not self._background:
			self._t.join()
