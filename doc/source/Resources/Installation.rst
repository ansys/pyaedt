Installation
=====================

**Summary**
________________________

pyaedt is intended to consolidate and extend all existing capital around AEDT-based scripting to allow re-use of existing code, sharing of best-practice adn collaboration.

This tool has actually been tested on HFSS, Icepak and Maxwell 3D.

Basic support is given for EDB and Circuit (Nexxim)

**Requirements**
________________________
In addition to the runtime dependencies listed in the Installing section below, EDB Utilities requires ANSYS EM Suite 2021 R1 or later.

**Installing on CPython v3.7-v3.8**
________________________________________________

Install Prerequisite packages: pythonnet, pywin32

.. code:: python

    pip install pyaedt


**Using IronPython in AEDT**
________________________________________________
Download pyaedt package
Extract files in AEDT (Ansys Electronics Desktop Framework) PersonalLib folder
Run install command described below

Install command

The below command uses the Python user-site convention for package storage. You may substitute an alternative location convention, such as the --home option instead of --user, and add the installed folder to IRONPYTHONPATH.

.. code:: python

    ipy64 setup.py install --user

**Using Standalone IronPython**
________________________________________________

.. code:: python

    ipy64 -X:Frames -m pip install pyaedt
