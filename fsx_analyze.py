#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import datetime
import os
import sys


# https://en.wikipedia.org/wiki/ANSI_escape_code
c = {
	'RESET': '\033[0;0m',
	'BOLD': '\033[;1m',
	'REVERSE': '\033[;7m',
	'GREY': '\033[1;30m',
	'RED': '\033[1;31m',
	'GREEN': '\033[1;32m',
	'YELLOW': '\033[1;33m',
	'BLUE': '\033[1;34m',
	'MAGENTA': '\033[1;35m',
	'CYAN': '\033[1;36m',
	'WHITE': '\033[1;37m'
	}


def print_line(line_dict):
	t = str(line_dict['t'])
	sys.stdout.write(c['GREY'] + t[:-9] + '.' + t[-9:] + c['RESET'] + ' ')
	if line_dict['s'] == 'FS':
		sys.stdout.write(c['RED'])
	else:
		sys.stdout.write(c['GREEN'])
	sys.stdout.write(line_dict['c'] + c['RESET'] + ' ')
	sys.stdout.write(c['WHITE'] + line_dict['p'] + c['RESET'])
	sys.stdout.write('\n')
	sys.stdout.flush()


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

	return seconds * 10**9 + microseconds * 10**3


def hex_to_dec(hex_str):

	return str(int(hex_str[2:], 16))


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

	param = param.replace('\t', ' ').replace('  ', ' ').strip()
	param = [item.strip(' ()') for item in param.split(' ')]
	param = [hex_to_dec(item) if item.startswith('0x') else item for item in param]
	param = [str(int((item))) if item.isdigit() else item for item in param]
	param = ' '.join(param)

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
		if ' fsx-linux ' in line and ' getattr ' not in line
		]

	log_fsx_lines = [
		parse_fsx_line(line) for line in
		log_fsx.split('\n')
		if line[:6].isdigit() and line[6] == ' '
		]

	log_lines = sorted(log_fs_lines + log_fsx_lines, key = lambda k: k['t'])

	for line in log_lines:
		print_line(line)


if __name__ == '__main__':
	main()
