Client-server
=============
You can launch PyAEDT on a remote machine if these conditions are met:

- AEDT and PyAEDT is installed on client and server machines.
- The same Python version is used on the client and server machines. (CPython 3.10+
  is embedded in the AEDT installation.)


gRPC connections
~~~~~~~~~~~~~~~~

In AEDT 2022 R2 and later, PyAEDT fully supports the gRPC API (except for EDB):

.. code:: python

    # Launch the latest installed version of AEDT in graphical mode.
    from ansys.aedt.core import Hfss
    from ansys.aedt.core.generic.settings import settings

    settings.use_grpc_api = True
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


Secure gRPC connections
~~~~~~~~~~~~~~~~~~~~~~~

PyAEDT supports secure gRPC connections using different transport modes:
**WNUA** (Windows), **UDS** (Linux), **mTLS**, or **insecure** modes.

The transport mode depends on whether you are using:

- **Local mode**: Same-machine connections using OS-native secure mechanisms.
- **Client-server mode**: Network connections for local or remote scenarios.

PyAEDT exposes these behaviors through environment variables and runtime settings.

.. warning::
   Secure connections (mTLS, WNUA, UDS) require specific service packs for each version.
   Versions without the required service pack only support insecure mode.

Version and service pack requirements
--------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 20 20 30 30

   * - Version
     - Required SP for Secure
     - Windows (default: **wnua**)
     - Linux (default: **uds**)
   * - 2024 R1 (241)
     - Not supported
     - insecure only
     - insecure only
   * - 2024 R2 (242)
     - **SP05+**
     - insecure, **wnua**, mtls
     - insecure, **uds**, mtls
   * - 2025 R1 (251)
     - **SP04+**
     - insecure, **wnua**, mtls
     - insecure, **uds**, mtls
   * - 2025 R2 (252)
     - **SP04+**
     - insecure, **wnua**, mtls
     - insecure, **uds**, mtls
   * - 2026 R1+ (261+)
     - All service packs
     - insecure, **wnua**, mtls
     - insecure, **uds**, mtls

.. note::
   - Ansys 2024 R1 (241) and earlier versions **only support insecure mode**.
   - If your installation does not have the required service pack listed above,
     only insecure mode is available.
   - To check your service pack version, look at the ``builddate.txt`` file in your
     Ansys installation directory.

Default configuration
---------------------

PyAEDT uses the following default settings::

    settings.grpc_secure_mode = True   # Enables secure connections
    settings.grpc_local = True         # Uses local transport mechanisms

These defaults enable secure, local communication using OS-native mechanisms.

Local mode
----------

When ``grpc_local = True`` (default), PyAEDT uses local inter-process communication
mechanisms optimized for same-machine connections.

WNUA (Windows named user access)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On **Windows**, with default settings (``grpc_secure_mode = True`` and
``grpc_local = True``), PyAEDT uses **WNUA** (Windows Named User Access).

**Characteristics:**

- Enabled by default.
- No additional user configuration required.
- **Local connections only** (same machine).
- Requires required service pack (see table above).

UDS (Unix domain sockets)
^^^^^^^^^^^^^^^^^^^^^^^^^

On **Linux**, with default settings (``grpc_secure_mode = True`` and
``grpc_local = True``), PyAEDT uses **UDS** (Unix Domain Sockets).

**Characteristics:**

- Enabled by default.
- No additional user configuration required.
- **Local connections only** (same machine).
- Requires required service pack (see table above).

Disabling secure local mode
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To disable secure local mode and use insecure transport, set:

    settings.grpc_secure_mode = False

This may be needed for:

- Debugging purposes.
- Compatibility with older service packs.
- Specific network configurations.

Client-server mode
------------------

When ``grpc_local = False``, PyAEDT uses client-server architecture suitable
for both local and remote connections over the network.

Secure client-server: mutual Transport Layer Security (mTLS)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

PyAEDT supports **mutual TLS (mTLS)** for secure client–server communication.
With mTLS, both the client and server authenticate each other using X.509
certificates.

**When mTLS is Used**

mTLS is automatically selected when:

- ``settings.grpc_secure_mode = True`` (default), **AND**
- ``ANSYS_GRPC_CERTIFICATES`` environment variable is set to a valid certificate directory

.. note::
   Setting ``ANSYS_GRPC_CERTIFICATES`` forces mTLS mode regardless of the
   ``grpc_local`` setting.

**Enabling mTLS**

Set the ``ANSYS_GRPC_CERTIFICATES`` environment variable on **both the client
and the server**::

    # Windows
    set ANSYS_GRPC_CERTIFICATES=C:\path\to\certificates

    # Linux
    export ANSYS_GRPC_CERTIFICATES=/path/to/certificates


Insecure client-server mode
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To use insecure client-server mode (no encryption), set::

    settings.grpc_secure_mode = False
    settings.grpc_local = False

This configuration uses standard gRPC without encryption.

Pre-service pack compatibility
------------------------------

For Ansys versions **prior to the required Service Pack** that introduced
updated gRPC arguments, set this environment variable::

    PYAEDT_USE_PRE_GRPC_ARGS=True

**When to Use:**

- Connecting to Ansys installations that predate the updated gRPC interface.
- Ensures compatibility with older gRPC startup arguments.

Configuration summary
---------------------

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Mode
     - Configuration
   * - **Local secure (Default)**
     - ``settings.grpc_secure_mode = True``

       ``settings.grpc_local = True``

   * - **Client-server secure**
     - ``settings.grpc_secure_mode = True``

       ``ANSYS_GRPC_CERTIFICATES=<path>``

       ``settings.grpc_local = False``

   * - **Client-Server insecure**
     - ``settings.grpc_secure_mode = False``

       ``settings.grpc_local = False``

   * - **Local insecure**
     - ``settings.grpc_secure_mode = False``

       Result: Insecure local connection
   * - **Pre-service pack Compatibility**
     - ``PYAEDT_USE_PRE_GRPC_ARGS=True``

Summary of gRPC transport mode selection
----------------------------------------

PyAEDT selects the gRPC transport mode based on this decision tree:

1. **If** ``settings.grpc_secure_mode = False``:

   → Uses **INSECURE** mode (no encryption)

2. **Else if** ``settings.grpc_secure_mode = True`` (default):

   a. **If** ``ANSYS_GRPC_CERTIFICATES`` environment variable **is set**:

      → Uses **mTLS** (mutual TLS with certificates)

      *Applies to both local and client-server modes*

   b. **Else if** ``settings.grpc_local = True`` (default) **AND** ``ANSYS_GRPC_CERTIFICATES`` is **not set**:

      → Uses **WNUA** (Windows) or **UDS** (Linux) for local connections

      *Local mode only - same machine*

   c. **Else** (``grpc_local = False`` **AND** no certificates):

      → Uses **INSECURE** client-server mode


PyAEDT remote service manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PyAEDT includes a service manager that can be run on the server machine and can be
launched on-demand in AEDT sessions and act as a file manager.
You can make a remote application call on a CPython server
or any Windows client machine in AEDT 2022 R2 and later.

On a CPython Server run the ``pyaedt_service_manager`` service that listens on port 17878
for incoming requests of connections from clients. The port is configurable.
Requirements:

- Python 3.10+ Virtual Environment.
- pyaedt > 0.6.0

On Linux, in addition to the preceding requirements, these environments are needed:

- You can use the CPython version in the AEDT installation folder if you first
  add the Python library folder to the ``LD_LIBRARY_PATH`` environment variable.
- You can use the Python 3.10 or later version that is installed.
- You can export ``ANSYSEM_ROOT252=/path/to/AnsysEM/v252/AnsysEM``.
- You can export ``LD_LIBRARY_PATH=$ANSYSEM_ROOT252/common/mono/Linux64/lib:$LD_LIBRARY_PATH``.

On the server, the ``pyaedt_service_manager`` service listen for incoming connections:

.. code:: python

    # Launch PyAEDT remote server on CPython
    from ansys.aedt.core.common_rpc import pyaedt_service_manager

    pyaedt_service_manager()


On any client machine, the user must establish the connection as shown in following example.
AEDT can be launched directly while creating the session or after the connection is established.

.. code:: python

    from ansys.aedt.core.common_rpc import create_session

    # User can establish the connection and start a new AEDT session
    cl1 = create_session(
        "server_name", launch_aedt_on_server=True, aedt_port=17880, non_graphical=True
    )

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

