# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	src/loggedfs/core.py: Module core

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
import os
import stat
import sys

from fuse import (
	FUSE,
	fuse_get_context,
	FuseOSError,
	Operations,
	UTIME_NOW,
	UTIME_OMIT,
	)
try:
	from fuse import __features__ as fuse_features
except ImportError:
	fuse_features = {}

from .filter import compile_filters
from .log import get_logger, log_msg
from .out import event
from .timing import time


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def loggedfs_factory(directory, **kwargs):

	return FUSE(
		loggedfs(
			directory,
			**kwargs
			),
		directory,
		raw_fi = True,
		nothreads = True,
		foreground = kwargs.get('fuse_foreground_bool', False),
		allow_other = kwargs.get('fuse_allowother_bool', False),
		default_permissions = kwargs.get('fuse_allowother_bool', False),
		attr_timeout = 0,
		entry_timeout = 0,
		negative_timeout = 0,
		sync_read = False, # relying on fuse.Operations class defaults?
		# max_readahead = 0, # relying on fuse.Operations class defaults?
		# direct_io = True, # relying on fuse.Operations class defaults?
		nonempty = True, # common options taken from LoggedFS
		use_ino = True # common options taken from LoggedFS
		)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CORE CLASS: Init and internal routines
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class loggedfs(Operations):


	flag_utime_omit_ok = 1


	requested_features = {
		'nanosecond_int': True,
		'utime_omit_none': True,
		'utime_now_auto': True
		}


	def __init__(self,
		directory,
		log_includes = None,
		log_excludes = None,
		log_file = None,
		log_syslog = False,
		log_enabled = True,
		log_printprocessname = True,
		log_configmsg = None,
		log_json = False,
		fuse_foreground_bool = None,
		fuse_allowother_bool = None
		):

		if log_includes is None:
			log_includes = []
		if log_excludes is None:
			log_excludes = []

		self._log_printprocessname = bool(log_printprocessname)
		self._log_json = bool(log_json)
		self.logger = get_logger('LoggedFS-python', log_enabled, log_file, log_syslog, self._log_json)

		if bool(fuse_foreground_bool):
			self.logger.info(log_msg(self._log_json, 'LoggedFS-python not running as a daemon'))
		if bool(fuse_allowother_bool):
			self.logger.info(log_msg(self._log_json, 'LoggedFS-python running as a public filesystem'))
		if bool(log_file):
			self.logger.info(log_msg(self._log_json, 'LoggedFS-python log file: %s' % log_file))

		self.logger.info(log_msg(self._log_json, 'LoggedFS-python starting at %s' % directory))
		try:
			self.root_path = directory # TODO check: permissions, existence
			self.root_path_fd = os.open(directory, os.O_RDONLY)
		except:
			self.logger.exception('Directory access failed.')
			sys.exit(1)

		self.logger.info(log_msg(self._log_json, log_configmsg))

		for flag_name in self.requested_features.keys():
			setattr(
				self,
				'flag_' + flag_name,
				self.requested_features[flag_name] and fuse_features.get(flag_name, False)
				)

		self.st_fields = [i for i in dir(os.stat_result) if i.startswith('st_')]
		self.stvfs_fields = [i for i in dir(os.statvfs_result) if i.startswith('f_')]

		self._f_incl, self._f_excl = compile_filters(log_includes, log_excludes)


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
# CORE CLASS: Filesystem & file methods - STUBS
#  ... addressing https://github.com/fusepy/fusepy/issues/81
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	def create(self, path, mode, fi = None):

		raise FuseOSError(errno.ENOSYS)


	def flush(self, path, fip):

		raise FuseOSError(errno.ENOSYS)


	def fsync(self, path, datasync, fip):

		raise FuseOSError(errno.ENOSYS) # the original loggedfs just returns 0


	def ioctl(self, path, cmd, arg, fh, flags, data):

		raise FuseOSError(errno.ENOSYS)


	def lock(self, path, fh, cmd, lock):

		raise FuseOSError(errno.ENOSYS)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CORE CLASS: Filesystem & file methods - IMPLEMENTATION
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	@event(format_pattern = '{param_path}')
	def access(self, path, mode):

		if not os.access(self._rel_path(path), mode, dir_fd = self.root_path_fd):
			raise FuseOSError(errno.EACCES)


	@event(format_pattern = '{param_path} to {param_mode}')
	def chmod(self, path, mode):

		os.chmod(self._rel_path(path), mode, dir_fd = self.root_path_fd)


	@event(format_pattern = '{param_path} to {param_uid_name}({param_uid}):{param_gid_name}({param_gid})')
	def chown(self, path, uid, gid):

		os.chown(self._rel_path(path), uid, gid, dir_fd = self.root_path_fd, follow_symlinks = False)


	@event(format_pattern = '{param_path}')
	def destroy(self, path):

		os.close(self.root_path_fd)


	@event(format_pattern = '{param_path} (fh={param_fip})')
	def getattr(self, path, fip):

		if not fip:
			try:
				st = os.lstat(self._rel_path(path), dir_fd = self.root_path_fd)
			except FileNotFoundError:
				raise FuseOSError(errno.ENOENT)
		else:
			st = os.fstat(fip.fh)

		ret_dict = {key: getattr(st, key) for key in self.st_fields}

		for key in ['st_atime', 'st_ctime', 'st_mtime']:
			if self.flag_nanosecond_int:
				ret_dict[key] = ret_dict.pop(key + '_ns')
			else:
				ret_dict.pop(key + '_ns')

		return ret_dict


	@event(format_pattern = '{param_path}')
	def init(self, path):

		pass


	@event(format_pattern = '{param_source_path} to {param_target_path}')
	def link(self, target_path, source_path):

		target_rel_path = self._rel_path(target_path)

		os.link(
			self._rel_path(source_path), target_rel_path,
			src_dir_fd = self.root_path_fd, dst_dir_fd = self.root_path_fd
			)

		uid, gid, pid = fuse_get_context()
		os.chown(target_rel_path, uid, gid, dir_fd = self.root_path_fd, follow_symlinks = False)


	@event(format_pattern = '{param_path} {param_mode}')
	def mkdir(self, path, mode):

		rel_path = self._rel_path(path)

		os.mkdir(rel_path, mode, dir_fd = self.root_path_fd)

		uid, gid, pid = fuse_get_context()

		os.chown(rel_path, uid, gid, dir_fd = self.root_path_fd, follow_symlinks = False)
		os.chmod(rel_path, mode, dir_fd = self.root_path_fd) # follow_symlinks = False


	@event(format_pattern = '{param_path} {param_mode}')
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
		os.chmod(rel_path, mode, dir_fd = self.root_path_fd) # follow_symlinks = False


	@event(format_pattern = '({param_fip}) {param_path} (fh={param_fip})')
	def open(self, path, fip):

		fip.fh = os.open(self._rel_path(path), fip.flags, dir_fd = self.root_path_fd)

		return 0


	@event(format_pattern = '{param_length} bytes from {param_path} at offset {param_offset} (fh={param_fip})')
	def read(self, path, length, offset, fip):

		ret = os.pread(fip.fh, length, offset)

		return ret


	@event(format_pattern = '{param_path}')
	def readdir(self, path, fh):

		rel_path = self._rel_path(path)

		dirents = ['.', '..']
		if stat.S_ISDIR(os.lstat(rel_path, dir_fd = self.root_path_fd).st_mode):
			dir_fd = os.open(rel_path, os.O_RDONLY, dir_fd = self.root_path_fd)
			dirents.extend(os.listdir(dir_fd))
			os.close(dir_fd)

		return dirents


	@event(format_pattern = '{param_path}')
	def readlink(self, path):

		pathname = os.readlink(self._rel_path(path), dir_fd = self.root_path_fd)

		if pathname.startswith('/'): # TODO check this ... actually required?
			return os.path.relpath(pathname, self.root_path)
		else:
			return pathname


	@event(format_pattern = '{param_path} (fh={param_fip})')
	def release(self, path, fip):

		os.close(fip.fh)


	@event(format_pattern = '{param_old_path} to {param_new_path}')
	def rename(self, old_path, new_path):

		os.rename(
			self._rel_path(old_path), self._rel_path(new_path),
			src_dir_fd = self.root_path_fd, dst_dir_fd = self.root_path_fd
			)


	@event(format_pattern = '{param_path}')
	def rmdir(self, path):

		os.rmdir(self._rel_path(path), dir_fd = self.root_path_fd)


	@event(format_pattern = '{param_path}')
	def statfs(self, path):

		fd = os.open(self._rel_path(path), os.O_RDONLY, dir_fd = self.root_path_fd)
		stv = os.statvfs(fd)
		os.close(fd)

		return {key: getattr(stv, key) for key in self.stvfs_fields}


	@event(format_pattern = 'from {param_source_path} to {param_target_path_}')
	def symlink(self, target_path_, source_path):

		target_rel_path = self._rel_path(target_path_)

		os.symlink(source_path, target_rel_path, dir_fd = self.root_path_fd)

		uid, gid, pid = fuse_get_context()
		os.chown(target_rel_path, uid, gid, dir_fd = self.root_path_fd, follow_symlinks = False)


	@event(format_pattern = '{param_path} to {param_length} bytes (fh={param_fip})')
	def truncate(self, path, length, fip = None):

		if fip is None:

			fd = os.open(self._rel_path(path), flags = os.O_WRONLY, dir_fd = self.root_path_fd)
			ret = os.ftruncate(fd, length)
			os.close(fd)
			return ret

		else:

			return os.ftruncate(fip.fh, length)


	@event(format_pattern = '{param_path}')
	def unlink(self, path):

		os.unlink(self._rel_path(path), dir_fd = self.root_path_fd)


	@event(format_pattern = '{param_path}')
	def utimens(self, path, times = None):

		def _fix_time_(atime, mtime):
			if any(val in (atime, mtime) for val in [UTIME_OMIT, None]):
				st = os.lstat(relpath, dir_fd = self.root_path_fd)
				if atime in [UTIME_OMIT, None]:
					atime = st.st_atime_ns
				if mtime in [UTIME_OMIT, None]:
					mtime = st.st_mtime_ns
			if UTIME_NOW in (atime, mtime):
				now = time.time_ns()
				if atime == UTIME_NOW:
					atime = now
				if mtime == UTIME_NOW:
					mtime = now
			return (atime, mtime)

		relpath = self._rel_path(path)

		if self.flag_nanosecond_int:
			os.utime(relpath, ns = _fix_time_(*times), dir_fd = self.root_path_fd, follow_symlinks = False)
		else:
			os.utime(relpath, times = times, dir_fd = self.root_path_fd, follow_symlinks = False)


	@event(format_pattern = '{param_buf_len} bytes to {param_path} at offset {param_offset} (fh={param_fip})')
	def write(self, path, buf, offset, fip):

		res = os.pwrite(fip.fh, buf, offset)

		return res
