# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	src/loggedfs/core.py: Module core

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

from copy import deepcopy
import errno
from functools import wraps
import grp
import math
import logging
import os
from pprint import pformat as pf
import pwd
import re
import signal
import stat
import sys

import fuse
from fuse import (
	FUSE,
	fuse_get_context,
	FuseOSError,
	Operations
	)
import xmltodict


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ERRORS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class loggedfs_timeout_error(Exception):
	pass


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def loggedfs_factory(
	directory,
	no_daemon_bool = False,
	allow_other = False,
	loggedfs_param_dict = {},
	log_file = None
	):

	# Change into mountpoint (must be abs path!)
	os.chdir(directory)
	# Open mount point
	directory_fd = os.open('.', os.O_RDONLY);

	return FUSE(
		loggedfs(
			(directory, directory_fd),
			loggedfs_param_dict,
			log_file
			),
		directory,
		nothreads = True,
		foreground = no_daemon_bool,
		allow_other = allow_other,
		default_permissions = True,
		attr_timeout = 0,
		entry_timeout = 0,
		negative_timeout = 0,
		nonempty = True, # common options taken from LoggedFS
		use_ino = True # common options taken from LoggedFS
		)


def __format_args__(args_list, kwargs_dict, items_list, format_func):

	for item in items_list:
		if isinstance(item, int):
			args_list[item] = format_func(args_list[item])
		elif isinstance(item, str):
			kwargs_dict[item] = format_func(kwargs_dict[item])


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

		return cmdline

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


def __log__(
	format_pattern = '',
	abs_path_fields = [], length_fields = [], uid_fields = [], gid_fields = [],
	path_filter_field = 0
	):

	def wrapper(func):

		@wraps(func)
		def wrapped(self, *func_args, **func_kwargs):

			try:

				uid, gid, pid = fuse_get_context()
				p_cmdname = __get_process_cmdline__(pid)

				abs_path = __get_abs_path__(func_args, func_kwargs, abs_path_fields, self._full_path)

				func_args_f = list(deepcopy(func_args))
				func_kwargs_f = deepcopy(func_kwargs)

				for field_list, format_func in [
					(abs_path_fields, lambda x: self._full_path(x)),
					(length_fields, lambda x: len(x)),
					(uid_fields, lambda x: '%s(%d)' % (__get_user_name_from_uid__(x), x)),
					(gid_fields, lambda x: '%s(%d)' % (__get_group_name_from_gid__(x), x))
					]:
					__format_args__(func_args_f, func_kwargs_f, field_list, format_func)

				log_msg = ' '.join([
					'%s \n\t%s\n\t' % (func.__name__, format_pattern.format(*func_args_f, **func_kwargs_f)),
					'{%s}\n\t',
					'[ pid = %d %s uid = %d ]\n\t' % (pid, p_cmdname, uid),
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

				__log_filter__(
					self.logger.error, log_msg,
					abs_path, uid, func.__name__, ret_status, ret_str,
					self._f_incl, self._f_excl
					)

		return wrapped

	return wrapper


def __log_filter__(
	out_func, log_msg,
	abs_path, uid, action, status, return_message,
	incl_filter_list, excl_filter_list
	):

	def match_filter(f_path, f_uid, f_action, f_status):
		return all([
			bool(f_path.match(abs_path)),
			(uid == f_uid) if isinstance(f_uid, int) else True,
			bool(f_action.match(action)),
			bool(f_status.match(status))
			])

	if len(incl_filter_list) != 0:
		included = False
		for filter_tuple in incl_filter_list:
			if match_filter(*filter_tuple):
				included = True
				break
		if not included:
			return

	for filter_tuple in excl_filter_list:
		if match_filter(*filter_tuple):
			return

	out_func(log_msg % (status, return_message))


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CORE CLASS: Init and internal routines
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class loggedfs: # (Operations):


	WITH_NANOSECOND_INT = True


	def __init__(self, root_tup, param_dict = {}, log_file = None):

		self.root_path, self.root_path_fd = root_tup
		self._p = param_dict

		self.flag_nanosecond_int = hasattr(self, 'WITH_NANOSECOND_INT') and hasattr(fuse, 'NANOSECOND_INT_AVAILABLE')

		log_formater = logging.Formatter('%(asctime)s (%(name)s) %(message)s')
		self.logger = logging.getLogger('LoggedFS-python')
		self.logger.setLevel(logging.DEBUG)

		ch = logging.StreamHandler()
		ch.setLevel(logging.DEBUG)
		ch.setFormatter(log_formater)
		self.logger.addHandler(ch)

		self._compile_filter()

		self.st_fields = [i for i in dir(os.stat_result) if i.startswith('st_')]
		self.stvfs_fields = [i for i in dir(os.statvfs_result) if i.startswith('f_')]

		if log_file is not None:

			fh = logging.FileHandler(os.path.join(log_file))
			fh.setLevel(logging.DEBUG)
			fh.setFormatter(log_formater)
			self.logger.addHandler(fh)


	def __call__(self, op, *args):

		if not hasattr(self, op):
			self.logger.critical('CRITICAL EFAULT: Operation "%s" unknown!' % op)
			raise FuseOSError(EFAULT)

		return getattr(self, op)(*args)


	def _compile_filter(self):

		def proc_filter_item(in_item):
			return (
				re.compile(in_item['@extension']),
				int(in_item['@uid']) if in_item['@uid'].isnumeric() else None,
				re.compile(in_item['@action']),
				re.compile(in_item['@retname'])
				)

		def proc_filter_list(in_list):
			if not isinstance(in_list, list):
				return [proc_filter_item(in_list)]
			return [proc_filter_item(item) for item in in_list]

		self._f_incl = proc_filter_list(self._p['includes']['include']) if self._p['includes'] is not None else []
		self._f_excl = proc_filter_list(self._p['excludes']['exclude']) if self._p['excludes'] is not None else []


	def _full_path(self, partial_path):

		if partial_path.startswith('/'):
			partial_path = partial_path[1:]
		path = os.path.join(self.root_path, partial_path)
		return path


	@staticmethod
	def _rel_path(partial_path):

		if len(partial_path) == 0:
			return '.'
		elif partial_path == '/':
			return '.'
		elif partial_path.startswith('/'):
			return partial_path[1:]
		elif partial_path.startswith('./'):
			return partial_path[2:]
		else:
			return partial_path


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CORE CLASS: Filesystem & file methods
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	@__log__(format_pattern = '{0}', abs_path_fields = [0])
	def access(self, path, mode):

		if not os.access(self._rel_path(path), mode, dir_fd = self.root_path_fd):
			raise FuseOSError(errno.EACCES)


	@__log__(format_pattern = '{0} to {1}', abs_path_fields = [0])
	def chmod(self, path, mode):

		return os.chmod(self._rel_path(path), mode, dir_fd = self.root_path_fd)


	@__log__(format_pattern = '{0} to {1}:{2}', abs_path_fields = [0], uid_fields = [1], gid_fields = [2])
	def chown(self, path, uid, gid):

		return os.chown(self._rel_path(path), uid, gid, dir_fd = self.root_path_fd, follow_symlinks = False)


	@__log__(format_pattern = '{0}')
	def destroy(self, path):

		os.close(self.root_path_fd)


	@__log__(format_pattern = '{0}', abs_path_fields = [0])
	def getattr(self, path, fh = None):

		try:

			st = os.lstat(self._rel_path(path), dir_fd = self.root_path_fd)
			ret_dict = {key: getattr(st, key) for key in self.st_fields}

			for key in ['st_atime', 'st_ctime', 'st_mtime']:
				if self.flag_nanosecond_int:
					ret_dict[key] = ret_dict.pop(key + '_ns')
				else:
					ret_dict.pop(key + '_ns')

			return ret_dict

		except FileNotFoundError:

			raise FuseOSError(errno.ENOENT)


	@__log__(format_pattern = '{0}')
	def init(self, path):

		os.fchdir(self.root_path_fd)


	@__log__(format_pattern = '{1} to {0}', abs_path_fields = [0, 1])
	def link(self, target_path, source_path):

		target_rel_path = self._rel_path(target_path)

		res = os.link(
			self._rel_path(source_path), target_rel_path,
			src_dir_fd = self.root_path_fd, dst_dir_fd = self.root_path_fd
			)

		uid, gid, pid = fuse_get_context()
		os.lchown(target_rel_path, uid, gid)

		return res


	@__log__(format_pattern = '{0} {1}', abs_path_fields = [0])
	def mkdir(self, path, mode):

		rel_path = self._rel_path(path)

		res = os.mkdir(rel_path, mode, dir_fd = self.root_path_fd)

		uid, gid, pid = fuse_get_context()
		os.lchown(rel_path, uid, gid)
		os.chmod(rel_path, mode) # HACK should be lchmod, which is only available on BSD

		return res


	@__log__(format_pattern = '{0} {1}', abs_path_fields = [0])
	def mknod(self, path, mode, dev):

		rel_path = self._rel_path(path)

		if stat.S_ISREG(mode):
			res = os.open(
				rel_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, mode,
				dir_fd = self.root_path_fd
				) # TODO broken, applies umask to mode no matter what ...
			if res >= 0:
				os.close(res)
		elif stat.S_ISFIFO(mode):
			os.mkfifo(rel_path, mode, dir_fd = self.root_path_fd)
		else:
			os.mknod(rel_path, mode, dev, dir_fd = self.root_path_fd)

		uid, gid, pid = fuse_get_context()
		os.chown(rel_path, uid, gid, dir_fd = self.root_path_fd, follow_symlinks = False)
		os.chmod(rel_path, mode, dir_fd = self.root_path_fd) # HACK should be lchmod, which is only available on BSD

		return 0


	@__log__(format_pattern = '({1}) {0}', abs_path_fields = [0])
	def open(self, path, flags):

		res = os.open(self._rel_path(path), flags, dir_fd = self.root_path_fd)
		os.close(res)

		return 0


	@__log__(format_pattern = '{1} bytes from {0} at offset {2}', abs_path_fields = [0])
	def read(self, path, length, offset, fh):

		# ret is a bytestring!

		fh_loc = os.open(self._rel_path(path), os.O_RDONLY, dir_fd = self.root_path_fd)
		ret = os.pread(fh_loc, length, offset)
		os.close(fh_loc)

		return ret


	@__log__(format_pattern = '{0}', abs_path_fields = [0])
	def readdir(self, path, fh):

		rel_path = self._rel_path(path)

		dirents = ['.', '..']
		if stat.S_ISDIR(os.lstat(rel_path, dir_fd = self.root_path_fd).st_mode):
			dir_fd = os.open(rel_path, os.O_RDONLY, dir_fd = self.root_path_fd)
			dirents.extend(os.listdir(dir_fd))
			os.close(dir_fd)

		return dirents


	@__log__(format_pattern = '{0}', abs_path_fields = [0])
	def readlink(self, path):

		pathname = os.readlink(self._rel_path(path), dir_fd = self.root_path_fd)

		if pathname.startswith('/'): # TODO check this ... actually required?
			return os.path.relpath(pathname, self.root_path)
		else:
			return pathname


	@__log__(format_pattern = '{0} to {1}', abs_path_fields = [0, 1])
	def rename(self, old, new):

		return os.rename(
			self._rel_path(old), self._rel_path(new),
			src_dir_fd = self.root_path_fd, dst_dir_fd = self.root_path_fd
			)


	@__log__(format_pattern = '{0}', abs_path_fields = [0])
	def rmdir(self, path):

		return os.rmdir(self._rel_path(path), dir_fd = self.root_path_fd)


	@__log__(format_pattern = '{0}', abs_path_fields = [0])
	def statfs(self, path):

		fd = os.open(self._rel_path(path), os.O_RDONLY, dir_fd = self.root_path_fd)
		stv = os.statvfs(fd)
		os.close(fd)

		return {key: getattr(stv, key) for key in self.stvfs_fields}


	@__log__(format_pattern = 'from {1} to {0}', abs_path_fields = [1])
	def symlink(self, target_path, source_path):

		target_rel_path = self._rel_path(target_path)

		res = os.symlink(source_path, target_rel_path, dir_fd = self.root_path_fd)

		uid, gid, pid = fuse_get_context()
		os.chown(target_rel_path, uid, gid, dir_fd = self.root_path_fd, follow_symlinks = False)

		return res


	@__log__(format_pattern = '{0} to {1} bytes', abs_path_fields = [0])
	def truncate(self, path, length, fh = None):

		fd = os.open(self._rel_path(path), os.O_WRONLY | os.O_TRUNC, dir_fd = self.root_path_fd)
		os.truncate(fd, length)
		os.close(fd)


	@__log__(format_pattern = '{0}', abs_path_fields = [0])
	def unlink(self, path):

		return os.unlink(self._rel_path(path), dir_fd = self.root_path_fd)


	@__log__(format_pattern = '{0}', abs_path_fields = [0])
	def utimens(self, path, times = None):

		if self.flag_nanosecond_int:
			os.utime(self._rel_path(path), ns = times, dir_fd = self.root_path_fd)
		else:
			os.utime(self._rel_path(path), times = times, dir_fd = self.root_path_fd)


	@__log__(format_pattern = '{1} bytes to {0} at offset {2}', abs_path_fields = [0], length_fields = [1])
	def write(self, path, buf, offset, fh):

		# buf is a bytestring!

		fh_loc = os.open(self._rel_path(path), os.O_WRONLY, dir_fd = self.root_path_fd)
		res = os.pwrite(fh_loc, buf, offset)
		os.close(fh_loc)

		return res
