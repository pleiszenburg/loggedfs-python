# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	tests/lib/scope.py: Provides test scope

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

import pytest

from .const import TEST_FS_LOGGEDFS
from .base import fstest_base_class
from .pre import fstest_pre_class
from .prove import fstest_prove_class
from .post import fstest_post_class


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@pytest.fixture(scope = 'module')
def fstest_scope(request):
	"""Runs in project root!
	"""

	fs_type = request.config.getoption('M')

	fstest = fstest_class(fs_type = fs_type)

	def __finalizer__():
		fstest.destroy()

	request.addfinalizer(__finalizer__)

	return fstest


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: CORE
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class fstest_class(
	fstest_base_class,
	fstest_pre_class,
	fstest_prove_class,
	fstest_post_class
	):


	def __init__(self, fs_type = TEST_FS_LOGGEDFS):

		self.init(fs_type = fs_type)
