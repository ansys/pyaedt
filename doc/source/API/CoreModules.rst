Application Modules
===================
This section contains the following PyAEDT application modules:

#. Modeler
#. Objects
#. Edb
#. Design
#. Variable
#. DesignXPloration



Modeler
~~~~~~~

This module contains all properties and methods needed to edit a
modeler, including all primitives methods and properties.

.. currentmodule:: pyaedt.modeler

.. autosummary::
   :toctree: _autosummary
   :template: custom-class-template.rst
   :nosignatures:

   Modeler.Modeler
   Modeler.GeometryModeler
   Modeler.CoordinateSystem
   GeometryOperators
   Model2D.Modeler2D
   Model3D.Modeler3D
   Model3DLayout.Modeler3DLayout


Objects
~~~~~~~

.. currentmodule:: pyaedt.modeler.Object3d

.. autosummary::
   :toctree: _autosummary
   :template: custom-class-template.rst
   :nosignatures:

   Object3d
   FacePrimitive
   EdgePrimitive
   VertexPrimitive


EDB
~~~
This module contains all EDT functionalities for reading and writing
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
