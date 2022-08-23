Mesh
====
Mesh operations are very important in engineering simulation. PyAEDT can read all mesh
operations already present in a design, edit them, and create them. All mesh operations
are listed in the mesh object:

.. code:: python


    from pyaedt import Maxwell3d
    m3d = Maxwell3d()
    all_mesh_ops = m3d.mesh.meshoperations
    my_mesh_op = all_mesh_ops[0]
    # all properties are in props dictionary.
    my_mesh_op.props["my_prop"] = "my_value"
    my_mesh_op.update()


.. image:: ../Resources/Mesh_Operations.png
  :width: 800
  :alt: Mesh object List

