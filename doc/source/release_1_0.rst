.. _release_1_0:

Breaking changes in release 1.0
===============================

This document outlines the breaking changes expected in the upcoming major version `1.0` of PyAEDT.
These changes include the deprecation of certain function argument names and the restructuration
of the sources.

Deprecation of function argument names
--------------------------------------

In the next major version, several function argument names will be deprecated and will no longer
be allowed. Please review your code and check the warning that are logged at run time.
Below is an example of a warning triggered by the use of an argument that is currently tolerated
but which will not work with version `1.0`.

.. code-block:: python

    from pyaedt import Circuit
    c = Circuit(designname="whatever")

Expected log output:

.. code-block:: text

    PyAEDT WARNING: Argument `designname` is deprecated for method `__init__`; use `design` instead.

Restructuration of the codebase
-------------------------------

To facilitate the maintenance of our package and to adhere to PyAnsys' guidelines, we are
restructuring the codebase. The sources will be moved from `pyaedt` to `src.ansys.aedt`.
This change aims to improve the organization and maintainability of the codebase.

The new structure will be as follows:

.. code-block:: text

    Old Structure:
    --------------
    pyaedt/
    ├── application/
    └── ...

    New Structure:
    --------------
    src/
    └── ansys/
        └── aedt/
            ├── application/
            ├── ...

When migrating to major release `1.0`, please update any references or imports in your project
accordingly. An example of migration is shown below:

.. code-block:: python

    from pyaedt import Circuit    

should be updated into

.. code-block:: python

    from ansys.aedt import Circuit

Other changes to reach release 1.0
==================================

In addition to the major changes described above, we are continuously making regular
modifications to improve the quality of the project, its maintainability, its documentation, and
to ensure we can meet user needs as efficiently as possible. This includes ensuring
consistency on argument names; strengthening our CI/CD; extracting examples to a dedicated
project to increase clarity, homogeneity and facilite integration; ...

See `PyAEDT Milestone <https://github.com/ansys/pyaedt/milestone/3>`_ for more information on
the status of the release.
