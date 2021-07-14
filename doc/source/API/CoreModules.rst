Application Modules
===================
This section contains information about PyAEDT application modules:

#. Design
#. Variables
#. Analysis
#. Edb
#. Modeler
#. Objects
#. DesignXPloration


Analysis
~~~~~~~~

.. toctree::
   :maxdepth: 2
   :caption: This module contains all properties and methods needed to
             set up and run AEDT analyses.

   AnalysisCore


Modeler
~~~~~~~

This module contains all properties and methods needed to edit a
modeler, including all primitives methods and properties.

.. currentmodule:: pyaedt.modeler

.. autosummary::
   :toctree: _autosummary
   :template: custom-class-template.rst

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

   Object3d
   FacePrimitive
   EdgePrimitive
   VertexPrimitive


EDB
~~~
.. toctree::
   :maxdepth: 2
   :caption: This module contains all EDT functionalities for reading
             and writing information to AEDB files.

   Edb


Design
~~~~~~

.. toctree::
   :maxdepth: 2
   :caption: This module contains all properties and methods
             applicable to projects and designs.

   Design


Variable
~~~~~~~~

.. toctree::
   :maxdepth: 2
   :caption: This module contains all methods for managing AEDT
             variables for both projects and designs.

   Variables


DesignXploration
~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 2
   :caption: This module contains all properties and methods needed to
             create optimetrics setups.

   DesignXPlorer



