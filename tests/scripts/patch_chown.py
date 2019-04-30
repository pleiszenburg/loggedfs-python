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


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def patch_script(in_data):

	# TODO

	return in_data


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
