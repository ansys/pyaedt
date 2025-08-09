.. _ref_release_notes:

Release notes
#############

This document contains the release notes for the project.

.. vale off

.. towncrier release notes start

`0.15.6 <https://github.com/ansys/pyaedt/releases/tag/v0.15.6>`_ - April 22, 2025
=================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - populate named expressions and improve doc
          - `#6027 <https://github.com/ansys/pyaedt/pull/6027>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - bump ansys/actions from 8 to 9
          - `#6039 <https://github.com/ansys/pyaedt/pull/6039>`_

        * - bump actions/setup-python from 5.4.0 to 5.5.0
          - `#6040 <https://github.com/ansys/pyaedt/pull/6040>`_

        * - bump actions/download-artifact from 4.1.9 to 4.2.1
          - `#6041 <https://github.com/ansys/pyaedt/pull/6041>`_

        * - update pytest-cov requirement from <6.1,>=4.0.0 to >=4.0.0,<6.2
          - `#6042 <https://github.com/ansys/pyaedt/pull/6042>`_

        * - bump codecov/codecov-action from 5.4.0 to 5.4.2
          - `#6062 <https://github.com/ansys/pyaedt/pull/6062>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update ``CONTRIBUTORS.md`` with the latest contributors
          - `#6046 <https://github.com/ansys/pyaedt/pull/6046>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Exception error for multiple design
          - `#5937 <https://github.com/ansys/pyaedt/pull/5937>`_

        * - Adding missed properties
          - `#6045 <https://github.com/ansys/pyaedt/pull/6045>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - update CHANGELOG for v0.15.5
          - `#6044 <https://github.com/ansys/pyaedt/pull/6044>`_

        * - Update pre-commit hooks and intend to fix auto update
          - `#6058 <https://github.com/ansys/pyaedt/pull/6058>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Pathlib hfss.py
          - `#6054 <https://github.com/ansys/pyaedt/pull/6054>`_

        * - Pathlib hfss3dlayout.py
          - `#6057 <https://github.com/ansys/pyaedt/pull/6057>`_


`0.15.5 <https://github.com/ansys/pyaedt/releases/tag/v0.15.5>`_ - April 11, 2025
=================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Field distribution extension
          - `#5818 <https://github.com/ansys/pyaedt/pull/5818>`_

        * - extensions link
          - `#6021 <https://github.com/ansys/pyaedt/pull/6021>`_

        * - post layout extension
          - `#6034 <https://github.com/ansys/pyaedt/pull/6034>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - bump osmnx from 2.0.1 to 2.0.2
          - `#6009 <https://github.com/ansys/pyaedt/pull/6009>`_

        * - Refactor install targets
          - `#6031 <https://github.com/ansys/pyaedt/pull/6031>`_

        * - Remove patch on build
          - `#6032 <https://github.com/ansys/pyaedt/pull/6032>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Add log and nosec in checked subprocess calls
          - `#6001 <https://github.com/ansys/pyaedt/pull/6001>`_

        * - Update ``CONTRIBUTORS.md`` with the latest contributors
          - `#6015 <https://github.com/ansys/pyaedt/pull/6015>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Insert row fix for tables
          - `#5931 <https://github.com/ansys/pyaedt/pull/5931>`_

        * - adding missing  argument for 2d electrostatic balloon BC
          - `#6011 <https://github.com/ansys/pyaedt/pull/6011>`_

        * - color not working properly for traces in single plot
          - `#6020 <https://github.com/ansys/pyaedt/pull/6020>`_

        * - Compliance contour BER check
          - `#6023 <https://github.com/ansys/pyaedt/pull/6023>`_

        * - Update Spisim to relative path
          - `#6033 <https://github.com/ansys/pyaedt/pull/6033>`_

        * - Improve extension unit tests using ANSYS-HSD_V1 file
          - `#6043 <https://github.com/ansys/pyaedt/pull/6043>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Add dependabot cooldown for pip
          - `#5999 <https://github.com/ansys/pyaedt/pull/5999>`_

        * - Pin actions version and avoid dependabot autorun
          - `#6000 <https://github.com/ansys/pyaedt/pull/6000>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - FilterSolutions unit test improvements
          - `#5987 <https://github.com/ansys/pyaedt/pull/5987>`_

        * - Improve code quality and handling of subprocess calls
          - `#5995 <https://github.com/ansys/pyaedt/pull/5995>`_

        * - move points cloud extension at project level
          - `#6004 <https://github.com/ansys/pyaedt/pull/6004>`_

        * - Improve assign balloon method
          - `#6017 <https://github.com/ansys/pyaedt/pull/6017>`_

        * - pathlib refactor primitives_circuit.py
          - `#6024 <https://github.com/ansys/pyaedt/pull/6024>`_

        * - move add calculation to CommonOptimetrics
          - `#6030 <https://github.com/ansys/pyaedt/pull/6030>`_


`0.15.4 <https://github.com/ansys/pyaedt/releases/tag/v0.15.4>`_ - April 03, 2025
=================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Added DUT Image to the Compliance report
          - `#5985 <https://github.com/ansys/pyaedt/pull/5985>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update install targets and dependencies
          - `#5997 <https://github.com/ansys/pyaedt/pull/5997>`_

        * - Temporary add bound to wheel
          - `#6002 <https://github.com/ansys/pyaedt/pull/6002>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Improve robustness of field summary dictionary to DataFrame conversion
          - `#5986 <https://github.com/ansys/pyaedt/pull/5986>`_

        * - Copy Design #5623
          - `#5993 <https://github.com/ansys/pyaedt/pull/5993>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - update CHANGELOG for v0.15.3
          - `#5981 <https://github.com/ansys/pyaedt/pull/5981>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Improve API and security in Desktop
          - `#5892 <https://github.com/ansys/pyaedt/pull/5892>`_

        * - split post_common_3d.py application
          - `#5955 <https://github.com/ansys/pyaedt/pull/5955>`_


`0.15.3 <https://github.com/ansys/pyaedt/releases/tag/v0.15.3>`_ - March 28, 2025
=================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Ibis reader
          - `#5954 <https://github.com/ansys/pyaedt/pull/5954>`_

        * - Move It extension
          - `#5966 <https://github.com/ansys/pyaedt/pull/5966>`_

        * - Layered impedance boundary
          - `#5970 <https://github.com/ansys/pyaedt/pull/5970>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Fix cloud extension grid
          - `#5960 <https://github.com/ansys/pyaedt/pull/5960>`_

        * - Clean up changelog issues
          - `#5962 <https://github.com/ansys/pyaedt/pull/5962>`_

        * - Documentation updates in FilterSolutions
          - `#5967 <https://github.com/ansys/pyaedt/pull/5967>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Fix get insertion loss
          - `#5964 <https://github.com/ansys/pyaedt/pull/5964>`_

        * - Compatibility with Python 3.8
          - `#5972 <https://github.com/ansys/pyaedt/pull/5972>`_

        * - Fix spisim.py in compute_erl
          - `#5976 <https://github.com/ansys/pyaedt/pull/5976>`_

        * - make get_field_extremum more resilient
          - `#5979 <https://github.com/ansys/pyaedt/pull/5979>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - update CHANGELOG for v0.15.2
          - `#5951 <https://github.com/ansys/pyaedt/pull/5951>`_

        * - Update vale logic to leverage reviewdog20
          - `#5974 <https://github.com/ansys/pyaedt/pull/5974>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - pathlib refactor multi-files
          - `#5943 <https://github.com/ansys/pyaedt/pull/5943>`_

        * - Remove aedt threading
          - `#5945 <https://github.com/ansys/pyaedt/pull/5945>`_

        * - Pathlib icepack.py
          - `#5973 <https://github.com/ansys/pyaedt/pull/5973>`_


`0.15.2 <https://github.com/ansys/pyaedt/releases/tag/v0.15.2>`_ - March 25, 2025
=================================================================================

.. tab-set::

  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Enhance native API coverage common.py
          - `#5757 <https://github.com/ansys/pyaedt/pull/5757>`_

        * - Improve circuit wire methods
          - `#5904 <https://github.com/ansys/pyaedt/pull/5904>`_

        * - Cloud point generator
          - `#5909 <https://github.com/ansys/pyaedt/pull/5909>`_

        * - circuit configuration
          - `#5920 <https://github.com/ansys/pyaedt/pull/5920>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Changelog settings
          - `#5908 <https://github.com/ansys/pyaedt/pull/5908>`_

        * - Choke designer issues
          - `#5915 <https://github.com/ansys/pyaedt/pull/5915>`_

        * - Prevent solution invalidation in `create_fieldplot_volume`
          - `#5922 <https://github.com/ansys/pyaedt/pull/5922>`_

        * - issue 5864. Solve inside ON for Network objects
          - `#5923 <https://github.com/ansys/pyaedt/pull/5923>`_

        * - Reduce number of units call from odesktop
          - `#5927 <https://github.com/ansys/pyaedt/pull/5927>`_

        * - "Time" removed from intrinsincs keys in Steady State simulations
          - `#5928 <https://github.com/ansys/pyaedt/pull/5928>`_

        * - colormap names in folder settings
          - `#5935 <https://github.com/ansys/pyaedt/pull/5935>`_

        * - RCS postprocessing
          - `#5942 <https://github.com/ansys/pyaedt/pull/5942>`_

        * - Fixed IBIS differential buffer creation
          - `#5947 <https://github.com/ansys/pyaedt/pull/5947>`_

        * - Modify SolveSetup for Parametrics
          - `#5948 <https://github.com/ansys/pyaedt/pull/5948>`_

  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - populate pyvista object refactoring
          - `#5887 <https://github.com/ansys/pyaedt/pull/5887>`_

        * - Move internal files to a new directory
          - `#5910 <https://github.com/ansys/pyaedt/pull/5910>`_

        * - Delete ML patch class
          - `#5916 <https://github.com/ansys/pyaedt/pull/5916>`_

        * - FilterSolutions_class_refacoring
          - `#5917 <https://github.com/ansys/pyaedt/pull/5917>`_

        * - add arg coefficient in core loss mat
          - `#5939 <https://github.com/ansys/pyaedt/pull/5939>`_

  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - update CHANGELOG for v0.15.1
          - `#5903 <https://github.com/ansys/pyaedt/pull/5903>`_

        * - Add attestation to release notes
          - `#5906 <https://github.com/ansys/pyaedt/pull/5906>`_

  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Add setuptools bound to avoid PEP639 issues
          - `#5949 <https://github.com/ansys/pyaedt/pull/5949>`_


.. vale on