AEDT Modules
============
This section lists the core PyAEDT application modules:

* Design
* Variable
* DesignXPloration




Design
~~~~~~
This module contains all properties and methods applicable to projects
and designs.

.. currentmodule:: pyaedt.application.Design

.. autosummary::
   :toctree: _autosummary
   :template: custom-class-template.rst
   :nosignatures:

   DesignCache


Variable
~~~~~~~~
This module provides all functionalities for creating and editing
design and project variables in the 3D tools.

.. currentmodule:: pyaedt.application.Variables

.. autosummary::
   :toctree: _autosummary
   :template: custom-class-template.rst
   :nosignatures:

   CSVDataset
   VariableManager
   Variable
   DataSet


DesignXploration
~~~~~~~~~~~~~~~~
This module contains all properties and methods needed to create
optimetrics setups.

.. currentmodule:: pyaedt.modules.DesignXPloration

.. autosummary::
   :toctree: _autosummary
   :template: custom-class-template.rst
   :nosignatures:

   CommonOptimetrics
   DXSetups
   ParametericsSetups
   SensitivitySetups
   StatisticalSetups
   DOESetups
   OptimizationSetups
