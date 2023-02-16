HFSS templates and arguments
============================

This section lists all setup templates with their default values and keys available in HFSS.

You can edit a setup after it is created. Here is an example:

.. code:: python

    Launch AEDT 2021 R1 in non-graphical mode

    from pyaedt import Hfss

    hfss = Hfss()
    # Any property of this setup can be found on this page.
    setup = hfss.create_setup()
    setup.props["AdaptMultipleFreqs"] = True
    setup.update()



.. pprint:: pyaedt.modules.SetupTemplates.HFSSDrivenAuto
.. pprint:: pyaedt.modules.SetupTemplates.HFSSDrivenDefault
.. pprint:: pyaedt.modules.SetupTemplates.HFSSDrivenDefault
.. pprint:: pyaedt.modules.SetupTemplates.HFSSTransient
.. pprint:: pyaedt.modules.SetupTemplates.HFSSSBR

