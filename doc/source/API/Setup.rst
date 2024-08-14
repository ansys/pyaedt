Setup
=====
This section lists setup modules:

* ``Setup`` for HFSS, Maxwell 2D, Maxwell 3D, Q2D Extractor, and Q3D Extractor
* ``Setup3DLayout`` for HFSS 3D Layout
* ``SetupCircuit`` for Circuit and Twin Builder

The ``Setup`` object is accessible through the ``create_setup`` method and ``setups`` object list.

.. currentmodule:: ansys.aedt.core.modules.solve_setup

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   SetupHFSS
   SetupHFSSAuto
   SetupSBR
   SetupQ3D
   SetupMaxwell
   Setup
   Setup3DLayout
   SetupCircuit

.. code:: python

    from ansys.aedt.core import Hfss
    app = Hfss(specified_version="2023.1",
               non_graphical=False, new_desktop_session=True,
               close_on_exit=True, student_version=False)

    # This call returns the Setup class
    my_setup = app.setups[0]


    # This call returns a Setup object
    setup = app.create_setup("MySetup")

    ...


Sweep classes
=============
This section lists sweep classes and their default values:

* ``SweepHFSS`` for HFSS
* ``SweepHFSS3DLayout`` for HFSS 3D Layout
* ``SweepMatrix`` for Q3D and 2D Extractor

The ``Setup`` object is accessible through the methods available for sweep creation.


.. currentmodule:: ansys.aedt.core.modules.solve_sweeps

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   SweepHFSS
   SweepHFSS3DLayout
   SweepMatrix
