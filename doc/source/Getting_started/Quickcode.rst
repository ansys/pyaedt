Quick code
==========

Documentation and issues
------------------------
Documentation for the latest stable release of PyAEDT is hosted at
`PyAEDT documentation <https://aedt.docs.pyansys.com/version/stable/>`_.

In the upper right corner of the documentation's title bar, there is an option
for switching from viewing the documentation for the latest stable release
to viewing the documentation for the development version or previously
released versions.

You can also view or download PyAEDT cheat sheets, which are one-page references
providing syntax rules and commands for using the PyAEDT API and PyEDB API:

- `View PyAEDT cheat sheet <https://cheatsheets.docs.pyansys.com/pyaedt_API_cheat_sheet.png>`_ or
  `download PyAEDT cheat sheet <https://cheatsheets.docs.pyansys.com/pyaedt_API_cheat_sheet.pdf>`_ the
  PyAEDT API cheat sheet.

- `View EDB cheat sheet <https://cheatsheets.docs.pyansys.com/pyedb_API_cheat_sheet.png>`_ or
  `download EDB cheat sheet  <https://cheatsheets.docs.pyansys.com/pyedb_API_cheat_sheet.pdf>`_ the
  PyAEDT API cheat sheet.


On the `PyAEDT Issues <https://github.com/ansys/PyAEDT/issues>`_ page, you can
create issues to report bugs and request new features. On the `PyAEDT Discussions
<https://github.com/ansys/pyaedt/discussions>`_ page or the `Discussions <https://discuss.ansys.com/>`_
page on the Ansys Developer portal, you can post questions, share ideas, and get community feedback.

To reach the project support team, email `pyansys.core@ansys.com <pyansys.core@ansys.com>`_.


Example workflow
----------------
Here’s a brief example of how PyAEDT works:

Connect to AEDT from a Python IDE
---------------------------------
PyAEDT works both inside AEDT and as a standalone app.
This Python library automatically detects whether it is running
in an IronPython or CPython environment and initializes AEDT accordingly.
PyAEDT also provides advanced error management. Usage examples follow.

Explicit AEDT declaration and error management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    # Launch AEDT 2023 R1 in non-graphical mode

    from pyaedt import Desktop, Circuit
    with Desktop(specified_version="2023.1",
                 non_graphical=False, new_desktop_session=True,
                 close_on_exit=True, student_version=False):
        circuit = Circuit()
        ...
        # Any error here will be caught by Desktop.
        ...

    # Desktop is automatically released here.


Implicit AEDT declaration and error management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    # Launch the latest installed version of AEDT in graphical mode

    from pyaedt import Circuit
    with Circuit(specified_version="2023.1",
                 non_graphical=False) as circuit:
        ...
        # Any error here will be caught by Desktop.
        ...

    # Desktop is automatically released here.


Remote application call
~~~~~~~~~~~~~~~~~~~~~~~
You can make a remote application call on a CPython server
or any Windows client machine.

On a CPython server:

.. code:: python

    # Launch PyAEDT remote server on CPython

    from pyaedt.common_rpc import pyaedt_service_manager
    pyaedt_service_manager()


On any Windows client machine:

.. code:: python

    from pyaedt.common_rpc import create_session
    cl1 = create_session("server_name")
    cl1.aedt(port=50000, non_graphical=False)
    hfss = Hfss(machine="server_name", port=50000)
    # your code here

Variables
~~~~~~~~~

.. code:: python

    from pyaedt.HFSS import HFSS
    with HFSS as hfss:
         hfss["dim"] = "1mm"   # design variable
         hfss["$dim"] = "1mm"  # project variable


Modeler
~~~~~~~

.. code:: python

    # Create a box, assign variables, and assign materials.

    from pyaedt.hfss import Hfss
    with Hfss as hfss:
         hfss.modeler.create_box([0, 0, 0], [10, "dim", 10],
                                 "mybox", "aluminum")
