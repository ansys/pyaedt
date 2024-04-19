3D modeler
==========

This section lists the core AEDT Modeler modules with 3D solvers (HFSS, Maxwell,
Icepak, Q3D, and Mechanical):

* Modeler
* Primitives
* Objects

They are accessible through the ``modeler`` property:

.. code:: python

    from pyaedt import Hfss
    app = Hfss(specified_version="2023.1",
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
modeler, including all primitives methods and properties for HFSS, Maxwell 3D, Q3D Extractor, and Icepak:



.. currentmodule:: pyaedt.modeler

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   modeler3d.Modeler3D


.. code:: python

    from pyaedt import Circuit
    app = Hfss(specified_version="2023.1",
                 non_graphical=False, new_desktop_session=True,
                 close_on_exit=True, student_version=False)

    # This call returns the NexximComponents class
    origin = [0,0,0]
    sizes = [10,5,20]
    #Material and name are not mandatory fields
    box_object = app.modeler.primivites.create_box(origin, sizes, name="mybox", material="copper")

    ...
