.. |build_master| image:: https://img.shields.io/travis/pleiszenburg/loggedfs-python/master.svg?style=flat-square
	:target: https://travis-ci.org/pleiszenburg/loggedfs-python
	:alt: Build Status: master / release

.. |build_develop| image:: https://img.shields.io/travis/pleiszenburg/loggedfs-python/develop.svg?style=flat-square
	:target: https://travis-ci.org/pleiszenburg/loggedfs-python
	:alt: Build Status: development branch

.. |license| image:: https://img.shields.io/pypi/l/loggedfs.svg?style=flat-square
	:target: https://github.com/pleiszenburg/loggedfs/blob/master/LICENSE
	:alt: Project License: Apache License v2

.. |status| image:: https://img.shields.io/pypi/status/loggedfs.svg?style=flat-square
	:target: https://github.com/pleiszenburg/loggedfs-python/milestone/1
	:alt: Project Development Status

.. |pypi_version| image:: https://img.shields.io/pypi/v/loggedfs.svg?style=flat-square
	:target: https://pypi.python.org/pypi/loggedfs
	:alt: Available on PyPi - the Python Package Index

.. |pypi_versions| image:: https://img.shields.io/pypi/pyversions/loggedfs.svg?style=flat-square
	:target: https://pypi.python.org/pypi/loggedfs
	:alt: Available on PyPi - the Python Package Index

.. |loggedfs_python_logo| image:: http://www.pleiszenburg.de/loggedfs-python_logo.png
	:target: https://github.com/pleiszenburg/loggedfs-python
	:alt: LoggedFS-python repository

|build_master| |build_develop| |license| |status| |pypi_version| |pypi_versions|

|loggedfs_python_logo|

Synopsis
========

LoggedFS-python is a FUSE-based filesystem which can log every operation that happens in it.
It is a pure Python re-implementation of `LoggedFS`_ by `Rémi Flament`_ maintaining CLI compatibility.
The project is heavily inspired by `Stavros Korokithakis`_' 2013 blog post entitled
"`Writing a FUSE filesystem in Python`_" (`source code repository`_).
The filesystem is fully `POSIX`_ compliant, passing the `pjdfstest test-suite`_, a descendant of FreeBSD's `fstest`_.
It furthermore passes stress tests with fsx-linux based on the `fsx-flavor`_  released by the `Linux Test Project`_.
It is intended to be suitable for production systems.

.. _LoggedFS: https://github.com/rflament/loggedfs
.. _Rémi Flament: https://github.com/rflament
.. _Stavros Korokithakis: https://github.com/skorokithakis
.. _Writing a FUSE filesystem in Python: https://www.stavros.io/posts/python-fuse-filesystem/
.. _source code repository: https://github.com/skorokithakis/python-fuse-sample
.. _POSIX: https://en.wikipedia.org/wiki/POSIX
.. _pjdfstest test-suite: https://github.com/pjd/pjdfstest
.. _fstest: https://github.com/zfsonlinux/fstest
.. _fsx-flavor: http://codemonkey.org.uk/projects/fsx/
.. _Linux Test Project: https://github.com/linux-test-project/ltp


CAVEATS
=======

* PROJECT STATUS: **BETA**
* A `CUSTOM BUG-FIXED VERSION OF FUSEPY`_ IS REQUIRED FOR FULL POSIX COMPLIANCE.
  IT IS AUTOMATICALLY INSTALLED FROM GITHUB AS A DEPENDENCY OF THIS PACKAGE.
  IF THE LATEST OFFICIAL RELEASE OF FUSEPY IS USED INSTEAD, TIMESTAMPS WILL BE
  INACCURATE ON A NANOSECOND TO MICROSECOND SCALE AND UTIME_NOW AS WELL AS
  UTIME_OMIT WILL NOT BE HONORED. THERE WAS A `PULL REQUEST`_ TO FIX THIS,
  WHICH HAS BEEN REJECTED. ALTERNATIVE APPROACHES ARE BEING RESEARCHED.
* THE FILESYSTEM IS CURRENTLY **ONLY** BEING DEVELOPED FOR AND TESTED ON **LINUX**.
  ANYONE INTERESTED IN ADDING MAC OS X AND/OR BSD SUPPORT?

.. _CUSTOM BUG-FIXED VERSION OF FUSEPY: https://github.com/s-m-e/fusepy
.. _PULL REQUEST: https://github.com/fusepy/fusepy/pull/79


Installation
============

From the `Python Package Index`_ (PyPI):

.. code:: bash

	pip install loggedfs

From GitHub:

.. code:: bash

	pip install git+https://github.com/pleiszenburg/loggedfs-python.git@master

**Supports Python 3.{4,5,6,7}.**

**Supports Linux.**
Support for MAC OS X and BSD requires a minor change only, but has yet not been added: Access to the system log is currently being achieved through ``logging.handlers.SysLogHandler(address = '/dev/log')``, a Linux-only solution.

.. _Python Package Index: https://pypi.org/


Simple usage example
====================

To start recording access to ``/tmp/TEST`` into ``/root/log.txt``, just do:

.. code:: bash

	sudo loggedfs -p -s -l /root/log.txt /tmp/TEST

To stop recording, just unmount as usual:

.. code:: bash

	sudo fusermount -u /tmp/TEST


Configuration
=============

LoggedFS-python can use an XML configuration file if you want it to log
operations only for certain files, for certain users, or for certain operations.
The format is fully compatible with LoggedFS' original format.

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


Need help?
==========

Feel free to post questions in the `GitHub issue tracker`_ of this project.

.. _GitHub issue tracker: https://github.com/pleiszenburg/loggedfs-python/issues


Bugs & issues
=============

Please report bugs in LoggedFS-python here in its `GitHub issue tracker`_.


Miscellaneous
=============

- Full project documentation

  - at `Read the Docs`_
  - at `LoggedFS-python repository`_

- `License`_ (**Apache License 2.0**)
- `Contributing`_ (**Contributions are highly welcomed!**)
- `FAQ`_
- `Authors`_
- `Changes`_
- `Long-term ideas`_
- `Upstream issues`_ (relevant bugs in dependencies)

.. _Read the Docs: http://loggedfs-python.readthedocs.io/en/latest/
.. _LoggedFS-python repository: https://github.com/pleiszenburg/loggedfs-python/blob/master/docs/index.rst
.. _License: https://github.com/pleiszenburg/loggedfs-python/blob/master/LICENSE
.. _Contributing: https://github.com/pleiszenburg/loggedfs-python/blob/master/CONTRIBUTING.rst
.. _FAQ: http://loggedfs-python.readthedocs.io/en/stable/faq.html
.. _Authors: https://github.com/pleiszenburg/loggedfs-python/blob/master/AUTHORS.rst
.. _Changes: https://github.com/pleiszenburg/loggedfs-python/blob/master/CHANGES.rst
.. _Long-term ideas: https://github.com/pleiszenburg/loggedfs-python/milestone/2
.. _Upstream issues: https://github.com/pleiszenburg/loggedfs-python/issues?q=is%3Aissue+is%3Aopen+label%3Aupstream
