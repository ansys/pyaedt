Report configuration file
=========================

The report configuration file allows to create a report based on a JSON file or a dictionary of properties.

This code shows how to create the JSON file:

.. code:: python

    from pyaedt import Hfss
    hfss = Hfss()
    compfile = hfss.components3d["Dipole_Antenna_DM"]
    geometryparams = hfss.get_components3d_vars("Dipole_Antenna_DM")
    hfss.modeler.insert_3d_component(compfile, geometryparams)
    hfss.create_setup()
    filename = "hfss_report_example.json"
    hfss.post.create_report_from_configuration(input_file=filename)
    hfss.release_desktop()

File structure example:

:download:`HFSS report example <../../Resources/hfss_report_example.json>`

For a practical demonstration, see the
`Report configuration file example <https://aedt.docs.pyansys.com/version/stable/examples/07-Circuit/Reports.html#sphx-glr-examples-07-circuit-reports-py>`_
