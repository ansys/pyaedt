.. _release_1_0:

Breaking changes in release 1.0
===============================

This page describes the breaking changes expected in the upcoming major version 1.0 of PyAEDT.
These changes include the deprecation of certain function argument names and the restructuring
of the codebase.

Deprecation of function argument names
--------------------------------------

In the 1.0 release, several function argument names are deprecated. You should review 
your code and check the warnings that are logged at run time.
The following example shows a warning triggered by the use of an argument that is currently acceptable but is not going to work with version 1.0.

.. code-block:: python

    from pyaedt import Circuit
    c = Circuit(designname="whatever")

Expected log output:

.. code-block:: text

    PyAEDT WARNING: Argument `designname` is deprecated for method `__init__`; use `design` instead.

Restructuring of the codebase
-----------------------------

To facilitate the maintenance of PyAEDT and to adhere to PyAnsys' guidelines, the codebase
is being restructured. The sources are to be moved from ``pyaedt`` to ``src.ansys.aedt``
to improve the organization and maintainability of the codebase.

The changes to the structure follow:

.. code-block:: text

    Old structure:
    --------------

    pyaedt/
    ├── application/
    └── ...

    New structure:
    --------------

    src/
    └── ansys/
        └── aedt/
            ├── application/
            ├── ...

When migrating to major release `1.0`, please update any references or imports in your project
accordingly. An example of migration is shown below:

**Old import:**

.. code-block:: python

    from pyaedt import Circuit    

**New import:**

.. code-block:: python

    from ansys.aedt import Circuit

Other changes in release 1.0
============================

In addition to the major changes described earlier, modifications are continuously performed to
improve the quality of the project, its maintainability, its documentation, and
to ensure users' need are met as efficiently as possible. This includes ensuring
consistent argument names, improving data encapsulation, strengthening CI/CD, and extracting
examples to a dedicated project.

For more information on the status of the 1.0 release, see `PyAEDT Milestone <https://github.com/ansys/pyaedt/milestone/3>` .
