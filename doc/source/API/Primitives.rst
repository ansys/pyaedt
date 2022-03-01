Modeler and  Primitives
=======================

This section lists the core AEDT Modeler modules:

* Modeler
* Primitives
* Objects

They are accessible through the ``modeler`` and ``modeler.objects`` property:

.. code:: python

    from pyaedt import Hfss
    app = Hfss(specified_version="2021.1",
                 non_graphical=False, new_desktop_session=True,
                 close_on_exit=True, student_version=False)

    # this call return the Modeler3D Class
    modeler = app.modeler

    # this call return a Primitives3D Object
    primitives = modeler

    # this call return a Object3d Object
    my_box = primitives.create_box([0,0,0],[10,10,10])
    my_box = primitives.objects[my_box.id]

    # this call return a FacePrimitive Object List
    my_box.faces
    # this call return a EdgePrimitive Object List
    my_box.edges
    my_box.faces[0].edges

    # this call return a VertexPrimitive Object List
    my_box.vertices
    my_box.faces[0].vertices
    my_box.faces[0].edges[0].vertices

    ...


Modeler
~~~~~~~

This module contains all properties and methods needed to edit a
modeler, including all primitives methods and properties.
* Modeler3D for ``Hfss``, ``Maxwell3d``, ``Q3d`` and ``Icepak``
* Modeler2D for ``Maxwell2D`` ``Q2d``
* Modeler3DLayout for ``Hfss3dLayout``
* ModelerNexxim for ``Circuit``
* ModelerTwinBuilder for ``TwinBuilder``
* ModelerEmit for ``Emit``


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
* Primitives3D for ``Hfss``, ``Maxwell3d``, ``Q3d`` and ``Icepak``
* Primitives2D for ``Maxwell2D`` ``Q2d``
* Primitives3DLayout for ``Hfss3dLayout``
* NexximComponents for ``Circuit``
* TwinBuilderComponents for ``TwinBuilder``
* CircuitComponents for ``Emit``
Primives objects are accessible through ``modeler`` property for
EM Solver and ``modeler.components`` for circuit solvers.

.. code:: python

    from pyaedt import Circuit
    app = Circuit(specified_version="2021.1",
                 non_graphical=False, new_desktop_session=True,
                 close_on_exit=True, student_version=False)

    # this call return the NexximComponents Class
    components = app.modeler.components

    ...


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



Objects
~~~~~~~
Those classes define the objects properties for 3D and 2D Solvers (excluding ``Hfss3dLayout``).
It contains all getter and setter to simplify object manipulation.

.. code:: python

    from pyaedt import Hfss
    app = Hfss(specified_version="2021.1",
               non_graphical=False, new_desktop_session=True,
               close_on_exit=True, student_version=False)

    # this call return the Modeler3D Class
    modeler = app.modeler

    # this call return a Primitives3D Object
    primitives = modeler

    # this call return a Object3d Object
    my_box = primitives.create_box([0,0,0],[10,10,10])

    # Getter and setter
    my_box.material_name
    my_box.material_name = "copper"

    my_box.faces[0].center

    ...


.. currentmodule:: pyaedt.modeler

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   Object3d.Object3d
   Object3d.FacePrimitive
   Object3d.EdgePrimitive
   Object3d.VertexPrimitive
   Object3d.Point
   Primitives.PolylineSegment
   Primitives.Polyline


Objects in Circuit
~~~~~~~~~~~~~~~~~~
Those classes define the objects properties for circuit tools.
It contains all getter and setter to simplify object manipulation.

.. code:: python

    from pyaedt import Circuit
    app = Circuit(specified_version="2021.1",
               non_graphical=False, new_desktop_session=True,
               close_on_exit=True, student_version=False)

    # this call return the Modeler Class
    modeler = app.modeler

    # this call return a Schematic Object
    schematic = modeler.schematic

    # this call return a Object3d Object
    my_res = schematic.create_resistor("R1", 50)

    # Getter and setter
    my_res.location
    my_res.parameters["R"]=100


    ...


.. currentmodule:: pyaedt.modeler

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   Object3d.CircuitComponent
   Object3d.CircuitPins
   Object3d.ComponentParameters


Objects in Hfss3d Layout
~~~~~~~~~~~~~~~~~~~~~~~~
Those classes define the objects properties for ``Hfss3dLayout``.
It contains all getter and setter to simplify object manipulation.

.. code:: python

    from pyaedt import Hfss3dLayout
    app = Hfss3dLayout(specified_version="2021.1",
               non_graphical=False, new_desktop_session=True,
               close_on_exit=True, student_version=False)

    # this call return the Modeler3DLayout Class
    modeler = app.modeler

    # this call return a Primitives3D Object
    primitives = modeler

    # this call return a Object3d Object
    my_rect = primitives.create_rectangle([0,0,0],[10,10])

    # Getter and setter
    my_rect.material_name

    ...


.. currentmodule:: pyaedt.modeler

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   Object3d.Objec3DLayout
   Object3d.Components3DLayout
   Object3d.Nets3DLayout
   Object3d.Pins3DLayout
   Object3d.Geometries3DLayout
   Object3d.Padstack


Coordinate System and Geometry Operators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module contains all properties and methods needed to edit a
Coordinate System and a set of useful Geometry Operators.
CoordinateSystem Class is accessible through ``create_coordinate_system`` method or ``coordinate_systems`` list.
GeometryOperators can be imported and used as it is made by static methods.


.. code:: python

    from pyaedt import Hfss
    app = Hfss(specified_version="2021.1",
                 non_graphical=False, new_desktop_session=True,
                 close_on_exit=True, student_version=False)

    # this call returns the CoordinateSystem Object lists
    cs = app.modeler.coordinate_systems

    # this call returns a CoordinateSystem Object
    new_cs = app.modeler.create_coordinate_system()

    ...


.. currentmodule:: pyaedt.modeler

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   Modeler.CoordinateSystem
   GeometryOperators