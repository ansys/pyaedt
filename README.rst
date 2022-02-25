|pypi| |PyPIact| |GH-CI| |codecov| |MIT| |black|


.. |pypi| image:: https://img.shields.io/pypi/v/pyaedt.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/pyaedt/

.. |PyPIact| image:: https://img.shields.io/pypi/dm/pyaedt.svg?label=PyPI%20downloads
   :target: https://pypi.org/project/pyaedt/

.. |GH-CI| image:: https://github.com/pyansys/pyaedt/actions/workflows/unit_tests.yml/badge.svg
   :target: https://github.com/pyansys/pyaedt/actions/workflows/unit_tests.yml

.. |codecov| image:: https://codecov.io/gh/pyansys/pyaedt/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/pyansys/pyaedt

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat
  :target: https://github.com/psf/black
  :alt: black


Introduction
------------
PyAEDT is part of the larger `PyAnsys <https://docs.pyansys.com>`_
effort to facilitate the use of Ansys technologies directly from Python.

PyAEDT is intended to consolidate and extend all existing
functionalities around scripting for Ansys Electronics Desktop (AEDT)
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
- EDB Database
- Twin Builder

What is PyAEDT?
---------------
PyAEDT is a Python library that interacts directly with the AEDT API
to make scripting simpler for the end user. Its architecture
can be reused for all AEDT 3D products (HFSS, Icepak, Maxwell 3D, and
Q3D), 2D tools, and Ansys Mechanical. It also provides support for circuit tools like
Nexxim and system simulation tools like Twin Builder. Finally it provides scripting 
capabilities in Ansys layout tools like HFSS 3D Layout and EDB. Its class and method
structures simplify operation for the end user while reusing information as much as
possible across the API.

Documentation and Issues
------------------------
In addition to installation, usage, and contribution information, the PyAEDT
documentation provides `API documentation <https://aedtdocs.pyansys.com/API/>`_,
`examples <https://aedtdocs.pyansys.com/examples/index.html>`_, and `code guidelines 
<https://aedtdocs.pyansys.com/Resources/Code_Guidelines.html>`_.

On the `PyAEDT Issues <https://github.com/pyansys/PyAEDT/issues>`_ page, you can
create issues to submit questions, report bugs, and request new features. To reach
the project support team, email `pyansys.support@ansys.com <pyansys.support@ansys.com>`_.

Dependencies
------------
To run PyAEDT, you must have a local licenced copy of AEDT.
PyAEDT supports AEDT versions 2021 R1 or newer.

Student Version
---------------

PyAEDT supports AEDT Student version 2021 R2. For more information, see
`Student Version page <https://www.ansys.com/academic/students/ansys-e
lectronics-desktop-student>`_.


Why PyAEDT?
-----------
A quick and easy approach for automating a simple operation in the 
AEDT UI is to record and reuse a script. However, disadvantages of 
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
environment and initializes AEDT accordingly. PyAEDT also
provides advanced error management. Usage examples follow.

Explicit Desktop Declaration and Error Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    Launch AEDT 2021 R1 in non-graphical mode

    from pyaedt import Desktop, Circuit
    with Desktop(specified_version="2021.1",
                 non_graphical=False, new_desktop_session=True,
                 close_on_exit=True, student_version=False):
        circuit = Circuit()
        ...
        # Any error here will be caught by Desktop.
        ...

    # Desktop is automatically released here.


Implicit Desktop Declaration and Error Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    # Launch the latest installed version of AEDT in graphical mode

    from pyaedt import Circuit
    with Circuit(specified_version="2021.2",
                 non_graphical=False) as circuit:
        ...
        # Any error here will be caught by Desktop.
        ...

    # Desktop is automatically released here.


Remote Application Call
~~~~~~~~~~~~~~~~~~~~~~~
You can make a remote application call on a CPython server
or any Windows client machine.

On a CPython Server:

.. code:: python

    Launch PyAEDT remote server on CPython

    from pyaedt.common_rpc import launch_server
    launch_server()


On any Windows client machine:

.. code:: python

    from pyaedt.common_rpc import client
    cl1 = client("server_name")
    hfss = cl1.root.hfss()
    # your code here

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

    # Create a box, assign variables, and assign materials.

    from pyaedt.hfss import Hfss
    with Hfss as hfss:
         hfss.modeler.create_box([0, 0, 0], [10, "dim", 10],
                                 "mybox", "aluminum")

License
-------
PyAEDT is licensed under the MIT license.

This module makes no commercial claim over Ansys whatsoever.
PyAEDT extends the functionality of AEDT by adding
an additional Python interface to AEDT without changing the core
behavior or license of the original software. The use of the
interactive control of PyAEDT requires a legally licensed
local copy of AEDT. For more information about AEDT, 
visit the `AEDT page <https://www.ansys.com/products/electronics>`_ 
on the Ansys website.
