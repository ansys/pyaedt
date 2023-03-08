RMXprt templates and arguments
==============================

This section lists all setup templates with their default values and keys available in RMXprt.

You can edit a setup after it is created. Here is an example:

.. code:: python

    from pyaedt import Hfss

    hfss = Hfss()
    # Any property of this setup can be found on this page.
    setup = hfss.create_setup()
    setup.props["AdaptMultipleFreqs"] = True
    setup.update()



.. pprint:: pyaedt.modules.SetupTemplates.GRM
.. pprint:: pyaedt.modules.SetupTemplates.DFIG
.. pprint:: pyaedt.modules.SetupTemplates.TPIM
.. pprint:: pyaedt.modules.SetupTemplates.TPSM
.. pprint:: pyaedt.modules.SetupTemplates.BLDC
.. pprint:: pyaedt.modules.SetupTemplates.ASSM
.. pprint:: pyaedt.modules.SetupTemplates.PMDC
.. pprint:: pyaedt.modules.SetupTemplates.SRM
.. pprint:: pyaedt.modules.SetupTemplates.LSSM
.. pprint:: pyaedt.modules.SetupTemplates.UNIM
.. pprint:: pyaedt.modules.SetupTemplates.DCM
.. pprint:: pyaedt.modules.SetupTemplates.CPSM
.. pprint:: pyaedt.modules.SetupTemplates.NSSM

