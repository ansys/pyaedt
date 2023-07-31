Troubleshooting
===============
This section contains common issues and suggestions around PyAEDT installation and usage.

Installation
~~~~~~~~~~~~

Error installing Python or Conda
--------------------------------
Some IT department do not allow you to install a Python interpreter in your machine.
In this case, you can use the interpreter available in the AEDT installation path. In AEDT
2023 R1 and earlier, Python 3.7 is available. In AEDT 2023 R2 and later, Python 3.10 is
available.

.. code:: python
   path\to\AnsysEM\v231\commonfiles\CPython\3_7\winx64\Release\python"


Error installing PyAEDT using pip
---------------------------------
1. Check if your internet connection is working.
2. Check if your firewall allows connections to pypi.com.

If your organization does not allow downloads from pypi.com, try using a wheelhouse.
A wheelhouse is a compressed file containing all needed packages that can be installed offline.
The PyAEDT wheelhouse can be found on the `Releases <https://github.com/ansys/pyaedt/releases>`_
page. After downloading the wheelhouse specific for your distribution and Python release, unzip it
in a folder and then run this Python command:

.. code:: python

    pip install --no-cache-dir --no-index --find-links=/path/to/pyaedt/wheelhouse pyaedt


Another option for installnig a wheelhouse is to download the
:download:`Python file for installing PyAEDT <../Resources/PyAEDTInstallerFromDesktop.py>`.
You can then run this file directly from AEDT **Script** menu, passing the wheelhouse file as
an argument.




Run PyAEDT
~~~~~~~~~~

COM vs GRPC
-----------
Up until AEDT 2022R2, the method for connecting Python to AEDT-API used COM.
COM is a technology which requires interfaces, classes, objects, and methods to be registered in Windows Registry.
All communication between Python and the AEDT API were translated through an intermediate layer by a
third-party module, pywin32. Usage of this module was limited to the Windows OS only.
Python.NET was added to make the connection to the AEDT API.

In 2022 R2, a new technology, gRPC, was added to replace COM. gRPC is a modern framework
that uses remote procedure calls to communicate with the API.


.. list-table:: GRPC Compatibility Table
   :widths: 25 25 75 75
   :header-rows: 1

   * -
     - <2022 R2
     - 2022 R2
     - >2022 R2
   * - AEDT
     - Only Python,NET
     - gRPC Beta
     - gRPC Available
   * - AEDT
     - Only Python.NET
     - Python.NET default.
       gRPC: pyaedt.settings.use_grpc_api = True
     - gRPC default
       Python.NET: pyaedt.settings.use_grpc_api = False

The preceding options are available only in Windows. Linux uses gRPC in any version as it is the only way to connect
to AEDT API.


How to check that the AEDT API is working and correctly configured
---------------------------------------------------------------------------
To start the AEDT server in gRPC mode, use this syntax:

.. code:: python

   path\to\AnsysEM\v231\Win64\ansysedt.exe -grpcsrv 50001   # Windows
   path/to/AnsysEM/v231/Lin64/ansysedt -grpcsrv 50352       # Linux

The port that the server is running on is the port that AEDT should use to listen and receive
any command from PyAEDT. This allows you to have multiple AEDT sessions running on the same machine
and listening on the same port.

Check that the AEDT gRPC API can run
-------------------------------------------
Native AEDT API commands can be used to launch the AEDT server from the command line.
You can run these commands even without PyAEDT to check that everything is set up correctly, 
including environment variables.

.. code:: python

    import sys
    sys.path.append(r"ANSYSEM_ROOT231\PythonFiles\DesktopPlugin")
    import ScriptEnv
    print(dir())
    ScriptEnv.Initialize("", False, "", 50051)
    print(dir())



Failures in connecting to GRPC API
----------------------------------
On Linux, PyAEDT can fail to initialize a new AEDT session or connect to an existing one.
Here are likely causes:
 - Firewall
 - Proxy
 - Permissions
 - License
 - Scheduler (like LSF) used to launch AEDT 

In case of issues with the proxy, you can try using this environment variable:

.. code:: python

    export no_proxy=localhost,127.0.0.1

If running your PyAEDT script still fails, then try adding this:

.. code:: python

    export http_proxy=

If running your PyAEDT script fails once again, perform these steps:

1. Check that AEDT starts correctly from the command line using the gRPC port option.
2. Enable all debug log variables as shown in the following code so that you can check the logs.

.. code:: python

    export ANSOFT_DEBUG_LOG=/tmp/testlogs/logs/lg
    export ANSOFT_DEBUG_LOG_SEPARATE=1
    export ANSOFT_DEBUG_LOG_TIMESTAMP=1
    export ANSOFT_DEBUG_LOG_THREAD_ID=1
    export ANSOFT_DEBUG_MODE=3


Turn on the gRPC trace on the server side too:

.. code:: python

    export GRPC_VERBOSITY=DEBUG
    export GRPC_TRACE=all

Then start the ``ansysedt.exe`` as file as the gRPC server.

.. code:: python

    ansysedt -grpcsrv 50051

The gRPC trace is printed on the terminal console. Capture the output as the ``server.txt`` file.
In another termina, run these commands:

.. code:: python

    export GRPC_VERBOSITY=DEBUG
    export GRPC_TRACE=all

Run the PyAEDT script, making sure that it is trying to connect to the same port as the gRPC server.
Capture the output as the ``client.txt`` file.
Send all the logs generated to Ansys Support.
