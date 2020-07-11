# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	src/loggedfs/_core/filter.py: Filtering events by criteria

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

from collections import OrderedDict
import re

import xmltodict

from .defaults import LOG_ENABLED_DEFAULT, LOG_PRINTPROCESSNAME_DEFAULT


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# FILTER FIELD CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class filter_field_class:


	def __init__(self, name, value):

		self._name_is_func = hasattr(name, '__call__')

		if not self._name_is_func and not isinstance(name, str):
			raise TypeError('name must either be callable or a string')
		if not hasattr(value, '__call__'):
			raise TypeError('value must either be callable')

		self._name = name
		self._value = value


	def __repr__(self):

		return '<filter_field name="%s" value="%s"/>' % (
			self._name if not self._name_is_func else '{callable:' + getattr(self._name, '__name__', 'NONAME') + '}',
			'{callable:' + getattr(self._value, '__name__', 'NONAME') + '}'
			)


	@property
	def name_is_func(self):

		return self._name_is_func


	@property
	def name(self):

		return self._name


	@property
	def value(self):

		return self._value


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# FILTER ITEM CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class filter_item_class:


	def __init__(self, fields_list):

		if not isinstance(fields_list, list):
			raise TypeError('fields_list must be of type list')
		if len(fields_list) == 0:
			raise ValueError('at least one field is required for setting up a filter')
		if any((not isinstance(item, filter_field_class) for item in fields_list)):
			raise TypeError('fields_list must only contain type filter_field_class')

		self._fields_list = fields_list
		self._field_names = {field.name for field in self._fields_list if not field.name_is_func}
		self._field_nofuncs = {field for field in self._fields_list if not field.name_is_func}
		self._field_funcs = {field for field in self._fields_list if field.name_is_func}


	def __repr__(self):

		return (
			'<filter_item>\n\t' +
			'\n\t'.join((repr(field) for field in self._fields_list))
			+ '\n</filter_item>'
			)


	def match(self, event_dict):

		if not isinstance(event_dict, dict):
			raise TypeError('event_dict must be of type dict')

		if len(self._field_names - event_dict.keys()) > 0:
			return False

		if any((not field.value(event_dict[field.name]) for field in self._field_nofuncs)):
			return False

		for field in self._field_funcs:
			key_match = None
			for key in event_dict.keys():
				if field.name(key):
					key_match = key
					break
			if key_match is None:
				return False
			if not field.value(event_dict[key_match]):
				return False

		return True


	@staticmethod
	def _from_xmldict(xml_dict):

		if not isinstance(xml_dict, OrderedDict) and not isinstance(xml_dict, dict):
			raise TypeError('can not construct filter item from non-dict type')
		if any((not isinstance(item, str) for item in xml_dict.keys())):
			raise TypeError('non-string key in dict')
		if any((not isinstance(item, str) for item in xml_dict.values())):
			raise TypeError('non-string value in dict')

		fields_list = []

		try:
			if xml_dict['@retname'] == 'SUCCESS':
				fields_list.append(filter_field_class('status', lambda x: x == True))
			elif xml_dict['@retname'] == 'FAILURE':
				fields_list.append(filter_field_class('status', lambda x: x == False))
			elif xml_dict['@retname'] != '.*':
				raise ValueError('unexpected value for "retname"')
		except KeyError:
			pass

		try:
			if xml_dict['@extension'] != '.*':
				fields_list.append(filter_field_class(
					lambda x: x.endswith('path'), re.compile(xml_dict['@extension']).match
					))
		except KeyError:
			pass

		try:
			if xml_dict['@uid'].isdecimal():
				fields_list.append(filter_field_class(
					'proc_uid', lambda x: x == int(xml_dict['@uid'])
					))
			elif xml_dict['@uid'] != '*':
				raise ValueError('unexpected value for "uid"')
		except KeyError:
			pass

		try:
			if xml_dict['@action'] != '.*':
				fields_list.append(filter_field_class(
					'action', re.compile(xml_dict['@action']).match
					))
		except KeyError:
			pass

		try:
			if xml_dict['@command'] != '.*':
				fields_list.append(filter_field_class(
					'proc_cmd', re.compile(xml_dict['@command']).match
					))
		except KeyError:
			pass

		if len(fields_list) > 0:
			return filter_item_class(fields_list)
		else:
			return None


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# FILTER PIPELINE CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class filter_pipeline_class:


	VALID_XML_BLOCKS = ('@logEnabled', '@printProcessName', 'includes', 'excludes')


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


	def __repr__(self):

		return (
			'<filter_pipeline>\n'
			+ '\t<include>\n'
			+ '\n'.join( (
				'\n'.join(('\t\t' + line for line in repr(item).split('\n') ))
				for item in self._include_list)
				) + ('\n' if len(self._include_list) > 0 else '')
			+ '\t</include>\n'
			+ '\t<exclude>\n'
			+ '\n'.join( (
				'\n'.join(('\t\t' + line for line in repr(item).split('\n') ))
				for item in self._exclude_list)
				) + ('\n' if len(self._exclude_list) > 0 else '')
			+ '\t</exclude>\n'
			+ '<filter_pipeline>'
			)


	def match(self, event_dict):

		if not isinstance(event_dict, dict):
			raise TypeError('event_dict must be of type dict')

		if len(self._include_list) > 0:
			if not any((item.match(event_dict) for item in self._include_list)):
				return False

		if any((item.match(event_dict) for item in self._exclude_list)):
			return False

		return True


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

		log_enabled = xml_dict.pop('@logEnabled', None)
		if log_enabled is None:
			log_enabled = LOG_ENABLED_DEFAULT
		else:
			log_enabled = log_enabled.lower() == 'true'
		log_printprocessname = xml_dict.pop('@printProcessName', None)
		if log_printprocessname is None:
			log_printprocessname = LOG_PRINTPROCESSNAME_DEFAULT
		else:
			log_printprocessname = log_printprocessname.lower() == 'true'

		group_list = []
		for f_type in ('includes', 'excludes'):
			group = xml_dict.pop(f_type, None)
			if group is None:
				group_list.append([])
				continue
			if not isinstance(group, OrderedDict) and not isinstance(group, dict):
				raise TypeError('malformed XML tree for %s' % f_type)
			group = group.get(f_type[:-1], None)
			if group is None:
				group_list.append([])
				continue
			if not any((
				isinstance(group, list), isinstance(group, OrderedDict), isinstance(group, dict)
				)):
				raise TypeError('malformed XML tree for %s' % f_type[:-1])
			if isinstance(group, list):
				tmp = [filter_item_class._from_xmldict(item) for item in group]
				tmp = [item for item in tmp if item is not None]
				group_list.append(tmp)
			else:
				tmp = filter_item_class._from_xmldict(group)
				if tmp is not None:
					group_list.append([tmp])
				else:
					group_list.append([])

		return log_enabled, log_printprocessname, filter_pipeline_class(*group_list)
