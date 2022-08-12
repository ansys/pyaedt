Setup templates
===============

This section lists all setup templates with their default values and keys. 

You can edit a setup after it is created. Here is an example:

.. code:: python

    Launch AEDT 2021 R1 in non-graphical mode

    from pyaedt import Hfss

    hfss = Hfss()
    # Any property of this setup can be found on this page.
    setup = hfss.create_setup()
    setup.props["AdaptMultipleFreqs"] = True
    setup.update()


.. currentmodule:: pyaedt.modules.SetupTemplates

HFSS
~~~~

.. autosummary::
   :toctree: _autosummary

   HFSSDrivenAuto
   HFSSDrivenDefault
   HFSSEigen
   HFSSTransient
   HFSSSBR


Maxwell 2D or 3D
~~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: _autosummary

   MaxwellTransient
   Magnetostatic
   Electrostatic
   EddyCurrent
   ElectricTransient


Q3D or Q2D Extractor
~~~~~~~~~~~~~~~~~~~~

.. autosummary::
   :toctree: _autosummary

   Matrix
   Close
   Open

Icepak
~~~~~~

.. autosummary::
   :toctree: _autosummary

   TransientFlowOnly
   TransientTemperatureOnly
   TransientTemperatureAndFlow


Nexxim
~~~~~~

.. autosummary::
   :toctree: _autosummary

   NexximLNA
   NexximDC
   NexximTransient


HFSS 3D Layout
~~~~~~~~~~~~~~

.. autosummary::
   :toctree: _autosummary

   HFSS3DLayout


Mechanical
~~~~~~~~~~

.. autosummary::
   :toctree: _autosummary

   MechTerm
   MechModal
   MechStructural


RMXprt
======

.. autosummary::
   :toctree: _autosummary

   GRM
