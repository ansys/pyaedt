Setup templates
===============

This section lists all setup templates with their default values and keys. 

You can edit a setup after it is created. Here is an example:

.. code:: python

    Launch AEDT 2023 R1 in non-graphical mode

    from ansys.aedt.core import Hfss

    hfss = Hfss()
    # Any property of this setup can be found on this page.
    setup = hfss.create_setup()
    setup.props["AdaptMultipleFreqs"] = True
    setup.update()


.. toctree::
   :maxdepth: 2

   SetupTemplatesHFSS
   SetupTemplates3DLayout
   SetupTemplatesMaxwell
   SetupTemplatesQ3D
   SetupTemplatesIcepak
   SetupTemplatesMechanical
   SetupTemplatesCircuit
   SetupTemplatesTwinBuilder
   SetupTemplatesRmxprt
