EDB editor
==========
An AEDB database is a folder that contains the database representing any part of a PCB.
It can be opened and edited using the ``Edb`` class.


.. currentmodule:: pyaedt

.. autosummary::
   :toctree: _autosummary

   Edb


.. code:: python

    from pyaedt import Edb
    # this call returns the Edb Class initialized on 2022 R1
    edb = Edb(myedb, edbversion="2022.1")

    ...


EDB modules
~~~~~~~~~~~
This section lists the core EDB modules for reading and writing information
to AEDB files.


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
   stackup.Stackup


.. code:: python

    from pyaedt import Edb
    edb = Edb(myedb, edbversion="2022.1")

    # this call returns the EdbHfss Class
    comp = edb.core_hfss

    # this call returns the Components Class
    comp = edb.core_components

    # this call returns the EdbSiwave Class
    comp = edb.core_siwave

    # this call returns the EdbPadstacks Class
    comp = edb.core_padstack

    # this call returns the EdbStackup Class
    comp = edb.core_stackup

    ...



EDB data classes
~~~~~~~~~~~~~~~~
These classes are the containers of data read from the EDB file:


.. currentmodule:: pyaedt.edb_core.edb_data

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   layer_data.LayerEdbClass
   layer_data.EDBLayer
   layer_data.EDBLayers
   padstacks_data.EDBPadProperties
   padstacks_data.EDBPadstack
   padstacks_data.EDBPadstackInstance
   components_data.EDBComponent
   components_data.EDBComponentDef
   nets_data.EDBNetsData
   primitives_data.EDBPrimitives
   simulation_configuration.SiwaveDCSetupTemplate
   simulation_configuration.SimulationConfiguration
   sources.ExcitationPorts
   sources.ExcitationProbes
   sources.ExcitationSources
   sources.ExcitationDifferential


.. code:: python

    from pyaedt import Edb
    edb = Edb(myedb, edbversion="2022.1")

    # this call returns the EDBLayers Class
    layer = edb.core_stackup.stackup_layers

    # this call returns the EDBLayer Class
    layer = edb.core_stackup.stackup_layers.layers["TOP"]
    ...
