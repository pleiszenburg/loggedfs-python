# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	src/loggedfs/_core/defaults.py: Default configurations

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
# CONST
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

FUSE_ALLOWOTHER_DEFAULT = False
FUSE_FOREGROUND_DEFAULT = False

LIB_MODE_DEFAULT = False

LOG_BUFFERS_DEFAULT = False
LOG_ENABLED_DEFAULT = True
LOG_JSON_DEFAULT = False
LOG_ONLYMODIFYOPERATIONS_DEFAULT = False
LOG_PRINTPROCESSNAME_DEFAULT = True
LOG_SYSLOG_DEFAULT = False
