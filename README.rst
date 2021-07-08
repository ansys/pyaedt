Introduction
------------
PyAEDT is intended to consolidate and extend all existing
functionalities around scripting for Ansys Electronics Dekstop (AEDT)
to allow reuse of existing code, sharing of best practices, and increased
collaboration. PyAEDT is licensed under the `MIT License
<https://github.com/pyansys/PyAEDT/blob/main/LICENSE>`_.

PyAEDT includes functionality for interacting with the following AEDT tools and Ansys products:

- HFSS and HFSS 3D Layout
- Icepak
- Maxwell 2D/3D and RMxprt
- Q3D/2DExtractor
- Mechanical
- Nexxim
- Simplorer
- EDB Database

What is PyAEDT?
---------------
PyAEDT is a Python library that interacts directly with the AEDT API
to make scripting simpler for the end user.  It uses an architecture
that can be reused for all AEDT 3D products (HFSS, Icepak, Maxwell 3D,
Q3D and Mechanical) as well as 2D tools and circuit tools like
Nexxim and Simplorer. Finally it provides scripting capabilities in Ansys
layout tools like HFSS 3D Layout and EDB. Its class and method structures simplify
operation for the end user while reusing information as much as
possible across the API.

Documentation and Issues
------------------------
See the `API Documentation <https://aedtdocs.pyansys.com/API/API.html>`_ page for more
details and the `Examples gallery
<https://aedtdocs.pyansys.com/examples/index.html>`_ for some
examples.

To post issues, questions, and code, go to `PyAEDT Issues
<https://github.com/pyansys/PyAEDT/issues>`_.


Project Transition - Legacy Support
-----------------------------------
This project was formerly known as AEDTLib.
Thanks to all early adopters, contributors, and users who submitted issues,
gave feedback, and contributed code through the years.

With PyAEDT, Ansys is leveraging its ability to create new Pythonic,
cross-platform, and multi-language service-based interfaces for Ansys products.
Your contributions to PyAEDT will help shape PyAEDT into a better solution.


Dependencies
------------
To run PyAEDT, you must have a local licenced copy of AEDT.
PyAEDT supports AEDT versions prior to and including 2021 R1.

Why PyAEDT?
-----------
A quick and easy approach for automating a simple operation in the 
AEDT UI is to record and reuse a scripts. However, disadvantages of 
this approach are:

- Recorded code is dirty and difficult to read and understand.
- Recorded scripts are difficult to reuse and adapt.
- Complex coding is required by many global users of AEDT.

The main advantages of PyAEDT are:

- Automatic initialization of all AEDT objects, such as desktop
  objects like the editor, boundaries, and so on
- Error management
- Log management
- Variable management
- Compatibility with IronPython and CPython
- Simplification of complex API syntax using data objects while
  maintaining PEP8 compliance.
- Code reusability across different solvers
- Clear documentation on functions and API
- Unit tests of code to increase quality across different AEDT versions


Example Workflow
-----------------
1. Initialize the ``Desktop`` class with the version of AEDT to use.
2. Initialize the application to use within AEDT.


Connect to Desktop from Python IDE
----------------------------------
PyAEDT works both inside AEDT and as a standalone application.
It automatically detects whether it is running in an IronPython or CPython
environment and initializes the Desktop accordingly. PyAEDT also provides
advanced error management. Usage examples follow.

Explicit Desktop declaration and error management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    Launch AEDT 2021 R1 in Non-Graphical mode

    from pyaedt import Desktop, Circuit
    with Desktop("2021.1", NG=True):
        circuit = Circuit()
        ...
        # Any error here will be caught by Desktop.
        ...

    # Desktop is automatically released here.


Implicit Desktop declaration and error management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    Launch the latest installed version of AEDT in graphical mode

    from pyaedt import Circuit    
    with Circuit() as circuit:
        ...
        # Any error here will be caught by Desktop.
        ...

    # Desktop is automatically released here.


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
PyAEDT is licensed under the MIT license.

This PyAEDT module makes no commercial claim over Ansys
whatsoever. PyAEDT extends the functionality of AEDT by adding
an additional Python interface to AEDT without changing the core
behavior or license of the original software. The use of the
interactive APDL control of PyAEDT requires a legally licensed
local copy of AEDT. For more information about AEDT, 
visit `Ansys <https://www.ansys.com/products/electronics>`_.
