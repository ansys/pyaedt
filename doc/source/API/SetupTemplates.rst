Setup Templates
===============
This page contains all the Setup Default Templates values and keys. it can be used to edit a setup after it is created
Example

.. code:: python

    Launch AEDT 2021 R1 in Non-Graphical mode

    from pyaedt import Hfss

    hfss = Hfss()
    # Any property of this setup can be found in this page.
    hfss.props["AdaptMultipleFreqs"] = True
    hfss.update()





HFSS Templates
==============

Hfss Automatic Setup
--------------------

.. autodata:: pyaedt.modules.SetupTemplates.HFSSDrivenAuto

Hfss Driven Modal
-----------------

.. autodata:: pyaedt.modules.SetupTemplates.HFSSDrivenDefault

Hfss Eigen Mode
---------------

.. autodata:: pyaedt.modules.SetupTemplates.HFSSEigen

Hfss Transient
--------------

.. autodata:: pyaedt.modules.SetupTemplates.HFSSTransient


Hfss SBR+
---------

.. autodata:: pyaedt.modules.SetupTemplates.HFSSSBR



Maxwell Templates
=================

Maxwell Transient
-----------------

.. autodata:: pyaedt.modules.SetupTemplates.MaxwellTransient


Maxwell Magnetostatic
---------------------

.. autodata:: pyaedt.modules.SetupTemplates.Magnetostatic


Maxwell Electrostatic
---------------------

.. autodata:: pyaedt.modules.SetupTemplates.Electrostatic

Maxwell EddyCurrent
-------------------

.. autodata:: pyaedt.modules.SetupTemplates.EddyCurrent

Maxwell ElectricTransient
-------------------------

.. autodata:: pyaedt.modules.SetupTemplates.ElectricTransient


Q3D Templates
=============

Q3d  Analysis
-------------

.. autodata:: pyaedt.modules.SetupTemplates.Matrix


Q2d Close Analysis
------------------

.. autodata:: pyaedt.modules.SetupTemplates.Close

Q2d Open Analysis
-----------------

.. autodata:: pyaedt.modules.SetupTemplates.Open
Icepak Templates
================


Transient Flow Only
-------------------

.. autodata:: pyaedt.modules.SetupTemplates.TransientFlowOnly

Temperature Flow Only
---------------------

.. autodata:: pyaedt.modules.SetupTemplates.TransientTemperatureOnly


Transient & Temperature Flow
----------------------------

.. autodata:: pyaedt.modules.SetupTemplates.TransientTemperatureAndFlow


Nexxim Analsyis
===============

LNA Analysis
------------

.. autodata:: pyaedt.modules.SetupTemplates.NexximLNA


DC Analysis
-----------

.. autodata:: pyaedt.modules.SetupTemplates.NexximDC


Transient Analysis
------------------

.. autodata:: pyaedt.modules.SetupTemplates.NexximTransient


HFSS 3D Layout
==============

.. autodata:: pyaedt.modules.SetupTemplates.HFSS3DLayout


Mechanical Analysis
===================


Mechanical Thermal
------------------

.. autodata:: pyaedt.modules.SetupTemplates.MechTerm


Mechanical Modal
----------------

.. autodata:: pyaedt.modules.SetupTemplates.MechModal


Mechanical MechStructural
-------------------------

.. autodata:: pyaedt.modules.SetupTemplates.MechStructural


RMXPrt Analysis
===============



.. autodata:: pyaedt.modules.SetupTemplates.GRM