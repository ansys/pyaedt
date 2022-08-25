.. _ref_user_guide:

==========
User guide
==========
PyAEDT works both inside AEDT and as a standalone application.
It automatically detects whether it is running in an IronPython or CPython
environment and initializes AEDT accordingly. PyAEDT also provides
advanced error management.

You can start AEDT in non-graphical mode from Python:

.. code:: python

    # Launch AEDT 2022 R1 in non-graphical mode

    from pyaedt import Desktop, Circuit
    with Desktop(specified_version="2022.1", non_graphical=True, new_desktop_session=True, close_on_exit=True,
                 student_version=False):
        circuit = Circuit()
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

    from pyaedt import Circuit
    with Circuit(specified_version="2022.1", non_graphical=False) as circuit:
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
