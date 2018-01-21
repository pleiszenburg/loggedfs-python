.. |build_master| image:: https://img.shields.io/travis/pleiszenburg/loggedfs-python/master.svg?style=flat-square
	:target: https://travis-ci.org/pleiszenburg/loggedfs-python
	:alt: Build Status: master / release

.. |build_develop| image:: https://img.shields.io/travis/pleiszenburg/loggedfs-python/develop.svg?style=flat-square
	:target: https://travis-ci.org/pleiszenburg/loggedfs-python
	:alt: Build Status: development branch

|build_master| |build_develop|


LoggedFS-python - Filesystem monitoring with Fuse and Python
************************************************************


Synopsis
========

LoggedFS-python is a FUSE-based filesystem which can log every operation that happens in it.
It is a pure Python re-implementation of `LoggedFS`_ by `Rémi Flament`_ maintaining CLI compatibility.
The project is heavily inspired by `Stavros Korokithakis`_' 2013 blog post entitled
"`Writing a FUSE filesystem in Python`_" (`source code repository`_).
The filesystem is fully `POSIX`_ compliant (passing the `pjdfstest test-suite`_)
and intended to be suitable for production system.

.. _LoggedFS: https://github.com/rflament/loggedfs
.. _Rémi Flament: https://github.com/rflament
.. _Stavros Korokithakis: https://github.com/skorokithakis
.. _Writing a FUSE filesystem in Python: https://www.stavros.io/posts/python-fuse-filesystem/
.. _source code repository: https://github.com/skorokithakis/python-fuse-sample
.. _POSIX: https://en.wikipedia.org/wiki/POSIX
.. _pjdfstest test-suite: https://github.com/pjd/pjdfstest


CAVEATS
=======

* PROJECT STATUS: **BETA**
* THE FILESYSTEM HAS YET **NOT** BEEN **STRESS-TESTED**.
* A `CUSTOM BUG-FIXED VERSION OF FUSEPY`_ IS REQUIRED FOR FULL POSIX COMPLIANCE.
  IF THE LATEST OFFICIAL RELEASE OF FUSEPY IS USED INSTEAD, TIMESTAMPS WILL BE
  INACCURATE ON A NANOSECOND TO MICROSECOND SCALE AND UTIME_NOW AS WELL AS
  UTIME_OMIT WILL NOT BE HONORED. THERE IS A `PENDING PULL REQUEST`_.
* THE FILESYSTEM IS CURRENTLY **ONLY** BEING DEVELOPED FOR AND TESTED ON **LINUX**.
  ANYONE INTERESTED IN ADDING MAC OS X AND/OR BSD SUPPORT?

.. _CUSTOM BUG-FIXED VERSION OF FUSEPY: https://github.com/s-m-e/fusepy
.. _PENDING PULL REQUEST: https://github.com/fusepy/fusepy/pull/79


Installation
============

.. code:: bash

	pip install git+https://github.com/pleiszenburg/loggedfs-python.git@master

This project has intentionally not yet been published in the `Python Package Index`_ (PyPI).
It will be released on PyPI once critical changes have been merged into `fusepy`_,
a dependency of LoggedFS-python.

**Supports Python 3.{4,5,6,7}.**

**Supports Linux.**
Support for MAC OS X and BSD likely requires minor changes only, but has yet not been added.

.. _Python Package Index: https://pypi.org/
.. _fusepy: https://github.com/fusepy/fusepy


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
