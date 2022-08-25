Modeler and  primitives
=======================

This section lists the core AEDT Modeler modules:

* Modeler
* Primitives
* Objects

They are accessible through the ``modeler`` and ``modeler.objects`` property:

.. code:: python

    from pyaedt import Hfss
    app = Hfss(specified_version="2022.1",
                 non_graphical=False, new_desktop_session=True,
                 close_on_exit=True, student_version=False)

    # This call return the Modeler3D class
    modeler = app.modeler

    # This call returns a Primitives3D object
    primitives = modeler

    # This call return an Object3d object
    my_box = primitives.create_box([0,0,0],[10,10,10])
    my_box = primitives.objects[my_box.id]

    # This call return a FacePrimitive object list
    my_box.faces
    # This call returns an EdgePrimitive object list
    my_box.edges
    my_box.faces[0].edges

    # This call returns a VertexPrimitive object list
    my_box.vertices
    my_box.faces[0].vertices
    my_box.faces[0].edges[0].vertices

    ...


Modeler
~~~~~~~

The ``Modeler`` module contains all properties and methods needed to edit a
modeler, including all primitives methods and properties:

* ``Modeler2D`` for Maxwell 2D and Q2D Extractor
* ``Modeler3D`` for HFSS, Maxwell 3D, Q3D Extractor, and Icepak
* ``Modeler3DLayout`` for HFSS 3D Layout
* ``ModelerNexxim`` for Circuit
* ``ModelerTwinBuilder`` for Twin Builder
* ``ModelerEmit`` for Emit


.. currentmodule:: pyaedt.modeler

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   Model2D.Modeler2D
   Model3D.Modeler3D
   Model3DLayout.Modeler3DLayout
   Circuit.ModelerNexxim
   Circuit.ModelerTwinBuilder
   Circuit.ModelerEmit



Primitives
~~~~~~~~~~

The ``Primitives`` module includes these classes:

* ``Primitives2D`` for Maxwell 2D and Q2D Extractor
* ``Primitives3D`` for HFSS, Maxwell 3D, Q3D Extractor, and Icepak
* ``Primitives3DLayout`` for HFSS 3D Layout
* ``NexximComponents`` for Circuit
* ``TwinBuilderComponents`` for Twin Builder
* ``CircuitComponents`` for Emit

Primitive objects are accessible through the ``modeler`` property for
EM Solver and ``modeler.components`` for Circuit solvers.


.. currentmodule:: pyaedt.modeler

.. autosummary::
   :toctree: _autosummary
   :nosignatures:


   Primitives2D.Primitives2D
   Primitives3D.Primitives3D
   Primitives3DLayout.Primitives3DLayout
   PrimitivesNexxim.NexximComponents
   PrimitivesTwinBuilder.TwinBuilderComponents
   PrimitivesCircuit.CircuitComponents

.. code:: python

    from pyaedt import Circuit
    app = Circuit(specified_version="2022.1",
                 non_graphical=False, new_desktop_session=True,
                 close_on_exit=True, student_version=False)

    # This call returns the NexximComponents class
    components = app.modeler.components

    ...


Objects
~~~~~~~
The following classes define objects properties for 3D and 2D Solvers (excluding HFSS 3D Layout).
They contain all getters and setters to simplify object manipulation.


.. currentmodule:: pyaedt.modeler

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   Object3d.Object3d
   Object3d.FacePrimitive
   Object3d.EdgePrimitive
   Object3d.VertexPrimitive
   Primitives.PolylineSegment
   Primitives.Polyline
   Object3d.Padstack
   Object3d.UserDefinedComponent

.. code:: python

    from pyaedt import Hfss
    app = Hfss(specified_version="2022.1",
               non_graphical=False, new_desktop_session=True,
               close_on_exit=True, student_version=False)

    # This call returns the Modeler3D class
    modeler = app.modeler

    # This call returns a Primitives3D object
    primitives = modeler

    # This call returns an Object3d object
    my_box = primitives.create_box([0,0,0],[10,10,10])

    # Getter and setter
    my_box.material_name
    my_box.material_name = "copper"

    my_box.faces[0].center

    ...

Objects in Circuit tools
~~~~~~~~~~~~~~~~~~~~~~~~
The following classes define the objects properties for Circuit tools.
They contain all getters and setters to simplify object manipulation.

.. currentmodule:: pyaedt.modeler

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   Object3d.CircuitComponent
   Object3d.CircuitPins

.. code:: python

    from pyaedt import Circuit
    app = Circuit(specified_version="2022.1",
               non_graphical=False, new_desktop_session=True,
               close_on_exit=True, student_version=False)

    # This call returns the Modeler class
    modeler = app.modeler

    # This call returns a Schematic object
    schematic = modeler.schematic

    # This call return an Object3d object
    my_res = schematic.create_resistor("R1", 50)

    # Getter and setter
    my_res.location
    my_res.parameters["R"]=100


    ...


Objects in HFSS 3D Layout
~~~~~~~~~~~~~~~~~~~~~~~~~
The following classes define the object properties for HFSS 3D Layout.
They contain all getters and setters to simplify object manipulation.

.. currentmodule:: pyaedt.modeler

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   object3dlayout.Components3DLayout
   object3dlayout.Nets3DLayout
   object3dlayout.Pins3DLayout
   object3dlayout.Line3dLayout
   object3dlayout.Polygons3DLayout
   object3dlayout.Circle3dLayout
   object3dlayout.Rect3dLayout
   object3dlayout.Points3dLayout
   object3dlayout.Point

.. code:: python

    from pyaedt import Hfss3dLayout
    app = Hfss3dLayout(specified_version="2022.1",
               non_graphical=False, new_desktop_session=True,
               close_on_exit=True, student_version=False)

    # This call returns the Modeler3DLayout class
    modeler = app.modeler

    # This call returns a Primitives3D object
    primitives = modeler

    # This call return a Object3d object
    my_rect = primitives.create_rectangle([0,0,0],[10,10])

    # Getter and setter
    my_rect.material_name

    ...


Coordinate systems and geometry operators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains all properties and methods needed to edit a
coordinate system and a set of useful geometry operators.
The ``CoordinateSystem`` class is accessible through the ``create_coordinate_system``
method or the ``coordinate_systems`` list. The ``GeometryOperators`` class can be
imported and used because it is made by static methods.


.. currentmodule:: pyaedt.modeler

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   Modeler.CoordinateSystem
   GeometryOperators


.. code:: python

    from pyaedt import Hfss
    app = Hfss(specified_version="2022.1",
                 non_graphical=False, new_desktop_session=True,
                 close_on_exit=True, student_version=False)

    # This call returns the CoordinateSystem object list
    cs = app.modeler.coordinate_systems

    # This call returns a CoordinateSystem object
    new_cs = app.modeler.create_coordinate_system()

    ...