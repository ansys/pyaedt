Modeler
=======
The AEDT 3D and 2D Modelers use object-oriented programming to create and manage objects. 
You can use getters and setters to create an object and change its properties:

.. code:: python

    Create a box, assign variables, and assign materials.

    from pyaedt.hfss import Hfss
    with Hfss as hfss:
         box = hfss.modeler.create_box([0, 0, 0], [10, "dim", 10],
                                       "mybox", "aluminum")
         print(box.faces)
         box.material_name = "copper"
         box.color = "Red"



.. image:: ../Resources/aedt_box.png
  :width: 800
  :alt: Modeler Object

Once an object is created or is present in the design (from a loaded project), you can
use a getter to get the related object. A getter works either with an object ID or
object name. The object returned has all features, even if it has not been created in PyAEDT.

This example shows how easily you can go deeper into edges and vertices of faces or 3D objects:

.. code:: python

     box = hfss.modeler["mybox2"]
     for face in box.faces:
        print(face.center)
        for edge in face:
            print(edge.midpoint)
            for vertice in edge.vertices:
                print(edge.position)
     for vertice in box.vertices:
        print(edge.position)


All objects support executing any modeler operation, such as union or subtraction:

.. code:: python


     box = hfss.modeler["mybox2"]
     cyl = hfss.modeler["mycyl"]
     box.unit(cyl)


.. image:: ../Resources/objects_operations.gif
  :width: 800
  :alt: Object Modeler Operations

