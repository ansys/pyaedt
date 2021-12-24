AEDT Modules
============
This section lists the core PyAEDT application modules:

* Design
* Variable
* DesignXPloration



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
    app.opti_parametric

    # returns the OptimizationSetups Class
    app.opti_optimization

    # returns the DOESetups Class
    app.opti_doe

    # returns the DXSetups Class
    app.opti_designxplorer

    # returns the SensitivitySetups Class
    app.opti_sensitivity

    # returns the StatisticalSetups Class
    app.opti_statistical

    # adds an optimization and returns Setup class with all settings and methods
    sweep3 = hfss.opti_optimization.add_optimization(calculation="dB(S(1,1))", calculation_value="2.5GHz")

    ...

.. currentmodule:: pyaedt.modules.DesignXPloration

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   DXSetups
   ParametericsSetups
   SensitivitySetups
   StatisticalSetups
   DOESetups
   OptimizationSetups



Design Cache
~~~~~~~~~~~~
This module contains all properties and methods applicable to projects
and designs.

.. currentmodule:: pyaedt.application.Design

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   DesignCache