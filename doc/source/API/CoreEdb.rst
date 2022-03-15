EDB Modules
===========
This section lists the core EDB application modules for reading and writing
information to AEDB files.

.. code:: python

    from pyaedt import Edb
    edb = Edb(myedb, edbversion="2021.2")

    # this call return the EdbHfss Class
    comp = edb.core_hfss

    # this call return the Components Class
    comp = edb.core_components

    # this call return the EdbSiwave Class
    comp = edb.core_siwave

    # this call return the EdbPadstacks Class
    comp = edb.core_padstack

    # this call return the EdbStackup Class
    comp = edb.core_stackup

    ...

.. currentmodule:: pyaedt.edb_core

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   components.Components
   hfss.EdbHfss
   siwave.EdbSiwave
   nets.EdbNets
   padstack.EdbPadstacks
   layout.EdbLayout
   stackup.EdbStackup



EDB Data Classes
~~~~~~~~~~~~~~~~
Those classes are the container of Data read from edb file.

.. code:: python

    from pyaedt import Edb
    edb = Edb(myedb, edbversion="2021.2")

    # this call return the EDBLayers Class
    layer = edb.core_stackup.stackup_layers

    # this call return the EDBLayer Class
    layer = edb.core_stackup.stackup_layers.layers["TOP"]
    ...


.. currentmodule:: pyaedt.edb_core

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   EDB_Data.EDBLayer
   EDB_Data.EDBLayers
   EDB_Data.EDBPadProperties
   EDB_Data.EDBPadstack
   EDB_Data.EDBPadstackInstance
   EDB_Data.EDBComponent
   EDB_Data.EDBNetsData
   EDB_Data.EDBPrimitives
   siwave.SiwaveDCSetupTemplate
