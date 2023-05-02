Modeler in  HFSS 3D Layout
==========================

This section lists the core AEDT Modeler modules available in HFSS 3D Layout:

* Modeler
* Primitives
* Objects

They are accessible through the ``modeler`` module and ``modeler.objects`` property:

.. code:: python

    from pyaedt import Hfss3dLayout
    hfss = Hfss3dLayout()
    my_modeler = hfss.modeler

    ...


Modeler
~~~~~~~

The ``Modeler`` module contains all properties and methods needed to edit a
modeler, including all primitives methods and properties:


* ``Modeler3DLayout`` for HFSS 3D Layout



.. currentmodule:: pyaedt.modeler

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   modelerpcb.Modeler3DLayout


Objects in HFSS 3D Layout
~~~~~~~~~~~~~~~~~~~~~~~~~
The following classes define the object properties for HFSS 3D Layout.
They contain all getters and setters to simplify object manipulation.

.. currentmodule:: pyaedt.modeler.pcb

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   object3dlayout.Components3DLayout
   object3dlayout.Nets3DLayout
   object3dlayout.Pins3DLayout
   object3dlayout.Line3dLayout
   object3dlayout.Polygons3DLayout
   object3dlayout.Circle3dLayout
   object3dlayout.Rect3dLayout
   object3dlayout.Points3dLayout
   object3dlayout.Padstack

.. code:: python

    from pyaedt import Hfss3dLayout
    app = Hfss3dLayout(specified_version="2023.1",
               non_graphical=False, new_desktop_session=True,
               close_on_exit=True, student_version=False)

    # This call returns the Modeler3DLayout class
    modeler = app.modeler

    # This call returns a Primitives3D object
    primitives = modeler

    # This call returns an Object3d object
    my_rect = primitives.create_rectangle([0,0,0],[10,10])

    # Getter and setter
    my_rect.material_name

    ...
