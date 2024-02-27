Primitives file
===============
The primitives configuration file allows you to create primitive shapes from a JSON file.

This code creates primitive shapes from the JSON file:

.. code:: python

    from pyaedt import Icepak
    ipk = Icepak()
    ipk.modeler.import_primitives_from_file("primitive_example.json")
    ipk.release_desktop()

File structure example:

:download:`Primitive example <../../Resources/primitive_example.json>`
