Circuit  templates and arguments
================================

This section lists all setup templates with their default values and keys available in Circuit.

You can edit a setup after it is created. Here is an example:

.. code:: python

    from ansys.aedt.core import Hfss

    hfss = Hfss()
    # Any property of this setup can be found on this page.
    setup = hfss.create_setup()
    setup.props["AdaptMultipleFreqs"] = True
    setup.update()



.. pprint:: ansys.aedt.core.modules.SetupTemplates.NexximLNA
.. pprint:: ansys.aedt.core.modules.SetupTemplates.NexximDC
.. pprint:: ansys.aedt.core.modules.SetupTemplates.NexximTransient
.. pprint:: ansys.aedt.core.modules.SetupTemplates.NexximQuickEye
.. pprint:: ansys.aedt.core.modules.SetupTemplates.NexximVerifEye
.. pprint:: ansys.aedt.core.modules.SetupTemplates.NexximAMI

