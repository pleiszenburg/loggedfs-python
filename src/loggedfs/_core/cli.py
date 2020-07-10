# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	src/loggedfs/_core/cli.py: Command line interface

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

import click

from .defaults import LOG_ENABLED_DEFAULT, LOG_PRINTPROCESSNAME_DEFAULT
from .fs import loggedfs_factory
from .filter import filter_pipeline_class


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINE
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@click.command()
@click.option(
	'-f',
	is_flag = True,
	help = 'Do not start as a daemon. Write logs to stdout if no log file is specified.'
	)
@click.option(
	'-p',
	is_flag = True,
	help = 'Allow every user to see the new loggedfs.'
	)
@click.option(
	'-c',
	type = click.File(mode = 'r'),
	help = 'Use the "config-file" to filter what you want to log.'
	)
@click.option(
	'-s',
	is_flag = True,
	help = 'Deactivate logging to syslog.'
	)
@click.option(
	'-l',
	type = click.Path(file_okay = True, dir_okay = False, resolve_path = True),
	help = ('Use the "log-file" to write logs to.')
	)
@click.option(
	'-j', '--json',
	is_flag = True,
	help = 'Format output as JSON instead of traditional loggedfs format.'
	)
@click.option(
	'-b', '--buffers',
	is_flag = True,
	help = 'Include read/write-buffers (compressed, BASE64) in log.'
	)
@click.option(
	'--lib',
	is_flag = True,
	help = 'Run in library mode. DO NOT USE THIS FROM THE COMMAND LINE!',
	hidden = True
	)
@click.option(
	'-m', '--only-modify-operations',
	is_flag = True,
	help = 'Exclude logging of all operations that can not cause changes in the filesystem. Convenience flag for accelerated logging.'
	)
@click.argument(
	'directory',
	type = click.Path(exists = True, file_okay = False, dir_okay = True, resolve_path = True)
	)
def cli_entry(f, p, c, s, l, json, buffers, lib, only_modify_operations, directory):
	"""LoggedFS-python is a transparent fuse-filesystem which allows to log
	every operation that happens in the backend filesystem. Logs can be written
	to syslog, to a file, or to the standard output. LoggedFS-python allows to specify an XML
	configuration file in which you can choose exactly what you want to log and
	what you don't want to log. You can add filters on users, operations (open,
	read, write, chown, chmod, etc.), filenames, commands and return code.
	"""

	loggedfs_factory(
		directory,
		**__process_config__(c, l, s, f, p, json, buffers, lib, only_modify_operations)
		)


def __process_config__(
	config_fh,
	log_file,
	log_syslog_off,
	fuse_foreground,
	fuse_allowother,
	log_json,
	log_buffers,
	lib_mode,
	log_only_modify_operations
	):

	if config_fh is not None:
		config_data = config_fh.read()
		config_fh.close()
		(
			log_enabled, log_printprocessname, filter_obj
			) = filter_pipeline_class.from_xmlstring(config_data)
		config_file = config_fh.name
	else:
		log_enabled = LOG_ENABLED_DEFAULT
		log_printprocessname = LOG_PRINTPROCESSNAME_DEFAULT
		filter_obj = filter_pipeline_class()
		config_file = None

	return {
		'fuse_foreground': fuse_foreground,
		'fuse_allowother': fuse_allowother,
		'lib_mode': lib_mode,
		'log_buffers': log_buffers,
		'_log_configfile' : config_file,
		'log_enabled': log_enabled,
		'log_file': log_file,
		'log_filter': filter_obj,
		'log_json': log_json,
		'log_only_modify_operations': log_only_modify_operations,
		'log_printprocessname': log_printprocessname,
		'log_syslog': not log_syslog_off
		}
