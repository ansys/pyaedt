Client-server
=============
You can launch PyAEDT on a remote machine if these conditions are met:

- AEDT and PyAEDT is installed on client and server machines.
- The same Python version is used on the client and server machines. (CPython 3.8+
  is embedded in the AEDT installation.)

gRPC connection in AEDT 2022 R2 and later
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In AEDT 2022 R2 and later, PyAEDT fully supports the gRPC API (except for EDB):

.. code:: python

    # Launch the latest installed version of AEDT in graphical mode.
    from pyaedt import Hfss
    from pyaedt import settings
    settings.use_grpc_api=True
    hfss = Hfss(machine="fullmachinename", port=portnumber)

If the ``machine`` argument is provided and the machine is a remote machine, AEDT
must be up and running on the remote server listening on the specified port ``portnumber``.

To start AEDT in listening mode on the remote machine:

.. code::

   path/to/ANSYSEM/v222/Win64/ansysedt.exe -grpcsrv portnumber  #windows
   path/to/ANSYSEM/v222/Lin64/ansysedt -grpcsrv portnumber   #linux

If the connection is local, the ``machine`` argument must be left empty. PyAEDT then
starts the AEDT session automatically. Machine and port arguments are available to
all applications except EDB.


PyAEDT remote service manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
PyAEDT includes a service manager that can be run on the server machine and can be
launched on-demand in AEDT sessions and act as a file manager.
You can make a remote application call on a CPython server
or any Windows client machine in AEDT 2022 R2 and later.

On a CPython Server run the ``pyaedt_service_manager`` service that listens on port 17878
for incoming requests of connections from clients. The port is configurable.
Requirements:

- Python 3.8+ Virtual Environment.
- pyaedt > 0.6.0

On Linux, in addition to the preceding requirements, these environments are needed:
- You can use the CPython version in the AEDT installation folder if you first
add the Python library folder to the ``LD_LIBRARY_PATH`` environment variable.
- You can use the Python 3.8 or later version that is installed.
- You can export ``ANSYSEM_ROOT242=/path/to/AnsysEM/v242/Linux64``.
- You can export ``LD_LIBRARY_PATH=$ANSYSEM_ROOT242/common/mono/Linux64/lib:$ANSYSEM_ROOT242/Delcross:$LD_LIBRARY_PATH``.

On the server, the ``pyaedt_service_manager`` service listen for incoming connections:

.. code:: python

    # Launch PyAEDT remote server on CPython
    from pyaedt.common_rpc import pyaedt_service_manager
    pyaedt_service_manager()


On any client machine, the user must establish the connection as shown in following example.
AEDT can be launched directly while creating the session or after the connection is established.

.. code:: python

    from pyaedt.common_rpc import create_session
    # User can establish the connection and start a new AEDT session
    cl1 = create_session("server_name", launch_aedt_on_server=True, aedt_port=17880, non_graphical=True)

    # Optionally AEDT can be launched after the connection is established
    cl2 = create_session("server_name", launch_aedt_on_server=False)
    cl2.aedt(port=17880, non_graphical=True)


Once AEDT is started then user can connect an application to it.

.. code:: python

    hfss = Hfss(machine=cl1.server_name, port=cl1.aedt_port)
    # your code here

The client can be used also to upload or download files from the server.

.. code:: python

    cl1.filemanager.upload(local_path, remote_path)
    file_content = cl1.open_file(remote_file)

