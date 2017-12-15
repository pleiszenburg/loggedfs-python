# LoggedFS-python
# Filesystem monitoring with Fuse and Python
# https://github.com/pleiszenburg/loggedfs-python
#
#	makefile: GNU makefile for project management
#
# 	Copyright (C) 2017 Sebastian M. Ernst <ernst@pleiszenburg.de>
#
# <LICENSE_BLOCK>
# The contents of this file are subject to the Apache License
# Version 2 ("License"). You may not use this file except in
# compliance with the License. You may obtain a copy of the License at
# https://www.apache.org/licenses/LICENSE-2.0
# https://github.com/pleiszenburg/loggedfs-python/blob/master/LICENSE
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
# specific language governing rights and limitations under the License.
# </LICENSE_BLOCK>


T = ""

# docu:
# 	@(cd docs; make clean; make html)

release:
	-rm dist/*
	-rm -r src/*.egg-info
	python setup.py sdist bdist_wheel
	gpg --detach-sign -a dist/literatur*.whl
	gpg --detach-sign -a dist/literatur*.tar.gz

upload:
	for filename in $$(ls dist/*.tar.gz dist/*.whl) ; do \
		twine upload $$filename $$filename.asc ; \
	done

upload_test:
	for filename in $$(ls dist/*.tar.gz dist/*.whl) ; do \
		twine upload $$filename $$filename.asc -r pypitest ; \
	done

install:
	pip install --process-dependency-links .[dev]
	make install_fstest

install_link:
	pip install --process-dependency-links -e .[dev]
	make install_fstest

install_fstest:
	python3 -c 'import sys; import os; sys.path.append(os.path.join(os.getcwd(), "tests")); import loggedfs_libtest; loggedfs_libtest.install_fstest()'

mount:
	python3 -c 'import sys; import os; sys.path.append(os.path.join(os.getcwd(), "tests")); import loggedfs_libtest; loggedfs_libtest.quick_cli_mount()'

test:
	# make docu
	-rm tests/__pycache__/*.pyc
	-rm tests/loggedfs_libtest/__pycache__/*.pyc
	# USAGE: make test T="-T chmod/01.t -T chmod/02.t"
	pytest $(T)

# test_freeze:
# 	python3 -c 'import sys; import os; sys.path.append(os.path.join(os.getcwd(), "tests")); import loggedfs_libtest; loggedfs_libtest.freeze_results()'

umount:
	python3 -c 'import sys; import os; sys.path.append(os.path.join(os.getcwd(), "tests")); import loggedfs_libtest; loggedfs_libtest.quick_cli_umount()'
