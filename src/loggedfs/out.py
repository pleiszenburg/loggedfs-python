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

import errno
from functools import wraps
import grp
import pwd
import sys

from fuse import (
	fuse_get_context,
	FuseOSError,
	)

from .filter import match_filters


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def event(
	format_pattern = '',
	abs_path_fields = None, length_fields = None,
	uid_fields = None, gid_fields = None,
	fip_fields = None,
	path_filter_field = 0
	):

	if abs_path_fields is None:
		abs_path_fields = tuple() # TODO tuple enough?
	if length_fields is None:
		length_fields = tuple() # TODO tuple enough?
	if uid_fields is None:
		uid_fields = tuple() # TODO tuple enough?
	if gid_fields is None:
		gid_fields = tuple() # TODO tuple enough?
	if fip_fields is None:
		fip_fields = tuple() # TODO tuple enough?

	def wrapper(func):

		@wraps(func)
		def wrapped(self, *func_args, **func_kwargs):

			try:

				uid, gid, pid = fuse_get_context()

				if self._log_printprocessname:
					p_cmdname = __get_process_cmdline__(pid).strip()
					if len(p_cmdname) > 0:
						p_cmdname = '%s ' % p_cmdname
				else:
					p_cmdname = ''

				abs_path = __get_abs_path__(func_args, func_kwargs, abs_path_fields, self._full_path)

				func_args_f = list(func_args)
				func_kwargs_f = func_kwargs.copy()

				for field_list, format_func in [
					(abs_path_fields, self._full_path),
					(length_fields, len),
					(uid_fields, lambda x: '%s(%d)' % (__get_user_name_from_uid__(x), x)),
					(gid_fields, lambda x: '%s(%d)' % (__get_group_name_from_gid__(x), x)),
					(fip_fields, lambda x: '%d' % __get_fh_from_fip__(x))
					]:
					__format_args__(func_args_f, func_kwargs_f, field_list, format_func)

				log_msg = ' '.join([
					'%s %s' % (func.__name__, format_pattern.format(*func_args_f, **func_kwargs_f)),
					'{%s}',
					'[ pid = %d %suid = %d ]' % (pid, p_cmdname, uid),
					'( %s )'
					])

			except:

				self.logger.exception('Something just went terribly wrong unexpectedly ON INIT ...')
				raise

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

			except:

				ret_status = 'FAILURE'
				e = sys.exc_info()[0]

				if hasattr(e, 'errno'): # all subclasses of OSError
					ret_str = 'e = %s' % errno.errorcode[e.errno]
					raise FuseOSError(e.errno)
				else:
					ret_str = '?'
					self.logger.exception('Something just went terribly wrong unexpectedly ...')
					raise e

			else:

				return ret_value

			finally:

				if match_filters(
					abs_path, uid, func.__name__, ret_status,
					self._f_incl, self._f_excl
					):
					self.logger.info(log_msg % (ret_status, ret_str))

		return wrapped

	return wrapper


def __format_args__(args_list, kwargs_dict, items_list, format_func):

	for item in items_list:
		if isinstance(item, int):
			args_list[item] = format_func(args_list[item] if item < len(args_list) else -10) # ERROR CODE -10
		elif isinstance(item, str):
			kwargs_dict[item] = format_func(kwargs_dict.get(item, -11)) # ERROR CODE -11


def __get_abs_path__(args_list, kwargs_dict, path_item_list, abs_func):

	if len(path_item_list) == 0:
		return ''
	item = path_item_list[0]

	if isinstance(item, int):
		return abs_func(args_list[item])
	elif isinstance(item, str):
		return abs_func(kwargs_dict[item])


def __get_process_cmdline__(pid):

	try:

		f = open('/proc/%d/cmdline' % pid, 'r')
		cmdline = f.read()
		f.close()

		return cmdline.replace('\x00', ' ').strip()

	except FileNotFoundError:

		return ''


def __get_group_name_from_gid__(gid):

	try:
		return grp.getgrgid(gid).gr_name
	except KeyError:
		return '[gid: omitted argument]'


def __get_user_name_from_uid__(uid):

	try:
		return pwd.getpwuid(uid).pw_name
	except KeyError:
		return '[uid: omitted argument]'


def __get_fh_from_fip__(fip):

	if fip is None:
		return -1
	if not hasattr(fip, 'fh'):
		return -2
	if not isinstance(fip.fh, int):
		return -3
	return fip.fh
