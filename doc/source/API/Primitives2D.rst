2D modeler
===========

This section lists the core AEDT Modeler modules for 2D and 3D solvers (Maxwell 2D, 2D Extractor).


They are accessible through the ``modeler`` property:

.. code:: python

    from pyaedt import Maxwell2d
    app = Maxwell2d(specified_version="2023.1",
                 non_graphical=False, new_desktop_session=True,
                 close_on_exit=True, student_version=False)

    # This call return the Modeler2D class
    modeler = app.modeler


    ...



The ``Modeler`` module contains all properties and methods needed to edit a
modeler, including all primitives methods and properties:


.. currentmodule:: pyaedt.modeler

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   modeler2d.Modeler2D



.. code:: python

    from pyaedt import Maxwell2d
    app = Maxwell2d(specified_version="2023.1",
                 non_graphical=False, new_desktop_session=True,
                 close_on_exit=True, student_version=False)

    # This call returns the NexximComponents class
    origin = [0,0,0]
    dimensions = [10,5,20]
    #Material and name are not mandatory fields
    box_object = app.modeler.primivites.create_rectangle([15, 20, 0], [5, 5], material="aluminum")

    ...
