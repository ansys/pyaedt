Components
==========
This sections contains API references for net management.
The main component object is called directly from main application using the property ``nets``.

.. code:: python

    from pyaedt import Edb
    edb = Edb(myedb, edbversion="2022.2")

    edb.nets.plot(None,None)

    ...


.. currentmodule:: pyaedt.edb_core.nets

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   EdbNets


Net Properties
--------------
The following class is the container of data management for nets.



.. currentmodule:: pyaedt.edb_core.edb_data.nets_data

.. autosummary::
   :toctree: _autosummary
   :nosignatures:


   EDBNetsData


.. code:: python

    from pyaedt import Edb
    edb = Edb(myedb, edbversion="2022.2")

    edb.nets["M_MA<6>"].delete()


    ...