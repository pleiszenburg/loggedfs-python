# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	src/loggedfs/cli.py: Command line interface

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

from collections import OrderedDict

from .core import loggedfs_factory

import click
import xmltodict


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
	# type = click.File(mode = 'a'),
	type = click.Path(file_okay = True, dir_okay = False, resolve_path = True),
	help = ('Use the "log-file" to write logs to.')
	)
@click.argument(
	'directory',
	type = click.Path(exists = True, file_okay = False, dir_okay = True, resolve_path = True)
	)
def cli_entry(f, p, c, s, l, directory):
	"""LoggedFS-python is a transparent fuse-filesystem which allows to log
	every operations that happens in the backend filesystem. Logs can be written
	to syslog, to a file, or to the standard output. LoggedFS comes with an XML
	configuration file in which you can choose exactly what you want to log and
	what you don't want to log. You can add filters on users, operations (open,
	read, write, chown, chmod, etc.), filenames and return code. Filename
	filters are regular expressions.
	"""

	loggedfs_factory(
		directory,
		**__process_config__(c, l, s, f, p)
		)


def __process_config__(
	config_fh,
	log_file,
	log_syslog_off,
	fuse_foreground_bool,
	fuse_allowother_bool
	):

	def proc_filter_item(in_item):
		return {
			'extension': in_item['@extension'],
			'uid': in_item['@uid'],
			'action': in_item['@action'],
			'retname': in_item['@retname']
			}

	def proc_filter_list(in_list):
		if in_list is None:
			return []
		if not isinstance(in_list, list):
			return [proc_filter_item(in_list)]
		return [proc_filter_item(item) for item in in_list]

	config_dict = OrderedDict({
		'@logEnabled': True,
		'@printProcessName': True,
		'includes': {},
		'excludes': {}
		})

	config_file = None
	if config_fh is not None:
		config_file = config_fh.name
		config_dict.update(xmltodict.parse(config_fh.read())['loggedFS'])
		config_fh.close()

	for f_type in ['includes', 'excludes']:
		config_dict[f_type] = proc_filter_list(config_dict[f_type].get(f_type[:-1], None))

	return {
		'log_includes': config_dict['includes'],
		'log_excludes': config_dict['excludes'],
		'log_file': log_file,
		'log_syslog': not log_syslog_off,
		'log_configmsg': 'LoggedFS-python using configuration file %s' % config_file,
		'log_enabled': config_dict['@logEnabled'],
		'log_printprocessname': config_dict['@printProcessName'],
		'fuse_foreground_bool': fuse_foreground_bool,
		'fuse_allowother_bool': fuse_allowother_bool
		}
