Initial Setup and Launching AEDT
================================

`pyaedt` works both inside AEDT and as a standalone application.
It automatically detects whether it is running in an IronPython or CPython
environment and initializes AEDT accordingly.


Initial Setup and Launching AEDT Locally
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


AEDT can be started from Python in the graphical/non-graphical mode using AEDT.

.. code:: python

    Launch AEDT 2021 R2 in Non-Graphical mode

    from pyaedt import Desktop, Maxwell3d
    with Desktop(specified_version="2021.2", non_graphical=True, new_desktop_session=True, close_on_exit=True,
                 student_version=False):
        m3d = Maxwell3d()
        ...
        # Any error here will be caught by Desktop.
        ...

    # Desktop is automatically closed here.


The same result can be obtained with the following code:


.. code:: python

    # Launch the latest installed version of AEDT in graphical mode.

    from pyaedt import Maxwell3d
    m3d = Maxwell3d(specified_version="2021.2", non_graphical=False)
    ...
    # Put your code here
    ...
    m3d.release_desktop(close_projects =True, close_desktop=True)

    # Desktop is automatically released here.



Initial Setup and Launching AEDT Remotely
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pyaedt can also be launched on a remote machine. To do that, the following conditions are needed:

1. Pyaedt has to be installed on Client and Server machines
2. No need to have AEDT installed on client machine
3. Same Python version has to be used on client and server (CPython 3.6+ or Ironpython embedded in AEDT Installation)
4. CPython to IronPython can be used with some data type limitations and potential issues. As an example, when getting
   lists from a command you can access every item (e.g. ``mylist[i]``) and len (e.g. ``mylist.__len__()``) but not ``len(mylist)``.

Here one example of usage on Windows Server or Linux Server (Ironpython):

.. code:: python

    # Launch the latest installed version of AEDT in graphical mode.

    from pyaedt.common_rpc import launch_server
    # ansysem_path and non_graphical are needed only for Linux Ironpython Server
    launch_server(ansysem_path="/path/to/ansys/executable/folder", non_graphical=True)

On Linux, the IronPython console can be launched with the following command:
/path/to/AnsysEM21.x/Linux64/common/mono/Linux64/bin/mono /path/to/AnsysEM21.x/Linux64/common/IronPython/ipy64.exe

On client side:

.. code:: python

    # Launch the latest installed version of AEDT in non-graphical mode.

    from pyaedt.common_rpc import client
    my_client = client("full_name_of_server")
    circuit = my_client.root.circuit(specified_version="2021.2", non_graphical=True)
    ...
    # code like locally
    ...


The Linux CPython server is also supported but allows you only to run PyAEDT in a script (in a non-interactive session).
Here one example of usage on Linux Server (CPython):

.. code:: python

    # Launch the latest installed version of AEDT in graphical mode.

    from pyaedt.common_rpc import launch_server
    launch_server()

On Client Side:

.. code:: python

    # Launch the latest installed version of AEDT in graphical mode.

    from pyaedt.common_rpc import client
    my_client = client("full_name_of_server")
    example_script = ["from pyaedt import Circuit", circuit="Circuit()", "circuit.save_project('project_name')"]
    ansysem = "/path/to/AnsysEMxxx/Linux64"
    my_client.root.run_script(example_script, ansysem_path=ansysem)
    my_client.root.run_script(example_script, aedt_version="2021.2") #if ANSYSEM_ROOTxxx env variable is present


As an alternative, the user can upload the script to run to the server and run it.

.. code:: python

    # Launch the latest installed version of AEDT in graphical mode.

    from pyaedt.common_rpc import client, upload
    my_client = client("full_name_of_server")
    local_script ="path/to/my/local/pyaedt/script.py"
    remote_script ="path/to/my/remote/pyaedt/script.py"
    upload(local_script, remote_script, "servername")
    ansysem = "/path/to/AnsysEMxxx/Linux64"
    my_client.root.run_script(remote_script, ansysem_path=ansysem)
