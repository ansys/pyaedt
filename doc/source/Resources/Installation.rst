Installation
============

PyAEDT consolidates and extends all existing capital around scripting for Ansys Electronics Desktop (AEDT), allowing re-use of existing code, sharing of best practices, and collaboration.

This tool has been tested on HFSS, Icepak, and Maxwell 3D. It also provides basic support for EDB and Circuit (Nexxim).

Requirements
~~~~~~~~~~~~
In addition to the runtime dependencies listed in the installation information, EDB Utilities requires ANSYS EM Suite 2021 R1 or later.

Installing on CPython v3.7-v3.8
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To install the prerequisite packages ``pythonnet`` and ``pywin32``, run this ``install`` command:

.. code:: python

    pip install pyaedt


Using IronPython in AEDT
~~~~~~~~~~~~~~~~~~~~~~~~
To use IronPython in AEDT:

1. Download the PyAEDT package from ``https://pypi.org/project/pyaedt/#files``
2. Extract the files.
3. Copy pyaedt folder to the ``PersonalLib`` folder of the AEDT framework.
4. Run Aedt

If you don't know which is current ``PersonalLib`` folder:
    - run AEDT
    - go to Tools-> Options -> General Options
    - Select Directories Menus
    - View and Set your PersonalLib Folder

Using Standalone IronPython
~~~~~~~~~~~~~~~~~~~~~~~~~~~
To use standalone IronPython, run this ``install`` command:

.. code:: python

    ipy64 -X:Frames -m pip install pyaedt
