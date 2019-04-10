#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def main():
	with open('tests/test_logs/loggedfs.log', 'r', encoding = 'utf-8') as f:
		log_fs = f.read()
	with open('tests/test_logs/iotest.fsxlog', 'r', encoding = 'utf-8') as f:
		log_fsx = f.read()

if __name__ == '__main__':
	main()
