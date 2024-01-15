Materials file
==============

The material configuration file allows you to create materials from a JSON file.

This code creates the JSON file:

.. code:: python

    from pyaedt import Maxwell3d
    maxwell = Maxwell3d()
    maxwell.materials.export_materials_to_file("materials.json")
    maxwell.release_desktop()

This code imports materials from the JSON file:

.. code:: python

    from pyaedt import Maxwell3d
    maxwell = Maxwell3d()
    maxwell.materials.import_materials_from_file("material_example.json")
    maxwell.release_desktop()


File structure example:

:download:`Material example <../../Resources/material_example.json>`
