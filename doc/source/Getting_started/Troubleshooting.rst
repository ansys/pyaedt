Troubleshooting
===============
This section contains common issues and suggestions related to installation and use of PyAEDT.

Installation
~~~~~~~~~~~~

Error installing Python or Conda
--------------------------------
Sometimes users are not allowed to install a Python interpreter.
In this case, a Python interpreter is available in installation path of
Ansys Electronics Desktop.
Note that Python 3.7 is available in AEDT <= 2023R1 while Ansys Electronics Desktop 2023 R2
is shipped with Python 3.10.

*Python 3.7 Path in the 23R1 Installation:*

.. code:: python

   path\to\AnsysEM\v231\commonfiles\CPython\3_7\winx64\Release\python"


Error installing PyAEDT using pip
---------------------------------
1. **Proxy Server** If your company uses a proxy server you may have to update proxy
   settings at the command line.
   See the `pip documentation <https://pip.pypa.io/en/stable/user_guide/#using-a-proxy-server>`_ for details.
2. **Install Permission** Make sure you have write access to the directory where the Python interpreter is
   installed. The use of a `virtual environment <https://docs.python.org/3/library/venv.html>`_ helps
   mitigate this issue by placing the Python interpreter and dependencies in a location that is owned
   by the user.
3. **Firewall** Some corporate firewalls may block pip. If you face this issue you'll have to work with your IT
   administrator to enable pip. The proxy server settings (described above) allow you to explicitly define
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
:download:`PyAEDT Installer Python file <../Resources/PyAEDTInstallerFromDesktop.py>`.
Run this script directly from AEDT and pass the wheelhouse file name as an argument.




Run PyAEDT
~~~~~~~~~~

COM vs gRPC
-----------
Prior to the 2022R2 release CPython automation in AEDT used
`COM <https://learn.microsoft.com/en-us/windows/win32/com/com-objects-and-interfaces>`_  which
requires all interfaces to be registered in the Windows Registry.
Communication between Python and the AEDT API were translated through an intermediate layer using
`pywin32 <https://github.com/mhammond/pywin32>`_ and  `PythonNET <https://pythonnet.github.io/pythonnet/>`_.

`gRPC <https://grpc.io/>`_ is a modern open source high performance Remote Procedure Call (RPC)
framework that can run in any environment and supports client/server remote calls.
Starting from 2022R2 and later, the AEDT API has replaced COM interface with gRPC interface.


.. list-table:: *gRPC Compatibility:*
   :widths: 65 65 65
   :header-rows: 1

   * - < 2022R2
     - 2022R2
     - > 2022R2
   * - Only Python.NET
     - Default: Python.NET
       Enable gRPC: ``pyaedt.settings.use_grpc_api = True``
     - Default: gRPC
       Enable Python.NET: ``pyaedt.settings.use_grpc_api = False``

The options shown here apply only to the Windows platform.
On Linux, the Python interface to AEDT uses gRPC for all versions.

.. _GRPC ref:

Check the AEDT API configuration
--------------------------------
To start the Electronics Desktop server in gRPC mode use the following syntax:

*Windows:*

.. code:: console

   path\to\AnsysEM\v231\Win64\ansysedt.exe -grpcsrv 50001

*Linux:*

.. code:: console

   path\to\AnsysEM\v231\Lin64\ansysedt -grpcsrv 50352

The server port number is used by AEDT to listen and receive
commands from PyAEDT client instances. This configuration
supports multiple sessions of AEDT running on a single server
and listening on the same port.

Check the gRPC interface
------------------------
The native Electronics Desktop API can be used to launch
Electronics Desktop from the command line.
This can be done even without PyAEDT to check that everything is set up correctly
and all environment
variables have been defined.

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
or to connect to an existing server session.
This may be due to:
 - Firewall
 - Proxy
 - Permissions
 - License
 - Scheduler (for example if the gRPC server was started from LSF, Slurm, ...)

In case of issues due to use of a proxy server, you may set the following environment variable to
disable the proxy server for the *localhost*.

.. code:: console

    export no_proxy=localhost,127.0.0.1

Run your PyAEDT script.

If it still fails, the proxy server can be disabled:

.. code:: console

    export http_proxy=

Run your PyAEDT script. If the errors persist try the following:

1. Check that AEDT starts correctly from command line by
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

Then start ansysedt.exe as a gRPC server.

.. code:: console

    ansysedt -grpcsrv 50051 > /path/to/file/server.txt

The above command redirects the gRPC trace is
to the file *server.txt*.

Open another terminal window to trace the
gRPC calls on the client where the Python script will be run.

.. code:: console

    export GRPC_VERBOSITY=DEBUG
    export GRPC_TRACE=all

Now run the PyAEDT script
(make sure it connects to the same port as the gRPC server, 50051).
Capture the output in a file *client.txt* and send all the logs
to `Ansys Support <https://www.ansys.com/it-solutions/contacting-technical-support>`_.
