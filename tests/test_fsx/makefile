# LoggedFS-python
# Filesystem monitoring with Fuse and Python
# https://github.com/pleiszenburg/loggedfs-python
#
#	tests/test_fsx/makefile: GNU makefile for fsx-linux
#
# 	Copyright (C) 2017-2020 Sebastian M. Ernst <ernst@pleiszenburg.de>
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


CC      = gcc
CFLAGS  = -g -O2 -fno-strict-aliasing -pipe -Wall -W -Wold-style-definition -D_FORTIFY_SOURCE=2 -DNO_XFS -D_LARGEFILE64_SOURCE -D_GNU_SOURCE
LDFLAGS =

FSX = fsx-linux

all: $(FSX)

$(FSX): $(FSX).c
	$(CC) $(FSX).c $(CFLAGS) -o $(FSX) $(LDFLAGS)

install:
	cp -av $(FSX) $(VIRTUAL_ENV)/bin/

clean:
	rm -rf $(FSX) $(FSX).o
