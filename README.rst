PyAEDT
======

Introduction
------------
PyAEDT is intended to consolidate and extend all existing
functionalities around AEDT-based scripting to allow re-use of
existing code, sharing of best-practice and increase collaboration
collaboration.  PyAEDT is licensed under the `MIT License
<https://github.com/pyansys/PyAEDT/blob/main/LICENSE>`_

This tool includes functionality to interact with HFSS, Icepak,
Maxwell 3D, and Q3D.


What is PyAEDT
--------------
PyAEDT is an Python library which interacts directly with the AEDT API
to make scripting simpler for the end user.  It uses an architecture
that can be reused for all 3D tools (Maxwell, Q3D, HFSS, Icepak), and
in future for all other desktop tools. Its classes and methods
structures simplifies operation for end-user while reusing as much as
possible of the information across the API.

.. figure:: https://github.com/pyansys/PyAEDT/raw/main/doc/source/Resources/Items.png
    :width: 600pt

    PyAEDT Architecture Overview for 3D Solvers


Why PyAEDT
----------
Recording and reusing script is a quick and easy approach for
automating simple operations in Desktop UI. However:

- Code recorded is dirty and difficult to read and understand.
- Difficult to reuse and adapt recorded scripts.
- Complex Coding is a need for many global users of AEDT.

Main advantages of PyAEDT are:

- Automatic initialization of all the AEDT Objects (e.g. desktop
  objects like editor, boundaries, etc.)
- Error Management
- Log management
- Variable Management
- Compatibility with IronPython and CPython.
- Simplification of complex API syntax using to Data Objects while
  maintaining PEP8 compliance.
- Code reusability across different solvers.
- Clear documentation on functions and API.
- Unit Test of code to increase quality across different AEDT versions.


.. figure:: https://github.com/pyansys/PyAEDT/raw/main/doc/source/Resources/BlankDiagram3DModeler.png
    :width: 600pt

    PyAEDT Architecture Overview for 3D Solvers

.. figure:: https://github.com/pyansys/PyAEDT/raw/main/doc/source/Resources/BlankDiagram3DLayout.png
    :width: 600pt

    PyAEDT Architecture Overview for HFSS 3DLayout/EDB Solver


.. figure:: https://github.com/pyansys/PyAEDT/raw/main/doc/source/Resources/BlankDiagramCircuit.png
    :width: 600pt

    PyAEDT Architecture Overview for Circuit Solvers (Nexxim/Simplorer)


Example Workflow
----------------
1. Initialize the ``Desktop`` class with the version of AEDT to use.
2. Initialize the application to use within AEDT.


Connect to Desktop from Python IDE
----------------------------------
Work inside Electronics Desktop and as a standalone application.
Detects automatically if running in an IronPython or CPython
environment and initializes Desktop accordingly.  Also provides
advanced error management.  Examples of usage:

Explicit Desktop declaration and error management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    AEDT 2020R1 in Non-Graphical mode will be launched

    from pyaedt. import Desktop, Circuit
    with Desktop("2020.1", NG=True):
        circuit = Circuit()
        ...
        # Any error here will be caught by Desktop...
        ...

    # Desktop is automatically released here


Implicit Desktop Declaration and error management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    Launch the latest version of Desktop in Graphical mode

    from pyaedt import Circuit    
    with Circuit as circuit:
        ...
        # Any error here will be caught by Desktop...
        ...

    # Desktop is automatically released here


Variables
~~~~~~~~~

.. code:: python

    from pyaedt.HFSS import HFSS
    with HFSS as hfss:
         hfss["dim"] = "1mm"   # design variable
         hfss["$dim"] = "1mm"  # project variable


Modeler
~~~~~~~

.. code:: python

    Create a box, assign variables, and assign materials.

    from pyaedt.HFSS import HFSS
    with HFSS as hfss:
         hfss.modeler.primitives.create_box([0, 0, 0], [10, "dim", 10],
                                            "mybox", "aluminum")
