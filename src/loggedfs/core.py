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
from pprint import pformat as pf

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


def __get_process_cmdline__(pid):

	try:

		f = open('/proc/%d/cmdline' % pid, 'r')
		cmdline = f.read()
		f.close()

		return cmdline

	except FileNotFoundError:

		return ''


def __log__(format_pattern = '', abs_path_fields = []):

	def wrapper(func):

		@wraps(func)
		def wrapped(self, *func_args, **func_kwargs):

			uid, gid, pid = fuse_get_context()
			p_cmdname = __get_process_cmdline__(pid)

			log_msg = ' '.join([
				'%s %s' % (func.__name__, format_pattern.format(*func_args, **func_kwargs)),
				'%s',
				'[ pid = %d %s uid = %d ]' % (pid, p_cmdname, uid)
				])

			try:
				self.logger.info(log_msg % '...')
				ret_value = func(self, *func_args, **func_kwargs)
				self.logger.info(log_msg % '\{SUCCESS\}')
			except FuseOSError:
				ret_value = None
				self.logger.error(log_msg % '\{FAILURE\}')
				raise FuseOSError
			except:
				ret_value = None
				self.logger.exception('Something just went terribly wrong unexpectedly ...')
				self.logger.error(log_msg % '\{FAILURE\}')
				raise FuseOSError

			return ret_value

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


	def _rel_path(self, partial_path):

		return '.' + partial_path


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CORE CLASS: Filesystem methods
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	@__log__('{0}', [0])
	def access(self, path, mode): # HACK

		rel_path = self._rel_path(path)
		if not os.access(rel_path, mode):
			raise FuseOSError(errno.EACCES)


	@__log__('{0} {1}')
	def chmod(self, path, mode):

		full_path = self._full_path(path)
		return os.chmod(full_path, mode)


	@__log__('{0} {1} {2}')
	def chown(self, path, uid, gid):

		full_path = self._full_path(path)
		return os.chown(full_path, uid, gid)


	@__log__('{0}', [0])
	def getattr(self, path, fh = None): # HACK

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


	@__log__('{0}')
	def init(self, path): # HACK

		os.fchdir(self.root_path_fd)
		os.close(self.root_path_fd)


	@__log__('{0} {1}')
	def link(self, target, name):

		return os.link(self._full_path(name), self._full_path(target))


	@__log__('{0} {1}')
	def mkdir(self, path, mode):

		return os.mkdir(self._full_path(path), mode)


	@__log__('{0} {1} {2}')
	def mknod(self, path, mode, dev):

		return os.mknod(self._full_path(path), mode, dev)


	@__log__('{0}', [0])
	def readdir(self, path, fh): # HACK

		rel_path = self._rel_path(path)

		dirents = ['.', '..']
		if os.path.isdir(rel_path):
			dirents.extend(os.listdir(rel_path))
		for r in dirents:
			yield r


	@__log__('{0}', [0])
	def readlink(self, path): # HACK

		pathname = os.readlink(self._rel_path(path))

		if pathname.startswith('/'): # TODO check this ... actually required?
			return os.path.relpath(pathname, self.root_path)
		else:
			return pathname


	@__log__('{0} {1}')
	def rename(self, old, new):

		return os.rename(self._full_path(old), self._full_path(new))


	@__log__('{0}')
	def rmdir(self, path):

		full_path = self._full_path(path)
		return os.rmdir(full_path)


	@__log__('{0}')
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


	@__log__('{0} {1}')
	def symlink(self, name, target):

		# TODO Check order of arguments, possible bug in original LoggedFS
		return os.symlink(target, self._full_path(name))


	@__log__('{0}')
	def unlink(self, path):

		return os.unlink(self._full_path(path))


	@__log__('{0} {1}')
	def utimens(self, path, times = None):

		return os.utime(self._full_path(path), times)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CORE CLASS: File methods
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	@__log__('{0} {1}')
	def open(self, path, flags):

		full_path = self._full_path(path)
		return os.open(full_path, flags)


	@__log__('{0} {1} {2}')
	def create(self, path, mode, fi = None):

		uid, gid, pid = fuse_get_context()
		full_path = self._full_path(path)
		fd = os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)
		os.chown(full_path, uid, gid)
		return fd


	@__log__('{0} {1}')
	def flush(self, path, fh):

		return os.fsync(fh)


	@__log__('{0} {1} {2}')
	def fsync(self, path, fdatasync, fh):

		return self.flush(path, fh)


	@__log__('{0} {1} {2} {3}')
	def read(self, path, length, offset, fh):

		os.lseek(fh, offset, os.SEEK_SET)
		return os.read(fh, length)


	@__log__('{0} {1}')
	def release(self, path, fh):

		return os.close(fh)


	@__log__('{0} {1} {2}')
	def truncate(self, path, length, fh = None):

		full_path = self._full_path(path)
		with open(full_path, 'r+') as f:
			f.truncate(length)


	@__log__('{0} {1} {2} {3}')
	def write(self, path, buf, offset, fh):

		os.lseek(fh, offset, os.SEEK_SET)
		return os.write(fh, buf)
