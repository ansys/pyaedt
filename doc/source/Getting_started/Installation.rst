Installation
============
PyAEDT consolidates and extends all existing capital around scripting for AEDT,
allowing reuse of existing code, sharing of best practices, and collaboration.

This PyAnsys library has been tested on HFSS, Icepak, and Maxwell 3D. It also provides
basic support for EDB and Circuit (Nexxim).

Requirements
~~~~~~~~~~~~
In addition to the runtime dependencies listed in the installation information, PyAEDT
requires Ansys Electronics Desktop (AEDT) 2022 R1 or later. The AEDT Student Version is also supported.


.. _install-from-pyaedt-installer:

Install from PyAEDT installer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The following Python script automatically installs PyAEDT from AEDT,
using the CPython interpreter included in the AEDT installation.

In order to do that you can:

- Download the following file: :download:`PyAEDT Installer Python file <../Resources/pyaedt_installer_from_aedt.py>`

- Open an Electronics Desktop Session and click on Tools->Run Script and execute the file.

- Offline installation is also possible using wheelhouses.

.. note::
    A wheelhouse is a zip containing all needed packages that can be installed offline.
    PyAEDT wheelhouse can be found at `Releases <https://github.com/ansys/pyaedt/releases>`_.
    After downloading the wheelhouse zip specific for your distribution and Python release,
    run the script from Electronics Desktop using the zip full path as argument.
    Please note that AEDT 2023 R1 and lower requires Python 3.7 wheelhouse while AEDT 2023 R2
    and higher requires the Python 3.10 wheelhouse.

.. image:: ../Resources/wheelhouse_installation.png
  :width: 800
  :alt: PyAEDT run script

Starting from 2023R2, panels are available in the Automation Tab. For detailed information about
PyAEDT panels, see :doc:`panels`.

.. image:: ../Resources/toolkits_ribbon.png
  :width: 800
  :alt: PyAEDT toolkit panels available in AEDT

If you have installation problems, visit :ref:`Troubleshooting<panel_error>`.

You can watch the following video to see how to install PyAEDT:

.. raw:: html

  <iframe width="560" height="315" src="https://www.youtube.com/embed/c-zl8iMjP4M?si=zpdREiZhzODW-kW1" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>


.. _pyaedt_bundled_aedt:

PyAEDT bundled with AEDT (2026 R2 service pack 2)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Starting with AEDT 2026 R2 service pack 2, PyAEDT ships as part of the AEDT installation.
This bundled PyAEDT only includes the main runtime dependencies (no optional extras).

If you need to update PyAEDT or install extra dependencies, install PyAEDT into your own
virtual environment as described in the other sections of this page (for example,
:ref:`Install on CPython from PyPI <install-on-cpython-from-pypi>`), or use the
:ref:`PyAEDT installer script <install-from-pyaedt-installer>`.

In addition, the **Extension Manager** can be installed using the bundled PyAEDT directly
from the PyAEDT Console in AEDT by running:

.. code:: python

    from ansys.aedt.core.extensions.installer.pyaedt_installer import add_extension_manager

    add_extension_manager("YourPersonalLibPath")

Replace ``"YourPersonalLibPath"`` with the full path of your ``PersonalLib`` (or ``syslib``)
as configured in AEDT.


.. _extension_manager:

Extension manager
~~~~~~~~~~~~~~~~~

The **PyAEDT Extension Manager** provides a centralized interface for accessing, launching, and managing automation workflows directly within AEDT.

From this window, you can:

- Browse and launch **project-level toolkits** organized by design type.
- Add **custom extensions** from your local environment.
- Control whether extensions appear in the **AEDT Automation ribbon** for quick access.

There are three types of extensions supported:

- **Pre-installed extensions** already available in the PyAEDT library.

- **Open source PyAEDT toolkits** described in the `PyAEDT Common Toolkit documentation <https://aedt.common.toolkit.docs.pyansys.com/>`_.

- **Custom PyAEDT extensions**.

See `Extension Manager <https://aedt.docs.pyansys.com/version/stable/User_guide/extensions.html>`_ for more information.

.. image:: ../Resources/extension_manager_1.png
  :width: 800
  :alt: PyAEDT toolkit manager 1

Each extension tile shows its name, icon, and a **Launch** button.
Extensions that are not currently linked to the AEDT ribbon show a muted icon.
Pinned extensions are marked and appears in the corresponding AEDT design ribbon tab.


Selecting the **Custom** tile in the Extension Manager opens a dialog where you can add your own PyAEDT-based extension.

.. image:: ../Resources/extension_manager_2.png
  :width: 400
  :alt: PyAEDT toolkit manager 2

In the dialog, you can:

- **Browse for a Python script** that implements the extension behavior.
- **Optionally leave the script path empty**. If no script is provided, a default extension script is automatically generated using a predefined template.

You must also specify an **Extension Name**, which appears in the AEDT Automation.

Once configured, click **OK** to register the extension. It then appears alongside other extensions in the manager interface.

A message bar at the bottom provides real-time feedback about actions, such as launching extensions or errors.

For additional information about AEDT extensions,
see `Extensions <https://aedt.docs.pyansys.com/version/stable/User_guide/extensions.html>`_.

.. raw:: html

  <iframe width="560" height="315" src="https://www.youtube.com/embed/Et-mLCzaGno?si=TBzxvkhqg6Ep0_yR" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>


Version manager
~~~~~~~~~~~~~~~
The **Version manager** extension allows users to manage and update **PyAEDT** and **PyEDB** installations.

There are several available options:

- **Display environment details**:
  - Python virtual environment path
  - Python version
  - Installed versions of PyAEDT and PyEDB

- **Check latest releases on PyPI**:
  - View the most recent versions of PyAEDT and PyEDB available on PyPI

- **Update from PyPI**:
  - Install the latest official release of PyAEDT and PyEDB from PyPI

- **Install from a GitHub branch**:
  - Uses the `main` development branch by default
  - Other existing branch names can be specified

- **Update from a local wheelhouse**:
  - Automatically checks compatibility before installation

- **Reset and update PyAEDT panels in AEDT**:
  - Direct access to reset and update options within the AEDT interface

.. image:: ../Resources/version_manager_ui.png
  :width: 800
  :alt: PyAEDT version manager


.. _install-on-cpython-from-pypi:

Install on CPython from PyPI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can install PyAEDT on CPython from PyPI:

.. code:: bash

    pip install pyaedt

You can also install PyAEDT from Conda-Forge:

.. code:: bash

    conda install -c conda-forge pyaedt

To ensure you have all the necessary dependencies, including optional components, use the following command:

.. code:: bash

    pip install pyaedt[all]

If you are not utilizing gRPC, you can install the required dotnet dependencies separately:

.. code:: bash

    pip install pyaedt[dotnet]

Finally, in the Python console, run the following commands:

.. code:: python

    from ansys.aedt.core.extensions.installer.pyaedt_installer import add_pyaedt_to_aedt

    add_pyaedt_to_aedt("path_to_aedtlib")

- Replace "your_aedt_version" with the version of AEDT you are using (for example "2026.1").
- Replace "path_to_aedtlib" with the full path of your PersonalLib or syslib as specified in AEDT.
- If you use your PersonalLib, the PyAEDT icons are installed at user level in the AEDT ribbon.
- If you use the syslib, the PyAEDT icons are installed at application level in the AEDT ribbon.
- You can skip the installation of the version manager by specifying the extra argument skip_version_manager=True:

  .. code::

      add_pyaedt_to_aedt(r“path_to_aedtlib", skip_version_manager=True)

.. note::
  If you created your own virtual environment and you are managing a centralized installation of pyAEDT,
  it is better to do not install the version manager.


Linux support
~~~~~~~~~~~~~

PyAEDT works with CPython 3.10 through 3.13 on Linux in AEDT 2022 R2 and later.
However, you must set up the following environment variables before launching Python.
Replace the version number and path with your actual AEDT installation:

.. code:: bash

    export ANSYSEM_ROOT261=/path/to/AnsysEM/v261/AnsysEM
    export LD_LIBRARY_PATH=$ANSYSEM_ROOT261:$LD_LIBRARY_PATH

The version suffix in ``ANSYSEM_ROOT<XYZ>`` must match your installed AEDT release
(for example, ``251`` for 2025 R1, ``252`` for 2025 R2, ``261`` for 2026 R1).
The default installation path on Linux is typically
``/opt/AnsysEM/v<XYZ>/AnsysEM`` or ``/usr/ansys_inc/v<XYZ>/AnsysEM``.

.. note::

    On some Linux distributions (such as RHEL/CentOS 8), the ``ss`` utility used
    for session discovery lives in ``/usr/sbin/ss``, which may not be included in
    ``$PATH`` by default for non-root users. PyAEDT automatically probes
    ``/usr/sbin/ss`` and falls back to reading ``/proc/net/unix`` directly, so
    session detection works in most cases without any configuration changes.

    If you still experience issues with PyAEDT opening a new AEDT session instead
    of connecting to an existing one, you can add ``/usr/sbin`` to your ``$PATH``
    permanently:

    .. code::

        echo 'export PATH=$PATH:/usr/sbin' >> ~/.bashrc
        source ~/.bashrc


Install offline from a wheelhouse
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Using a wheelhouse can be helpful if you work for a company that restricts access to external networks.

Wheelhouses for CPython 3.10, 3.11, 3.12, 3.13 and 3.14 are available in the releases for both Windows and Linux.
From the `Releases <https://github.com/ansys/pyaedt/releases>`_
page in the PyAEDT repository, you can find the wheelhouses for a particular release in its
assets and download the wheelhouse specific to your setup.

You can then install PyAEDT and all of its dependencies from one single entry point that can be shared internally,
which eases the security review of the PyAEDT package content.

For example, on Windows with Python 3.10, install PyAEDT and all its dependencies from a wheelhouse with code like this:

.. code::

    pip install --no-cache-dir --no-index --find-links=file:///<path_to_wheelhouse>/PyAEDT-v<release_version>-wheelhouse-Windows-3.10 pyaedt[all]

Finally, in the Python console, run the following commands:

.. code::

     from ansys.aedt.core.extensions.installer.pyaedt_installer import add_pyaedt_to_aedt
     add_pyaedt_to_aedt(r“path_to_aedtlib")

- Replace "your_aedt_version" with the version of AEDT you are using (for example "2026.1").
- Replace "path_to_aedtlib" with the full path of your PersonalLib or syslib as specified in AEDT, depending if you want to install the PyAEDT icons at user level or application level.
- You can skip the installation of the version manager by specifying the extra argument skip_version_manager=True:

  .. code::

      add_pyaedt_to_aedt(r“path_to_aedtlib", skip_version_manager=True)


Using uv to manage virtual environments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The project and the PyAEDT installer support using the `uv` tool to manage
package installation and speed up installs.
`uv` can be used inside a virtual environment to perform pip installs, to
install from local wheelhouses, and to improve reliability for long-running
package downloads.

You can use `uv` to install PyAEDT into your own virtual environment. The
steps below show how to create a virtual environment, activate it, install `uv`, and then
install PyAEDT. Examples are provided for Windows (PowerShell) and Linux (bash).


Create and activate a virtual environment (Windows - PowerShell)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code:: powershell

    python -m venv C:\path\to\pyaedt_venv
    C:\path\to\pyaedt_venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    pip install uv
    uv pip install pyaedt[all]


Create and activate a virtual environment (Linux)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code:: bash

    python3 -m venv ~/pyaedt_venv
    source ~/pyaedt_venv/bin/activate
    python -m pip install --upgrade pip
    pip install uv
    uv pip install pyaedt[all]

.. note::
  Virtual environments should be created with `venv` and not directly with `uv` to avoid potential issues.


Installing from a wheelhouse using uv
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you need to install from an offline wheelhouse, install `uv` and then use
it to perform an offline install from the wheelhouse directory. Example (Windows):

.. code:: powershell

    pip install --no-cache-dir --no-index --find-links=file:///<path_to_wheelhouse> uv
    uv pip install --no-cache-dir --no-index --find-links=file:///<path_to_wheelhouse> pyaedt[all]

Example (Linux):

.. code:: bash

    pip install --no-cache-dir --no-index --find-links=file:///<path_to_wheelhouse> uv
    uv pip install --no-cache-dir --no-index --find-links=file:///<path_to_wheelhouse> pyaedt[all]


After installation
~~~~~~~~~~~~~~~~~~
Once PyAEDT is installed in your virtual environment, you can run the
`add_pyaedt_to_aedt` helper to register the toolkits in AEDT (if applicable):

.. code:: python

    from ansys.aedt.core.extensions.installer.pyaedt_installer import add_pyaedt_to_aedt

    add_pyaedt_to_aedt(r"path_to_aedtlib")

Note
~~~~
- Using `uv` inside a virtual environment improves installation reliability and
  supports installation from offline wheelhouses.
- If you manage a centralized installation or custom virtual environments, you
  may choose to skip installing the Version Manager when linking PyAEDT into
  AEDT (see `add_pyaedt_to_aedt` options).


Install PyAEDT in Conda virtual environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Create virtual environment

.. code:: bash

    conda create --name pyaedt_py310 python=3.10

Activate virtual environment

.. code:: bash

    conda activate pyaedt_py310

You can also install PyAEDT from Conda-Forge with this command:

.. code:: bash

    conda install -c conda-forge pyaedt


Upgrade PyAEDT to the latest version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    pip install -U pyaedt
