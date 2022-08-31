Setup
=====
Setup, optimetrics, and sweeps are the last operations before running analysis.
PyAEDT can read all setups, optimetrics, and sweeps already present in a design,
edit them, and create them. All setup operations are listed in the setups list:

.. code:: python


    from pyaedt import Maxwell3d
    m3d = Maxwell3d()
    all_setups = m3d.setups
    my_setup = all_setups[0]
    # all properties are in props dictionary.
    my_setup.props['MaximumPasses'] = 10

    new_setup = m3d.create_setup("New_Setup")



.. image:: ../Resources/Setups.png
  :width: 800
  :alt: Setup Editing and Creation

