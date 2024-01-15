Minimal example
===============

You can initiate AEDT in non-graphical mode from Python using this code:

.. code:: python

    # Launch AEDT 2023 R2 in non-graphical mode
    import pyaedt
    with pyaedt.Desktop(specified_version="2023.2", non_graphical=True, new_desktop_session=True, close_on_exit=True,
                 student_version=False):
        circuit = pyaedt.Circuit()
        ...
        # Any error here will be caught by Desktop.
        ...
    # Desktop is automatically closed here.

The preceding code launches AEDT and initializes a new Circuit design.

.. image:: ../Resources/aedt_first_page.png
  :width: 800
  :alt: Electronics Desktop launched

This code creates a project and saves it with PyAEDT:

.. code:: python

    # Launch the latest installed version of AEDT in graphical mode.
    import pyaedt
    cir =  pyaedt.Circuit(non_graphical=False)
    cir.save_project(my_path)
    ...
    cir.release_desktop(save_project=True, close_desktop=True)
    # Desktop is released here.
