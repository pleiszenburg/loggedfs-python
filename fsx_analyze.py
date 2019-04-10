#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import datetime
import os


def parse_iso_datestring(date_str):

	return (
		int(datetime.datetime(
			*(int(v) for v in date_str[:19].replace('-', ' ').replace(':', ' ').split(' '))
			).timestamp())
		* 10**9 + int(date_str[20:])
		)


def parse_timestamp(date_str):

	seconds, microseconds = date_str.split('.')
	seconds = int(seconds)
	microseconds = int(microseconds)

	return seconds * 10**9 + microseconds * 10**6


def parse_fs_line(line):

	payload = line[48:]
	command, payload = payload.split(' ', 1)
	if '{SUCCESS}' in payload:
		param, remaining = payload.split(' {SUCCESS} ', 1)
	else:
		param, remaining = payload.split(' {FAILURE} ', 1)

	return {
		't': parse_iso_datestring(line[:29]), # time
		'c': command, # command
		'p': param, # param
		's': 'FS' # log source
		}


def parse_fsx_line(line):

	_, payload = line.split(' ', 1)
	ts, payload = payload.split(' ', 1)
	command, param = payload.split(' ', 1)

	return {
		't': parse_timestamp(ts), # time
		'c': command, # command
		'p': param,  # param
		's': 'XX' # log source
		}


def main():

	with open('tests/test_logs/loggedfs.log', 'r', encoding = 'utf-8') as f:
		log_fs = f.read()

	with open('tests/test_logs/iotest.fsxlog', 'r', encoding = 'utf-8') as f:
		log_fsx = f.read()

	log_fs_lines = [
		parse_fs_line(line) for line in
		log_fs.replace(os.path.join(os.path.abspath('.'), 'tests/test_mount/test_child'), '').split('\n')
		if ' fsx-linux ' in line
		]

	log_fsx_lines = [
		parse_fsx_line(line) for line in
		log_fsx.split('\n')
		if line[:6].isdigit() and line[6] == ' '
		]

	print(log_fs_lines[-3])
	print(log_fsx_lines[-3])

if __name__ == '__main__':
	main()
