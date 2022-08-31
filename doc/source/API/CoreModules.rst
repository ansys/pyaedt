AEDT modules
============
This section lists the core PyAEDT app modules:

* Design
* Variable
* DesignXploration
* Configurations



Variable
~~~~~~~~
This module provides all functionalities for creating and editing
design and project variables in the 3D tools.

.. code:: python

    from pyaedt import Hfss
    app = Hfss(specified_version="2022.1",
                 non_graphical=False, new_desktop_session=True,
                 close_on_exit=True, student_version=False)

    # This call returns the VariableManager Class
    variable_manager = self.aedtapp._variable_manager

    # Set and get a variable
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
    app = Hfss(specified_version="2022.1",
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



Boundary class
~~~~~~~~~~~~~~

The ``Boundary`` class is very important because it automates the creation of the AEDT syntax for
boundary and excitation creation.

.. toctree::
   :maxdepth: 2

   Boundaries