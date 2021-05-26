.. pyaedt documentation master file, created by
   sphinx-quickstart on Fri Jun 12 11:39:54 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

About pyaedt
===================================

Introduction to pyaedt  version |version|
--------------------------------------------



pyaedt is intended to consolidate and extend all existing functionalities around AEDT-based scripting to allow re-use of existing code, sharing of best-practice and  increase collaboration collaboration.
pyaedt is run under `MIT License <LICENSE.html>`_

This tool has actually been tested on HFSS, Icepak and Maxwell 3D.

Useful Links:

- `Coding Guidelines <Resources/Code_Guidelines.md>`_


- `Installation Guidelines <Resources/Installation.md>`_

- `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`_

- `Clean Code - R. C. Martin <https://www.amazon.com/Robert-Martin-Clean-Code-Collection-ebook/dp/B00666M59G>`_



**What is pyaedt**

pyaedt is an python library which interacts directly with AEDT API making coding to end user much simpler.
It uses an architecture that can be reused for all 3D tools (Maxwell, Q3D, HFSS, Icepak), and in future for all other desktop tools. Its classes and methods structures allows to simplify operation for end-user while reusing as much as possible of the information across the API.

**Why the need pyaedt**

Recording and reusing script is a very fast approach for simple operations in Desktop UI. But:

- Code recorded is very dirty

- Code reusability is very low

- Complex Coding are demanded to few people across the Globe

Main advantages of pyaedt are:
- Automatic initialization of all the AEDT Objects (from desktop to every single objects like editor, boundaries, etc…)

- Error Management

- Log management

- Variable Management

- Compatibility with Ironpython and CPython

- Simplification of complex API syntax thanks to Data Objects and PEP8 compatibility

- Sharing of new codes across FES team with TFS

- User can reuse most of the code across different solvers



.. figure:: ./Resources/BlankDiagram3Dmodeler.png
    :width: 600pt

    pyaedt Architecture Overview for 3D Solvers

.. figure:: ./Resources/BlankDiagram3DLayout.png
    :width: 600pt

    pyaedt Architecture Overview for HFSS 3DLayout/EDB Solver


.. figure:: ./Resources/BlankDiagramCircuit.png
    :width: 600pt

    pyaedt Architecture Overview for Circuit Solvers (Nexxim/Simplorer)

Its classes and methods structures allows to simplify operation for end-user while reusing as much as possible of the information across the API.
Main advantages:

Automatic initialization of all the AEDT Objects (from desktop to every single objects like editor, boundaries, etc…)
- Error Management
- Variable Management
- Compatibility with Ironpython and CPython
- Compatibility on Windows and Linux (Ironpython only). This requires further intensive tests
- Simplification of complex API syntax thanks to Data Objects and PEP8 compatibility
- Sharing of new codes across FES team with TFS
- User can reuse most of the code across different solvers
- Docstrings on functions for better understanding and tool usage
- Unit Test of code to increase quality across different AEDT Version

**Usage Workflow**

User has to:
1. Initialize Desktop Class with version of AEDT to be used.
2. initialize application to use within AEDT

**Desktop.py - Connect to Desktop from Python IDE**

- Works inside Electronics Desktop and as a Standalone Application
- Automatically detect if it is Ironpython or CPython and initialize accordingly the Desktop
- Advanced Error Management

Examples of usage:

- Explicit Desktop Declaration and error management

.. code:: python

    from pyaedt.Destkop import Desktop
    from pyaedt.Circuit import Circuit
    with Desktop("2020.1", NG=True):
        print("AEDT 2020R1 in Non-Graphicalmode will be launched)
        circuit = Circuit()
        ...
        print("any error here will be catched by Desktop=
        ...
    print("here Desktop is automatically release")


- Implicit Desktop Declaration and error management


.. code:: python

    from pyaedt.Circuit import Circuit
    with Circuit as circuit:
        print("Latest version of Desktop in Graphical mode will be launched")
        ...
        print("any error here will be catched by Desktop")
        ...
    print("here Desktop is automatically release")

- Variables

.. code:: python

    from pyaedt.HFSS import HFSS
    with HFSS as hfss:
         hfss["dim"]="1mm"   #this is a design variable
         hfss["$dim"] = "1mm"  #this is a project variable


- modeler

.. code:: python

    from pyaedt.HFSS import HFSS
    with HFSS as hfss:
         # Same command to create the box, assign variables, and assign materials
         hfss.modeler.primitives.create_box([0,0,0], [10,"dim",10], "mybox", "aluminum")



.. toctree::
   :hidden:

   LICENSE
   Resources/Installation
   API/API
   examples/index
   Resources/Code_Guidelines







Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
