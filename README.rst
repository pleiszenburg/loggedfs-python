.. |build_master| image:: https://img.shields.io/travis/pleiszenburg/loggedfs-python/master.svg?style=flat-square
	:target: https://travis-ci.org/pleiszenburg/loggedfs-python
	:alt: Build Status: master / release

.. |build_develop| image:: https://img.shields.io/travis/pleiszenburg/loggedfs-python/develop.svg?style=flat-square
	:target: https://travis-ci.org/pleiszenburg/loggedfs-python
	:alt: Build Status: development branch

|build_master| |build_develop|

LoggedFS-python - Filesystem monitoring with Fuse and Python
============================================================

**PROJECT STATUS IS ALPHA** (UNDER DEVELOPMENT).

**WARNING**: FILE SYSTEM DOES **NOT** PASS `TEST SUITE FOR POSIX COMPLIANCE`_.

CURRENT STATUS: **12 TEST** OUT OF 232 (5%) ARE **FAILING**.

A CUSTOM BUG-FIXED VERSION OF `FUSEPY`_ IS REQUIRED.

BESIDES, CLI SWITCHES ARE NOT FULLY TESTED. THERE ARE ODD EDGE CASES ...

.. _FUSEPY: https://github.com/s-m-e/fusepy
.. _TEST SUITE FOR POSIX COMPLIANCE: https://github.com/pjd/pjdfstest

Description
-----------

LoggedFS-python is a fuse-based filesystem which can log every operation that
happens in it. It is a pure Python re-implementation of
`LoggedFS`_ by `Rémi Flament`_ - heavily inspired by `Stavros Korokithakis`_'
2013 blog post entitled "`Writing a FUSE filesystem in Python`_"
(`source code repository`_).

How does it work?

Fuse does almost everything. LoggedFS-python only sends a message to ``syslog``
when called by fuse and then let the real filesystem do the rest of the job.

.. _LoggedFS: https://github.com/rflament/loggedfs
.. _Rémi Flament: https://github.com/rflament
.. _Stavros Korokithakis: https://github.com/skorokithakis
.. _Writing a FUSE filesystem in Python: https://www.stavros.io/posts/python-fuse-filesystem/
.. _source code repository: https://github.com/skorokithakis/python-fuse-sample

Installation
------------

.. code:: bash

	pip install git+https://github.com/pleiszenburg/loggedfs-python.git@master

Simplest usage
--------------

To record access to ``/tmp/TEST`` into ``~/log.txt``, just do:

.. code:: bash

	loggedfs -l ~/log.txt /tmp/TEST

To stop recording, just unmount as usual:

.. code:: bash

	sudo umount /tmp/TEST

``~/log.txt`` will need to be changed to readable by setting permissions:

.. code:: bash

	chmod 0666 ~/log.txt

Configuration
-------------

LoggedFS-python can use an XML configuration file if you want it to log
operations only for certain files, for certain users, or for certain operations.
The format is compatible with LoggedFS' original format.

Here is a sample configuration file :

.. code:: xml

	<?xml version="1.0" encoding="UTF-8"?>

	<loggedFS logEnabled="true" printProcessName="true">
		<includes>
			<include extension=".*" uid="*" action=".*" retname=".*"/>
		</includes>
		<excludes>
			<exclude extension=".*\.bak$" uid="*" action=".*" retname="SUCCESS"/>
			<exclude extension=".*" uid="1000" action=".*" retname="FAILURE"/>
			<exclude extension=".*" uid="*" action="getattr" retname=".*"/>
		</excludes>
	</loggedFS>

This configuration can be used to log everything except if it concerns a
``*.bak`` file, or if the ``uid`` is 1000, or if the operation is ``getattr``.

Launching LoggedFS-python
-------------------------

If you just want to test LoggedFS-python you don't need any configuration file.

Just use that command:

.. code:: bash

	loggedfs -f -p /var

You should see logs like these :

::

	tail -f /var/log/syslog
	2017-12-09 17:29:34,910 (loggedfs-python) LoggedFS-python running as a public filesystem
	2017-12-09 17:29:34,915 (loggedfs-python) LoggedFS-python not running as a daemon
	2017-12-09 17:29:34,920 (loggedfs-python) LoggedFS-python starting at /var.
	2017-12-09 17:29:34,950 (loggedfs-python) chdir to /var
	2017-12-09 17:29:35,246 (loggedfs-python) getattr /var/ {SUCCESS} [ pid = 8700 kded [kdeinit] uid = 1000 ]
	2017-12-09 17:29:41,841 (loggedfs-python) getattr /var/ {SUCCESS} [ pid = 10923 ls uid = 1000 ]
	2017-12-09 17:29:41,858 (loggedfs-python) getattr /var/run {SUCCESS} [ pid = 10923 ls uid = 1000 ]
	2017-12-09 17:29:41,890 (loggedfs-python) getattr /var/run/nscd {FAILURE} [ pid = 10923 ls uid = 1000 ]
	2017-12-09 17:29:41,912 (loggedfs-python) readdir /var/ {SUCCESS} [ pid = 10923 ls uid = 1000 ]
	2017-12-09 17:29:41,987 (loggedfs-python) getattr /var/pouak {SUCCESS} [ pid = 10923 ls uid = 1000 ]

If you have a configuration file to use you should use this command:

.. code:: bash

	./loggedfs -c loggedfs.xml -p /var

If you want to log what other users do on your filesystem, you should use the
``-p`` option to allow them to see your mounted files. For a complete
documentation see the manual page.
