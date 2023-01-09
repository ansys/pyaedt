EDB sources
===========
These classes are the containers of sources methods of the EDB for both HFSS and Siwave.


.. code:: python

    from pyaedt import Edb
    edb = Edb(myedb, edbversion="2022.2")

    # this call returns the EDB excitations dictionary
    edb.excitations
    ...


.. currentmodule:: pyaedt.edb_core.edb_data.sources

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   ExcitationPorts
   ExcitationProbes
   ExcitationSources
   ExcitationDifferential

