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

Mesh in Icepak
--------------

Icepak has a different approach to the mesh operations.
Those are managed through mesh regions and can be edited directly from the pyaedt object.

**Global mesh region**

The global mesh region object can be accessed using:

.. code:: python

    glob_msh = ipk.mesh.global_mesh_region

This object allows to edit  the global mesh setting through its settings property that can be used like a dictionary. As an example:

.. code:: python

    glob_msh.settings["MeshRegionResolution"] = 3

Available keys are different depending if the manual settings or automatic settings are used. This can be changed using the manual_settings boolean property of the global mesh region object.

In order to modify the global region dimensions, it is possible to access the global_region property and modify its attributes. As an example:

.. code:: python

    glob_msh.global_region.positive_z_padding_type="Absolute Offset"
    glob_msh.global_region.positive_z_padding="5 mm"

Finally, to modify the properties on the Region object (i.e. the gas inside the region), it is possible to access the object property of the global_region object:

.. code:: python

    glob_reg =glob_msh.global_region
    glob_reg.object.material_name="Carbon Monoxide"

This is a pointer to the same object it is possible to get from ipk.modeler["Region"].

To summarize this three objects, refer to the image below:

.. image:: ../Resources/icepak_global_mesh_region_objects.png
  :width: 80%
  :alt: Global Mesh objects and sub-objects

This is a complete example using the global mesh region:

.. code:: python

    ipk = Icepak()

    # Global mesh region
    glob_msh=ipk.mesh.global_mesh_region
    glob_msh.manual_settings = True
    glob_msh.settings["MaxElementSizeX"] = "2mm"
    glob_msh.settings["MaxElementSizeY"] = "3mm"
    glob_msh.settings["MaxElementSizeZ"] = "4mm"
    glob_msh.settings["MaxSizeRatio"] = 2
    glob_msh.settings["UserSpecifiedSettings"] = True
    glob_msh.settings["UniformMeshParametersType"] = "XYZ Max Sizes"
    glob_msh.settings["MaxLevels"] = 2
    glob_msh.settings["BufferLayers"] = 1
    glob_msh.update()

**Local mesh regions**

To create a mesh region it is sufficient to use the assign_mesh_region function:

.. code:: python

    mesh_region = ipk.mesh.assign_mesh_region(name = object_name)

To modify the settings of the object returned, it is possible to use the same approach of the global mesh region object.

To access the subregion that define the local mesh regions and modify its dimensions:

.. code:: python

    subregion=mesh_region.assignment
    subregion.positive_z_padding_type="Absolute Offset"
    subregion.positive_z_padding="5 mm"

Finally, to access the parts included in the subregion:

.. code:: python

    subregion.parts


In AEDT 2024 R1, a big revamp of mesh region paradigm has been introduced. Because of this, support for older version is limited.
In order to use the same function in older versions, the region box must be defined first, and it must be passed as the first argument of assign_mesh_region

**Mesh Operations**

- to assign a mesh level to some objects it is possible to use assign_mesh_level method:

  .. code:: python

    ipk.mesh.assign_mesh_level(mesh_order={"Box1": 2, "Cylinder1": 4})

- to assign a mesh file to reuse to some objects it is possible to use the assign_mesh_reuse method:

  .. code:: python

    ipk.mesh.assign_mesh_reuse(assignment=["Box1", "Cylinder1"], level=mesh_path)

Mesh in HFSS 3D Layout
----------------------

In HFSS 3D Layout, you add mesh operations to nets and layers like this:

.. code:: python

    from pyedt import Hfss3dLayout

    h3d = Hfss3dLayout("myproject.aedt")
    setup = h3d.create_setup("HFSS")
    mop1 = h3d.mesh.assign_length_mesh("HFSS", layer_name="PWR", net_name="GND")
    mop2 = h3d.mesh.assign_skin_depth("HFSS",  layer_name="LAY2", net_name="VCC")