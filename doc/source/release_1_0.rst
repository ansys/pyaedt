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
is being restructured. The sources are to be moved from ``pyaedt`` to ``ansys.aedt.core``
to improve the organization and maintainability of the codebase.

The changes follow the structure below:

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
            └── core/
                ├── application/
                ├── ...

When migrating to major release `1.0`, please update any references or imports in your project
accordingly. An example of migration is shown below:

**Old import:**

.. code-block:: python

    from pyaedt import Circuit    

**New import:**

.. code-block:: python

    from ansys.aedt.core import Circuit

Python files renaming
---------------------

To harmonize the names of the Python files and to follow PEP 8 conventions, some Python
files are being renamed. This initiative aims to improve the consistency of the codebase
and ensure that file names are clearer and adhere to Python community best practices.
For further information, see
`PEP 8 Package and Module Names <https://peps.python.org/pep-0008/#package-and-module-names>`_ .

An example of migration is shown below:

**Old import:**

.. code-block:: python

    from pyaedt.application.Analysis3DLayout import FieldAnalysis3DLayout

**New import:**

.. code-block:: python

    from ansys.aedt.core.application.analysis_3d_layout import FieldAnalysis3DLayout

The following table list the name changes with the old and new paths:

+----------------------------------------------------------------+--------------------------------------------------------------------------+
| Old path without file rename                                   | New path with renamed file                                               |
+================================================================+==========================================================================+
| pyaedt\\application\\Analysis3D.py                             | src\\ansys\\aedt\\core\\application\\analysis_3d.py                      |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\application\\Analysis3DLayout.py                       | src\\ansys\\aedt\\core\\application\\analysis_3d_layout.py               |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\application\\AnalysisMaxwellCircuit.py                 | src\\ansys\\aedt\\core\\application\\analysis_maxwell_circuit.py         |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\application\\AnalysisNexxim.py                         | src\\ansys\\aedt\\core\\application\\analysis_nexxim.py                  |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\application\\AnalysisRMxprt.py                         | src\\ansys\\aedt\\core\\application\\analysis_r_m_xprt.py                |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\application\\AnalysisTwinBuilder.py                    | src\\ansys\\aedt\\core\\application\\analysis_twin_builder.py            |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\application\\JobManager.py                             | src\\ansys\\aedt\\core\\application\\job_manager.py                      |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\generic\\DataHandlers.py                               | src\\ansys\\aedt\\core\\generic\\data_handlers.py                        |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\generic\\LoadAEDTFile.py                               | src\\ansys\\aedt\\core\\internal\\load_aedt_file.py                      |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\modeler\\modeler2d.py                                  | src\\ansys\\aedt\\core\\modeler\\modeler_2d.py                           |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\modeler\\modeler3d.py                                  | src\\ansys\\aedt\\core\\modeler\\modeler_3d.py                           |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\modeler\\modelerpcb.py                                 | src\\ansys\\aedt\\core\\modeler\\modeler_pcb.py                          |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\modeler\\cad\\Primitives2D.py                          | src\\ansys\\aedt\\core\\modeler\\cad\\primitives_2d.py                   |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\modeler\\cad\\Primitives3D.py                          | src\\ansys\\aedt\\core\\modeler\\cad\\primitives_3d.py                   |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\modeler\\cad\\elements3d.py                            | src\\ansys\\aedt\\core\\modeler\\cad\\elements_3d.py                     |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\modeler\\cad\\object3d.py                              | src\\ansys\\aedt\\core\\modeler\\cad\\object_3d.py                       |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\modeler\\circuits\\PrimitivesCircuit.py                | src\\ansys\\aedt\\core\\modeler\\circuits\\primitives_circuit.py         |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\modeler\\circuits\\PrimitivesEmit.py                   | src\\ansys\\aedt\\core\\modeler\\circuits\\primitives_emit.py            |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\modeler\\circuits\\PrimitivesMaxwellCircuit.py         | src\\ansys\\aedt\\core\\modeler\\circuits\\primitives_maxwell_circuit.py |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\modeler\\circuits\\PrimitivesNexxim.py                 | src\\ansys\\aedt\\core\\modeler\\circuits\\primitives_nexxim.py          |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\modeler\\circuits\\PrimitivesTwinBuilder.py            | src\\ansys\\aedt\\core\\modeler\\circuits\\primitives_twin_builder.py    |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\modeler\\circuits\\object3dcircuit.py                  | src\\ansys\\aedt\\core\\modeler\\circuits\\object_3d_circuit.py          |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\modeler\\pcb\\Primitives3DLayout.py                    | src\\ansys\\aedt\\core\\modeler\\pcb\\primitives_3d_layout.py            |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\modeler\\pcb\\object3dlayout.py                        | src\\ansys\\aedt\\core\\modeler\\pcb\\object_3d_layout.py                |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\modules\\AdvancedPostProcessing.py                     | src\\ansys\\aedt\\core\\modules\\advanced_post_processing.py             |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\modules\\CableModeling.py                              | src\\ansys\\aedt\\core\\modules\\cable_modeling.py                       |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\modules\\CircuitTemplates.py                           | src\\ansys\\aedt\\core\\modules\\circuit_templates.py                    |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\modules\\DesignXPloration.py                           | src\\ansys\\aedt\\core\\modules\\design_xploration.py                    |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\modules\\LayerStackup.py                               | src\\ansys\\aedt\\core\\modules\\layer_stackup.py                        |        
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\modules\\MaterialLib.py                                | src\\ansys\\aedt\\core\\modules\\material_lib.py                         |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\modules\\Mesh3DLayout.py                               | src\\ansys\\aedt\\core\\modules\\mesh_3d_layout.py                       |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\modules\\MeshIcepak.py                                 | src\\ansys\\aedt\\core\\modules\\mesh_icepak.py                          |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\modules\\OptimetricsTemplates.py                       | src\\ansys\\aedt\\core\\modules\\optimetrics_templates.py                |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\modules\\PostProcessor.py                              | src\\ansys\\aedt\\core\\modules\\post_general.py                         |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\modules\\SetupTemplates.py                             | src\\ansys\\aedt\\core\\modules\\setup_templates.py                      |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\modules\\SolveSetup.py                                 | src\\ansys\\aedt\\core\\modules\\solve_setup.py                          |
+----------------------------------------------------------------+--------------------------------------------------------------------------+
| pyaedt\\modules\\SolveSweeps.py                                | src\\ansys\\aedt\\core\\modules\\solve_sweeps.py                         |
+----------------------------------------------------------------+--------------------------------------------------------------------------+

Dotnet changes in Linux
-----------------------

To improve compatibility with system libraries in Linux, the Python package `dotnetcore2` is being removed from PyAEDT's dotnet installation target.
Indeed, the embedded version of `.NET` associated to `dotnetcore2` is old and has **incompatibilities** with recent versions of `openssl` such as the one installed by default in Ubuntu 22.04.

The impact of this decision is that users need to install `.NET` themselves.
The installation process can be done following the official
Microsoft documentation for `.NET` on Linux to ensure proper setup and compatibility. See
`Register Microsoft package repository <https://learn.microsoft.com/en-us/dotnet/core/install/linux-ubuntu#register-the-microsoft-package-repository>`_
and `Install .NET <https://learn.microsoft.com/en-us/dotnet/core/install/linux-ubuntu#install-net>`_.

.. note::
    Starting with Ubuntu 22.04, `.NET` is available in the official Ubuntu repository.
    If you want to use the Microsoft package to install `.NET`, you can use the following
    approach to *"demote"* the Ubuntu packages so that the Microsoft packages take precedence.

    1. Ensure the removal of any existing `.NET` installation. In Ubuntu, this can be done with
    the following command:

    .. code::

        sudo apt remove dotnet* aspnetcore* netstandard*

    2. Create a preference file in `/etc/apt/preferences.d`, for example `microsoft-dotnet.pref`,
    with the following content:

    .. code::

        Package: dotnet* aspnet* netstandard*
        Pin: origin "archive.ubuntu.com"
        Pin-Priority: -10

        Package: dotnet* aspnet* netstandard*
        Pin: origin "security.ubuntu.com"
        Pin-Priority: -10

    3. Perform an update and install of the version you want, for example .NET 6.0 or 8.0

    .. code::

        sudo apt update && sudo apt install -y dotnet-sdk-6.0

Other changes in release 1.0
============================

In addition to the major changes described earlier, modifications are continuously performed to
improve the quality of the project, its maintainability, its documentation, and
to ensure users' needs are met as efficiently as possible. This includes ensuring
consistent argument names, improving data encapsulation, strengthening CI/CD, and migrate
examples to a different repository.

For more information on the status of the 1.0 release, see `PyAEDT Milestone <https://github.com/ansys/pyaedt/milestone/3>`_ .
