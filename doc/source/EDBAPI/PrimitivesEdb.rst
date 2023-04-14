Modeler & primitives
====================
These classes are the containers of primitives and all relative methods.
Primitives are planes, lines, rectangles, and circles.


.. code:: python

    from pyaedt import Edb
    edb = Edb(myedb, edbversion="2023.1")

    top_layer_obj = edb.modeler.create_rectangle("TOP", net_name="gnd",
                                                 lower_left_point=plane_lw_pt,
                                                 upper_right_point=plane_up_pt)

    ...

.. currentmodule:: pyaedt.edb_core.layout

.. autosummary::
   :toctree: _autosummary
   :nosignatures:


   EdbLayout


Primitives properties
---------------------
These classes are the containers of data management for primitives and arcs.

.. currentmodule:: pyaedt.edb_core.edb_data.primitives_data

.. autosummary::
   :toctree: _autosummary
   :nosignatures:


   EDBPrimitives
   EDBArcs


.. code:: python

    from pyaedt import Edb
    edb = Edb(myedb, edbversion="2023.1")

    polygon = edbapp.modeler.polygons[0]
    polygon.is_void
    poly2 = polygon.clone()

    ...
