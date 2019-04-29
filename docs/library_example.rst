Using LoggedFS-python as a library
==================================

Create a new directory, for instance in your current working directory, named ``demo_dir``. Then fire up an interactive Python shell such as Jupyter Notebook or Jupyter Lab. Now you can try the following:

.. code:: python

    import re
    import loggedfs

    demo_filter = loggedfs.filter_pipeline_class(
        include_list = [loggedfs.filter_item_class([loggedfs.filter_field_class(
            name = 'proc_cmd', value = re.compile('.*kate.*').match
            )])]
        )
    demo_data = []
    demo_err = []

    demo = loggedfs.loggedfs_notify(
        'demo_dir',
        background = True,
        log_filter = demo_filter,
        consumer_out_func = demo_data.append,
        consumer_err_func = demo_err.append
        )

You have just stated recording all filesystem events that involve a command containing the string ``kate``. Leave the Python shell and write some stuff into the ``demo_dir`` using ``Kate``, the KDE text editor. Once you are finished, go back to your Python shell and terminate the recording.

.. code:: python

    demo.terminate()

Notice that the recorded data ends with an "end of transmission" marker. For convenience, remove it first:

.. code:: python

    assert isinstance(demo_data[-1], loggedfs.end_of_transmission)
    demo_data = demo_data[:-1]

Let's have a look at what you have recorded:

.. code:: python

    print(demo_data[44]) # index 44 might show something different in your case

::

    {'proc_cmd': '/usr/bin/kate -b /test/demo_dir/demo_file.txt',
    'proc_uid': 1000,
    'proc_uid_name': 'ernst',
    'proc_gid': 100,
    'proc_gid_name': 'users',
    'proc_pid': 11716,
    'action': 'read',
    'status': True,
    'param_path': '/test/demo_dir/demo_file.txt',
    'param_length': 4096,
    'param_offset': 0,
    'param_fip': 5,
    'return_len': 1486,
    'return': '',
    'time': 1556562162704772619}

Every single event is represented as a dictionary. ``demo_data`` is therefore a list of dictionaries. The following columns / keys are always present:

- proc_cmd: Command line of the process ordering the operation.
- proc_uid: UID (user ID) of the owner of the process ordering the operation.
- proc_uid_name: User name of the owner of the process ordering the operation.
- proc_gid: GID (group ID) of the owner of the process ordering the operation.
- proc_gid_name: Group name of the owner of the process ordering the operation.
- proc_pid: PID (process ID) of the process ordering the operation.
- action: Name of filesystem operation, such as ``open``, ``read`` or ``write``.
- status: Boolean, describing the success of the operation.
- return: Return value of operation. ``None`` if there is none.
- time: System time, nanoseconds, UTC

Other columns / keys are optional and depend on the operation and its status. With this knowledge, you can run typical Python data analysis frameworks across this data. Pandas for instance:

.. code:: python

    import pandas as pd
    data_df = pd.DataFrame.from_records(demo_data, index = 'time')

    data_df[data_df['action'] == 'write'][['param_buf_len', 'param_offset', 'return']]

::

                            param_buf_len   param_offset   return
    time
    1556562164301499774     57.0            0.0            57
    1556562164304043463     2.0             57.0           2
    1556562164621417400     1487.0          0.0            1487
    1556562165260276486     53.0            0.0            53
    1556562165532797611     1486.0          0.0            1486
