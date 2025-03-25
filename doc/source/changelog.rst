.. _ref_release_notes:

Release notes
#############

This document contains the release notes for the project.

.. vale off

.. towncrier release notes start

`0.15.2 <https://github.com/ansys/pyaedt/releases/tag/v0.15.2>`_ - March 25, 2025
=================================================================================

.. tab-set::


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Add setuptools bound to avoid PEP639 issues
          - `#5949 <https://github.com/ansys/pyaedt/pull/5949>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - "Time" removed from intrinsincs keys in Steady State simulations
          - `#5928 <https://github.com/ansys/pyaedt/pull/5928>`_

        * - Fixed IBIS differential buffer creation
          - `#5947 <https://github.com/ansys/pyaedt/pull/5947>`_

        * - Modify SolveSetup for Parametrics
          - `#5948 <https://github.com/ansys/pyaedt/pull/5948>`_


`0.15.2 <https://github.com/ansys/pyaedt/releases/tag/v0.15.2>`_ - March 24, 2025
=================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - circuit configuration
          - `#5920 <https://github.com/ansys/pyaedt/pull/5920>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Reduce number of units call from odesktop
          - `#5927 <https://github.com/ansys/pyaedt/pull/5927>`_

        * - colormap names in folder settings
          - `#5935 <https://github.com/ansys/pyaedt/pull/5935>`_

        * - RCS postprocessing
          - `#5942 <https://github.com/ansys/pyaedt/pull/5942>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - add arg coefficient in core loss mat
          - `#5939 <https://github.com/ansys/pyaedt/pull/5939>`_


`0.15.2 <https://github.com/ansys/pyaedt/releases/tag/v0.15.2>`_ - March 21, 2025
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


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - update CHANGELOG for v0.15.1
          - `#5903 <https://github.com/ansys/pyaedt/pull/5903>`_

        * - Add attestation to release notes
          - `#5906 <https://github.com/ansys/pyaedt/pull/5906>`_


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


.. vale on