Perceive EM
===========
Perceive EM is a highly performant, physical optics (PO)-based shooting and bouncing rays (SBR)
technology deployed through a lightweight API that seamlessly integrates into any digital twin platform.

.. note::
    Requires Perceive EM 2025 R1 or later.


The ``PerceiveEM`` class is the main interface to the **Ansys Perceive EM API**, designed to provide simulation control,
scene management, and material definition for radar sensor simulation scenarios. It acts as a Python wrapper
within PyAEDT to seamlessly interact with the underlying native API.

.. currentmodule:: ansys.aedt.core.perceive_em.core.api_interface

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   PerceiveEM


Initialization
--------------

.. code-block:: python

    from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM

    perceive_em = PerceiveEM()

The constructor allows specifying a Perceive EM version. If not provided, it attempts to auto-detect
the latest supported version installed on the system.

Initialization
--------------

.. grid:: 2

   .. grid-item-card:: Scene
            :link: perceive_em/scene
            :link-type: doc
            :margin: 2 2 0 0

            Manage actors and antenna platforms

.. toctree::
   :hidden:
   :maxdepth: 2

   perceive_em/scene
