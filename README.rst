LoggedFS-python - Filesystem monitoring with Fuse and Python
============================================================

Description
-----------

LoggedFS-python is a fuse-based filesystem which can log every operations that
happens in it. It is a pure Python re-implementation of `loggedfs`_ by Rémi
Flament - heavily inspired by Stavros Korokithakis' 2013 blog post entitled
"`Writing a FUSE filesystem in Python`_" (`source code repository`_).

How does it work?

Fuse does almost everything. LoggedFS-python only sends a message to ``syslog``
when called by fuse and then let the real filesystem do the rest of the job.

.. _loggedfs by Rémi Flament: https://github.com/rflament/loggedfs
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

	loggedfs-python -l ~/log.txt /tmp/TEST

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

	loggedfs-python -f -p /var

You should see logs like these :

::

	tail -f /var/log/syslog
	17:29:34 (loggedfs-python) LoggedFS-python running as a public filesystem
	17:29:34 (loggedfs-python) LoggedFS-python not running as a daemon
	17:29:34 (loggedfs-python) LoggedFS-python starting at /var.
	17:29:34 (loggedfs-python) chdir to /var
	17:29:35 (loggedfs-python) getattr /var/ {SUCCESS} [ pid = 8700 kded [kdeinit] uid = 1000 ]
	17:29:41 (loggedfs-python) getattr /var/ {SUCCESS} [ pid = 10923 ls uid = 1000 ]
	17:29:41 (loggedfs-python) getattr /var/run {SUCCESS} [ pid = 10923 ls uid = 1000 ]
	17:29:41 (loggedfs-python) getattr /var/run/nscd {FAILURE} [ pid = 10923 ls uid = 1000 ]
	17:29:41 (loggedfs-python) readdir /var/ {SUCCESS} [ pid = 10923 ls uid = 1000 ]
	17:29:41 (loggedfs-python) getattr /var/pouak {SUCCESS} [ pid = 10923 ls uid = 1000 ]

If you have a configuration file to use you should use this command:

.. code:: bash

	./loggedfs-python -c loggedfs.xml -p /var

If you want to log what other users do on your filesystem, you should use the
``-p`` option to allow them to see your mounted files. For a complete
documentation see the manual page.
