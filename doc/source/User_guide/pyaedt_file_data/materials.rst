Materials File
==============

The material configuration file allows to create materials from a JSON file.

This file can be created using the following command:

.. code:: python

    from pyaedt import Maxwell3d
    maxwell = Maxwell3d()
    maxwell.materials.export_materials_to_file("materials.json")
    maxwell.release_desktop()

You can import this file:

.. code:: python

    from pyaedt import Maxwell3d
    maxwell = Maxwell3d()
    maxwell.materials.import_materials_from_file("material_example.json")
    maxwell.release_desktop()


The main file skeleton is shown below.

:download:`Material example <../../Resources/material_example.json>`
