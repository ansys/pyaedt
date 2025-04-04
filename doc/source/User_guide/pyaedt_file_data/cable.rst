Cable file
==========

The cable configuration file allows you to create a cable geometry with shielding from a JSON file.

This file can be created using the following command:

.. code:: python

    from ansys.aedt.core import Hfss
    from ansys.aedt.core.modules.cable_modeling import Cable
    from ansys.aedt.core.generic.DataHandlers import json_to_dict
    hfss = Hfss()
    cable = Cable(hfss,"set_cable_properties.json"))
    cable.create_cable()
    hfss.release_desktop()

File structure example:

:download:`Cable example <../../Resources/cable_example.json>`

For a practical demonstration, see the
`Cable API <https://aedt.docs.pyansys.com/version/stable/API/CableModeling.html>`_ example.
