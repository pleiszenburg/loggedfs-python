How to contribute to *LoggedFS-python*
======================================

Thank you for considering contributing to *LoggedFS-python*!
**Contributions are highly welcomed!**

Reporting issues
----------------

Issues are tracked on `Gitbub`_.

- Describe what you expected to happen.
- If possible, include a `minimal, complete, and verifiable example`_ to help
  identify the issue. This also helps check that the issue is not with your
  own code.
- Describe what actually happened. Include the full traceback if there was an
  exception.
- Add log files if possible. Careful, they tend to be huge.
- List your operating system, *Python*, *FUSE* and *LoggedFS-python* versions.
  If possible, check if this issue is already fixed in the repository
  (development branch).

.. _Gitbub: https://github.com/pleiszenburg/loggedfs-python/issues
.. _minimal, complete, and verifiable example: https://stackoverflow.com/help/mcve

Submitting patches
------------------

- Run ``make test`` before submission and attach the resulting
  ``tests/test_status_diff.yaml`` file to your pull request (indicating which
  tests the file-system now passes that did worked before).
- Use **tabs** for indentation.
- No, there is no line limit. Let your editor wrap the lines for you, if you want.
- Add as many comments as you can - code-readability matters.
- The ``master`` branch is supposed to be stable - request merges into the
  ``develop`` branch instead.
- Commits are preferred to be signed (GPG). Seriously, sign your code.

Looking for work? Check `tests flagged as false`_. There are plenty of them.

.. _tests flagged as false: https://github.com/pleiszenburg/loggedfs-python/blob/develop/tests/test_status_frozen.yaml

First time setup
----------------

- Make sure you have *FUSE* installed and working.
- Download and install the `latest version of git`_.
- Configure git with your `username`_ and `email`_:

.. code:: bash

	git config --global user.name 'your name'
	git config --global user.email 'your email'

- Make sure you have a `GitHub account`_.
- Fork *LoggedFS-python* to your GitHub account by clicking the `Fork`_ button.
- `Clone`_ your GitHub fork locally:

.. code:: bash

	git clone https://github.com/{username}/loggedfs-python
	cd loggedfs-python

- Add the main repository as a remote to update later:

.. code:: bash

	git remote add pleiszenburg https://github.com/pleiszenburg/loggedfs-python
	git fetch pleiszenburg

- Create a virtualenv:

.. code:: bash

	python3 -m venv env
	. env/bin/activate

- Install *LoggedFS-python* in editable mode with development dependencies.

.. code:: bash

	make install_link

- Check the installation by testing it:

.. code:: bash

	make test

.. _GitHub account: https://github.com/join
.. _latest version of git: https://git-scm.com/downloads
.. _username: https://help.github.com/articles/setting-your-username-in-git/
.. _email: https://help.github.com/articles/setting-your-email-in-git/
.. _Fork: https://github.com/pleiszenburg/loggedfs-python#fork-destination-box
.. _Clone: https://help.github.com/articles/fork-a-repo/#step-2-create-a-local-clone-of-your-fork
