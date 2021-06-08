Introduction
------------
PyAEDT is intended to consolidate and extend all existing
functionalities around AEDT-based scripting to allow reuse of
existing code, sharing of best practices, and increased collaboration.
PyAEDT is licensed under the `MIT License
<https://github.com/pyansys/PyAEDT/blob/main/LICENSE>`_.

This tool includes functionality to interact with these AEDT tools: HFSS, Icepak,
Maxwell 3D, and Q3D.

What is PyAEDT?
-----------------
PyAEDT is a Python library that interacts directly with the AEDT API
to make scripting simpler for the end user.  It uses an architecture
that can be reused for all AEDT 3D tools (HFSS, Icepak, Maxwell 3D, and Q3D) and,
in the future, for all other AEDT tools. Its class and method
structures simplify operation for the end user while reusing information as much as
possible across the API.

This figure shows an overview of the pyAEDT architecture for 3D solvers:

.. figure:: https://aedtdocs.pyansys.com/_images/Items.png
    :width: 600pt

    PyAEDT Architecture Overview for 3D Solvers

Documentation and Issues
-----------------------------------
See the `Documentation <https://aedtdocs.pyansys.com>`_ page for more
details, and the `Examples gallery
<https://aedtdocs.pyansys.com/examples/index.html>`_ for some
examples.

Please feel free to post issues and other questions at `PyAedt Issues
<https://github.com/pyansys/pyaedt/issues>`_.  This is the best place
to post questions and code.


Project Transition - Legacy Support
-------------------------------------
This project was formerly known as AEDTLib, and we'd like to thank all the early adopters, contributors, and users who submitted issues, gave feedback, and contributed code through the years. The pyaedt project has been taken up Ansys and will be leveraged in creating new Pythonic, cross-platform, and multi-language service based interfaces for Ansys's products. Your contributions to PyAEDT have shaped it into a better solution.



Dependencies
------------
You will need a local licenced copy of Ansys Electronics Desktop to run pyaedt prior and including 2021R1.

Why PyAEDT?
------------
Recording and reusing script is a quick and easy approach for
automating simple operations in the AEDT UI. However, disadvantages of this approach are:

- The code recorded is dirty and difficult to read and understand.
- Recorded scripts are difficult to reuse and adapt.
- Complex coding is required by many global users of AEDT.

The main advantages of PyAEDT are:

- Automatic initialization of all AEDT objects, such as desktop
  objects like the editor, boundaries, and so on)
- Error management
- Log management
- Variable management
- Compatibility with IronPython and CPython
- Simplification of complex API syntax using data objects while
  maintaining PEP8 compliance.
- Code reusability across different solvers
- Clear documentation on functions and API
- Unit test of code to increase quality across different AEDT versions

This figure shows an overview of the PyAEDT architecture for 3D solvers:

.. figure:: https://aedtdocs.pyansys.com/_images/BlankDiagram3DModeler.png
    :width: 600pt

This figure shows an overview of the PyAEDT architecture for the HFSS 3DLayout and EDB solver:

.. figure:: https://aedtdocs.pyansys.com/_images/BlankDiagram3DLayout.png
    :width: 600pt

This figure shows an overview of the PyAEDT architecture for Circuit solvers (Simplorer and Nexxim):

.. figure:: https://aedtdocs.pyansys.com/_images/BlankDiagramCircuit.png
    :width: 600pt


Example Workflow
-----------------
1. Initialize the ``Desktop`` class with the version of AEDT to use.
2. Initialize the application to use within AEDT.


Connect to Desktop from Python IDE
----------------------------------
PyAEDT works inside AEDT and as a standalone application.
It automatically detects whether it is running in an IronPython or CPython
environment and initializes the Desktop accordingly.  PyAEDT also provides
advanced error management.  Usage examples follow.

Explicit Desktop declaration and error management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    AEDT 2020R1 in Non-Graphical mode will be launched

    from pyaedt import Desktop, Circuit
    with Desktop("2020.1", NG=True):
        circuit = Circuit()
        ...
        # Any error here will be caught by Desktop...
        ...

    # Desktop is automatically released here


Implicit Desktop declaration and error management
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

    from pyaedt.hfss import Hfss
    with Hfss as hfss:
         hfss.modeler.primitives.create_box([0, 0, 0], [10, "dim", 10],
                                            "mybox", "aluminum")

License
-------
``PyAEDT`` is licensed under the MIT license.

This PyAEDT module makes no commercial claim over Ansys
whatsoever.  This tool extends the functionality of AEDT by adding
an additioanl Python interface to AEDT without changing the core
behavior or license of the original software.  The use of the
interactive APDL control of PyAEDT requires a legally licensed
local copy of AEDT.

To purchase AEDT, please visit `Ansys <https://www.ansys.com/>`_.
