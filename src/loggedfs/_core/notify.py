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

from .defaults import LOG_BUFFERS_DEFAULT
from .ipc import receive


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: NOTIFY
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class notify_class:


	def __init__(self,
		directory,
		consumer_func = None, # consumes signals
		exit_func = None, # called on exit
		log_buffers = LOG_BUFFERS_DEFAULT,
		background = False # thread in background
		):

		if not isinstance(directory, str):
			raise TypeError('directory must be of type string')
		if not os.path.isdir(directory):
			raise ValueError('directory must be a path to an existing directory')
		if not os.access(directory, os.W_OK | os.R_OK):
			raise ValueError('not sufficient permissions on directory')

		if consumer_func is None or not hasattr(consumer_func, '__call__'):
			raise ValueError('consumer_func must be callable')
		if len(inspect.signature(consumer_func).parameters.keys()) != 1:
			raise ValueError('consumer_func must have one parameter')
		if exit_func is not None and not hasattr(exit_func, '__call__'):
			raise ValueError('exit_func must either be None or callable')
		if not isinstance(log_buffers, bool):
			raise TypeError('log_buffers must be of type bool')
		if not isinstance(background, bool):
			raise TypeError('background must be of type bool')

		self._directory = os.path.abspath(directory)
		self._exit_func = exit_func
		self._consumer_func = consumer_func
		self._log_buffers = log_buffers
		self._background = background

		command = ['loggedfs',
			'-f', # foreground
			'-p', # allow other users
			'-s', # no syslog
			'--lib' # "hidden" library mode
			]
		if self._log_buffers:
			command.append('-b') # also log read and write buffers


	def terminate(self):

		command = ['fusermount', '-u', self._directory]
