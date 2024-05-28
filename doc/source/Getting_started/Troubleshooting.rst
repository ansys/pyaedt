Troubleshooting
===============
This section contains common issues and suggestions related to installation and use of PyAEDT.

Installation
~~~~~~~~~~~~

Error installing Python or Conda
--------------------------------
Sometimes companies do not allow installation of a Python interpreter.
In this case, you can use the Python interpreter available in the AEDT installation.

.. note::

   Python 3.7 is available in AEDT 2023 R1 and earlier. Python 3.10 is available in AEDT 2023 R2.

Here is the path to the Python 3.7 interpreter for the 2023 R1 installation:

.. code:: python

   path\to\AnsysEM\v231\commonfiles\CPython\3_7\winx64\Release\python"


Error installing PyAEDT using pip
---------------------------------
- **Proxy server**: If your company uses a proxy server, you may have to update proxy
  settings at the command line. For more information, see the `Using a Proxy
  Server <https://pip.pypa.io/en/stable/user_guide/#using-a-proxy-server>`_ in the pip
  documentation.
- **Install permission**: Make sure that you have write access to the directory where the
   Python interpreter is
   installed. The use of a `virtual environment <https://docs.python.org/3/library/venv.html>`_ helps
   mitigate this issue by placing the Python interpreter and dependencies in a location that is owned
   by the user.
- **Firewall**: Some corporate firewalls may block pip. If you face this issue, you'll have to work with your IT
   administrator to enable pip. The proxy server settings (described earlier) allow you to explicitly define
   the ports used by pip.

If downloads from `pypi <https://pypi.org/>`_ are not allowed, you may use a
`wheelhouse <https://pypi.org/project/Wheelhouse/>`_.
The wheelhouse file contains all dependencies for PyAEDT and allows full installation without a need to
download additional files.
The wheelhouse for PyAEDT can be found `here <https://github.com/ansys/pyaedt/releases>`_.
After downloading the wheelhouse for your distribution and Python release, unzip the file to a folder and
run the Python command:

.. code:: python

    >>> pip install --no-cache-dir --no-index --find-links=/path/to/pyaedt/wheelhouse pyaedt


Another option to install PyAEDT from the wheelhouse is to download the following file
:download:`PyAEDT Installer Python file <../Resources/pyaedt_installer_from_aedt.py>`.
Run this script directly from AEDT and pass the wheelhouse file name as an argument.




Run PyAEDT
~~~~~~~~~~

COM and gRPC
------------
Prior to the 2022 R2 release, CPython automation in AEDT used
`COM <https://learn.microsoft.com/en-us/windows/win32/com/com-objects-and-interfaces>`_ , which
requires all interfaces to be registered in the Windows Registry.
Communication between Python and the AEDT API were translated through an intermediate layer using
`pywin32 <https://github.com/mhammond/pywin32>`_ and  `PythonNET <https://pythonnet.github.io/pythonnet/>`_.

`gRPC <https://grpc.io/>`_ is a modern open source high performance Remote Procedure Call (RPC)
framework that can run in any environment and supports client/server remote calls.
Starting from 2022R2 the AEDT API has replaced the COM interface with a gRPC interface.


.. list-table:: *gRPC Compatibility:*
   :widths: 65 65 65
   :header-rows: 1

   * - < 2022 R2
     - 2022 R2
     - > 2022 R2
   * - Only ``Python.NET``
     - | ``Python.NET``: *Default*
       | Enable gRPC: ``pyaedt.settings.use_grpc_api = True``
     - | gRPC: *Default*
       | Enable ``Python.NET``: ``pyaedt.settings.use_grpc_api = False``

The options shown here apply only to the Windows platform.
On Linux, the Python interface to AEDT uses gRPC for all versions.

.. _GRPC ref:

Check the AEDT API configuration
--------------------------------
Run the following command to start AEDT as a gRPC server:

*Windows:*

.. code:: console

   path\to\AnsysEM\v231\Win64\ansysedt.exe -grpcsrv 50001

**On Linux:**

.. code:: console

   path\to\AnsysEM\v231\Lin64\ansysedt -grpcsrv 50352

The server port number is used by AEDT to listen and receive
commands from the PyAEDT client. This configuration
supports multiple sessions of AEDT running on a single server
and listening on the same port.

Check the gRPC interface
------------------------
The native Electronics Desktop API can be used to launch
AEDT from the command line.
PyAEDT is not required to verify the setup for the server and ensure that
all environment
variables have been defined correctly.

.. code:: python

    import sys
    sys.path.append(r"ANSYSEM_ROOT231\PythonFiles\DesktopPlugin")
    import ScriptEnv
    print(dir())
    ScriptEnv.Initialize("", False, "", 50051)
    print(dir())



Failure connecting to the gRPC server
-------------------------------------
On Linux, PyAEDT may fail to initialize a new instance of the gRPC server
or connect to an existing server session.
This may be due to:

- Firewall
- Proxy
- Permissions
- License
- Scheduler (for example if the gRPC server was started from LSF or Slurm)

For issues related to use of a proxy server, you may set the following environment variable to
disable the proxy server for the *localhost*.

.. code:: console

    export no_proxy=localhost,127.0.0.1

Run your PyAEDT script.

If it still fails, you can disable the proxy server:

.. code:: console

    export http_proxy=

Run your PyAEDT script. If the errors persist, perform these steps:

1. Check that AEDT starts correctly from the command line by
   starting the :ref:`gRPC server<GRPC ref>`.
2. Enable debugging.

.. code:: console

    export ANSOFT_DEBUG_LOG=/tmp/testlogs/logs/lg
    export ANSOFT_DEBUG_LOG_SEPARATE=1
    export ANSOFT_DEBUG_LOG_TIMESTAMP=1
    export ANSOFT_DEBUG_LOG_THREAD_ID=1
    export ANSOFT_DEBUG_MODE=3


Enable the gRPC trace on the server:

.. code:: console

    export GRPC_VERBOSITY=DEBUG
    export GRPC_TRACE=all

Then run ansysedt.exe as a gRPC server and redirect the output.

.. code:: console

    ansysedt -grpcsrv 50051 > /path/to/file/server.txt

The preceding command redirects the gRPC trace
to the file ``server.txt``.

Open another terminal window to trace the
gRPC calls on the client where the Python script is to be run.

.. code:: console

    export GRPC_VERBOSITY=DEBUG
    export GRPC_TRACE=all

Now run the PyAEDT script, (making sure it connects to the same port as the gRPC server - 50051).
Capture the output in a file. For example *client.txt*. Then send all the logs
to `Ansys Support <https://www.ansys.com/it-solutions/contacting-technical-support>`_.
