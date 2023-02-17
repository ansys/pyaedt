Twin Builder templates and arguments
====================================


This section lists all setup templates with their default values and keys available in Twin Builder.

You can edit a setup after it is created. Here is an example:

.. code:: python

    from pyaedt import Hfss

    hfss = Hfss()
    # Any property of this setup can be found on this page.
    setup = hfss.create_setup()
    setup.props["AdaptMultipleFreqs"] = True
    setup.update()



.. pprint:: pyaedt.modules.SetupTemplates.TR
