Mesh operations
===============
The ``Mesh`` module includes these classes:

* ``Mesh`` for HFSS, Maxwell 2D, Maxwell 3D, Q2D Extractor, and Q3D Extractor
* ``IcepakMesh`` for Icepak
* ``Mesh3d`` for HFSS 3D Layout

They are accessible through the mesh property:

.. currentmodule:: pyaedt.modules

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   Mesh.Mesh
   MeshIcepak.IcepakMesh
   Mesh3DLayout.Mesh3d

.. code:: python

    from pyaedt import Maxwell3d
    app = Maxwell3d(specified_version="2022.1",
                 non_graphical=False, new_desktop_session=True,
                 close_on_exit=True, student_version=False)
    # This call returns the Mesh class
    my_mesh = app.mesh
    # This call executes a Mesh method
    my_mesh.assign_surface_mesh("MyBox", 2)
    ...
