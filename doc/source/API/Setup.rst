Setup
=====
This section lists setup modules:

* ``Setup`` for HFSS, Maxwell 2D, Maxwell 3D, Q2D Extractor, and Q3D Extractor
* ``Setup3DLayout`` for HFSS 3D Layout
* ``SetupCircuit`` for Circuit and Twin Builder

The ``Setup`` object is accessible through the ``create_setup`` method and ``setups`` object list.

.. currentmodule:: pyaedt.modules.SolveSetup

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   Setup
   Setup3DLayout
   SetupCircuit

.. code:: python

    from pyaedt import Hfss
    app = Hfss(specified_version="2022.1",
               non_graphical=False, new_desktop_session=True,
               close_on_exit=True, student_version=False)

    # This call returns the Setup class
    my_setup = app.setups[0]


    # This call returns a Setup object
    setup = app.create_setup("MySetup")

    ...


Sweep Classes
=============
This section lists sweep classes and their default values:

* ``SweepHFSS`` for HFSS
* ``SweepHFSS3DLayout`` for HFSS 3D Layout
* ``SweepQ3D`` for Q3D Extractor

The ``Setup`` object is accessible through the methods available for sweep creation.


.. currentmodule:: pyaedt.modules.SetupTemplates

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   SweepHFSS
   SweepHFSS3DLayout
   SweepQ3D
