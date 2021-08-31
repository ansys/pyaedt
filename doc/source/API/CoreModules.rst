Application Modules
===================
This section lists the core PyAEDT application modules:

* EDB
* Design
* Variable
* DesignXPloration




EDB
~~~
This module contains all EDB functionalities for reading and writing
information to AEDB files.

.. currentmodule:: pyaedt.edb_core

.. autosummary::
   :toctree: _autosummary
   :template: custom-class-template.rst
   :nosignatures:

   components.Components
   hfss.Edb3DLayout
   siwave.EdbSiwave
   nets.EdbNets
   padstack.EdbPadstacks
   layout.EdbLayout
   stackup.EdbStackup
   EDB_Data.EDBLayer
   EDB_Data.EDBLayers
   EDB_Data.EDBPadProperties
   EDB_Data.EDBPadstack
   EDB_Data.EDBPinInstances
   EDB_Data.EDBComponent
   siwave.SiwaveDCSetupTemplate


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
