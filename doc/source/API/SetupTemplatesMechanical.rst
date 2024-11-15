Mechanical templates and arguments
==================================

This section lists all setup templates with their default values and keys available in Mechanical.

You can edit a setup after it is created. Here is an example:

.. code:: python


    from ansys.aedt.core import Mechanical

    app = Mechanical()
    # Any property of this setup can be found on this page.
    setup = app.create_setup(MaxModes=6)




.. pprint:: ansys.aedt.core.modules.setup_templates.MechTerm
.. pprint:: ansys.aedt.core.modules.setup_templates.MechModal
.. pprint:: ansys.aedt.core.modules.setup_templates.MechStructural

