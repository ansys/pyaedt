HFSS 3D Layout and arguments
============================

This section lists all setup templates with their default values and keys available in HFSS 3D Layout.

You can edit a setup after it is created. Here is an example:

.. code:: python

    from ansys.aedt.core import Hfss3dLayout

    hfss = Hfss3dLayout()
    setup = hfss.create_setup()
    setup.props["MeshSizeFactor"] = 2


.. pprint:: ansys.aedt.core.modules.setup_templates.HFSS3DLayout
