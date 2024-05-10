Basic tutorial
==============

You can initiate AEDT in non-graphical mode from Python using this code:

.. code:: python

    # Launch AEDT 2023 R2 in non-graphical mode
    import pyaedt
    with pyaedt.Desktop(specified_version="2023.2", non_graphical=True, new_desktop_session=True, close_on_exit=True,
                 student_version=False):
        circuit = pyaedt.Circuit()
        ...
        # Any error here is caught by AEDT.
        ...
    # AEDT is automatically closed here.

The preceding code launches AEDT and initializes a new Circuit design.

.. image:: ../Resources/aedt_first_page.webp
  :width: 800
  :alt: AEDT launched

This code creates a project and saves it with PyAEDT:

.. code:: python

    # Launch the latest installed version of AEDT in graphical mode.
    import pyaedt
    cir =  pyaedt.Circuit(non_graphical=False)
    cir.save_project(my_path)
    ...
    cir.release_desktop(save_project=True, close_desktop=True)
    # Desktop is released here.

This code uses PyAEDT to access the Ansys EDB proprietary layout format:

.. code:: python

    # Launch the latest installed version of EDB.
    import pyaedt
    edb = pyaedt.Edb("mylayout.aedb")

    # User can launch EDB directly from the PyEDB class.

    import pyedb
    edb = pyedb.Edb("mylayout.aedb")
