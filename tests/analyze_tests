#!/usr/bin/env python3


from pprint import pprint as pp


def __compile_stats__(in_dict):

	tests_total = 0
	tests_failed = 0

	for item_key in in_dict.keys():
		tests_total += 1
		if not in_dict[item_key]:
			tests_failed += 1

	return {
		'int_tests': tests_total,
		'int_failed': tests_failed
		}


def __process_raw_results__(in_str):

	lines = in_str.split('\n')
	ret_dict = {}

	for line in lines:

		line = line.strip()
		if line == '':
			break

		if line.startswith('Failed') or line == 'ok':
			continue

		if line.startswith('/'):
			current_path = line.split('fstest/tests/')[1].split(' ')[0]
			continue

		if '..' in line:
			index = 1
			continue

		if line.startswith('ok '):
			res = True
		elif line.startswith('not ok '):
			res = False
		else:
			print(current_path, index, line)
			raise

		if not line.endswith(str(index)):
			raise

		ret_dict.update({'%s:%d' % (current_path, index): res})
		index += 1

	return ret_dict


def __read_file__(filename):

	f = open(filename, 'r')
	data = f.read()
	f.close()
	return data


if __name__ == '__main__':

	test_log_fn = 'test.log'
	test_results_fn = 'test_results.log'
	test_errors_fn = 'test_errors.log'

	test_results_raw_log = __read_file__(test_results_fn)
	test_results = __process_raw_results__(test_results_raw_log)

	pp(test_results)
	pp(__compile_stats__(test_results))
