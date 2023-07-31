Troubleshooting
===============
This section contains common issues and suggestion around PyAEDT installation and usage.

Installation
~~~~~~~~~~~~

Error installing Python or Conda
--------------------------------
It may happen, that IT Department doesn't allow users to install a Python interpreter in the machine.
In this case user can use the interpreter available in installation path of Ansys Electronics Desktop.
Please note that Python 3.7 is available in AEDT <= 2023R1 while Python 3.10 is available on Ansys Electronics
Desktop 2023 R2.

.. code:: python
   path\to\AnsysEM\v231\commonfiles\CPython\3_7\winx64\Release\python"


Error installing PyAEDT using pip
---------------------------------
1. Check if internet connection is working.
2. Check if firewall allows connections to pypi.com.

In case downloads from pypi are not allowed in your organization try using a wheelhouse.
A wheelhouse is a zip containing all needed packages that can be installed offline.
PyAEDT wheelhouse can be found at `Releases <https://github.com/ansys/pyaedt/releases>`_.
After downloading the wheelhouse zip specific for your distribution and Python release, unzip it in a folder and,
then, run the Python command:

.. code:: python

    pip install --no-cache-dir --no-index --find-links=/path/to/pyaedt/wheelhouse pyaedt


In addition user can install a wheelhouse using the following file
:download:`PyAEDT Installer Python file <../Resources/PyAEDTInstallerFromDesktop.py>`
this can be run directly from AEDT Script menu and the wheelhouse zip file can be passed as an argument.




Run PyAEDT
~~~~~~~~~~

COM vs GRPC
-----------
Up until AEDT 2022R2, the method for connecting Python to AEDT-API used COM.
COM is an a technology which requires interfaces, classes, objects and methods to be registered in Windows Registry.
All communication between Python and AEDT-API were translated through an intermediate layer by a
third party module called pywin32. This module usage was limited to Windows OS only.
PythonNET was added to make the connection to the AEDT-API.
In 2022R2, a new technology was added to replace COM: GRPC. GRPC is a modern remote procedure calls framework
to communicate with the API via remote calls.


.. list-table:: GRPC Compatibility Table
   :widths: 25 25 75 75
   :header-rows: 1

   * -
     - <2022R2
     - 2022R2
     - >2022R2
   * - AEDT
     - Only PythonNET
     - GRPC Beta
     - GRPC Available
   * - AEDT
     - Only PythonNET
     - PythonNET default.
       GRPC: pyaedt.settings.use_grpc_api = True
     - GRPC default
       PythonNET: pyaedt.settings.use_grpc_api = False

Above options are available only in windows. Linux uses grpc in any version as it is the only way to connect
to AEDT API.


How to check that Electronics Desktop API is working and correctly configured
-----------------------------------------------------------------------------
To start Electronics desktop server in grpc mode use the following syntax:

.. code:: python

   path\to\AnsysEM\v231\Win64\ansysedt.exe -grpcsrv 50001   # Windows
   path\to\AnsysEM\v231\Lin64\ansysedt -grpcsrv 50352       # Linux

The number on which the server is running is the port that AEDT should use to listen and receive
any command from PyAEDT. This allows to have multiple AEDT sessions running on the same machine
and listening on the same port.

Check that AEDT GRPC API can run
--------------------------------
Native Electronics Desktop API command can be used to launch Electronics Desktop from command line.
This can be done even without PyAEDT to check that everything is setup correctly and all environment
variables have been correctly setup.

.. code:: python
    import sys
    sys.path.append(r"ANSYSEM_ROOT231\PythonFiles\DesktopPlugin")
    import ScriptEnv
    print(dir())
    ScriptEnv.Initialize("", False, "", 50051)
    print(dir())



Failures in connecting to GRPC API
----------------------------------
On Linux, it may happens that PyAEDT fails to initialize a new session of Electronics Desktop
or to connect to an existing one.
This may be due to:
 - Firewall
 - Proxy
 - Permissions
 - License
 - Scheduler used to launch AEDT like LSF

In case of issues with proxy, you may try the following environment variable:

.. code:: python
    export no_proxy=localhost,127.0.0.1

Run your PyAEDT script. If it still fails, then try:

.. code:: python
    export http_proxy=

Run your PyAEDT script. If the errors still persists, try the following:

1. Check that AEDT starts correctly from command line using grpc port option
2. enable all debug log variables and check logs.

.. code:: python

    export ANSOFT_DEBUG_LOG=/tmp/testlogs/logs/lg
    export ANSOFT_DEBUG_LOG_SEPARATE=1
    export ANSOFT_DEBUG_LOG_TIMESTAMP=1
    export ANSOFT_DEBUG_LOG_THREAD_ID=1
    export ANSOFT_DEBUG_MODE=3


Turn on the GRPC trace on the server side too:

.. code:: python

    export GRPC_VERBOSITY=DEBUG
    export GRPC_TRACE=all

Then start ansysedt.exe as GRPC server.

.. code:: python

    >./ansysedt -grpcsrv 50051

The GRPC trace is printed on the terminal console. Capture the output as the server.txt file.
In another terminal:

.. code:: python

    export GRPC_VERBOSITY=DEBUG
    export GRPC_TRACE=all

Run the PyAedt script(make sure it is trying to connect to the same port as the GRPC server).
Capture the output as the client.txt file. Send all the logs generated to Ansys Support.
