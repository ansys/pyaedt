Installation
============
PyAEDT consolidates and extends all existing capital around scripting for AEDT,
allowing re-use of existing code, sharing of best practices, and collaboration.

This PyAnsys library has been tested on HFSS, Icepak, and Maxwell 3D. It also provides
basic support for EDB and Circuit (Nexxim).

Requirements
~~~~~~~~~~~~
In addition to the runtime dependencies listed in the installation information, PyAEDT
requires Ansys Electronics Desktop (AEDT) 2022 R1 or later. The AEDT Student Version is also supported.


Install from PyAEDT installer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The following python script automatically installs PyAEDT from AEDT,
using the CPython interpreter included in the AEDT installation.

In order to do that you can:

- Download the following file: :download:`PyAEDT Installer Python file <../Resources/PyAEDTInstallerFromDesktop.py>`

- Open an Electronics Desktop Session and click on Tools->Run Script and execute the file.

- Offline install is also possible using wheelhouses.

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

Starting from 2023R2, buttons are available in the Automation Tab as in the example below.

.. image:: ../Resources/toolkits_ribbon.png
  :width: 800
  :alt: PyAEDT toolkit buttons available in AEDT


Toolkit Manager
~~~~~~~~~~~~~~~
The user can install or uninstall automated workflows using the toolkit manager.
There are three options:

- Custom PyAEDT scripts.

- Internal PyAEDT scripts. Existing workflows in the PyAEDT library.

- Open source PyAEDT toolkits. Open source PyAEDT toolkits following the `common library <https://aedt.common.toolkit.docs.pyansys.com/>`_ standard.

.. image:: ../Resources/toolkit_manager_1.png
  :width: 800
  :alt: PyAEDT toolkit manager 1

The user can select the AEDT application to install the specific workflow.

.. image:: ../Resources/toolkit_manager_2.png
  :width: 400
  :alt: PyAEDT toolkit manager 2


Install on CPython from PyPI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can install PyAEDT on CPython 3.7 through 3.10 from PyPI:

.. code:: python

    pip install pyaedt

You can also install PyAEDT from Conda-Forge:

.. code:: python

    conda install -c conda-forge pyaedt

To ensure you have all the necessary dependencies, including optional components, use the following command:

.. code:: python

    pip install pyaedt[all]

If you are not utilizing gRPC, you can install the required dotnet dependencies separately:

.. code:: python

    pip install pyaedt[dotnet]


Linux support
~~~~~~~~~~~~~

PyAEDT works with CPython 3.7 through 3.10 on Linux in AEDT 2022 R2 and later.
However, you must set up the following environment variables:

.. code::

    export ANSYSEM_ROOT222=/path/to/AedtRoot/AnsysEM/v222/Linux64
    export LD_LIBRARY_PATH=$ANSYSEM_ROOT222/common/mono/Linux64/lib64:$ANSYSEM_ROOT222/Delcross:$LD_LIBRARY_PATH


Install offline from a wheelhouse
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Using a wheelhouse can be helpful if you work for a company that restricts access to external networks.
Wheelhouses for CPython 3.7, 3.8, and 3.9 are available in the releases for PyAEDT v0.4.70
and later for both Windows and Linux. From the `Releases <https://github.com/ansys/pyaedt/releases>`_
page in the PyAEDT repository, you can find the wheelhouses for a particular release in its
assets and download the wheelhouse specific to your setup.

You can then install PyAEDT and all of its dependencies from one single entry point that can be shared internally,
which eases the security review of the PyAEDT package content.

For example, on Windows with Python 3.7, install PyAEDT and all its dependencies from a wheelhouse with code like this:

.. code::

    pip install --no-cache-dir --no-index --find-links=file:///<path_to_wheelhouse>/PyAEDT-v<release_version>-wheelhouse-Windows-3.7 pyaedt


Use IronPython in AEDT
~~~~~~~~~~~~~~~~~~~~~~
PyAEDT is designed to work in CPython 3.7+ and supports many advanced processing packages like
``matplotlib``, ``numpy``, and ``pyvista``. A user can still use PyAEDT in the IronPython
environment available in AEDT with many limitations.

To use IronPython in AEDT:

1. Download the PyAEDT package from ``https://pypi.org/project/pyaedt/#files``.
2. Extract the files.
3. Install PyAEDT into AEDT, specifying the full paths to ``ipy64`` and ``setup-distutils.py`` as needed:

.. code::

    ipy64 setup-distutils.py install --user


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
