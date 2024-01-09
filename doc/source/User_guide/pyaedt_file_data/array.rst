Array file
==========

The array configuration file allows to create a 3D Component array from a JSON file.

This file can be created using the following command:

.. code:: python

    from pyaedt import Hfss
    from pyaedt.generic.DataHandlers import json_to_dict
    hfss = Hfss()
    dict_in = json_to_dict("array_simple.json")
    dict_in["Circ_Patch_5GHz1"] = "Circ_Patch_5GHz_232.a3dcomp"
    dict_in["cells"][(3, 3)] = {"name": "Circ_Patch_5GHz1"}
    component_array = hfss.add_3d_component_array_from_json(dict_in)
    hfss.release_desktop()

The main file skeleton is shown below.

:download:`Array example <../../Resources/array_example.json>`
