# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	src/loggedfs/filter.py: Filtering events by criteria

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
import re

import xmltodict


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def new_filter():

	return {
		'log_enabled': True,
		'log_printprocessname': True,
		'log_includes': {},
		'log_excludes': {}
		}


def new_filter_item():

	return {
		'extension': '.*',
		'uid': '*',
		'action': '.*',
		'retname': '.*',
		'command': '.*'
		}


def parse_filters(config_xml_str = None):

	config_xml_dict = xmltodict.parse(config_xml_str)['loggedFS']

	for field_new, field_old in (
		('log_enabled', '@logEnabled'),
		('log_printprocessname', '@printProcessName'),
		('log_includes', 'includes'),
		('log_excludes', 'excludes')
		):
		try:
			config_xml_dict[field_new] = config_xml_dict.pop(field_old)
		except KeyError:
			pass

	config_dict = new_filter()

	if config_xml_str is not None:
		config_dict.update(config_xml_dict)

	for f_type in ('log_includes', 'log_excludes'):
		config_dict[f_type] = _parse_filter_list_(config_dict.pop(f_type).get(f_type[4:-1], None))

	return config_dict


def _parse_filter_item_(in_item):

	ret = new_filter_item()
	tmp = {k[1:]: v for k, v in in_item.items()}
	ret.update({k: tmp[k] for k in tmp.keys() & ret.keys()})

	return ret


def _parse_filter_list_(in_list):

	if in_list is None:
		return []
	if not isinstance(in_list, list):
		return [_parse_filter_item_(in_list)]

	return [_parse_filter_item_(item) for item in in_list]


def compile_filters(include_list, exclude_list):

	if len(include_list) == 0:
		include_list.append(new_filter_item())

	return tuple(
		[_compile_filter_item_(item) for item in in_list]
		for in_list in (include_list, exclude_list)
		)


def _compile_filter_item_(in_item):

	return (
		re.compile(in_item['extension']),
		int(in_item['uid']) if in_item['uid'].isnumeric() else None,
		re.compile(in_item['action']),
		re.compile(in_item['retname']),
		re.compile(in_item['command'])
		)


def match_filters(
	abs_path, uid, action, ret_status, command,
	incl_filter_list, excl_filter_list
	):

	if len(incl_filter_list) != 0:
		included = False
		for filter_tuple in incl_filter_list:
			if _match_filter_item_(abs_path, uid, action, ret_status, command, *filter_tuple):
				included = True
				break
		if not included:
			return False

	for filter_tuple in excl_filter_list:
		if _match_filter_item_(abs_path, uid, action, ret_status, command, *filter_tuple):
			return False

	return True


def _match_filter_item_(
	abs_path, uid, action, ret_status, command,
	f_path, f_uid, f_action, f_status, f_command
	):

	return all((
		bool(f_path.match(abs_path)),
		(uid == f_uid) if isinstance(f_uid, int) else True,
		bool(f_action.match(action)),
		bool(f_status.match(ret_status)),
		bool(f_command.match(command))
		))
