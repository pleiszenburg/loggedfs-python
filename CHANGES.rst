Changes
=======

0.0.6 (2019-XX-XX)
------------------

* Dropped Python 3.4 support

0.0.5 (2019-05-06)
------------------

* Switched from `fusepy`_ to `refuse`_

.. _fusepy: https://github.com/fusepy/fusepy
.. _refuse: https://github.com/pleiszenburg/refuse

0.0.4 (2019-05-01)
------------------

* FEATURE: New flag ``-m``, explicitly excluding all operations from the log that do not have the potential to change the filesystem. Added for convenience.
* FIX: Terminating a notify session started in the background would not join all relevant threads properly. Terminating a notify session started in the foreground would cause an exception due to it attempting to join non-existing threads.
* Added Jupyter Notebook example to documentation.

0.0.3 (2019-05-01)
------------------

* FEATURE: LoggedFS-python can be used as a library in other Python software, enabling a user to specify callback functions on filesystem events. The relevant infrastructure is exported as ``loggedfs.loggedfs_notify``. See library example under ``docs``.
* FEATURE: New programmable filter pipeline, see ``loggedfs.filter_field_class``, ``loggedfs.filter_item_class`` and ``loggedfs.filter_pipeline_class``
* FEATURE: New flag ``-b``, explicitly activating logging of read and write buffers
* FEATURE: In "traditional" logging mode (not JSON), read and write buffers are also logged zlib-compressed and BASE64 encoded.
* FEATURE: Convenience function for decoding logged buffers, see ``loggedfs.decode_buffer``
* FIX: LoggedFS-python would have crashed if no XML configuration file had been specified.
* FIX: **Directory listing (``ls``) was broken.**
* FIX: Testing infrastructure did not catch all exceptions in tests.
* FIX: Testing infrastructure did not handle timeouts on individual tests correctly.

0.0.2 (2019-04-23)
------------------

* FEATURE: New flag ``-j`` for JSON-formatted log output
* FEATURE: New field ``command`` allowed in XML configuration files for filtering for command strings with regular expressions
* FEATURE: All fields in ``include`` and ``exclude`` tags, e.g. ``extension`` or ``uid``, become optional / implicit and can be omitted.
* FEATURE: (UNTESTED) Mac OS X support. Test framework still relies on Linux.
* FIX: Several implementations of FUSE calls such as truncate did rely on the assumption that the current working directory of the file system process would not change. This was risky. LoggedFS-python does also NOT change the current working directory anymore on its own.
* Code cleanup

0.0.1 (2019-04-11)
------------------

* First official BETA-release of *LoggedFS-python*
