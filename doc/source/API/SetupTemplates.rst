Setup Templates
===============

This page lists all setup templates with their default values and keys. 

You can edit a setup after it is created. Here an example:

.. code:: python

    Launch AEDT 2021 R1 in Non-Graphical mode

    from pyaedt import Hfss

    hfss = Hfss()
    # Any property of this setup can be found in this page.
    hfss.props["AdaptMultipleFreqs"] = True
    hfss.update()




.. currentmodule:: pyaedt.modules.SetupTemplates

HFSS Templates
==============

.. autosummary::
   :toctree: _autosummary

   HFSSDrivenAuto
   HFSSDrivenDefault
   HFSSEigen
   HFSSTransient
   HFSSSBR


Maxwell Templates
=================

.. autosummary::
   :toctree: _autosummary

   MaxwellTransient
   Magnetostatic
   Electrostatic
   EddyCurrent
   ElectricTransient


Q3D Templates
=============

.. autosummary::
   :toctree: _autosummary

   Matrix
   Close
   Open

Icepak Templates
================

.. autosummary::
   :toctree: _autosummary

   TransientFlowOnly
   TransientTemperatureOnly
   TransientTemperatureAndFlow


Nexxim Analsyis
===============

.. autosummary::
   :toctree: _autosummary

   NexximLNA
   NexximDC
   NexximTransient


HFSS 3D Layout
==============

.. autosummary::
   :toctree: _autosummary

   HFSS3DLayout


Mechanical Analysis
===================

.. autosummary::
   :toctree: _autosummary

   MechTerm
   MechModal
   MechStructural


RMXprt Analysis
===============

.. autosummary::
   :toctree: _autosummary

   GRM
