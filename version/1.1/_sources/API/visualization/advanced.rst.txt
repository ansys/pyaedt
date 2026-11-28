Advanced
========

You can use PyAEDT for postprocessing of AEDT results to display graphics object and plot data.


Touchstone
~~~~~~~~~~

TouchstoneData class is based on `scikit-rf <https://scikit-rf.readthedocs.io/en/latest/>`_ package and allows advanced
touchstone post-processing.
The following methods allows to read and check touchstone files.

.. currentmodule:: ansys.aedt.core.visualization.advanced.touchstone_parser

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
   read_touchstone
   check_touchstone_files
   find_touchstone_files


Here an example on how to use TouchstoneData class.

.. code:: python

    from ansys.aedt.core.visualization.advanced.touchstone_parser import TouchstoneData

    ts1 = TouchstoneData(touchstone_file=os.path.join(test_T44_dir, "port_order_1234.s8p"))
    assert ts1.get_mixed_mode_touchstone_data()
    ts2 = TouchstoneData(touchstone_file=os.path.join(test_T44_dir, "port_order_1324.s8p"))
    assert ts2.get_mixed_mode_touchstone_data(port_ordering="1324")

    assert ts1.plot_insertion_losses(plot=False)
    assert ts1.get_worst_curve(curve_list=ts1.get_return_loss_index(), plot=False)


Farfield
~~~~~~~~

PyAEDT offers sophisticated tools for advanced farfield post-processing.
There are two complementary classes: ``FfdSolutionDataExporter`` and ``FfdSolutionData``.

- FfdSolutionDataExporter: Enables efficient export and manipulation of farfield data. It allows users to convert simulation results into a standard metadata format for further analysis, or reporting.

- FfdSolutionData: Focuses on the direct access and processing of farfield solution data. It supports a comprehensive set of postprocessing operations, from visualizing radiation patterns to computing key performance metrics.


.. currentmodule:: ansys.aedt.core.visualization.advanced.farfield_visualization

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   FfdSolutionData


This code shows how you can get the farfield data and perform some post-processing:

.. code:: python

    import ansys.aedt.core
    from ansys.aedt.core.generic.farfield_visualization import FfdSolutionDataExporter

    app = ansys.aedt.core.Hfss()
    ffdata = app.get_antenna_data(
        frequencies=None,
        setup="Setup1 : Sweep",
        sphere="3D",
        variations=None,
        overwrite=False,
        link_to_hfss=True,
        export_touchstone=True,
    )
    incident_power = ffdata.incident_power
    ffdata.plot_cut(primary_sweep="Theta", theta=0)
    ffdata.plot_contour(polar=True)
    ffdata.plot_3d(show_geometry=False)
    app.release_desktop(False, False)

If you exported the farfield data previously, you can directly get the farfield data:

.. code:: python

    from ansys.aedt.core.generic.farfield_visualization import FfdSolutionData

    input_file = r"path_to_ffd\pyaedt_antenna_metadata.json"
    ffdata = FfdSolutionData(input_file)
    incident_power = ffdata.incident_power
    ffdata.plot_cut(primary_sweep="Theta", theta=0)
    ffdata.plot_contour(polar=True)
    ffdata.plot_3d(show_geometry=False)
    app.release_desktop(False, False)

The following diagram shows both classes work. You can use them independently or from the ``get_antenna_data`` method.

  .. image:: ../../_static/farfield_visualization_pyaedt.png
    :width: 800
    :alt: Farfield data with PyAEDT


If you have existing farfield data, or you want to export it manually, you can still use FfdSolutionData class.

  .. image:: ../../_static/farfield_visualization_aedt.png
    :width: 800
    :alt: Farfield data with AEDT


Monostatic RCS
~~~~~~~~~~~~~~

PyAEDT provides tools for exporting monostatic radar cross section (RCS) data through the ``MonostaticRCSExporter`` class.
For advanced RCS post-processing, analysis, and visualization, use the **Radar Explorer Toolkit**.

.. note::
   Advanced RCS features (``MonostaticRCSData`` and ``MonostaticRCSPlotter``) have been moved to the
   `Radar Explorer Toolkit <https://aedt.radar.explorer.toolkit.docs.pyansys.com/version/stable/>`_.

   Install the toolkit with:

   .. code:: bash

       pip install ansys-aedt-toolkits-radar-explorer


PyAEDT RCS exporter
^^^^^^^^^^^^^^^^^^^

The ``MonostaticRCSExporter`` class enables efficient export of RCS simulation data into a standardized
metadata format for further analysis with the Radar Explorer Toolkit.

.. currentmodule:: ansys.aedt.core.visualization.post.rcs_exporter

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   MonostaticRCSExporter

Export RCS data from HFSS:

.. code:: python

    from ansys.aedt.core import Hfss

    app = Hfss()
    setup_name = "Setup1 : LastAdaptive"
    frequencies = [77e9]

    # Export RCS data
    rcs_exporter = app.get_rcs_data(
        frequencies=frequencies, setup=setup_name, variation_name="rcs_solution"
    )

    # Metadata file is created for use with Radar Explorer Toolkit
    metadata_file = rcs_exporter.metadata_file

Radar explorer toolkit
^^^^^^^^^^^^^^^^^^^^^^

For comprehensive RCS analysis and visualization, use the **radar explorer toolkit**:

- **MonostaticRCSData**: Advanced processing of RCS solution data with support for range profiles,
  waterfall plots, and ISAR imaging.

- **MonostaticRCSPlotter**: Interactive 3D visualization and post-processing of RCS data.

Example using the radar explorer toolkit:

.. code:: python

    # Install first: pip install ansys-aedt-toolkits-radar-explorer
    from ansys.aedt.toolkits.radar_explorer.rcs_visualization import MonostaticRCSData
    from ansys.aedt.toolkits.radar_explorer.rcs_visualization import MonostaticRCSPlotter

    # Load RCS data exported from PyAEDT
    input_file = r"path_to_data\pyaedt_rcs_metadata.json"
    rcs_data = MonostaticRCSData(input_file)

    # Create plotter for visualization
    rcs_plotter = MonostaticRCSPlotter(rcs_data)

    # Generate various plots
    rcs_plotter.plot_rcs(primary_sweep="IWavePhi")
    rcs_plotter.plot_3d()
    rcs_plotter.add_range_profile()
    rcs_plotter.plot_scene()

For complete documentation and API reference, see:

- `Radar explorer API <https://aedt.radar.explorer.toolkit.docs.pyansys.com/version/stable/toolkit/api.html>`_


FRTM processing
~~~~~~~~~~~~~~~

PyAEDT offers sophisticated tools for FRTM post-processing.
There are two complementary classes: ``FRTMData``, and ``FRTMPlotter``.

- FRTMData: Focuses on the direct access and processing of FRTM solution data. It supports a comprehensive set of postprocessing operations, like range profile and range doppler processing.

- FRTMPlotter: Focuses on the post-processing of FRTM solution data.


.. currentmodule:: ansys.aedt.core.visualization.advanced.frtm_visualization

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   FRTMData
   FRTMPlotter


This code shows how you can get the FRTM data:

.. code:: python

    from ansys.aedt.core.visualization.advanced.frtm_visualization import FRTMPlotter
    from ansys.aedt.core.visualization.advanced.frtm_visualization import FRTMData

    input_dir = r"path_to_data"

    doppler_data_frames = {}
    frames_dict = get_results_files(input_dir)

    for frame, data_frame in frames_dict.items():
        doppler_data = FRTMData(data_frame)
        doppler_data_frames[frame] = doppler_data

    frtm_plotter = FRTMPlotter(doppler_data_frames)
    frtm_plotter.plot_range_doppler()

The following picture shows the output of the previous code.

  .. image:: ../../_static/frtm_doppler.gif
    :width: 800
    :alt: Range doppler PyAEDT


Heterogeneous data message
~~~~~~~~~~~~~~~~~~~~~~~~~~

Heterogeneous data message (HDM) is the file exported from SBR+ solver containing rays information.
The following methods allows to read and plot rays information.

.. currentmodule:: ansys.aedt.core.visualization.advanced

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   hdm_plot.HDMPlotter
   sbrplus.hdm_parser.Parser


Open street map
~~~~~~~~~~~~~~~

PyAEDT provides comprehensive tools for importing and processing OpenStreetMap (OSM) data to create
realistic 3D environments for electromagnetic simulations. The OSM module enables automatic generation
of buildings, roads, and terrain meshes suitable for large-scale RF propagation and antenna placement studies.

The module consists of three main preparation classes:

- **BuildingsPrep**: Generates 3D building models from OSM building footprints with estimated heights
- **RoadPrep**: Creates road network geometries with proper elevation mapping
- **TerrainPrep**: Generates terrain meshes with elevation data

.. currentmodule:: ansys.aedt.core.modeler.advanced_cad.osm

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   BuildingsPrep
   RoadPrep
   TerrainPrep
   convert_latlon_to_utm
   convert_utm_to_latlon


Use the high-level ``import_from_openstreet_map`` method to import complete OSM scenes:

.. code:: python

    from ansys.aedt.core import Hfss

    app = Hfss()

    # Define location (latitude, longitude)
    center = [40.7128, -74.0060]  # New York City

    # Import OSM data with buildings, roads, and terrain
    scene = app.modeler.import_from_openstreet_map(
        latitude_longitude=center,
        terrain_radius=500,
        include_osm_buildings=True,
        including_osm_roads=True,
        import_in_aedt=True,
    )

For advanced control, use the preparation classes directly:

.. code:: python

    from ansys.aedt.core.modeler.advanced_cad.osm import (
        BuildingsPrep,
        RoadPrep,
        TerrainPrep,
    )

    # Define location
    center = [40.7128, -74.0060]  # New York City
    output_path = "./osm_output"

    # Generate terrain
    terrain_prep = TerrainPrep(cad_path=output_path)
    terrain_data = terrain_prep.get_terrain(center, max_radius=500, grid_size=30)

    # Generate buildings aligned to terrain
    building_prep = BuildingsPrep(cad_path=output_path)
    building_data = building_prep.generate_buildings(
        center, terrain_data["mesh"], max_radius=400
    )

    # Generate roads aligned to terrain
    road_prep = RoadPrep(cad_path=output_path)
    road_data = road_prep.create_roads(
        center, terrain_data["mesh"], max_radius=500, road_width=8
    )

The module automatically:

- Downloads geographic data from OpenStreetMap
- Converts coordinates from lat/lon to local UTM system
- Generates 3D STL meshes for buildings, roads, and terrain
- Aligns all geometries to terrain elevation
- Exports files ready for AEDT import

.. note::
   Building heights are estimated from OSM ``building:levels`` tags or ``height`` attributes.
   Large radius values may result in significant download and processing times.

For complete documentation, see the example:
`City scenario with OpenStreetMap <https://examples.aedt.docs.pyansys.com/version/dev/examples/high_frequency/antenna/large_scenarios/city.html>`_


Miscellaneous
~~~~~~~~~~~~~

PyAEDT has additional advanced post-processing features:

.. currentmodule:: ansys.aedt.core.visualization.advanced.misc

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   convert_nearfield_data
   parse_rdat_file
   nastran_to_stl
   simplify_stl

