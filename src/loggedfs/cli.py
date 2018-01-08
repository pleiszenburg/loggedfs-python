# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	src/loggedfs/cli.py: Command line interface

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

from pprint import pformat as pf

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
	help = 'Allow every users to see the new loggedfs.'
	)
@click.option(
	'-c',
	type = click.File(mode = 'r'),
	help = 'Use the "config-file" to filter what you want to log.'
	)
@click.option(
	'-l',
	# type = click.File(mode = 'a'),
	type = click.Path(file_okay = True, dir_okay = False, resolve_path = True),
	help = ('Use the "log-file" to write logs to. If no log file is specified'
		'then logs are only written to syslog or to stdout, depending on -f.')
	)
@click.argument(
	'directory',
	type = click.Path(exists = True, file_okay = False, dir_okay = True, resolve_path = True)
	)
def cli_entry(f, p, c, l, directory):
	"""LoggedFS-python is a transparent fuse-filesystem which allows to log
	every operations that happens in the backend filesystem. Logs can be written
	to syslog, to a file, or to the standard output. LoggedFS comes with an XML
	configuration file in which you can choose exactly what you want to log and
	what you don't want to log. You can add filters on users, operations (open,
	read, write, chown, chmod, etc.), filenames and return code. Filename
	filters are regular expressions.
	"""

	click.echo(pf((
		f, p, c, l, directory
		)))

	loggedfs_factory(
		directory,
		no_daemon_bool = f,
		allow_other = p,
		loggedfs_param_dict = __process_config__(c, f),
		log_file = l
		)


def __process_config__(config_fh, no_daemon_bool):

	def __process_xml__(in_xml):
		return xmltodict.parse(in_xml)['loggedFS']

	if config_fh is not None:
		param = __process_xml__(config_fh.read())
	elif False: # TODO check /etc
		param = {} # TODO fetch from /etc
	else:
		param = {}

	param.update({'daemon': not no_daemon_bool})

	return param
