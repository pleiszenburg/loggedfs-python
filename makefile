# LoggedFS-python
# Filesystem monitoring with Fuse and Python
# https://github.com/pleiszenburg/loggedfs-python
#
#	makefile: GNU makefile for project management
#
# 	Copyright (C) 2017-2019 Sebastian M. Ernst <ernst@pleiszenburg.de>
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

clean:
	-rm -r build/*
	-rm -r dist/*
	-rm -r src/*.egg-info
	# -rm -r htmlconv/*
	# -rm .coverage*
	coverage erase
	find src/ tests/ -name '*.pyc' -exec rm -f {} +
	find src/ tests/ -name '*.pyo' -exec rm -f {} +
	# find src/ tests/ -name '*~' -exec rm -f {} +
	find src/ tests/ -name '__pycache__' -exec rm -fr {} +
	# find src/ tests/ -name '*.htm' -exec rm -f {} +
	# find src/ tests/ -name '*.html' -exec rm -f {} +
	# find src/ tests/ -name '*.so' -exec rm -f {} +

# docu:
# 	@(cd docs; make clean; make html)

release:
	make clean
	python setup.py sdist bdist_wheel
	gpg --detach-sign -a dist/loggedfs*.whl
	gpg --detach-sign -a dist/loggedfs*.tar.gz

upload:
	for filename in $$(ls dist/*.tar.gz dist/*.whl) ; do \
		twine upload $$filename $$filename.asc ; \
	done

upload_test:
	for filename in $$(ls dist/*.tar.gz dist/*.whl) ; do \
		twine upload $$filename $$filename.asc -r pypitest ; \
	done

install:
	pip install .[dev]
	make install_fstest
	make install_fsx

install_link:
	pip install -e .[dev]
	make install_fstest
	make install_fsx

install_fstest:
	python3 -c 'import tests; tests.lib.install_fstest()'

install_fsx:
	python3 -c 'import tests; tests.lib.install_fsx()'

cleanup:
	python3 -c 'import tests; tests.lib.quick_cli_clean()'
init:
	python3 -c 'import tests; tests.lib.quick_cli_init()'
init_parentfs:
	python3 -c 'import tests; tests.lib.quick_cli_init_parentfs()'
init_childfs:
	python3 -c 'import tests; tests.lib.quick_cli_init_childfs()'
destroy:
	python3 -c 'import tests; tests.lib.quick_cli_destroy()'
destroy_parentfs:
	python3 -c 'import tests; tests.lib.quick_cli_destroy_parentfs()'
destroy_childfs:
	python3 -c 'import tests; tests.lib.quick_cli_destroy_childfs()'
destroy_force:
	-sudo fusermount -u tests/test_mount/test_child
	-sudo umount tests/test_mount

test:
	make test_posix
	make test_stress

test_posix:
	# make docu
	-rm tests/__pycache__/*.pyc
	-rm tests/lib/__pycache__/*.pyc
	# USAGE: make test T="-T chmod/01.t -T chmod/02.t"
	# REFERENCE TEST WITH EXT4: make test T="-M ext4"
	pytest $(T)

test_stress:
	tests/scripts/fsx
