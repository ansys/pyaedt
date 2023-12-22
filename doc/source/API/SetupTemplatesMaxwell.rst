Maxwell templates and arguments
===============================


This section lists all setup templates with their default values and keys available in Maxwell 2D and 3D.

You can edit a setup after it is created. Here is an example:

.. code:: python

    from pyaedt import Maxwell3d

    Maxwell3d = Maxwell3d ()
    # Any property of this setup can be found on this page.
    setup = Maxwell3d.create_setup ()
    setup.props["MaximumPasses"] = 5
    setup.update ()

.. pprint:: pyaedt.modules.SetupTemplates.MaxwellTransient
.. pprint:: pyaedt.modules.SetupTemplates.Magnetostatic
.. pprint:: pyaedt.modules.SetupTemplates.Electrostatic
.. pprint:: pyaedt.modules.SetupTemplates.EddyCurrent
.. pprint:: pyaedt.modules.SetupTemplates.ElectricTransient
