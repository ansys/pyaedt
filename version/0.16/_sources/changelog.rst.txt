.. _ref_release_notes:

Release notes
#############

This document contains the release notes for the project.

.. vale off

.. towncrier release notes start

`0.16.2 <https://github.com/ansys/pyaedt/releases/tag/v0.16.2>`_ - May 16, 2025
===============================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - FRTM class
          - `#6018 <https://github.com/ansys/pyaedt/pull/6018>`_

        * - Added automatic search in modeler getitem of FaceID and Edge Ids.
          - `#6109 <https://github.com/ansys/pyaedt/pull/6109>`_

        * - Added new section in VirtualCompliance to compute skew parameters from Report.
          - `#6114 <https://github.com/ansys/pyaedt/pull/6114>`_

        * - Uncover face
          - `#6122 <https://github.com/ansys/pyaedt/pull/6122>`_

        * - Added support for pass_fail criteria into the main.json
          - `#6124 <https://github.com/ansys/pyaedt/pull/6124>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - update jupyterlab requirement from <4.4,>=3.6.0 to >=3.6.0,<4.5
          - `#6104 <https://github.com/ansys/pyaedt/pull/6104>`_

        * - update joblib requirement from <1.5,>=1.4.0 to >=1.4.0,<1.6
          - `#6140 <https://github.com/ansys/pyaedt/pull/6140>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Add docstring to some classes in constants.py
          - `#6099 <https://github.com/ansys/pyaedt/pull/6099>`_

        * - Update ``CONTRIBUTORS.md`` with the latest contributors
          - `#6105 <https://github.com/ansys/pyaedt/pull/6105>`_, `#6144 <https://github.com/ansys/pyaedt/pull/6144>`_

        * - Add hint for toolkit icon visiblity
          - `#6123 <https://github.com/ansys/pyaedt/pull/6123>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - improvements in circuit config
          - `#6012 <https://github.com/ansys/pyaedt/pull/6012>`_

        * - Adding close desktop function
          - `#6052 <https://github.com/ansys/pyaedt/pull/6052>`_

        * - Fix name of setup to match setup type
          - `#6125 <https://github.com/ansys/pyaedt/pull/6125>`_

        * - fix small bug in time domain report
          - `#6126 <https://github.com/ansys/pyaedt/pull/6126>`_

        * - External circuit import of renamed sources
          - `#6128 <https://github.com/ansys/pyaedt/pull/6128>`_

        * - Change units in non linear properties
          - `#6130 <https://github.com/ansys/pyaedt/pull/6130>`_

        * - Output variable with differential pairs
          - `#6132 <https://github.com/ansys/pyaedt/pull/6132>`_

        * - Add mesh link wrong source design solution selection
          - `#6133 <https://github.com/ansys/pyaedt/pull/6133>`_

        * - Add blocking to optimetrics analyze method
          - `#6135 <https://github.com/ansys/pyaedt/pull/6135>`_

        * - Fix equivalent circuit export
          - `#6139 <https://github.com/ansys/pyaedt/pull/6139>`_

        * - fields documentation extension
          - `#6147 <https://github.com/ansys/pyaedt/pull/6147>`_

        * - Correct unit for h-field in set_non_linear() for bh curve definition
          - `#6156 <https://github.com/ansys/pyaedt/pull/6156>`_

        * - ISAR 2D range extents
          - `#6162 <https://github.com/ansys/pyaedt/pull/6162>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - update CHANGELOG for v0.16.1
          - `#6098 <https://github.com/ansys/pyaedt/pull/6098>`_

        * - Bump dev version into v0.17.dev0
          - `#6102 <https://github.com/ansys/pyaedt/pull/6102>`_

        * - Add vulnerability checking
          - `#6112 <https://github.com/ansys/pyaedt/pull/6112>`_

        * - Extend smoke tests with py313
          - `#6116 <https://github.com/ansys/pyaedt/pull/6116>`_

        * - Add nosec B110 to random AEDT failure
          - `#6137 <https://github.com/ansys/pyaedt/pull/6137>`_

        * - Pin ansys/actions to the latest stable release
          - `#6148 <https://github.com/ansys/pyaedt/pull/6148>`_

        * - Fix missing call to actions/doc-build
          - `#6155 <https://github.com/ansys/pyaedt/pull/6155>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - 12_post_processing refactoring
          - `#6051 <https://github.com/ansys/pyaedt/pull/6051>`_

        * - Add required graphics decorator
          - `#6087 <https://github.com/ansys/pyaedt/pull/6087>`_

        * - Refactor/12 post processing test
          - `#6095 <https://github.com/ansys/pyaedt/pull/6095>`_

        * - Updates related to vulnerabilities and documentation
          - `#6110 <https://github.com/ansys/pyaedt/pull/6110>`_

        * - Extension manager compatible with toolkits
          - `#6115 <https://github.com/ansys/pyaedt/pull/6115>`_

        * - Refactored quaternion implementation
          - `#6151 <https://github.com/ansys/pyaedt/pull/6151>`_


`0.16.1 <https://github.com/ansys/pyaedt/releases/tag/v0.16.1>`_ - May 01, 2025
===============================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Added DUT Image to the Compliance report
          - `#5985 <https://github.com/ansys/pyaedt/pull/5985>`_

        * - improved pdf  image management
          - `#6076 <https://github.com/ansys/pyaedt/pull/6076>`_

        * - Add assignment argument to plane wave
          - `#6077 <https://github.com/ansys/pyaedt/pull/6077>`_

        * - args deprecation decorator
          - `#6086 <https://github.com/ansys/pyaedt/pull/6086>`_

        * - Add Version manager to main panels
          - `#6089 <https://github.com/ansys/pyaedt/pull/6089>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update install targets and dependencies
          - `#5997 <https://github.com/ansys/pyaedt/pull/5997>`_

        * - Temporary add bound to wheel
          - `#6002 <https://github.com/ansys/pyaedt/pull/6002>`_

        * - bump actions/setup-python from 5.5.0 to 5.6.0
          - `#6081 <https://github.com/ansys/pyaedt/pull/6081>`_

        * - bump actions/download-artifact from 4.2.1 to 4.3.0
          - `#6082 <https://github.com/ansys/pyaedt/pull/6082>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update priority level in doctree removal
          - `#6078 <https://github.com/ansys/pyaedt/pull/6078>`_

        * - Update ``CONTRIBUTORS.md`` with the latest contributors
          - `#6084 <https://github.com/ansys/pyaedt/pull/6084>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Improve robustness of field summary dictionary to DataFrame conversion
          - `#5986 <https://github.com/ansys/pyaedt/pull/5986>`_

        * - Copy Design #5623
          - `#5993 <https://github.com/ansys/pyaedt/pull/5993>`_

        * - fix extension manager + add missing icon fields distribution
          - `#6066 <https://github.com/ansys/pyaedt/pull/6066>`_

        * - Return value of download_icepak_3d_component
          - `#6071 <https://github.com/ansys/pyaedt/pull/6071>`_

        * - Return value of download_multiparts
          - `#6075 <https://github.com/ansys/pyaedt/pull/6075>`_

        * - Speedup extension cutout
          - `#6079 <https://github.com/ansys/pyaedt/pull/6079>`_

        * - Only force download file if specified
          - `#6083 <https://github.com/ansys/pyaedt/pull/6083>`_

        * - Fix locale error that happens after matplotlib plot is created
          - `#6088 <https://github.com/ansys/pyaedt/pull/6088>`_

        * - Remove dummy project fixture
          - `#6091 <https://github.com/ansys/pyaedt/pull/6091>`_

        * - Schematic name argument optional in edit_external_circuit method
          - `#6092 <https://github.com/ansys/pyaedt/pull/6092>`_

        * - Added some improvement to VirtualCompliance class
          - `#6096 <https://github.com/ansys/pyaedt/pull/6096>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - update CHANGELOG for v0.15.3
          - `#5981 <https://github.com/ansys/pyaedt/pull/5981>`_

        * - update CHANGELOG for v0.15.6
          - `#6065 <https://github.com/ansys/pyaedt/pull/6065>`_

        * - Update package metadata license (PEP 639)
          - `#6094 <https://github.com/ansys/pyaedt/pull/6094>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Improve API and security in Desktop
          - `#5892 <https://github.com/ansys/pyaedt/pull/5892>`_

        * - split post_common_3d.py application
          - `#5955 <https://github.com/ansys/pyaedt/pull/5955>`_

        * - Add examples folder and rework download logic
          - `#6055 <https://github.com/ansys/pyaedt/pull/6055>`_

        * - Refactor virtual compliance class
          - `#6073 <https://github.com/ansys/pyaedt/pull/6073>`_


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