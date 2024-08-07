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


Plot 3D objects and fields
~~~~~~~~~~~~~~~~~~~~~~~~~~
ModelPlotter is a class that benefits of `pyvista <https://docs.pyvista.org/>`_ package and allows to generate
models and 3D plots.


.. currentmodule:: pyaedt.generic.plot

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   ModelPlotter


Plot touchstone data outside AEDT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TouchstoneData class is based on `scikit-rf <https://scikit-rf.readthedocs.io/en/latest/>`_ package and allows advanced
touchstone post-processing.
The following methods allows to read and check touchstone files.


.. currentmodule:: pyaedt.generic.touchstone_parser

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   read_touchstone
   check_touchstone_files


Using the above methods you are getting an object of a class TouchstoneData.
The class TouchstoneData  is based on `scikit-rf <https://scikit-rf.readthedocs.io/en/latest/>`_,
Additional methods are added to provide easy access to touchstone curves.


.. currentmodule:: pyaedt.generic.touchstone_parser

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   TouchstoneData.get_insertion_loss_index
   TouchstoneData.plot_insertion_losses
   TouchstoneData.plot
   TouchstoneData.plot_return_losses
   TouchstoneData.get_mixed_mode_touchstone_data
   TouchstoneData.get_return_loss_index
   TouchstoneData.get_insertion_loss_index_from_prefix
   TouchstoneData.get_next_xtalk_index
   TouchstoneData.get_fext_xtalk_index_from_prefix
   TouchstoneData.plot_next_xtalk_losses
   TouchstoneData.plot_fext_xtalk_losses
   TouchstoneData.get_worst_curve



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


Farfield
~~~~~~~~
PyAEDT offers sophisticated tools for advanced farfield post-processing.
There are two complementary classes: ``FfdSolutionDataExporter`` and ``FfdSolutionData``.

- FfdSolutionDataExporter: Enables efficient export and manipulation of farfield data. It allows users to convert simulation results into a standard metadata format for further analysis, or reporting.

- FfdSolutionData: Focuses on the direct access and processing of farfield solution data. It supports a comprehensive set of postprocessing operations, from visualizing radiation patterns to computing key performance metrics.


.. currentmodule:: pyaedt.generic.farfield_visualization

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   FfdSolutionDataExporter
   FfdSolutionData

This code shows how you can get the farfield data and perform some post-processing:

.. code:: python

    import pyaedt
    from pyaedt.generic.farfield_visualization import FfdSolutionDataExporter
    app = pyaedt.Hfss()
    ffdata = app.get_antenna_data(frequencies=None,
                                  setup="Setup1 : Sweep",
                                  sphere="3D",
                                  variations=None,
                                  overwrite=False,
                                  link_to_hfss=True,
                                  export_touchstone=True)
    incident_power = ffdata.incident_power
    ffdata.plot_cut(primary_sweep="Theta", theta=0)
    ffdata.plot_contour(polar=True)
    ffdata.plot_3d(show_geometry=False)
    app.release_desktop(False, False)

If you exported the farfield data previously,you can directly get the farfield data:

.. code:: python

    from pyaedt.generic.farfield_visualization import FfdSolutionData
    input_file = r"path_to_ffd\pyaedt_antenna_metadata.json"
    ffdata = FfdSolutionData(input_file)
    incident_power = ffdata.incident_power
    ffdata.plot_cut(primary_sweep="Theta", theta=0)
    ffdata.plot_contour(polar=True)
    ffdata.plot_3d(show_geometry=False)
    app.release_desktop(False, False)

The following diagram shows both classes work. You can use them independently or from the ``get_antenna_data`` method.

  .. image:: ../_static/farfield_visualization_pyaedt.png
    :width: 800
    :alt: Farfield data with PyAEDT


If you have existing farfield data, or you want to export it manually, you can still use FfdSolutionData class.

  .. image:: ../_static/farfield_visualization_aedt.png
    :width: 800
    :alt: Farfield data with AEDT


Heterogeneous data message
~~~~~~~~~~~~~~~~~~~~~~~~~~
Heterogeneous data message (HDM) is the file exported from SBR+ solver containing rays information.
The following methods allows to read and plot rays information.

.. currentmodule:: pyaedt.sbrplus

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   hdm_parser.Parser
   plot.HDMPlotter
