# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	src/loggedfs/_core/filter.py: Filtering events by criteria

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
# FILTER ITEM CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class filter_item_class:


	def __init__(self, **fields):

		pass


	def match_all(self):

		pass


	def match_any(self):

		pass


	@staticmethod
	def _from_xmldict(xml_dict):

		if not ininstance(xml_dict, OrderedDict) and not ininstance(xml_dict, dict):
			raise TypeError('can not construct filter item from non-dict type')

		if any((not isinstance(item, str) for item in xml_dict.keys())):
			raise TypeError('non-string key in dict')
		if any((not isinstance(item, str) for item in xml_dict.values())):
			raise TypeError('non-string value in dict')

		fields_dict = {}

		try:
			if xml_dict['retname'] == 'SUCCESS':
				fields_dict['status'] = True
			elif xml_dict['retname'] == 'FAILURE':
				fields_dict['status'] = False
			elif xml_dict['retname'] != '.*':
				raise ValueError('unexpected value for "retname"')
		except KeyError:
			pass

		try:
			fields_dict['_abspath'] = xml_dict['extension']
		except KeyError:
			pass

		try:
			if xml_dict['uid'].isdecimal():
				fields_dict['proc_uid'] = int(xml_dict['uid'])
			elif xml_dict['uid'] != '*':
				raise ValueError('unexpected value for "uid"')
		except KeyError:
			pass

		try:
			fields_dict['action'] = xml_dict['action']
		except KeyError:
			pass

		try:
			fields_dict['command'] = xml_dict['command']
		except KeyError:
			pass

		return filter_item_class(**fields_dict)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# FILTER PIPELINE CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class filter_pipeline_class:


	VALID_XML_BLOCKS = ('@logEnabled', '@printProcessName', 'includes', 'excludes')
	# VALID_CFG_KEYS = ('log_enabled', 'log_printprocessname', 'log_includes', 'log_excludes')


	def __init__(self, include_list = None, exclude_list = None):

		if include_list is None:
			include_list = []
		if exclude_list is None:
			exclude_list = []

		if not isinstance(include_list, list):
			raise TypeError('include_list must have type list')
		if not isinstance(exclude_list, list):
			raise TypeError('exclude_list must have type list')
		if any((not isinstance(item, filter_item_class) for item in include_list)):
			raise TypeError('include_list must only contain type filter_item_class')
		if any((not isinstance(item, filter_item_class) for item in exclude_list)):
			raise TypeError('exclude_list must only contain type filter_item_class')

		self._include_list = include_list
		self._exclude_list = exclude_list


	@staticmethod
	def from_xmlstring(xml_str):
		"""Parse XML configuration string and return instance of filter_pipeline_class.
		Compatibility layer for original LoggedFS XML configuration file format.
		"""

		if not isinstance(xml_str, str):
			raise TypeError('xml_str must have type str')
		if len(xml_str) == 0:
			raise ValueError('xml_str must not be empty')
		try:
			xml_dict = xmltodict.parse(xml_str)
		except:
			raise ValueError('xml_str does not contain valid XML')
		try:
			xml_dict = xml_dict['loggedFS']
		except KeyError:
			raise ValueError('XML tree does not have loggedFS top-level tag')
		if len(xml_dict.keys() - set(filter_pipeline_class.VALID_XML_BLOCKS)) > 0:
			raise ValueError('unexpected tags and/or parameters in XML tree')

		log_enabled = xml_dict.pop('@logEnabled', 'true').lower() == 'true'
		log_printprocessname = xml_dict.pop('@printProcessName', 'true').lower() == 'true'

		group_list = []
		for f_type in ('includes', 'excludes'):
			group = xml_dict.pop(f_type, None)
			if group is None:
				group_list.append([])
				continue
			if not ininstance(group, OrderedDict) and not ininstance(group, dict):
				raise TypeError('malformed XML tree for %s' % f_type)
			group = group.get(f_type[:-1], None)
			if group is None:
				group_list.append([])
				continue
			if not ininstance(group, list):
				raise TypeError('malformed XML tree for %s' % f_type[:-1])
			group_list.append([filter_item_class._from_xmldict(item) for item in group])

		return log_enabled, log_printprocessname, filter_pipeline_class(*group_list)


	def match(self, *args):

		pass


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
