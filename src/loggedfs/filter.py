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
		'@logEnabled': True,
		'@printProcessName': True,
		'includes': {},
		'excludes': {}
		}


def parse_filters(config_xml_str = None):

	config_dict = new_filter()

	if config_xml_str is not None:
		config_dict.update(xmltodict.parse(config_xml_str)['loggedFS'])

	for f_type in ['includes', 'excludes']:
		config_dict[f_type] = _parse_filter_list_(config_dict[f_type].get(f_type[:-1], None))

	return config_dict


def _parse_filter_item_(in_item):
	return {
		'extension': in_item['@extension'],
		'uid': in_item['@uid'],
		'action': in_item['@action'],
		'retname': in_item['@retname']
		}


def _parse_filter_list_(in_list):
	if in_list is None:
		return []
	if not isinstance(in_list, list):
		return [_parse_filter_item_(in_list)]
	return [_parse_filter_item_(item) for item in in_list]


def compile_filters(include_list, exclude_list):

	if len(include_list) == 0:
		include_list.append({
			'extension': '.*',
			'uid': '*',
			'action': '.*',
			'retname': '.*'
			})

	return tuple(
		[_compile_filter_item_(item) for item in in_list]
		for in_list in (include_list, exclude_list)
		)


def _compile_filter_item_(in_item):

	return (
		re.compile(in_item['extension']),
		int(in_item['uid']) if in_item['uid'].isnumeric() else None,
		re.compile(in_item['action']),
		re.compile(in_item['retname'])
		)


def match_filters(
	abs_path, uid, action, ret_status,
	incl_filter_list, excl_filter_list
	):

	if len(incl_filter_list) != 0:
		included = False
		for filter_tuple in incl_filter_list:
			if _match_filter_item_(abs_path, uid, action, ret_status, *filter_tuple):
				included = True
				break
		if not included:
			return False

	for filter_tuple in excl_filter_list:
		if _match_filter_item_(abs_path, uid, action, ret_status, *filter_tuple):
			return False

	return True


def _match_filter_item_(
	abs_path, uid, action, ret_status,
	f_path, f_uid, f_action, f_status
	):

	return all((
		bool(f_path.match(abs_path)),
		(uid == f_uid) if isinstance(f_uid, int) else True,
		bool(f_action.match(action)),
		bool(f_status.match(ret_status))
		))
