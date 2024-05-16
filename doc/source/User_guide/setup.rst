Setup
=====

Setup and sweeps are the last operations before running an analysis.
PyAEDT facilitates seamless interaction with these operations by enabling
the reading, editing, and creation of setups and sweeps within a design.
All setup operations are conveniently accessible and organized in the setups list,
providing a clear and intuitive interface for managing and customizing these
essential components of the simulation process:

.. code:: python

    from pyaedt import Maxwell3d
    m3d = Maxwell3d()
    all_setups = m3d.setups
    my_setup = all_setups[0]
    # All properties are in props dictionary.
    my_setup.props['MaximumPasses'] = 10
    new_setup = m3d.create_setup("New_Setup")


.. image:: ../Resources/Setups.webp
  :width: 800
  :alt: Setup Editing and Creation

