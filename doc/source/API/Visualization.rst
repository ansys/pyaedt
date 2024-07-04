Visualization
=============
This section lists modules for creating and editing data outside AEDT.

Plot fields and data outside AEDT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
PyAEDT supports external report capabilities available with installed third-party
packages like `numpy <https://numpy.org/doc/stable/>`_,
`pandas <https://pandas.pydata.org/>`_, `matplotlib <https://matplotlib.org/>`_,
and `pyvista <https://docs.pyvista.org/>`_.


.. currentmodule:: pyaedt.modules

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   solutions.SolutionData
   solutions.FieldPlot
   solutions.FfdSolutionData


ModelPlotter is a class that benefits of `pyvista <https://docs.pyvista.org/>`_ package and allows to generate
models and 3D plots.


.. currentmodule:: pyaedt.generic.plot

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   ModelPlotter


The class TouchstoneData instead, is based on `scikit-rf <https://scikit-rf.readthedocs.io/en/latest/>`_,


.. currentmodule:: pyaedt.generic.touchstone_parser

.. autoclass:: TouchstoneData


Here an example on how to use TouchstoneData class.

.. code:: python

    from pyaedt.generic.touchstone_parser import TouchstoneData

    ts1 = TouchstoneData(touchstone_file=os.path.join(test_T44_dir, "port_order_1234.s8p"))
    assert ts1.get_mixed_mode_touchstone_data()
    ts2 = TouchstoneData(touchstone_file=os.path.join(test_T44_dir, "port_order_1324.s8p"))
    assert ts2.get_mixed_mode_touchstone_data(port_ordering="1324")

    assert ts1.plot_insertion_losses(plot=False)
    assert ts1.get_worst_curve(curve_list=ts1.get_return_loss_index(), plot=False)
    ...

