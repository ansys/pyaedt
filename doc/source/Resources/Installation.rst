Installation
============

PyAEDT consolidates and extends all existing capital around scripting for Ansys Electronics Desktop (AEDT), allowing re-use of existing code, sharing of best practices, and collaboration.

This tool has been tested on HFSS, Icepak, and Maxwell 3D. It also provides basic support for EDB and Circuit (Nexxim).

Requirements
~~~~~~~~~~~~
In addition to the runtime dependencies listed in the installation information, PyAEDT requires ANSYS EM Suite 2021 R1 or later.

.. todo::
   Add how to install from the AEDT installer like as in https://mapdldocs.pyansys.com/getting_started/running_mapdl.html


Installing on CPython v3.7-v3.9
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To install the prerequisite packages ``pythonnet`` and ``pywin32``, run this ``install`` command:

.. code:: python

    pip install pyaedt


Using IronPython in AEDT
~~~~~~~~~~~~~~~~~~~~~~~~
To use IronPython in AEDT:

1. Download the PyAEDT package from ``https://pypi.org/project/pyaedt/#files``
2. Extract the files.
3. Run the following command to install PyAEDT into Electronics Desktop (specify the full paths to ipy64 and setup-distutils.py as needed)

``ipy64 setup-distutils.py install --user``

Using Standalone IronPython
~~~~~~~~~~~~~~~~~~~~~~~~~~~
To use standalone IronPython, run this ``install`` command:

.. code:: python

    ipy64 -X:Frames -m pip install pyaedt
