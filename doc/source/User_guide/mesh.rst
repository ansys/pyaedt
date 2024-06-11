Mesh
====

Mesh operations are very important in engineering simulation.
PyAEDT can read existing mesh operations in a design, make edits, and create new operations.
All mesh operations are conveniently listed within the mesh object:

.. code:: python

    from pyaedt import Maxwell3d
    m3d = Maxwell3d()
    all_mesh_ops = m3d.mesh.meshoperations
    my_mesh_op = all_mesh_ops[0]
    # All properties are in props dictionary.
    my_mesh_op.props["my_prop"] = "my_value"
    my_mesh_op.update()


.. image:: ../Resources/Mesh_Operations.png
  :width: 800
  :alt: Mesh object List


Icepak has a different approach to the mesh operations.
Those are managed through mesh regions and can be edited directly from the pyaedt object.

.. code:: python

    icepak_b = Icepak()

    # Global mesh region

    icepak_b.mesh.global_mesh_region.MaxElementSizeX = "2mm"
    icepak_b.mesh.global_mesh_region.MaxElementSizeY = "3mm"
    icepak_b.mesh.global_mesh_region.MaxElementSizeZ = "4mm"
    icepak_b.mesh.global_mesh_region.MaxSizeRatio = 2
    icepak_b.mesh.global_mesh_region.UserSpecifiedSettings = True
    icepak_b.mesh.global_mesh_region.UniformMeshParametersType = "XYZ Max Sizes"
    icepak_b.mesh.global_mesh_region.MaxLevels = 2
    icepak_b.mesh.global_mesh_region.BufferLayers = 1
    icepak_b.mesh.global_mesh_region.update()

    box1 = icepak_b.modeler.create_box([0,0,0], [10,20,20])

    # Local mesh region

    new_mesh_region = icepak_b.mesh.assign_mesh_region([box1.name])


In HFSS 3D Layout, you add mesh operations to nets and layers like this:

.. code:: python

    from pyedt import Hfss3dLayout

    h3d = Hfss3dLayout("myproject.aedt")
    setup = h3d.create_setup("HFSS")
    mop1 = h3d.mesh.assign_length_mesh("HFSS", layer_name="PWR", net_name="GND")
    mop2 = h3d.mesh.assign_skin_depth("HFSS",  layer_name="LAY2", net_name="VCC")