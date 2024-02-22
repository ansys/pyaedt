EDB examples
~~~~~~~~~~~~
EDB is a powerful API for efficiently controlling PCB data.
You can either use EDB standalone or embedded in HFSS 3D Layout in AEDT.
The ``EDB`` class in now part of the PyEDB package, which is currently installed with PyAEDT and backward-compatible with PyAEDT.
All EDB related examples have been moved
to the `Examples page <https://edb.docs.pyansys.com/version/stable/examples/index.html>`_ in the PyEDB
documentation.
These examples use EDB (Electronics Database) with PyAEDT.

.. code:: python

    # Launch the latest installed version of AEDB.
    import pyaedt
    edb = pyaedt.Edb("mylayout.aedb")

    # You can also launch EDB directly from PyEDB.

    import pyedb
    edb = pyedb.Edb("mylayout.aedb")
