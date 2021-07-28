Modeler and  Primitives
=======================

This section lists the core AEDT Modeler modules:

* Modeler
* Primitives
* Objects


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

Primitives
~~~~~~~~~~

The ``Primitives`` module includes these classes:

.. currentmodule:: pyaedt.modeler

.. autosummary::
   :toctree: _autosummary
   :template: custom-class-template.rst
   :nosignatures:

   Primitives.PolylineSegment
   Primitives.Polyline
   Primitives2D.Primitives2D
   Primitives3D.Primitives3D
   Primitives3DLayout.Primitives3DLayout
   PrimitivesNexxim.NexximComponents
   PrimitivesSimplorer.SimplorerComponents
   PrimitivesCircuit.CircuitComponents



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
