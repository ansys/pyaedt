Setup
=====
This section lists setup modules:
* Setup for ``Hfss``, ``Maxwell2D``, ``Maxwell3d``, ``Q2d`` and ``Q3d``
* SetupCircuit for ``Circuit`` and ``Simplorer``
* Setup3DLayout for ``Hfss3dLayout``
Setup object is accessible through the ``create_setup`` method and ``setups`` object list.

.. code:: python

    from pyaedt import Hfss
    app = Hfss(specified_version="2021.1",
               non_graphical=False, new_desktop_session=True,
               close_on_exit=True, student_version=False)

    # this call returns the Setup Class
    my_setup = app.setups[0]


    # this call returns a Setup Object
    setup = app.create_setup("MySetup")

    ...

.. currentmodule:: pyaedt.modules.SolveSetup

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   Setup
   Setup3DLayout
   SetupCircuit

Sweep Classes
=============
This section lists Sweep classes and their default values.
* SweepHFSS for ``Hfss``,
* SweepQ3D for ``Q3d``
* SweepHFSS3DLayout for ``Hfss3dLayout``
Setup object is accessible through the methods available for sweep creation.


.. currentmodule:: pyaedt.modules.SetupTemplates

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   SweepHFSS
   SweepHFSS3DLayout
   SweepQ3D
