# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	src/loggedfs/_core/out.py: Log output formatting and filtering

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

import base64
import errno
from functools import wraps
import grp
import inspect
import json
import pwd
import zlib

from refuse.high import (
	fuse_get_context,
	FuseOSError,
	)

from .ipc import send
from .log import log_msg
from .timing import time


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CONST
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

STATUS_DICT = {
	True: 'SUCCESS',
	False: 'FAILURE'
	}

ATTR_NAME = '__name__'
ATTR_ERRNO = 'errno'

NAME_OSERROR = 'OSError'
NAME_FUSEOSERROR = 'FuseOSError'
NAME_UNKNOWN = 'Unknown Exception'

ERROR_STAGE1 = 'UNEXPECTED in operation stage (1)'
ERROR_STAGE2 = 'UNEXPECTED in log stage (2)'


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def event(format_pattern = ''):

	def wrapper(func):

		_func_param = inspect.signature(func).parameters
		func_arg_names = tuple(_func_param.keys())[1:]
		func_arg_abspath = func_arg_names[[item.endswith('path') for item in func_arg_names].index(True)]
		func_arg_defaults = {
			k: _func_param[k].default
			for k in func_arg_names
			if _func_param[k].default != inspect._empty
			}
		del _func_param

		@wraps(func)
		def wrapped(self, *func_args, **func_kwargs):

			ret_value = None
			ret_status = False
			try:
				ret_value = func(self, *func_args, **func_kwargs)
				ret_status = True
			except FuseOSError as e:
				ret_value = (NAME_FUSEOSERROR, e.errno)
				raise e
			except OSError as e:
				ret_value = (NAME_OSERROR, e.errno)
				raise FuseOSError(e.errno)
			except Exception as e:
				if hasattr(e, ATTR_ERRNO): # all subclasses of OSError
					ret_value = (getattr(type(e), ATTR_NAME, NAME_UNKNOWN), e.errno)
					raise FuseOSError(e.errno)
				else:
					self._logger.exception(log_msg(self._log_json, ERROR_STAGE1))
					raise e
			else:
				return ret_value
			finally:
				try:
					_log_event_(
						self,
						func, func_arg_names, func_arg_abspath, func_arg_defaults, func_args, func_kwargs,
						format_pattern,
						ret_status, ret_value
						)
				except Exception as e:
					self._logger.exception(log_msg(self._log_json, ERROR_STAGE2))
					raise e

		return wrapped

	return wrapper


def decode_buffer(in_buffer):

	if not isinstance(in_buffer, str):
		raise TypeError('in_buffer must be a string')

	return zlib.decompress(base64.b64decode(in_buffer.encode('utf-8')))


def _encode_buffer_(in_bytes):

	return base64.b64encode(zlib.compress(in_bytes, 1)).decode('utf-8') # compress level 1 (weak)


def _get_fh_from_fip_(fip):

	if fip is None:
		return -1
	if not hasattr(fip, 'fh'):
		return -2
	if not isinstance(fip.fh, int):
		return -3
	return fip.fh


def _get_group_name_from_gid_(gid):

	try:
		return grp.getgrgid(gid).gr_name
	except KeyError:
		return '[gid: omitted argument]'


def _get_process_cmdline_(pid):

	try:
		with open('/proc/%d/cmdline' % pid, 'r') as f: # TODO encoding, bytes?
			cmdline = f.read()
		return cmdline.replace('\x00', ' ').strip()
	except FileNotFoundError:
		return ''


def _get_user_name_from_uid_(uid):

	try:
		return pwd.getpwuid(uid).pw_name
	except KeyError:
		return '[uid: omitted argument]'


def _log_event_(
	self,
	func, func_arg_names, func_arg_abspath, func_arg_defaults, func_args, func_kwargs,
	format_pattern,
	ret_status, ret_value
	):

	if self._log_only_modify_operations:
		if func.__name__ not in (
			'chmod',
			'chown',
			'link',
			'mkdir',
			'mknod',
			'rename',
			'rmdir',
			'symlink',
			'truncate',
			'unlink',
			'utimens',
			'write'
			):
			return

	uid, gid, pid = fuse_get_context()

	p_cmdname = ''
	if self._log_printprocessname or self._log_json:
		p_cmdname = _get_process_cmdline_(pid).strip()

	log_dict = {
		'proc_cmd': p_cmdname,
		'proc_uid': uid,
		'proc_uid_name': _get_user_name_from_uid_(uid),
		'proc_gid': gid,
		'proc_gid_name': _get_group_name_from_gid_(gid),
		'proc_pid': pid,
		'action': func.__name__,
		'status': ret_status,
		}

	arg_dict = {
		arg_name: arg
		for arg_name, arg in zip(func_arg_names, func_args)
		}
	arg_dict.update({
		arg_name: func_kwargs.get(arg_name, func_arg_defaults[arg_name])
		for arg_name in func_arg_names[len(func_args):]
		})

	try:
		arg_dict['uid_name'] = _get_user_name_from_uid_(arg_dict['uid'])
	except KeyError:
		pass
	try:
		arg_dict['gid_name'] = _get_group_name_from_gid_(arg_dict['gid'])
	except KeyError:
		pass
	try:
		arg_dict['fip'] = _get_fh_from_fip_(arg_dict['fip'])
	except KeyError:
		pass
	for k in arg_dict.keys():
		if k.endswith('path'):
			arg_dict[k] = self._full_path(arg_dict[k])
	try:
		arg_dict['buf_len'] = len(arg_dict['buf'])
		arg_dict['buf'] = _encode_buffer_(arg_dict['buf']) if self._log_buffers else ''
	except KeyError:
		pass

	log_dict.update({'param_%s' % k: v for k, v in arg_dict.items()})

	if log_dict['status']: # SUCCESS
		if any((
			ret_value is None,
			isinstance(ret_value, int),
			isinstance(ret_value, str),
			isinstance(ret_value, dict),
			isinstance(ret_value, list)
			)):
			log_dict['return'] = ret_value
		elif isinstance(ret_value, bytes):
			log_dict['return_len'] = len(ret_value)
			log_dict['return'] = _encode_buffer_(ret_value) if self._log_buffers else ''

	else: # FAILURE
		log_dict.update({
			'return': None,
			'return_exception': ret_value[0],
			'return_errno': ret_value[1],
			'return_errorcode': errno.errorcode[ret_value[1]]
			})

	if not self._lib_mode:
		if not self._log_filter.match(log_dict):
			return

	if self._log_json and not self._lib_mode:
		self._logger.info( json.dumps(log_dict, sort_keys = True)[1:-1] )
		return
	elif self._lib_mode:
		log_dict['time'] = time.time_ns()
		send(log_dict)
		return

	log_out = ' '.join([
		'%s %s' % (func.__name__, format_pattern.format(**log_dict)),
		'{%s}' % STATUS_DICT[ret_status],
		'[ pid = %d %suid = %d ]' % (pid, ('%s ' % p_cmdname) if len(p_cmdname) > 0 else '', uid),
		'( r = %s )' % str(log_dict['return'])
			if log_dict['status'] else
		'( %s = %d )' % ret_value
		])

	self._logger.info(log_out)
