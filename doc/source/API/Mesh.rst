Mesh Operations
===============
The ``Mesh`` module includes these classes:

* Mesh for ``Hfss``, ``Maxwell2D``, ``Maxwell3d``, ``Q2d`` and ``Q3d``
* IcepakMesh for ``Icepak``
* Mesh3d for ``Hfss3dLayout``.

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
    # this call return the Mesh Class
    my_mesh = app.mesh
    # this call execute a Mesh Methods
    my_mesh.assign_surface_mesh("MyBox", 2)
    ...
