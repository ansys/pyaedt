Components
==========
This section contains API references for component management.
The main component object is called directly from main application using the property ``components``.

.. code:: python

    from pyaedt import Edb
    edb = Edb(myedb, edbversion="2023.1")

    pins =edb.components.get_pin_from_component("U2A5")

    ...


.. currentmodule:: pyaedt.edb_core.components

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   Components


Instances and definitions
-------------------------
These classes are the containers of data management for components reference designator and  definitions.


.. currentmodule:: pyaedt.edb_core.edb_data.components_data

.. autosummary::
   :toctree: _autosummary
   :nosignatures:


   EDBComponent
   EDBComponentDef


.. code:: python

    from pyaedt import Edb
    edb = Edb(myedb, edbversion="2023.1")

    comp = edb.components["C1"]

    comp.is_enabled = True
    part = edb.components.definitions["AAA111"]
    ...