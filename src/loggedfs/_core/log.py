# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	src/loggedfs/_core/log.py: Logging

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

import json
import logging
import logging.handlers
import os
import platform

from .timing import time


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CONST
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

SYSLOG_ADDRESS = {
	'Linux': '/dev/log',
	'Darwin': '/var/run/syslog'
	}


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# LOGGING: Support nano-second timestamps
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class _LogRecord_ns_(logging.LogRecord):

	def __init__(self, *args, **kwargs):

		self.created_ns = time.time_ns() # Fetch precise timestamp
		super().__init__(*args, **kwargs)


class _Formatter_ns_(logging.Formatter):

	default_nsec_format = '%s,%09d'

	def formatTime(self, record, datefmt=None):

		if datefmt is not None: # Do not handle custom formats here ...
			return super().formatTime(record, datefmt) # ... leave to original implementation
		ct = self.converter(record.created_ns / 1e9)
		t = time.strftime(self.default_time_format, ct)
		s = self.default_nsec_format % (t, record.created_ns - (record.created_ns // 10**9) * 10**9)
		return s


logging.setLogRecordFactory(_LogRecord_ns_)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def get_logger(name, log_enabled, log_file, log_syslog, log_json):

	if log_json:
		log_formater = _Formatter_ns_('{"time": "%(asctime)s", "logger": "%(name)s", %(message)s}')
		log_formater_short = _Formatter_ns_('{%(message)s}')
	else:
		log_formater = _Formatter_ns_('%(asctime)s (%(name)s) %(message)s')
		log_formater_short = _Formatter_ns_('%(message)s')

	logger = logging.getLogger(name)

	if not bool(log_enabled):
		logger.setLevel(logging.CRITICAL)
		return logger
	logger.setLevel(logging.DEBUG)

	ch = logging.StreamHandler()
	ch.setLevel(logging.DEBUG)
	ch.setFormatter(log_formater)
	logger.addHandler(ch)

	if bool(log_syslog):
		try:
			sl = logging.handlers.SysLogHandler(address = SYSLOG_ADDRESS[platform.system()])
		except KeyError:
			raise NotImplementedError('unsupported operating system')
		sl.setLevel(logging.DEBUG)
		sl.setFormatter(log_formater_short)
		logger.addHandler(sl)

	if log_file is None:
		return logger

	fh = logging.FileHandler(os.path.join(log_file)) # TODO
	fh.setLevel(logging.DEBUG)
	fh.setFormatter(log_formater)
	logger.addHandler(fh)

	return logger


def log_msg(log_json, msg):

	if log_json:
		return '"msg": %s' % json.dumps(msg)
	else:
		return msg
