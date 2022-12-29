AEDT apps
=========
The PyAEDT API includes classes for apps and modules. You must initialize the 
app to get access to all modules and methods. Availables apps are:

- Hfss
- Hfss3dLayout
- Maxwell3d
- Maxwell2d
- MaxwellCircuit
- Q3d
- Q2d
- Icepak
- Mechanical
- Rmxprt
- Emit
- Circuit
- TwinBuilder


.. image:: ../Resources/aedt_2.png
  :width: 800
  :alt: Ansys Electronics Desktop (AEDT) is a platform that enables true electronics system design.


All other classes and methods are inherited into the app class.
The desktop app is implicitly launched in any of the other applications.
Before accessing an AEDT app the Desktop has to be launched and initialized.
Desktop can be explicitily or implicitily initialized as in following examples.

Example with ``Desktop`` class explicit initialization:

.. code:: python

    from pyaedt import launch_desktop, Circuit
    d = launch_desktop(specified_version="2022.2",
                       non_graphical=False,
                       new_desktop_session=True,
                       close_on_exit=True,
                       student_version=False):
     circuit = Circuit()
     ...
     # Any error here will be caught by Desktop.
     ...
     d.release_desktop()

Example with ``Desktop`` class implicit initialization:

.. code:: python

    from pyaedt import Circuit
    circuit = Circuit(specified_version="2022.2",
                      non_graphical=False,
                      new_desktop_session=True,
                      close_on_exit=True,
                      student_version=False):
     circuit = Circuit()
     ...
     # Any error here will be caught by Desktop.
     ...
     circuit.release_desktop()


.. autosummary::
   :toctree: _autosummary

   pyaedt.desktop.Desktop
   pyaedt.hfss.Hfss
   pyaedt.q3d.Q3d
   pyaedt.q3d.Q2d
   pyaedt.maxwell.Maxwell2d
   pyaedt.maxwell.Maxwell3d
   pyaedt.icepak.Icepak
   pyaedt.hfss3dlayout.Hfss3dLayout
   pyaedt.mechanical.Mechanical
   pyaedt.rmxprt.Rmxprt
   pyaedt.circuit.Circuit
   pyaedt.maxwellcircuit.MaxwellCircuit
   pyaedt.emit.Emit
   pyaedt.twinbuilder.TwinBuilder

