EDB layer classes
=================
These classes are the containers of the layer and stackup manager of the EDB API.


.. code:: python

    from pyaedt import Edb
    edb = Edb(myedb, edbversion="2022.2")

    # this call returns the EDBLayers class
    layer = edb.core_stackup.stackup_layers

    # this call returns the EDBLayer class
    layer = edb.core_stackup.stackup_layers.layers["TOP"]
    ...


.. currentmodule:: pyaedt.edb_core.edb_data.layer_data

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   LayerEdbClass
   EDBLayer
   EDBLayers

