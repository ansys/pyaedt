AEDT apps
=========
The PyAEDT API includes classes for apps and modules. You must initialize the 
app case. All other classes and methods are inherited into the app class.
The desktop app is implicitly launched in any of the other applications.

Example with AEDT:

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

Example without desktop:

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

