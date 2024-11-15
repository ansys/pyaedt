HFSS 3D Layout and arguments
============================

This section lists all setup templates with their default values and keys available in HFSS 3D Layout.

You can edit a setup after it is created. Here is an example:

.. code:: python

    Launch AEDT 2023 R1 in non-graphical mode

    from ansys.aedt.core import Hfss

    hfss = Hfss()
    # Any property of this setup can be found on this page.
    setup = hfss.create_setup()
    setup.props["AdaptMultipleFreqs"] = True
    setup.update()



.. pprint:: ansys.aedt.core.modules.setup_templates.HFSS3DLayout
