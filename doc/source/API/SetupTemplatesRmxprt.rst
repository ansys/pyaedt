RMXprt templates and arguments
==============================

This section lists all setup templates with their default values and keys available in RMXprt.

You can edit a setup after it is created. Here is an example:

.. code:: python

    from ansys.aedt.core import Hfss

    hfss = Hfss()
    # Any property of this setup can be found on this page.
    setup = hfss.create_setup()
    setup.props["AdaptMultipleFreqs"] = True
    setup.update()



.. pprint:: ansys.aedt.core.modules.SetupTemplates.GRM
.. pprint:: ansys.aedt.core.modules.SetupTemplates.DFIG
.. pprint:: ansys.aedt.core.modules.SetupTemplates.TPIM
.. pprint:: ansys.aedt.core.modules.SetupTemplates.TPSM
.. pprint:: ansys.aedt.core.modules.SetupTemplates.BLDC
.. pprint:: ansys.aedt.core.modules.SetupTemplates.ASSM
.. pprint:: ansys.aedt.core.modules.SetupTemplates.PMDC
.. pprint:: ansys.aedt.core.modules.SetupTemplates.SRM
.. pprint:: ansys.aedt.core.modules.SetupTemplates.LSSM
.. pprint:: ansys.aedt.core.modules.SetupTemplates.UNIM
.. pprint:: ansys.aedt.core.modules.SetupTemplates.DCM
.. pprint:: ansys.aedt.core.modules.SetupTemplates.CPSM
.. pprint:: ansys.aedt.core.modules.SetupTemplates.NSSM

