EDB padstack
============
These classes are the containers of data management for padstacks and padstack definitions.

.. code:: python

    from pyaedt import Edb
    edb = Edb(myedb, edbversion="2022.2")

    edb.core_padstack.create_padstack(
    padstackname="SVIA", holediam="$via_hole_size", antipaddiam="$antipaddiam", paddiam="$paddiam"
    )


    ...


.. currentmodule:: pyaedt.edb_core.edb_data.padstacks_data

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   EDBPadProperties
   EDBPadstack
   EDBPadstackInstance
