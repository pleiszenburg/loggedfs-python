#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import os

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CONST
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

TEST_NAME = '00.t'
TEST_PATH = 'tests/test_suite/tests/chown'
TEST_BACKUP = 'tests/scripts'

PATCH_ROUTINES = [
	'expect',
	'jexpect',
	'test_check'
	]


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def patch_script(in_str):

	old_lines = in_str.split('\n')
	new_lines = []

	test_count = 1
	for line in old_lines:
		tabs_num = len(line) - len(line.lstrip('\t'))
		if any((line.lstrip('\t').startswith(item) for item in PATCH_ROUTINES)):
			new_lines.append('\t' * tabs_num + 'todo Linux "PJD COUNT %d"' % test_count)
			test_count += 1
		new_lines.append(line)

	return '\n'.join(new_lines) + '\n'


def main():

	if not os.path.exists(os.path.join(TEST_BACKUP, TEST_NAME)):
		with open(os.path.join(TEST_PATH, TEST_NAME), 'r') as f:
			data = f.read()
		with open(os.path.join(TEST_BACKUP, TEST_NAME), 'w') as f:
			f.write(data)

	with open(os.path.join(TEST_BACKUP, TEST_NAME), 'r') as f:
		data = f.read()
	data = patch_script(data)
	with open(os.path.join(TEST_PATH, TEST_NAME), 'w') as f:
		f.write(data)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ENTRY POINT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if __name__ == '__main__':

	main()
