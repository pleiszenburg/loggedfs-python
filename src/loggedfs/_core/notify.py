# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	src/loggedfs/_core/notify.py: Notification backend - LoggedFS as a library

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

import atexit
import inspect
import os
import subprocess
import sys
import threading

from .defaults import (
	FUSE_ALLOWOTHER_DEFAULT,
	LOG_BUFFERS_DEFAULT,
	LOG_ONLYMODIFYOPERATIONS_DEFAULT
	)
from .filter import filter_pipeline_class
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
		consumer_out_func = None, # consumes signals
		consumer_err_func = None, # consumes anything on stderr
		post_exit_func = None, # called on exit
		log_filter = None,
		log_buffers = LOG_BUFFERS_DEFAULT,
		log_only_modify_operations = LOG_ONLYMODIFYOPERATIONS_DEFAULT,
		fuse_allowother = FUSE_ALLOWOTHER_DEFAULT,
		background = False # thread in background
		):
		"""Creates a filesystem notifier object.

		- directory: Relative or absolute path as a string
		- consumer_out_func: None or callable, consumes events provided as a dictionary
		- consumer_err_func: None or callable, consumes output from stderr
		- post_exit_func: None or callable, called when notifier was terminated
		- log_filter: None or instance of filter_pipeline_class
		- log_buffers: Boolean, activates logging of read and write buffers
		- fuse_allowother: Boolean, allows other users to see the LoggedFS filesystem
		- background: Boolean, starts notifier in a thread
		"""

		if log_filter is None:
			log_filter = filter_pipeline_class()

		if not isinstance(directory, str):
			raise TypeError('directory must be of type string')
		if not os.path.isdir(directory):
			raise ValueError('directory must be a path to an existing directory')
		if not os.access(directory, os.W_OK | os.R_OK):
			raise ValueError('not sufficient permissions on directory')

		if consumer_out_func is not None and not hasattr(consumer_out_func, '__call__'):
			raise TypeError('consumer_out_func must either be None or callable')
		if hasattr(consumer_out_func, '__call__'):
			if len(inspect.signature(consumer_out_func).parameters.keys()) != 1:
				raise ValueError('consumer_out_func must have one parameter')
		if consumer_err_func is not None and not hasattr(consumer_err_func, '__call__'):
			raise TypeError('consumer_err_func must either be None or callable')
		if hasattr(consumer_err_func, '__call__'):
			if len(inspect.signature(consumer_err_func).parameters.keys()) != 1:
				raise ValueError('consumer_err_func must have one parameter')
		if post_exit_func is not None and not hasattr(post_exit_func, '__call__'):
			raise TypeError('post_exit_func must either be None or callable')
		if not isinstance(log_filter, filter_pipeline_class):
			raise TypeError('log_filter must either be None or of type filter_pipeline_class')
		if not isinstance(log_buffers, bool):
			raise TypeError('log_buffers must be of type bool')
		if not isinstance(log_only_modify_operations, bool):
			raise TypeError('log_only_modify_operations must be of type bool')
		if not isinstance(fuse_allowother, bool):
			raise TypeError('fuse_allowother must be of type bool')
		if not isinstance(background, bool):
			raise TypeError('background must be of type bool')

		self._directory = os.path.abspath(directory)
		self._post_exit_func = post_exit_func
		self._consumer_out_func = consumer_out_func
		self._consumer_err_func = consumer_err_func
		self._log_filter = log_filter
		self._log_buffers = log_buffers
		self._log_only_modify_operations = log_only_modify_operations
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
		if self._log_only_modify_operations:
			command.append('-m')
		if self._fuse_allowother:
			command.append('-p')
		command.append(self._directory)

		args = (command, self._handle_stdout, self._handle_stderr, self._handle_exit)

		atexit.register(self.terminate)
		if self._background:
			self._t = threading.Thread(target = receive, args = args, daemon = False)
			self._t.start()
		else:
			receive(*args)


	def _handle_stderr(self, msg):

		if self._consumer_err_func is not None:
			self._consumer_err_func(msg)
		else:
			sys.stderr.write(c['RED'] + str(msg).rstrip('\n') + c['RESET'] + '\n')
			sys.stderr.flush()


	def _handle_stdout(self, msg):

		if not isinstance(msg, end_of_transmission):
			if not self._log_filter.match(msg):
				return

		if self._consumer_out_func is not None:
			self._consumer_out_func(msg)
		else:
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

		if self._background:
			self._t.join()
