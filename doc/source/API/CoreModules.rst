AEDT Modules
============
This section lists the core PyAEDT application modules:

* Design
* Variable
* DesignXPloration
* Configurations



Variable
~~~~~~~~
This module provides all functionalities for creating and editing
design and project variables in the 3D tools.

.. code:: python

    from pyaedt import Hfss
    app = Hfss(specified_version="2021.1",
                 non_graphical=False, new_desktop_session=True,
                 close_on_exit=True, student_version=False)

    # this call return the VariableManager Class
    variable_manager = self.aedtapp._variable_manager

    # Set and Get a variable
    app["w"] = "10mm"
    a = app["w"]
    ...


.. currentmodule:: pyaedt.application.Variables

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   CSVDataset
   VariableManager
   Variable
   DataSet


DesignXploration
~~~~~~~~~~~~~~~~
This module contains all properties and methods needed to create
optimetrics setups.

.. code:: python

    from pyaedt import Hfss
    app = Hfss(specified_version="2021.1",
                 non_graphical=False, new_desktop_session=True,
                 close_on_exit=True, student_version=False)

    # returns the ParametericsSetups Class
    app.parametrics

    # returns the OptimizationSetups Class
    app.optimizations

    # adds an optimization and returns Setup class with all settings and methods
    sweep3 = hfss.opti_optimization.add_optimization(calculation="dB(S(1,1))", calculation_value="2.5GHz")

    ...

.. currentmodule:: pyaedt.modules.DesignXPloration

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   ParametricSetups
   OptimizationSetups
   SetupParam
   SetupOpti



Design Cache
~~~~~~~~~~~~
This module contains all properties and methods applicable to projects
and designs.

.. currentmodule:: pyaedt.application.Design

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   DesignCache

Configurations Files
~~~~~~~~~~~~~~~~~~~~
This module contains all methods to export project settings to json file
and import and apply settings to a new design.
Actually the configuration covers the following applications:
* Hfss
* Q2d and Q3d
* Maxwell
* Icepak
* Mechanical

The sections covered are:

* Variables
* Mesh Operations (except Icepak)
* Setup and Optimetrics
* Material Properties
* Object Properties
* Boundaries and Excitations

When a boundary is attached to a face the tool will try to match it with a
FaceByPosition on the same object name on the target design.
If, for any reason, that face position has changed or object name in the target design has changed,
the boundary will fail to apply.

.. code:: python

    from pyaedt import Hfss
    app = Hfss(project_name="original_project", specified_version="2022.1",
                 non_graphical=False, new_desktop_session=True,
                 close_on_exit=True, student_version=False)

    conf_file = self.aedtapp.configurations.export_config()

    app2 = Hfss(projec_name='newproject')
    app2.modeler.import_3d_cad(file_path)
    out = app2.configurations.import_config(conf_file)
    app2.configurations.results.global_import_success

    ...

.. currentmodule:: pyaedt.generic.configurations

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   Configurations
   ConfigurationsOptions
   ImportResults