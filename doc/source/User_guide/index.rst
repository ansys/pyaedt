.. _ref_user_guide:

==========
User guide
==========
PyAEDT works both inside AEDT and as a standalone application.
It automatically detects whether it is running in an IronPython (limited capabilities) or CPython
environment and initializes AEDT accordingly. PyAEDT also provides
advanced error management.

You can start AEDT in non-graphical mode from Python:

.. code:: python

    # Launch AEDT 2023 R1 in non-graphical mode

    import pyaedt
    with pyaedt.Desktop(specified_version="2023.1", non_graphical=True, new_desktop_session=True, close_on_exit=True,
                 student_version=False):
        circuit = pyaedt.Circuit()
        ...
        # Any error here will be caught by Desktop.
        ...

    # Desktop is automatically closed here.


The preceding code launches AEDT and initializes a new Circuit design.

.. image:: ../Resources/aedt_first_page.png
  :width: 800
  :alt: Electronics Desktop Launched


You can obtain the same result with:

.. code:: python

    # Launch the latest installed version of AEDT in graphical mode.

    import pyaedt
    with pyaedt.Circuit(specified_version="2023.1", non_graphical=False) as circuit:
        ...
        # Any error here will be caught by Desktop.
        ...

    # Desktop is automatically released here.



.. toctree::
   :hidden:
   :maxdepth: 2

   variables
   modeler
   mesh
   setup
   optimetrics
   postprocessing
