# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	src/loggedfs/core.py: Module core

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

from copy import deepcopy
import errno
from functools import wraps
import grp
import logging
import os
from pprint import pformat as pf
import pwd

from fuse import (
	FUSE,
	fuse_get_context,
	FuseOSError,
	Operations
	)
import xmltodict


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
		loggedfs(directory, directory_fd, loggedfs_param_dict, log_file),
		directory,
		nothreads = True,
		foreground = no_daemon_bool,
		# allow_other = allow_other,
		nonempty = True, # common options taken from LoggedFS
		use_ino = True # common options taken from LoggedFS
		)


def __format_args__(args_list, kwargs_dict, items_list, format_func):

	for item in items_list:
		if isinstance(item, int):
			args_list[item] = format_func(args_list[item])
		elif isinstance(item, str):
			kwargs_dict[item] = format_func(kwargs_dict[item])


def __get_process_cmdline__(pid):

	try:

		f = open('/proc/%d/cmdline' % pid, 'r')
		cmdline = f.read()
		f.close()

		return cmdline

	except FileNotFoundError:

		return ''


def __get_group_name_from_gid__(gid):

	return grp.getgrgid(gid).gr_name


def __get_user_name_from_uid__(uid):

	return pwd.getpwuid(uid).pw_name


def __log__(
	format_pattern = '',
	abs_path_fields = [],
	length_fields = [],
	uid_fields = [],
	gid_fields = []
	):

	def wrapper(func):

		@wraps(func)
		def wrapped(self, *func_args, **func_kwargs):

			uid, gid, pid = fuse_get_context()
			p_cmdname = __get_process_cmdline__(pid)

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
				'%s %s' % (func.__name__, format_pattern.format(*func_args_f, **func_kwargs_f)),
				'%s',
				'[ pid = %d %s uid = %d ]' % (pid, p_cmdname, uid)
				])

			self.logger.info(log_msg % '\{...\}')

			try:

				ret_value = func(self, *func_args, **func_kwargs)

				self.logger.info(log_msg % '\{SUCCESS\}')
				return ret_value

			except FuseOSError:

				self.logger.error(log_msg % '\{FAILURE\}')
				raise FuseOSError

			except:

				self.logger.exception('Something just went terribly wrong unexpectedly ...')
				self.logger.error(log_msg % '\{FAILURE\}')
				raise FuseOSError

		return wrapped

	return wrapper


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CORE CLASS: Init and internal routines
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class loggedfs(Operations):


	def __init__(self, root, root_fd, param_dict = {}, log_file = None):

		self.root_path = root
		self.root_path_fd = root_fd
		self._p = param_dict

		log_formater = logging.Formatter('%(asctime)s (%(name)s) %(message)s')
		self.logger = logging.getLogger('LoggedFS-python')
		self.logger.setLevel(logging.DEBUG)

		ch = logging.StreamHandler()
		ch.setLevel(logging.DEBUG)
		ch.setFormatter(log_formater)
		self.logger.addHandler(ch)

		if log_file is not None:

			fh = logging.FileHandler(os.path.join(log_file))
			fh.setLevel(logging.DEBUG)
			fh.setFormatter(log_formater)
			self.logger.addHandler(fh)


	def _full_path(self, partial_path):

		if partial_path.startswith('/'):
			partial_path = partial_path[1:]
		path = os.path.join(self.root_path, partial_path)
		return path


	@staticmethod
	def _rel_path(partial_path):

		return '.' + partial_path


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CORE CLASS: Filesystem methods
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	@__log__(format_pattern = '{0}', abs_path_fields = [0])
	def access(self, path, mode):

		rel_path = self._rel_path(path)
		if not os.access(rel_path, mode):
			raise FuseOSError(errno.EACCES)


	@__log__(format_pattern = '{0} to {1}', abs_path_fields = [0])
	def chmod(self, path, mode):

		return os.chmod(self._rel_path(path), mode)


	@__log__(format_pattern = '{0} to {1}:{2}', abs_path_fields = [0], uid_fields = [1], gid_fields = [2])
	def chown(self, path, uid, gid):

		return os.chown(self._rel_path(path), uid, gid)


	@__log__(format_pattern = '{0}', abs_path_fields = [0])
	def getattr(self, path, fh = None):

		rel_path = self._rel_path(path)

		try:

			st = os.lstat(rel_path)
			return {key: getattr(st, key) for key in (
				'st_atime',
				'st_blocks',
				'st_ctime',
				'st_gid',
				'st_mode',
				'st_mtime',
				'st_nlink',
				'st_size',
				'st_uid'
				)}

		except (FileNotFoundError, OSError):

			raise FuseOSError


	@__log__(format_pattern = '{0}')
	def init(self, path):

		os.fchdir(self.root_path_fd)
		os.close(self.root_path_fd)


	@__log__(format_pattern = '{1} to {0}', abs_path_fields = [0, 1])
	def link(self, target_path, source_path):

		# TODO Check order of arguments, possible bug in original LoggedFS

		# PYTHON:
		# 	os.link(src, dst, *, src_dir_fd=None, dst_dir_fd=None, follow_symlinks=True)
		# 	Create a hard link to a file.
		# 	(From symlink: Create a symbolic link pointing to src named dst.)
		# FUSEPY:
		# 	def link(self, target, source):
		# 		'creates a hard link `target -> source` (e.g. ln source target)'

		target_rel_path = self._rel_path(target_path)

		res = os.link(self._rel_path(source_path), target_rel_path)

		uid, gid, pid = fuse_get_context()
		os.lchown(target_rel_path, uid, gid)

		return res


	@__log__(format_pattern = '{0} {1}', abs_path_fields = [0])
	def mkdir(self, path, mode):

		rel_path = self._rel_path(path)

		res = os.mkdir(rel_path, mode)

		uid, gid, pid = fuse_get_context()
		os.lchown(rel_path, uid, gid)

		return res


	@__log__(format_pattern = '{0} {1}', abs_path_fields = [0])
	def mknod(self, path, mode, dev):

		rel_path = self._rel_path(path)

		res = os.mknod(rel_path, mode, dev)

		uid, gid, pid = fuse_get_context()
		os.lchown(rel_path, uid, gid)

		return res


	@__log__(format_pattern = '{0}', abs_path_fields = [0])
	def readdir(self, path, fh):

		rel_path = self._rel_path(path)

		dirents = ['.', '..']
		if os.path.isdir(rel_path):
			dirents.extend(os.listdir(rel_path))

		# TODO
		# https://github.com/rflament/loggedfs/blob/master/src/loggedfs.cpp#L248
		# The original loggedfs does some inode number stuff here

		return dirents


	@__log__(format_pattern = '{0}', abs_path_fields = [0])
	def readlink(self, path):

		pathname = os.readlink(self._rel_path(path))

		if pathname.startswith('/'): # TODO check this ... actually required?
			return os.path.relpath(pathname, self.root_path)
		else:
			return pathname


	@__log__(format_pattern = '{0} to {1}', abs_path_fields = [0, 1])
	def rename(self, old, new):

		return os.rename(self._rel_path(old), self._rel_path(new))


	@__log__(format_pattern = '{0}', abs_path_fields = [0])
	def rmdir(self, path):

		return os.rmdir(self._rel_path(path))


	@__log__(format_pattern = '{0}', abs_path_fields = [0])
	def statfs(self, path):

		stv = os.statvfs(self._rel_path(path))
		return {key: getattr(stv, key) for key in (
			'f_bavail',
			'f_bfree',
			'f_blocks',
			'f_bsize',
			'f_favail',
			'f_ffree',
			'f_files',
			'f_flag',
			'f_frsize',
			'f_namemax'
			)}


	@__log__(format_pattern = 'from {1} to {0}', abs_path_fields = [1])
	def symlink(self, target_path, source_path):

		# TODO Check order of arguments, possible bug in original LoggedFS

		# PYTHON:
		# 	os.symlink(src, dst, target_is_directory=False, *, dir_fd=None)
		# 	Create a symbolic link pointing to src named dst.
		# FUSEPY:
		# 	def symlink(self, target, source):
		# 		'creates a symlink `target -> source` (e.g. ln -s source target)'

		target_rel_path = self._rel_path(target_path)

		res = os.symlink(source_path, target_rel_path)

		uid, gid, pid = fuse_get_context()
		os.lchown(target_rel_path, uid, gid)

		return res


	@__log__(format_pattern = '{0}', abs_path_fields = [0])
	def unlink(self, path):

		return os.unlink(self._rel_path(path))


	@__log__(format_pattern = '{0}', abs_path_fields = [0])
	def utimens(self, path, times = None):

		return os.utime(self._rel_path(path), times)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CORE CLASS: File methods
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	@__log__(format_pattern = '({1}) {0}', abs_path_fields = [0])
	def open(self, path, flags):

		return os.open(self._rel_path(path), flags)


	@__log__(format_pattern = '({1}) {0}', abs_path_fields = [0])
	def create(self, path, mode, fi = None):

		# NOT provided by original LoggedFS

		uid, gid, pid = fuse_get_context()
		rel_path = self._rel_path(path)
		fd = os.open(rel_path, os.O_WRONLY | os.O_CREAT, mode)
		os.chown(rel_path, uid, gid)
		return fd


	@__log__(format_pattern = '{0}', abs_path_fields = [0])
	def flush(self, path, fh):

		# NOT provided by original LoggedFS

		return os.fsync(fh)


	@__log__(format_pattern = '{0}', abs_path_fields = [0])
	def fsync(self, path, fdatasync, fh):

		# The original LoggedFS has a stub, only:
		# "This method is optional and can safely be left unimplemented"

		return self.flush(path, fh)


	@__log__(format_pattern = '{1} bytes from {0} at offset {2}', abs_path_fields = [0])
	def read(self, path, length, offset, fh):

		os.lseek(fh, offset, os.SEEK_SET)
		return os.read(fh, length)


	@__log__(format_pattern = '{0}', abs_path_fields = [0])
	def release(self, path, fh):

		# The original LoggedFS has a stub, only:
		# "This method is optional and can safely be left unimplemented"

		return os.close(fh)


	@__log__(format_pattern = '{0} to {1} bytes', abs_path_fields = [0])
	def truncate(self, path, length, fh = None):

		with open(self._rel_path(path), 'r+') as f:
			f.truncate(length)


	@__log__(format_pattern = '{1} bytes to {0} at offset {2}', abs_path_fields = [0], length_fields = [1])
	def write(self, path, buf, offset, fh):

		os.lseek(fh, offset, os.SEEK_SET)
		return os.write(fh, buf)
