Launching LoggedFS-python
=========================

If you just want to test LoggedFS-python you don't need any configuration file.

Just use that command:

.. code:: bash

	sudo loggedfs -s -f -p /var

You should see logs like these:

::

	tail -f /var/log/syslog
	2017-12-09 17:29:34,910 (loggedfs-python) LoggedFS-python running as a public filesystem
	2017-12-09 17:29:34,915 (loggedfs-python) LoggedFS-python not running as a daemon
	2017-12-09 17:29:34,920 (loggedfs-python) LoggedFS-python starting at /var
	2017-12-09 17:29:34,950 (loggedfs-python) chdir to /var
	2017-12-09 17:29:35,246 (loggedfs-python) getattr /var/ {SUCCESS} [ pid = 8700 kded [kdeinit] uid = 1000 ]
	2017-12-09 17:29:41,841 (loggedfs-python) getattr /var/ {SUCCESS} [ pid = 10923 ls uid = 1000 ]
	2017-12-09 17:29:41,858 (loggedfs-python) getattr /var/run {SUCCESS} [ pid = 10923 ls uid = 1000 ]
	2017-12-09 17:29:41,890 (loggedfs-python) getattr /var/run/nscd {FAILURE} [ pid = 10923 ls uid = 1000 ]
	2017-12-09 17:29:41,912 (loggedfs-python) readdir /var/ {SUCCESS} [ pid = 10923 ls uid = 1000 ]
	2017-12-09 17:29:41,987 (loggedfs-python) getattr /var/pouak {SUCCESS} [ pid = 10923 ls uid = 1000 ]

If you have a configuration file to use you should use this command:

.. code:: bash

	loggedfs -c loggedfs.xml -p /var

If you want to log what other users do on your filesystem, you should use the
``-p`` option to allow them to see your mounted files. For a complete
documentation see the manual page.
