Changes
=======

0.0.3 (2019-XX-XX)
------------------

* FEATURE: In "traditional" logging mode (not JSON), read and write buffers are also logged zlib-compressed and BASE64 encoded.
* FIX: LoggedFS-python would have crashed if no XML configuration file had been specified.

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
