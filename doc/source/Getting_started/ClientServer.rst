Client-server
=============
You can launch PyAEDT on a remote machine if these conditions are met:

- PyAEDT is installed on client and server machines. (There is no need to have AEDT
  installed on the client machine.)
- The same Python version is used on the client and server machines. (CPython 3.7+ or
  IronPython is embedded in the AEDT installation.)

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
must be up and running on the remote server listening on the specified port.

To start AEDT in listening mode on the remote machine:

.. code::

   path/to/aedt/ansysedt.exe -grpcsrv portnumber  #windows
   path/to/aedt/ansysedt -grpcsrv portnumber   #linux

If the connection is local, the ``machine`` argument can remain empty. PyAEDT then
starts the AEDT session automatically. Machine and port arguments are available to
all applications except EDB.


Remote application call
~~~~~~~~~~~~~~~~~~~~~~~
You can make a remote application call on a CPython server
or any Windows client machine starting from AEDT 2022.2.

On a CPython Server run the service pyaedt_service_manager that will listen on port 17878
for incoming requests of connection from clients. Port is configurable.
Requirements:

- Python 3.7+ Virtual Environment. You could use the CPython in AEDT installation folder but you need to add the
  Python lib folder to the LD_LIBRARY_PATH.
- pyaedt > 0.6.0
- export ANSYSEM_ROOT222=/path/to/AnsysEM/v222/Linux64 #Win64 in case of Windows Server
- export LD_LIBRARY_PATH=$ANSYSEM_ROOT222/common/mono/Linux64/lib:$ANSYSEM_ROOT222/Delcross:$LD_LIBRARY_PATH


.. code:: python

    # Launch PyAEDT remote server on CPython
    from pyaedt.common_rpc import pyaedt_service_manager
    pyaedt_service_manager()


On any Windows client machine user needs to establish the connection as shown in example below.
AEDT can be launched directly while creating the session or after the connection is established.

.. code:: python

    from pyaedt.common_rpc import create_session
    # User can establish the connection and start a new AEDT session.
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

