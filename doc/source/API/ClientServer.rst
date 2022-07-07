Initial Setup and Launching AEDT
================================
PyAEDT works both inside AEDT and as a standalone application.
It automatically detects whether it is running in an IronPython or CPython
environment and initializes AEDT accordingly.

Initial Setup and Launching AEDT Locally
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can start AEDT from Python in the graphical or non-graphical mode.

.. code:: python

    Launch AEDT 2022 R1 in non-graphical mode

    from pyaedt import Desktop, Maxwell3d
    with Desktop(specified_version="2022.1", non_graphical=True, new_desktop_session=True, close_on_exit=True,
                 student_version=False):
        m3d = Maxwell3d()
        ...
        # Any error here will be caught by Desktop.
        ...

    # Desktop is automatically closed here.


You can obtain the same result with:

.. code:: python

    # Launch the latest installed version of AEDT in graphical mode.

    from pyaedt import Maxwell3d
    m3d = Maxwell3d(specified_version="2022.1", non_graphical=False)
    ...
    # Put your code here
    ...
    m3d.release_desktop(close_projects =True, close_desktop=True)

    # Desktop is automatically released here.


Initial Setup and Launching AEDT Remotely
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can launch PyAEDT on a remote machine if the following conditions are met:

#. PyAEDT is installed on client and server machines. (You do not need to have AEDT
   installed on the client machine.)
#. The same Python version is used on the client and server machines. (CPython 3.6+
   or IronPython is embedded in the AEDT installation.)

CPython to IronPython can be used with some data type limitations and potential issues.
For example, when getting lists from a command, you can access every item (such as ``mylist[i]``)
and len (such as ``mylist.__len__()``) but not ``len(mylist)``.

Here is an usage example for a Windows server or Linux server (Ironpython):

.. code:: python

    # Launch the latest installed version of AEDT in graphical mode.

    from pyaedt.common_rpc import launch_server
    # ansysem_path and non_graphical are needed only for Linux Ironpython Server
    launch_server(ansysem_path="/path/to/ansys/executable/folder", non_graphical=True)

On Linux, you can launch the IronPython console with:

.. code:: python

   /path/to/AnsysEM21.x/Linux64/common/mono/Linux64/bin/mono /path/to/AnsysEM21.x/Linux64/common/IronPython/ipy64.exe


Here is a usage example for the client side:

.. code:: python

    # Launch the latest installed version of AEDT in non-graphical mode.

    from pyaedt.common_rpc import client
    my_client = client("full_name_of_server")
    circuit = my_client.root.circuit(specified_version="2022.1", non_graphical=True)
    ...
    # code like locally
    ...


The Linux CPython server is also supported but allows you only to run PyAEDT in a script (in a non-interactive session).
Here is an usage example for the Linux server (CPython):

.. code:: python

    # Launch the latest installed version of AEDT in graphical mode.

    from pyaedt.common_rpc import launch_server
    launch_server()

Here is a usage example for the client Side:

.. code:: python

    # Launch the latest installed version of AEDT in graphical mode.

    from pyaedt.common_rpc import client
    my_client = client("full_name_of_server")
    example_script = ["from pyaedt import Circuit", circuit="Circuit()", "circuit.save_project('project_name')"]
    ansysem = "/path/to/AnsysEMxxx/Linux64"
    my_client.root.run_script(example_script, ansysem_path=ansysem)
    my_client.root.run_script(example_script, aedt_version="2022.1") #if ANSYSEM_ROOTxxx env variable is present


As an alternative, you can upload the script to the server and run it from there:

.. code:: python

    # Launch the latest installed version of AEDT in graphical mode.

    from pyaedt.common_rpc import client, upload
    my_client = client("full_name_of_server")
    local_script ="path/to/my/local/pyaedt/script.py"
    remote_script ="path/to/my/remote/pyaedt/script.py"
    upload(local_script, remote_script, "servername")
    ansysem = "/path/to/AnsysEMxxx/Linux64"
    my_client.root.run_script(remote_script, ansysem_path=ansysem)


CPython on Linux with Client-Server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To bypass current IronPython limits, you can launch PyAEDT on a Linux machine:

1. Using ``pip``, install PyAEDT 0.4.23 or later on a Linux machine.
2. Launch CPython and run PyAEDT.

  .. code:: python

      # Launch the latest installed version of PyAEDT in graphical mode.
      
      from pyaedt.common_rpc import launch_ironpython_server
      client = launch_ironpython_server(aedt_path="/path/to/ansys/executable/folder", non_graphical=True, port=18000)
      hfss = client.root.hfss()
      # put your code here


3. If the method returns a list or dictionary, use this method to work around an
   issue with CPython handling:

.. code:: python

    box1 = hfss.modeler.create_box([0,0,0],[1,1,])
    # convert_remote_object method convert remote ironpython list to local cpython.
    faces = client.convert_remote_object(box1.faces)


.. image:: /Resources/IronPython2Cpython.png
  :width: 800
  :alt: Electronics Desktop Launched