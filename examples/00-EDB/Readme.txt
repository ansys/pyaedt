EDB examples
~~~~~~~~~~~~
EDB is a powerful API that allows to control PCB data efficently.
You can either use EDB standalone or embedded in HFSS 3D Layout in AEDT.
EDB class in now part of PyEDB package which is currently installed with PyAEDT and back compatible with PyAEDT.
All EDB related examples have been moved
at  `PyEDB examples page <https://edb.docs.pyansys.com/version/stable/examples/index.html>`_.
These examples use EDB (Electronics Database) with PyAEDT.

.. code:: python

    # Launch the latest installed version of AEDB.
    import pyaedt
    edb = pyaedt.Edb("mylayout.aedb")

    # You can also launch EDB directly from PyEDB.

    import pyedb
    edb = pyedb.Edb("mylayout.aedb")
