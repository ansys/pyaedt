# Installation

## Summary

PyAEDT is intended to consolidate and extend all existing capital around AEDT-based scripting to allow re-use of existing code, sharing of best practices, and collaboration.

This tool has been tested on HFSS, Icepak, and Maxwell 3D. Basic support is available for EDB and Circuit (Nexxim).

## Requirements

In addition to the runtime dependencies listed in the installation information, EDB Utilities requires ANSYS EM Suite 2019 R3 or later.

## Installing on CPython v3.7-v3.8

Install the prerequisite packages: pythonnet >=2.5 pywin32

.. code:: python

    pip install pyaedt


## Using IronPython in AEDT

1. Download PyAEDT from this link:

   [PyAedt](https://dev.azure.com/EMEA-FES-E/Public-Releases/_packaging?_a=package&feed=PyAedt_Public&package=PyAedt&protocolType=PyPI#)

2. Extract files in the ``AEDT PersonalLib`` folder

3. Run the ``install`` command.
   Note:This command uses the Python user-site convention for package storage. You may substitute an alternative location convention, such as the ``--home`` option rather than the ``--user`` option. You may also a path to the installation folder: ``IRONPYTHONPATH``

.. code:: python

    ipy64 setup.py install --user

## Using Standalone IronPython

Run this command:

.. code:: python

    ipy64 -X:Frames -m pip install pyaedt
