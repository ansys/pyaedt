Padstacks and vias
==================
This sections contains API references for padstack management.
The main padstack object is called directly from main application using the property ``padstacks``.

.. code:: python

    from pyaedt import Edb
    edb = Edb(myedb, edbversion="2022.2")

    edb.padstacks.create_padstack(
    padstackname="SVIA", holediam="$via_hole_size", antipaddiam="$antipaddiam", paddiam="$paddiam"
    )


    ...


.. currentmodule:: pyaedt.edb_core.padstack

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   padstack.EdbPadstacks


Instances and definitions
-------------------------
These classes are the containers of data management for padstacks instances and padstack definitions.


.. currentmodule:: pyaedt.edb_core.edb_data.padstacks_data

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   EDBPadProperties
   EDBPadstack
   EDBPadstackInstance
