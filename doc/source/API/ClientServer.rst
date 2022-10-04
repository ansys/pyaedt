Initial setup and launching AEDT
================================
PyAEDT works both inside AEDT and as a standalone application.
It automatically detects whether it is running in an IronPython or CPython
environment and initializes AEDT accordingly.

Initial setup and launching AEDT locally
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can start AEDT from Python in the graphical or non-graphical mode.

.. code:: python

    # Launch AEDT 2022 R1 in non-graphical mode

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


Initial setup and launching AEDT remotely
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can launch PyAEDT on a remote machine if the following conditions are met:

#. PyAEDT is installed on client and server machines. (You do not need to have AEDT
   installed on the client machine.)
#. The same Python version is used on the client and server machines. (CPython 3.7+)


Here is an usage example for a Windows server or Linux server:

.. code:: python

    # Launch the latest installed version of AEDT in graphical mode.

    from pyaedt.common_rpc import pyaedt_service_manager

    # service manager will listen on port 17878
    pyaedt_service_manager()



Here is a usage example for the client side:

.. code:: python

    # Launch the latest installed version of AEDT in non-graphical mode.

    from pyaedt.common_rpc import create_session
    my_client = create_session(server_name, 20000)
    my_client.aedt(port=22501, non_graphical=True)
    my_client.edb("path/to/aedbfolder")
 ...
    # code like locally
    ...

