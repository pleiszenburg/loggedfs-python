# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	src/loggedfs/core.py: Module core classes

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

import errno
from functools import wraps
import logging
import os

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
	loggedfs_param_dict = {}
	):

	return FUSE(
		loggedfs_class(directory, loggedfs_param_dict),
		directory,
		nothreads = True,
		foreground = no_daemon_bool,
		allow_other = allow_other
		)


def __log__(format_pattern = None):

	def wrapper(func):

		@wraps(func)
		def wrapped(self, *func_args, **func_kwargs):

			ret_value = func(self, *func_args, **func_kwargs)
			# use format_pattern here

			return ret_value

		return wrapped

	return wrapper


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CORE CLASS: Init and internal routines
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class loggedfs_class(Operations):


	def __init__(self, root, param_dict = {}):

		self.root_path = root
		self._p = param_dict


	def _full_path(self, partial_path):

		if partial_path.startswith('/'):
			partial_path = partial_path[1:]
		path = os.path.join(self.root_path, partial_path)
		return path


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CORE CLASS: Filesystem methods
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	@__log__()
	def access(self, path, mode):

		full_path = self._full_path(path)
		if not os.access(full_path, mode):
			raise FuseOSError(errno.EACCES)


	@__log__()
	def chmod(self, path, mode):

		full_path = self._full_path(path)
		return os.chmod(full_path, mode)


	@__log__()
	def chown(self, path, uid, gid):

		full_path = self._full_path(path)
		return os.chown(full_path, uid, gid)


	@__log__()
	def getattr(self, path, fh = None):

		full_path = self._full_path(path)
		st = os.lstat(full_path)
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


	@__log__()
	def link(self, target, name):

		return os.link(self._full_path(name), self._full_path(target))


	@__log__()
	def mkdir(self, path, mode):

		return os.mkdir(self._full_path(path), mode)


	@__log__()
	def mknod(self, path, mode, dev):

		return os.mknod(self._full_path(path), mode, dev)


	@__log__()
	def readdir(self, path, fh):

		full_path = self._full_path(path)

		dirents = ['.', '..']
		if os.path.isdir(full_path):
			dirents.extend(os.listdir(full_path))
		for r in dirents:
			yield r


	@__log__()
	def readlink(self, path):

		pathname = os.readlink(self._full_path(path))
		if pathname.startswith('/'):
			return os.path.relpath(pathname, self.root_path)
		else:
			return pathname


	@__log__()
	def rename(self, old, new):

		return os.rename(self._full_path(old), self._full_path(new))


	@__log__()
	def rmdir(self, path):

		full_path = self._full_path(path)
		return os.rmdir(full_path)


	@__log__()
	def statfs(self, path):

		full_path = self._full_path(path)
		stv = os.statvfs(full_path)
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


	@__log__()
	def symlink(self, name, target):

		# TODO Check order of arguments, possible bug in original LoggedFS
		return os.symlink(target, self._full_path(name))


	@__log__()
	def unlink(self, path):

		return os.unlink(self._full_path(path))


	@__log__()
	def utimens(self, path, times = None):

		return os.utime(self._full_path(path), times)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CORE CLASS: File methods
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	@__log__()
	def open(self, path, flags):

		full_path = self._full_path(path)
		return os.open(full_path, flags)


	@__log__()
	def create(self, path, mode, fi = None):

		uid, gid, pid = fuse_get_context()
		full_path = self._full_path(path)
		fd = os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)
		os.chown(full_path, uid, gid)
		return fd


	@__log__()
	def flush(self, path, fh):

		return os.fsync(fh)


	@__log__()
	def fsync(self, path, fdatasync, fh):

		return self.flush(path, fh)


	@__log__()
	def read(self, path, length, offset, fh):

		os.lseek(fh, offset, os.SEEK_SET)
		return os.read(fh, length)


	@__log__()
	def release(self, path, fh):

		return os.close(fh)


	@__log__()
	def truncate(self, path, length, fh = None):

		full_path = self._full_path(path)
		with open(full_path, 'r+') as f:
			f.truncate(length)


	@__log__()
	def write(self, path, buf, offset, fh):

		os.lseek(fh, offset, os.SEEK_SET)
		return os.write(fh, buf)
