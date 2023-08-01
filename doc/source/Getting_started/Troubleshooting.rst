Troubleshooting
===============
This section contains common issues and suggestions related to installation and use of PyAEDT.

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
1. **Proxy Server** If your company uses a proxy server you may have to update some settings at the command line.
   See the `pip documentation <https://pip.pypa.io/en/stable/user_guide/#using-a-proxy-server>`_ for details.
2. **Install Permission** Make sure you have write access to the directory where the Python interpreter is
   installed.  This is more reason to use a `virtual environment <https://docs.python.org/3/library/venv.html>`_.
3. **Firewall** Some corporate firewalls may block pip. If you face this issue you'll have to work with your IT
   administrator to enable pip. The proxy server settings (described above) allow you to explicitly define
   the ports used by pip.

If downloads from `pypi <https://pypi.org/>`_ are not allowed, you may use a
`wheelhouse <https://pypi.org/project/Wheelhouse/>`_.
The wheelhouse file contains all dependencies for pyaedt and allows full installation without a need to
download additional files.
The wheelhouse for PyAEDT can be found `here <https://github.com/ansys/pyaedt/releases>`_.
After downloading the wheelhouse for your distribution and Python release, unzip the file to a folder and
run the Python command:

.. code:: pycon

    >>> pip install --no-cache-dir --no-index --find-links=/path/to/pyaedt/wheelhouse pyaedt


Another option to install PyAedt from the wheelhouse is to download the following file
:download:`PyAEDT Installer Python file <../Resources/PyAEDTInstallerFromDesktop.py>`.
Run this script directly from AEDT and pass the wheelhouse file name as an argument.




Run PyAEDT
~~~~~~~~~~

COM vs GRPC
-----------
Prior to the 2022R2 release CPython automation in AEDT used
`COM <https://learn.microsoft.com/en-us/windows/win32/com/com-objects-and-interfaces>`_  which
requires all interfaces to be registered in the Windows Registry.
Communication between Python and the AEDT API were translated through an intermediate layer using
`pywin32 <https://github.com/mhammond/pywin32>`_. The recent addition of
`PythonNET <https://pythonnet.github.io/pythonnet/>`_ improves
cross-platform support and the COM interface is replaced by `GRPC <https://grpc.io/>`_,
for 2022R2 and later.


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

The options shown here apply only to the Windows platform.
On Linux, the Python interface to AEDT uses GRPC for all versions.


Check the Electronics Desktop API configuration
-----------------------------------------------------
To start the Electronics Desktop server in GRPC mode use the following syntax:

.. code:: bat
   :caption: Windows

   path\to\AnsysEM\v231\Win64\ansysedt.exe -grpcsrv 50001

.. code:: console
   :caption: Linux

   path\to\AnsysEM\v231\Lin64\ansysedt -grpcsrv 50352

The server port number is used by AEDT to listen and receive
commands from PyAEDT client instances. This configuration
supports multiple sessions of AEDT running on a single server
and listening on the same port.

Check the GRPC Interface
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

.. code:: console

    export no_proxy=localhost,127.0.0.1

Run your PyAEDT script. If it still fails, the proxy server can be disabled using

.. code:: console

    export http_proxy=

Run your PyAEDT script. If the errors still persists, try the following:

1. Check that AEDT starts correctly from command line using GRPC port option
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

    ansysedt -grpcsrv 50051

The GRPC trace is printed on the terminal console. Capture the output as the server.txt file.
In another terminal:

.. code:: python

    export GRPC_VERBOSITY=DEBUG
    export GRPC_TRACE=all

Run the PyAEDT script(make sure it is trying to connect to the same port as the GRPC server).
Capture the output as the client.txt file. Send all the logs generated to Ansys Support.
