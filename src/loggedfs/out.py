# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	src/loggedfs/out.py: Log output formatting and filtering

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

import base64
import errno
from functools import wraps
import grp
import inspect
import json
import pwd
import zlib

from fuse import (
	fuse_get_context,
	FuseOSError,
	)

from .filter import match_filters
from .log import log_msg


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def event(
	format_pattern = '',
	abs_path_fields = None,
	length_fields = None,
	uid_fields = None,
	gid_fields = None,
	fip_fields = None,
	path_filter_field = 0
	):

	if abs_path_fields is None:
		abs_path_fields = tuple()
	if length_fields is None:
		length_fields = tuple()
	if uid_fields is None:
		uid_fields = tuple() # only relevant for chown (target uid)
	if gid_fields is None:
		gid_fields = tuple() # only relevant for chown (target gid)
	if fip_fields is None:
		fip_fields = tuple()

	def wrapper(func):

		_func_param = inspect.signature(func).parameters
		func_arg_names = tuple(_func_param.keys())[1:]
		func_arg_defaults = {
			k: _func_param[k].default
			for k in func_arg_names
			if _func_param[k].default != inspect._empty
			}
		del _func_param

		@wraps(func)
		def wrapped(self, *func_args, **func_kwargs):

			try:
				uid, gid, pid = fuse_get_context()
				abs_path = _get_abs_path_(func_args, func_kwargs, abs_path_fields, self._full_path)
			except Exception as e:
				self.logger.exception(log_msg(self._log_json, 'UNEXPECTED in context stage (1)'))
				raise e

			ret_value = None
			try:
				ret_value = func(self, *func_args, **func_kwargs)
				ret_str = 'r = %s' % str(ret_value)
				ret_status = 'SUCCESS'
			except FuseOSError as e:
				ret_status = 'FAILURE'
				ret_str = 'FuseOS_e = %s' % errno.errorcode[e.errno]
				raise e
			except OSError as e:
				ret_status = 'FAILURE'
				ret_str = 'OS_e = %s' % errno.errorcode[e.errno]
				raise FuseOSError(e.errno)
			except Exception as e:
				ret_status = 'FAILURE'
				if hasattr(e, 'errno'): # all subclasses of OSError
					ret_str = 'e = %s' % errno.errorcode[e.errno]
					raise FuseOSError(e.errno)
				else:
					ret_str = '?'
					self.logger.exception(log_msg(self._log_json, 'UNEXPECTED in operation stage (2)'))
					raise e
			else:
				return ret_value
			finally:
				if match_filters(
					abs_path, uid, func.__name__, ret_status,
					self._f_incl, self._f_excl
					):
					try:
						_log_event_(
							self, uid, gid, pid, func, func_arg_names, func_arg_defaults, func_args, func_kwargs, format_pattern,
							abs_path_fields, length_fields, uid_fields, gid_fields, fip_fields,
							ret_status, ret_str, ret_value
							)
					except Exception as e:
						self.logger.exception(log_msg(self._log_json, 'UNEXPECTED in log stage (3)'))
						raise e

		return wrapped

	return wrapper


def _encode_bytes_(in_bytes):

	return base64.b64encode(zlib.compress(in_bytes, 1)).decode('utf-8') # compress level 1 (weak)


def _format_args_(args_list, kwargs_dict, items_list, format_func):

	for item in items_list:
		if isinstance(item, int):
			args_list[item] = format_func(args_list[item] if item < len(args_list) else -10) # ERROR CODE -10
		elif isinstance(item, str):
			kwargs_dict[item] = format_func(kwargs_dict.get(item, -11)) # ERROR CODE -11


def _get_abs_path_(args_list, kwargs_dict, path_item_list, abs_func):

	if len(path_item_list) == 0:
		return ''
	item = path_item_list[0]

	if isinstance(item, int):
		return abs_func(args_list[item])
	elif isinstance(item, str):
		return abs_func(kwargs_dict[item])


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
	self, uid, gid, pid, func, func_arg_names, func_arg_defaults, func_args, func_kwargs, format_pattern,
	abs_path_fields, length_fields, uid_fields, gid_fields, fip_fields,
	ret_status, ret_str, ret_value
	):

	p_cmdname = ''
	if self._log_printprocessname or self._log_json:
		p_cmdname = _get_process_cmdline_(pid).strip()

	if self._log_json:

		log_dict = {
			'proc_cmd': p_cmdname,
			'proc_uid': uid,
			'proc_gid': gid,
			'proc_pid': pid,
			'action': func.__name__,
			'status': ret_status == 'SUCCESS',
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
			arg_dict['buf'] = _encode_bytes_(arg_dict['buf'])
		except KeyError:
			pass

		log_dict.update({'param_%s' % k: v for k, v in arg_dict.items()})

		if log_dict['status']: # SUCCESS
			if isinstance(ret_value, int) or isinstance(ret_value, dict):
				log_dict['return'] = ret_value
			elif isinstance(ret_value, bytes):
				log_dict['return'] = _encode_bytes_(ret_value)
				log_dict['return_len'] = len(ret_value)
		else: # FAILURE
			log_dict['return'] = ret_str

		log_out = json.dumps(log_dict, sort_keys = True)[1:-1]

	else:

		func_args_f = list(func_args)
		func_kwargs_f = func_kwargs.copy()

		for field_list, format_func in [
			(abs_path_fields, self._full_path),
			(length_fields, len),
			(uid_fields, lambda x: '%s(%d)' % (_get_user_name_from_uid_(x), x)),
			(gid_fields, lambda x: '%s(%d)' % (_get_group_name_from_gid_(x), x)),
			(fip_fields, lambda x: '%d' % _get_fh_from_fip_(x))
			]:
			_format_args_(func_args_f, func_kwargs_f, field_list, format_func)

		log_out = ' '.join([
			'%s %s' % (func.__name__, format_pattern.format(*func_args_f, **func_kwargs_f)),
			'{%s}' % ret_status,
			'[ pid = %d %suid = %d ]' % (pid, ('%s ' % p_cmdname) if len(p_cmdname) > 0 else '', uid),
			'( %s )' % ret_str
			])

	self.logger.info(log_out)
