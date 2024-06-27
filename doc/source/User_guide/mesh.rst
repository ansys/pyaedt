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

Icepak employs a unique approach to mesh operations, managed through mesh regions, which can be edited directly from the pyaedt object.

**Global Mesh Region**

The global mesh region object is accessed using:

.. code:: python

    glob_msh = ipk.mesh.global_mesh_region

This object allows for the editing of global mesh settings through its `settings` property, which functions like a dictionary.

.. code:: python

    glob_msh.settings["MeshRegionResolution"] = 3

Available keys differ depending on whether manual or automatic settings are used. This can be adjusted using the `manual_settings` boolean property of the global mesh region object.

To modify the global region dimensions, access the `global_region` property and modify its attributes.

.. code:: python

    glob_msh.global_region.positive_z_padding_type = "Absolute Offset"
    glob_msh.global_region.positive_z_padding = "5 mm"

To modify the properties of the Region object (for example the gas inside the region), access the `object` property of the `global_region` object:

.. code:: python

    glob_reg = glob_msh.global_region
    glob_reg.object.material_name = "Carbon Monoxide"

This is a pointer to the same object accessible from `ipk.modeler["Region"]`.

The image below summarizes these three objects:

.. image:: ../Resources/icepak_global_mesh_region_objects.png
  :width: 80%
  :alt: Global Mesh objects and sub-objects

A complete example using the global mesh region is provided:

.. code:: python

    ipk = Icepak()
    glob_msh = ipk.mesh.global_mesh_region
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

**Local Mesh Regions**

To create a mesh region, the `assign_mesh_region` function is used:

.. code:: python

    mesh_region = ipk.mesh.assign_mesh_region(name=object_name)

The settings of the returned object can be modified using the same approach as with the global mesh region object.

To access the subregion that defines the local mesh region and modify its dimensions:

.. code:: python

    subregion = mesh_region.assignment
    subregion.positive_z_padding_type = "Absolute Offset"
    subregion.positive_z_padding = "5 mm"

To access the parts included in the subregion:

.. code:: python

    subregion.parts

In AEDT 2024 R1, a significant revamp of the mesh region paradigm has been introduced, resulting in limited support for older versions. To use the same functions in older versions, the region box must be defined first and passed as the first argument of `assign_mesh_region`.

**Mesh Operations**

- To assign a mesh level to some objects, use the `assign_mesh_level` method:

  .. code:: python

    ipk.mesh.assign_mesh_level(mesh_order={"Box1": 2, "Cylinder1": 4})

- To assign a mesh file for reuse to some objects, use the `assign_mesh_reuse` method:

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