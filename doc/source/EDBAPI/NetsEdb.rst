Nets
====
This section contains API references for net management.
The main component object is called directly from main application using the property ``nets``.

.. code:: python

    from pyaedt import Edb
    edb = Edb(myedb, edbversion="2023.1")

    edb.nets.plot(None,None)

    ...


.. currentmodule:: pyaedt.edb_core.nets

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   EdbNets


Net properties
--------------
The following class is the container of data management for nets, extended nets and differential pairs.


.. currentmodule:: pyaedt.edb_core.edb_data.nets_data

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   EDBNetsData
   EDBNetClassData
   EDBExtendedNetData
   EDBDifferentialPairData

.. code:: python

    from pyaedt import Edb
    edb = Edb(myedb, edbversion="2023.1")

    edb.nets["M_MA<6>"].delete()


    ...