AEDT Applications
=================
The PyAEDT API includes classes for applications and modules. You must initialize the 
application case. All other classes and methods are inherited into the application class.
The desktop application is implicitly launched in any of the other applications.

Example with Desktop:

.. code:: python

    from pyaedt import Desktop, Circuit
    d = Desktop(specified_version="2022.1",
                 non_graphical=False, new_desktop_session=True,
                 close_on_exit=True, student_version=False):
     circuit = Circuit()
     ...
     # Any error here will be caught by Desktop.
     ...
     d.release_desktop()

Example without Desktop:

.. code:: python

    from pyaedt import Circuit
    circuit = Circuit(specified_version="2022.1",
                 non_graphical=False, new_desktop_session=True,
                 close_on_exit=True, student_version=False):
     circuit = Circuit()
     ...
     # Any error here will be caught by Desktop.
     ...
     circuit.release_desktop()


.. currentmodule:: pyaedt

.. autosummary::
   :toctree: _autosummary

   Desktop
   Hfss
   Q3d
   Q2d
   Maxwell2d
   Maxwell3d
   Icepak
   Hfss3dLayout
   Mechanical
   Rmxprt
   Circuit
   Emit
   TwinBuilder

