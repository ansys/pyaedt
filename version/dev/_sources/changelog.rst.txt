.. _ref_release_notes:

Release notes
#############

This document contains the release notes for the project.

.. vale off

.. towncrier release notes start

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