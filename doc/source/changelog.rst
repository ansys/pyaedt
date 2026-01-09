.. _ref_release_notes:

Release notes
#############

This document contains the release notes for the project.

.. vale off

.. towncrier release notes start

`0.23.0 <https://github.com/ansys/pyaedt/releases/tag/v0.23.0>`_ - November 27, 2025
====================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Added method for Inception Voltage Evaluation for electrostatic Maxwell analyses. Issue #5310
          - `#6869 <https://github.com/ansys/pyaedt/pull/6869>`_

        * - Local test configuration cli
          - `#6880 <https://github.com/ansys/pyaedt/pull/6880>`_

        * - Enhance CLI output with colored messages for better visibility
          - `#6884 <https://github.com/ansys/pyaedt/pull/6884>`_

        * - Add panels command to manage PyAEDT panels in AEDT + tests
          - `#6886 <https://github.com/ansys/pyaedt/pull/6886>`_

        * - Make q23d tests independent
          - `#6894 <https://github.com/ansys/pyaedt/pull/6894>`_

        * - Show/hide traceback on extension raised exception
          - `#6909 <https://github.com/ansys/pyaedt/pull/6909>`_

        * - Record console setups into a python file
          - `#6914 <https://github.com/ansys/pyaedt/pull/6914>`_

        * - Allow hide plot with matplotlib
          - `#6918 <https://github.com/ansys/pyaedt/pull/6918>`_

        * - Allow FacePrimitive in assign_mass_flow_free_opening
          - `#6928 <https://github.com/ansys/pyaedt/pull/6928>`_

        * - Add compatibility with new grpc transport mechanism
          - `#6939 <https://github.com/ansys/pyaedt/pull/6939>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update pytest requirement from <8.5,>=7.4.0 to >=7.4.0,<9.1
          - `#6925 <https://github.com/ansys/pyaedt/pull/6925>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Improve Variable management in Circuit
          - `#6742 <https://github.com/ansys/pyaedt/pull/6742>`_

        * - #6920 handling port names with extra spaces at the end of the port names
          - `#6921 <https://github.com/ansys/pyaedt/pull/6921>`_

        * - Ibis buffer placement
          - `#6924 <https://github.com/ansys/pyaedt/pull/6924>`_

        * - IbisReader cache of models
          - `#6936 <https://github.com/ansys/pyaedt/pull/6936>`_

        * - Fix a bug in import_config from Circuit
          - `#6941 <https://github.com/ansys/pyaedt/pull/6941>`_

        * - Docstring improvement
          - `#6942 <https://github.com/ansys/pyaedt/pull/6942>`_

        * - Infinite loop when logging
          - `#6945 <https://github.com/ansys/pyaedt/pull/6945>`_

        * - Fixed version manager update
          - `#6946 <https://github.com/ansys/pyaedt/pull/6946>`_

        * - Added support to pages to gnd in import_config
          - `#6954 <https://github.com/ansys/pyaedt/pull/6954>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Make Independent 01 general tests
          - `#6891 <https://github.com/ansys/pyaedt/pull/6891>`_

        * - Update CHANGELOG for v0.22.2
          - `#6892 <https://github.com/ansys/pyaedt/pull/6892>`_

        * - Rework workflow to avoid testing
          - `#6897 <https://github.com/ansys/pyaedt/pull/6897>`_

        * - Make modeler tests independent
          - `#6902 <https://github.com/ansys/pyaedt/pull/6902>`_

        * - Fix uv setup in nightly tests
          - `#6926 <https://github.com/ansys/pyaedt/pull/6926>`_

        * - Extend manual workflow with EMIT and FS tests
          - `#6930 <https://github.com/ansys/pyaedt/pull/6930>`_


  .. tab-item:: Test

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Avoid skipping and disable plot
          - `#6889 <https://github.com/ansys/pyaedt/pull/6889>`_

        * - SBR+ tests independent
          - `#6903 <https://github.com/ansys/pyaedt/pull/6903>`_

        * - Independent mesh tests
          - `#6905 <https://github.com/ansys/pyaedt/pull/6905>`_

        * - Message manager tests independent
          - `#6911 <https://github.com/ansys/pyaedt/pull/6911>`_

        * - Independent Setup tests
          - `#6916 <https://github.com/ansys/pyaedt/pull/6916>`_

        * - Refactor test_15_ibis_reader to follow test guidelines
          - `#6917 <https://github.com/ansys/pyaedt/pull/6917>`_

        * - Independent circuit tests
          - `#6923 <https://github.com/ansys/pyaedt/pull/6923>`_

        * - Refactor already independent tests removing testclass
          - `#6933 <https://github.com/ansys/pyaedt/pull/6933>`_

        * - Refactor tests in \`\`test_13_LoadAEDTFile.py\`\` to make them independent
          - `#6935 <https://github.com/ansys/pyaedt/pull/6935>`_


`0.22.2 <https://github.com/ansys/pyaedt/releases/tag/v0.22.2>`_ - November 18, 2025
====================================================================================

.. tab-set::


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update plotly requirement from <6.4,>=6.0 to >=6.0,<6.5
          - `#6881 <https://github.com/ansys/pyaedt/pull/6881>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Test_configure_layout.py
          - `#6809 <https://github.com/ansys/pyaedt/pull/6809>`_

        * - Fixed blue checkboxes issue
          - `#6836 <https://github.com/ansys/pyaedt/pull/6836>`_

        * - ServiceManager.start_service ignores configured AEDT path in PYAEDT_SERVER_AEDT_PATH env var
          - `#6867 <https://github.com/ansys/pyaedt/pull/6867>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.22.1
          - `#6876 <https://github.com/ansys/pyaedt/pull/6876>`_


  .. tab-item:: Test

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Refactor HFSS tests to be independent from each other
          - `#6873 <https://github.com/ansys/pyaedt/pull/6873>`_


`0.22.1 <https://github.com/ansys/pyaedt/releases/tag/v0.22.1>`_ - November 13, 2025
====================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Add CLI using typer
          - `#6857 <https://github.com/ansys/pyaedt/pull/6857>`_

        * - Added multi-page support to Nexxim Circuit components
          - `#6863 <https://github.com/ansys/pyaedt/pull/6863>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump actions/download-artifact from 5.0.0 to 6.0.0
          - `#6843 <https://github.com/ansys/pyaedt/pull/6843>`_

        * - Bump actions/upload-artifact from 4.6.2 to 5.0.0
          - `#6845 <https://github.com/ansys/pyaedt/pull/6845>`_

        * - Update grpcio requirement from <1.76,>=1.50.0 to >=1.50.0,<1.77
          - `#6846 <https://github.com/ansys/pyaedt/pull/6846>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Kernel converter import fix
          - `#6871 <https://github.com/ansys/pyaedt/pull/6871>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Downgrade log message when error occurs in ansysedt session search loop
          - `#6853 <https://github.com/ansys/pyaedt/pull/6853>`_

        * - Remove static oDesktop string from add_pyaedt_to_aedt calls in installer script
          - `#6864 <https://github.com/ansys/pyaedt/pull/6864>`_

        * - Removed deprecation for design.close_desktop() method
          - `#6865 <https://github.com/ansys/pyaedt/pull/6865>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.22.0
          - `#6859 <https://github.com/ansys/pyaedt/pull/6859>`_

        * - Bump version 0.23.dev0
          - `#6860 <https://github.com/ansys/pyaedt/pull/6860>`_

        * - Leverage new vtk osmesa logic
          - `#6868 <https://github.com/ansys/pyaedt/pull/6868>`_


`0.22.0 <https://github.com/ansys/pyaedt/releases/tag/v0.22.0>`_ - November 05, 2025
====================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Flux lines plot
          - `#6575 <https://github.com/ansys/pyaedt/pull/6575>`_

        * - Filter deprecated methods from public_dir
          - `#6791 <https://github.com/ansys/pyaedt/pull/6791>`_

        * - Add TB spectral report context
          - `#6808 <https://github.com/ansys/pyaedt/pull/6808>`_

        * - Add magick method to EdgePrimitive
          - `#6819 <https://github.com/ansys/pyaedt/pull/6819>`_

        * - Add oDesktop logging to installer and automation tab functions
          - `#6821 <https://github.com/ansys/pyaedt/pull/6821>`_

        * - Edit sources harmonic loss q3d
          - `#6826 <https://github.com/ansys/pyaedt/pull/6826>`_

        * - Add create EM target design + add tests
          - `#6838 <https://github.com/ansys/pyaedt/pull/6838>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update pydantic requirement from <2.12,>=2.6.4 to >=2.6.4,<2.13
          - `#6783 <https://github.com/ansys/pyaedt/pull/6783>`_

        * - Bump ansys/actions from 10.1.4 to 10.1.5
          - `#6844 <https://github.com/ansys/pyaedt/pull/6844>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Add information about coverage and local_config
          - `#6681 <https://github.com/ansys/pyaedt/pull/6681>`_

        * - Update \`\`CONTRIBUTORS.md\`\` with the latest contributors
          - `#6786 <https://github.com/ansys/pyaedt/pull/6786>`_, `#6820 <https://github.com/ansys/pyaedt/pull/6820>`_

        * - Fix typos in modeler user guide
          - `#6798 <https://github.com/ansys/pyaedt/pull/6798>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Analyze_from_zero
          - `#6425 <https://github.com/ansys/pyaedt/pull/6425>`_

        * - EMIT Pyaedt fixes
          - `#6768 <https://github.com/ansys/pyaedt/pull/6768>`_

        * - Fixed panels in linux
          - `#6799 <https://github.com/ansys/pyaedt/pull/6799>`_

        * - Settings.aedt_version in desktop and design class fix
          - `#6802 <https://github.com/ansys/pyaedt/pull/6802>`_

        * - PyAEDT installer from AEDT
          - `#6803 <https://github.com/ansys/pyaedt/pull/6803>`_

        * - Allow Object3d to be used in create_current_source_from_objects
          - `#6804 <https://github.com/ansys/pyaedt/pull/6804>`_

        * - Small change to port naming when no names are provided to align with Circuit behaviour
          - `#6816 <https://github.com/ansys/pyaedt/pull/6816>`_

        * - Add error message if extension is started with an empty HFSS 3D Layout design
          - `#6822 <https://github.com/ansys/pyaedt/pull/6822>`_

        * - Bug in Transient Analysis which prevented to add Sweep Definition
          - `#6831 <https://github.com/ansys/pyaedt/pull/6831>`_

        * - Args native API create EM target design
          - `#6840 <https://github.com/ansys/pyaedt/pull/6840>`_

        * - Solved issue #6801, improved desktop.save_project()
          - `#6847 <https://github.com/ansys/pyaedt/pull/6847>`_

        * - Bug in Transient design which was creating a Freq Sweep in every transient analysis
          - `#6849 <https://github.com/ansys/pyaedt/pull/6849>`_

        * - Fix exception messaging
          - `#6850 <https://github.com/ansys/pyaedt/pull/6850>`_

        * - Export layout extension
          - `#6856 <https://github.com/ansys/pyaedt/pull/6856>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.21.2
          - `#6782 <https://github.com/ansys/pyaedt/pull/6782>`_

        * - Fix dependabot PR blocking job
          - `#6787 <https://github.com/ansys/pyaedt/pull/6787>`_

        * - Use flaky marker to avoid rerunning all tests
          - `#6789 <https://github.com/ansys/pyaedt/pull/6789>`_

        * - Add GitHub label for extension related changes
          - `#6814 <https://github.com/ansys/pyaedt/pull/6814>`_

        * - Disable flaky testing due to CI issues
          - `#6839 <https://github.com/ansys/pyaedt/pull/6839>`_

        * - Handle fpdf2 in CI and extend README
          - `#6841 <https://github.com/ansys/pyaedt/pull/6841>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Conftest refactoring and local_config cleaning
          - `#6727 <https://github.com/ansys/pyaedt/pull/6727>`_


  .. tab-item:: Test

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Extend flaky_linux test set
          - `#6793 <https://github.com/ansys/pyaedt/pull/6793>`_

        * - System tests for extension and version managers
          - `#6833 <https://github.com/ansys/pyaedt/pull/6833>`_

        * - Add settings for local testing
          - `#6834 <https://github.com/ansys/pyaedt/pull/6834>`_


`0.21.2 <https://github.com/ansys/pyaedt/releases/tag/v0.21.2>`_ - October 17, 2025
===================================================================================

.. tab-set::


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update Report type according to Solution Type in CreateOutputVariable
          - `#6726 <https://github.com/ansys/pyaedt/pull/6726>`_

        * - Update extension directory path handling in add_script_to_menu function
          - `#6779 <https://github.com/ansys/pyaedt/pull/6779>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.21.1
          - `#6777 <https://github.com/ansys/pyaedt/pull/6777>`_


`0.21.1 <https://github.com/ansys/pyaedt/releases/tag/v0.21.1>`_ - October 16, 2025
===================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Add dir as property
          - `#6716 <https://github.com/ansys/pyaedt/pull/6716>`_

        * - Project sheet
          - `#6757 <https://github.com/ansys/pyaedt/pull/6757>`_

        * - Update extension handling
          - `#6758 <https://github.com/ansys/pyaedt/pull/6758>`_

        * - Enhance custom extension dialog with display name and validation checks
          - `#6760 <https://github.com/ansys/pyaedt/pull/6760>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump peter-evans/create-or-update-comment from 4.0.0 to 5.0.0
          - `#6753 <https://github.com/ansys/pyaedt/pull/6753>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update \`\`CONTRIBUTORS.md\`\` with the latest contributors
          - `#6755 <https://github.com/ansys/pyaedt/pull/6755>`_

        * - Fix doc wheelhouse Installation.rst
          - `#6765 <https://github.com/ansys/pyaedt/pull/6765>`_

        * - Update troubleshooting guide with extension troubleshooting
          - `#6771 <https://github.com/ansys/pyaedt/pull/6771>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - F-string usage for IronPython compatibility
          - `#6748 <https://github.com/ansys/pyaedt/pull/6748>`_

        * - Design type check and update points cloud extension call
          - `#6750 <https://github.com/ansys/pyaedt/pull/6750>`_

        * - Added additional check to is_solved for circuit analysis
          - `#6759 <https://github.com/ansys/pyaedt/pull/6759>`_

        * - Fixed the issue of comp name same as model name in ibis file which caused issue in mapping
          - `#6761 <https://github.com/ansys/pyaedt/pull/6761>`_

        * - GeometryModeler __getitem__ for AEDT 24R2
          - `#6762 <https://github.com/ansys/pyaedt/pull/6762>`_

        * - _import_cad
          - `#6764 <https://github.com/ansys/pyaedt/pull/6764>`_

        * - Add platform-specific console termination handling in console_setup.py
          - `#6766 <https://github.com/ansys/pyaedt/pull/6766>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Add \`\`ansys/actions/check-actions-security\`\` action and related fixes
          - `#6743 <https://github.com/ansys/pyaedt/pull/6743>`_

        * - Update CHANGELOG for v0.21.0
          - `#6746 <https://github.com/ansys/pyaedt/pull/6746>`_

        * - Bump 0.22.dev0
          - `#6747 <https://github.com/ansys/pyaedt/pull/6747>`_


`0.21.0 <https://github.com/ansys/pyaedt/releases/tag/v0.21.0>`_ - October 09, 2025
===================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Add background update check for PyAEDT with user notification
          - `#6739 <https://github.com/ansys/pyaedt/pull/6739>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump ansys/actions from 10.1.2 to 10.1.4
          - `#6735 <https://github.com/ansys/pyaedt/pull/6735>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Fix a bug in TouchstoneData class that occurs when the port names are not correctly parsed.
          - `#6715 <https://github.com/ansys/pyaedt/pull/6715>`_

        * - Removed duplicated numbers.py
          - `#6721 <https://github.com/ansys/pyaedt/pull/6721>`_

        * - Fix issue 6719 get_string_version
          - `#6722 <https://github.com/ansys/pyaedt/pull/6722>`_

        * - Update some emit params
          - `#6728 <https://github.com/ansys/pyaedt/pull/6728>`_

        * - Fixed generated jsons test issue
          - `#6729 <https://github.com/ansys/pyaedt/pull/6729>`_

        * - Enhance package installation process with fallback to pip if uv fails
          - `#6730 <https://github.com/ansys/pyaedt/pull/6730>`_

        * - Version manager pip fallback
          - `#6732 <https://github.com/ansys/pyaedt/pull/6732>`_

        * - Enable to import the lib again from MacOS
          - `#6738 <https://github.com/ansys/pyaedt/pull/6738>`_

        * - Fixed pedb bug
          - `#6741 <https://github.com/ansys/pyaedt/pull/6741>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.20.1
          - `#6714 <https://github.com/ansys/pyaedt/pull/6714>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Solution Data
          - `#6706 <https://github.com/ansys/pyaedt/pull/6706>`_


`0.20.1 <https://github.com/ansys/pyaedt/releases/tag/v0.20.1>`_ - October 01, 2025
===================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Panels update automatically after update
          - `#6690 <https://github.com/ansys/pyaedt/pull/6690>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump ansys/actions from 10.1.1 to 10.1.2
          - `#6693 <https://github.com/ansys/pyaedt/pull/6693>`_

        * - Update grpcio requirement from <1.75,>=1.50.0 to >=1.50.0,<1.76
          - `#6694 <https://github.com/ansys/pyaedt/pull/6694>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Add documentation for the pyd folder settings
          - `#6689 <https://github.com/ansys/pyaedt/pull/6689>`_

        * - Update \`\`CONTRIBUTORS.md\`\` with the latest contributors
          - `#6697 <https://github.com/ansys/pyaedt/pull/6697>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Increased width to fit elements
          - `#6691 <https://github.com/ansys/pyaedt/pull/6691>`_

        * - Add -- to uv to pass options to pip
          - `#6696 <https://github.com/ansys/pyaedt/pull/6696>`_

        * - Added point cloud generator extension to Maxwell 2D
          - `#6699 <https://github.com/ansys/pyaedt/pull/6699>`_

        * - Ibis import of models when multiple component have same name
          - `#6705 <https://github.com/ansys/pyaedt/pull/6705>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.20.0
          - `#6683 <https://github.com/ansys/pyaedt/pull/6683>`_

        * - Fix nightly doc build (temporary)
          - `#6684 <https://github.com/ansys/pyaedt/pull/6684>`_

        * - Remove caching from wheelhouse
          - `#6685 <https://github.com/ansys/pyaedt/pull/6685>`_

        * - Bump v0.21.dev0
          - `#6686 <https://github.com/ansys/pyaedt/pull/6686>`_

        * - Remove ansys processes on self-hosted
          - `#6687 <https://github.com/ansys/pyaedt/pull/6687>`_

        * - Improve pyaedt installer script
          - `#6702 <https://github.com/ansys/pyaedt/pull/6702>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Nastran import refactoring
          - `#6236 <https://github.com/ansys/pyaedt/pull/6236>`_


`0.20.0 <https://github.com/ansys/pyaedt/releases/tag/v0.20.0>`_ - September 26, 2025
=====================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update create_setup method
          - `#6279 <https://github.com/ansys/pyaedt/pull/6279>`_

        * - Install pyaedt via uv
          - `#6338 <https://github.com/ansys/pyaedt/pull/6338>`_

        * - 6290 add profile class
          - `#6478 <https://github.com/ansys/pyaedt/pull/6478>`_

        * - Allow pass AEDT installation directory
          - `#6494 <https://github.com/ansys/pyaedt/pull/6494>`_

        * - Add Profile class
          - `#6593 <https://github.com/ansys/pyaedt/pull/6593>`_

        * - Added test iframe to the docs
          - `#6618 <https://github.com/ansys/pyaedt/pull/6618>`_

        * - Add emit_schematic and emitter_node classes
          - `#6639 <https://github.com/ansys/pyaedt/pull/6639>`_

        * - 6620 bug located in export image
          - `#6641 <https://github.com/ansys/pyaedt/pull/6641>`_

        * - Delete motion setup
          - `#6652 <https://github.com/ansys/pyaedt/pull/6652>`_

        * - Version-manager-uv-support
          - `#6655 <https://github.com/ansys/pyaedt/pull/6655>`_

        * - Display-all-logs-extension-manager
          - `#6661 <https://github.com/ansys/pyaedt/pull/6661>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump pyvista from <0.46 to <0.47
          - `#6602 <https://github.com/ansys/pyaedt/pull/6602>`_

        * - Bump actions/checkout from 4.2.2 to 5.0.0
          - `#6613 <https://github.com/ansys/pyaedt/pull/6613>`_

        * - Bump ansys/actions from 10.0.15 to 10.0.20
          - `#6614 <https://github.com/ansys/pyaedt/pull/6614>`_

        * - Bump actions/setup-python from 5.6.0 to 6.0.0
          - `#6642 <https://github.com/ansys/pyaedt/pull/6642>`_

        * - Bump actions/labeler from 5.0.0 to 6.0.1
          - `#6643 <https://github.com/ansys/pyaedt/pull/6643>`_

        * - Bump codecov/codecov-action from 5.4.3 to 5.5.1
          - `#6644 <https://github.com/ansys/pyaedt/pull/6644>`_

        * - Bump pypa/gh-action-pypi-publish from 1.12.4 to 1.13.0
          - `#6645 <https://github.com/ansys/pyaedt/pull/6645>`_

        * - Bump ansys/actions from 10.0.20 to 10.1.1
          - `#6668 <https://github.com/ansys/pyaedt/pull/6668>`_

        * - Update pytest-cov requirement from <6.3,>=4.0.0 to >=4.0.0,<7.1
          - `#6669 <https://github.com/ansys/pyaedt/pull/6669>`_

        * - Update cffi requirement from <1.18,>=1.16.0 to >=1.16.0,<2.1
          - `#6670 <https://github.com/ansys/pyaedt/pull/6670>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Fix typo in env variable
          - `#6626 <https://github.com/ansys/pyaedt/pull/6626>`_

        * - Added via design video iframe
          - `#6634 <https://github.com/ansys/pyaedt/pull/6634>`_

        * - Fix doc link
          - `#6640 <https://github.com/ansys/pyaedt/pull/6640>`_

        * - Fix is_dielectric docstring
          - `#6677 <https://github.com/ansys/pyaedt/pull/6677>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - MATLAB script amp2db.m
          - `#6559 <https://github.com/ansys/pyaedt/pull/6559>`_

        * - Aligned ports to the same plane
          - `#6605 <https://github.com/ansys/pyaedt/pull/6605>`_

        * - Fixed configurations.py for circuit import when no port_names is passed
          - `#6610 <https://github.com/ansys/pyaedt/pull/6610>`_

        * - Some minor updates to PyAedt
          - `#6621 <https://github.com/ansys/pyaedt/pull/6621>`_

        * - Improve analyze method
          - `#6624 <https://github.com/ansys/pyaedt/pull/6624>`_

        * - Page connector
          - `#6636 <https://github.com/ansys/pyaedt/pull/6636>`_

        * - Moved fpdf2 and rpyc in optional dependencies
          - `#6647 <https://github.com/ansys/pyaedt/pull/6647>`_

        * - Fixed bug in variations which prevented eye diagram plot
          - `#6653 <https://github.com/ansys/pyaedt/pull/6653>`_

        * - Fixes and improvements in edit_sources() for q3d
          - `#6660 <https://github.com/ansys/pyaedt/pull/6660>`_

        * - Fix an issue with psutil on machine with multiple users running aedt
          - `#6665 <https://github.com/ansys/pyaedt/pull/6665>`_

        * - Fixed theme switching bug
          - `#6674 <https://github.com/ansys/pyaedt/pull/6674>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Make EMIT tests independent
          - `#6546 <https://github.com/ansys/pyaedt/pull/6546>`_

        * - Update CHANGELOG for v0.19.0
          - `#6607 <https://github.com/ansys/pyaedt/pull/6607>`_

        * - Update v0.20.dev0
          - `#6608 <https://github.com/ansys/pyaedt/pull/6608>`_

        * - Improve visualization failure handling
          - `#6617 <https://github.com/ansys/pyaedt/pull/6617>`_

        * - Improve Touchstone parser test
          - `#6629 <https://github.com/ansys/pyaedt/pull/6629>`_

        * - Temporary fix doc-build
          - `#6672 <https://github.com/ansys/pyaedt/pull/6672>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Migrate kernel converter extension
          - `#6536 <https://github.com/ansys/pyaedt/pull/6536>`_

        * - Optimize field plot test
          - `#6597 <https://github.com/ansys/pyaedt/pull/6597>`_

        * - Migrate convert to circuit extension
          - `#6619 <https://github.com/ansys/pyaedt/pull/6619>`_

        * - Add terminal support
          - `#6622 <https://github.com/ansys/pyaedt/pull/6622>`_

        * - Migrate maxwell extension fields distribution
          - `#6625 <https://github.com/ansys/pyaedt/pull/6625>`_

        * - Migrate via clustering extension
          - `#6627 <https://github.com/ansys/pyaedt/pull/6627>`_

        * - Migrate post layout design toolkit
          - `#6638 <https://github.com/ansys/pyaedt/pull/6638>`_

        * - Move project section applications
          - `#6666 <https://github.com/ansys/pyaedt/pull/6666>`_

        * - Separate methods for releasing the desktop and closing the AEDT application
          - `#6667 <https://github.com/ansys/pyaedt/pull/6667>`_


  .. tab-item:: Test

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Added missing microvia test
          - `#6649 <https://github.com/ansys/pyaedt/pull/6649>`_


`0.19.0 <https://github.com/ansys/pyaedt/releases/tag/v0.19.0>`_ - September 04, 2025
=====================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - New extension manager
          - `#6406 <https://github.com/ansys/pyaedt/pull/6406>`_

        * - Automatic release desktop
          - `#6557 <https://github.com/ansys/pyaedt/pull/6557>`_

        * - Support pin reordering in config files
          - `#6561 <https://github.com/ansys/pyaedt/pull/6561>`_

        * - Extension MCAD assembly
          - `#6581 <https://github.com/ansys/pyaedt/pull/6581>`_

        * - Added offset to page port creation during connect_to_component.
          - `#6599 <https://github.com/ansys/pyaedt/pull/6599>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump ansys/actions from 10.0.13 to 10.0.14
          - `#6504 <https://github.com/ansys/pyaedt/pull/6504>`_

        * - Bump actions/download-artifact from 4.3.0 to 5.0.0
          - `#6542 <https://github.com/ansys/pyaedt/pull/6542>`_

        * - Bump actions/checkout from 4.2.2 to 5.0.0
          - `#6565 <https://github.com/ansys/pyaedt/pull/6565>`_

        * - Update ansys-sphinx-theme range from <1.6 to <1.7
          - `#6583 <https://github.com/ansys/pyaedt/pull/6583>`_

        * - Bump codecov/codecov-action from 5.4.3 to 5.5.0
          - `#6588 <https://github.com/ansys/pyaedt/pull/6588>`_

        * - Update plotly requirement from <6.3,>=6.0 to >=6.0,<6.4
          - `#6590 <https://github.com/ansys/pyaedt/pull/6590>`_

        * - Bump ansys/actions into v10.0.15
          - `#6592 <https://github.com/ansys/pyaedt/pull/6592>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Improving Maxwell circuit documentation
          - `#6521 <https://github.com/ansys/pyaedt/pull/6521>`_

        * - Update ``html_context`` with PyAnsys tags
          - `#6579 <https://github.com/ansys/pyaedt/pull/6579>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Observe specified output path for saving extension results (and minor improvements)
          - `#6459 <https://github.com/ansys/pyaedt/pull/6459>`_

        * - Fixed issue in schematic components dictionary.
          - `#6473 <https://github.com/ansys/pyaedt/pull/6473>`_

        * - Join load thread before opening project
          - `#6513 <https://github.com/ansys/pyaedt/pull/6513>`_

        * - Maxwell solution type name compatibility
          - `#6514 <https://github.com/ansys/pyaedt/pull/6514>`_

        * - Save project after recovering archive
          - `#6553 <https://github.com/ansys/pyaedt/pull/6553>`_

        * - Configure layout
          - `#6560 <https://github.com/ansys/pyaedt/pull/6560>`_

        * - Issue with circuit extensions
          - `#6563 <https://github.com/ansys/pyaedt/pull/6563>`_

        * - Move test_via_design_examples_success to unit tests
          - `#6571 <https://github.com/ansys/pyaedt/pull/6571>`_

        * - 3dlayout component coordinate
          - `#6574 <https://github.com/ansys/pyaedt/pull/6574>`_

        * - Configure layout test
          - `#6577 <https://github.com/ansys/pyaedt/pull/6577>`_

        * - Setting right default TDR options
          - `#6578 <https://github.com/ansys/pyaedt/pull/6578>`_

        * - Fix problem with extension manager hanging on some extensions
          - `#6585 <https://github.com/ansys/pyaedt/pull/6585>`_

        * - Add context em fields q3d/q2d
          - `#6586 <https://github.com/ansys/pyaedt/pull/6586>`_

        * - Via design extension
          - `#6598 <https://github.com/ansys/pyaedt/pull/6598>`_

        * - Circuit config fixes
          - `#6600 <https://github.com/ansys/pyaedt/pull/6600>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.18.1
          - `#6503 <https://github.com/ansys/pyaedt/pull/6503>`_

        * - Enforce ``ruff`` pydocstyle D rules with available autofixes
          - `#6520 <https://github.com/ansys/pyaedt/pull/6520>`_

        * - Add jupyter backend for pyvista plot
          - `#6564 <https://github.com/ansys/pyaedt/pull/6564>`_

        * - Enforce simple ``ruff`` "flake8-todos" TD rules
          - `#6570 <https://github.com/ansys/pyaedt/pull/6570>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Migrate choke designer extension
          - `#6364 <https://github.com/ansys/pyaedt/pull/6364>`_

        * - 6451 migrate export layout extension
          - `#6455 <https://github.com/ansys/pyaedt/pull/6455>`_

        * - 6507 migrate parametrize edb extension
          - `#6510 <https://github.com/ansys/pyaedt/pull/6510>`_

        * - 6511 migrate push excitation from file
          - `#6515 <https://github.com/ansys/pyaedt/pull/6515>`_

        * - 6516 migrate push excitation from file hfss3d
          - `#6518 <https://github.com/ansys/pyaedt/pull/6518>`_

        * - 6530 migrate import nastran extension
          - `#6537 <https://github.com/ansys/pyaedt/pull/6537>`_

        * - 6529 migrate create report extension
          - `#6545 <https://github.com/ansys/pyaedt/pull/6545>`_

        * - Extension Configure Layout
          - `#6552 <https://github.com/ansys/pyaedt/pull/6552>`_

        * - Configure layout
          - `#6567 <https://github.com/ansys/pyaedt/pull/6567>`_

        * - Insert layout component
          - `#6580 <https://github.com/ansys/pyaedt/pull/6580>`_

        * - Enhancement mcad assembly
          - `#6591 <https://github.com/ansys/pyaedt/pull/6591>`_

        * - Use use small snp for test
          - `#6596 <https://github.com/ansys/pyaedt/pull/6596>`_


`0.18.1 <https://github.com/ansys/pyaedt/releases/tag/v0.18.1>`_ - August 08, 2025
==================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Support new emitcom api for 25r2, add node classes for all emit node types
          - `#6068 <https://github.com/ansys/pyaedt/pull/6068>`_

        * - Add submit job class
          - `#6331 <https://github.com/ansys/pyaedt/pull/6331>`_

        * - Circuit configuration extension refactoring
          - `#6417 <https://github.com/ansys/pyaedt/pull/6417>`_

        * - Em fields in q3d
          - `#6421 <https://github.com/ansys/pyaedt/pull/6421>`_

        * - Add vector fields names in extension
          - `#6423 <https://github.com/ansys/pyaedt/pull/6423>`_

        * - Add  create ports by nets function
          - `#6428 <https://github.com/ansys/pyaedt/pull/6428>`_

        * - Add options to debug unit tests
          - `#6479 <https://github.com/ansys/pyaedt/pull/6479>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update scikit-rf requirement from <1.8,>=0.30.0 to >=0.30.0,<1.9
          - `#6437 <https://github.com/ansys/pyaedt/pull/6437>`_

        * - Update ansys-sphinx-theme requirement from <1.5,>=1.0.0 to >=1.0.0,<1.6
          - `#6438 <https://github.com/ansys/pyaedt/pull/6438>`_

        * - Update vtk requirement from <9.4,>=9.0 to >=9.0,<9.6
          - `#6439 <https://github.com/ansys/pyaedt/pull/6439>`_

        * - Bump ansys/actions from 10.0.12 to 10.0.13
          - `#6469 <https://github.com/ansys/pyaedt/pull/6469>`_

        * - Update grpcio requirement from <1.74,>=1.50.0 to >=1.50.0,<1.75
          - `#6487 <https://github.com/ansys/pyaedt/pull/6487>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Fix monitor documentation
          - `#6457 <https://github.com/ansys/pyaedt/pull/6457>`_

        * - Documentation improvement of create_report method
          - `#6468 <https://github.com/ansys/pyaedt/pull/6468>`_

        * - Improving primitives maxwell circuit documentation
          - `#6489 <https://github.com/ansys/pyaedt/pull/6489>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Save project before analyze
          - `#6432 <https://github.com/ansys/pyaedt/pull/6432>`_

        * - Import cad with none value in control file
          - `#6436 <https://github.com/ansys/pyaedt/pull/6436>`_

        * - Fix a typo error which was preventing optislang setup to be populated.
          - `#6448 <https://github.com/ansys/pyaedt/pull/6448>`_

        * - Use regex to check installed ansysem versions
          - `#6453 <https://github.com/ansys/pyaedt/pull/6453>`_

        * - Fix indentation when loading emit revision
          - `#6454 <https://github.com/ansys/pyaedt/pull/6454>`_

        * - Edb import
          - `#6458 <https://github.com/ansys/pyaedt/pull/6458>`_

        * - Fix issue in method to create tdr analysis which caused failure when more than 1 input is present
          - `#6460 <https://github.com/ansys/pyaedt/pull/6460>`_

        * - Fixed issue in export_results for q3d
          - `#6467 <https://github.com/ansys/pyaedt/pull/6467>`_

        * - Icepak boundary update is missing
          - `#6483 <https://github.com/ansys/pyaedt/pull/6483>`_

        * - Export model obj usage of relative path
          - `#6486 <https://github.com/ansys/pyaedt/pull/6486>`_

        * - Get evalauted value with correct unit scale
          - `#6492 <https://github.com/ansys/pyaedt/pull/6492>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update changelog for v0.18.0
          - `#6429 <https://github.com/ansys/pyaedt/pull/6429>`_

        * - Update 0.19.0dev0
          - `#6431 <https://github.com/ansys/pyaedt/pull/6431>`_

        * - Bump aedt version into 2025.2
          - `#6477 <https://github.com/ansys/pyaedt/pull/6477>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Submit job class
          - `#6349 <https://github.com/ansys/pyaedt/pull/6349>`_

        * - Pathlib in multiple files
          - `#6367 <https://github.com/ansys/pyaedt/pull/6367>`_

        * - 6375 migrate shielding effectiveness extension
          - `#6379 <https://github.com/ansys/pyaedt/pull/6379>`_

        * - 6380 migrate import schematic extension
          - `#6389 <https://github.com/ansys/pyaedt/pull/6389>`_

        * - 6390 migrate export to 3d extension
          - `#6391 <https://github.com/ansys/pyaedt/pull/6391>`_

        * - Scheduler logic
          - `#6398 <https://github.com/ansys/pyaedt/pull/6398>`_, `#6399 <https://github.com/ansys/pyaedt/pull/6399>`_

        * - Enforce design check in extensions
          - `#6433 <https://github.com/ansys/pyaedt/pull/6433>`_

        * - Implement Arbitrary Wave Port extension with new format and tests
          - `#6498 <https://github.com/ansys/pyaedt/pull/6498>`_


  .. tab-item:: Test

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Temporary skip test in linux 2025r2
          - `#6456 <https://github.com/ansys/pyaedt/pull/6456>`_


`0.18.0 <https://github.com/ansys/pyaedt/releases/tag/v0.18.0>`_ - July 17, 2025
================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Added method reduce to the TouchstoneData class
          - `#6191 <https://github.com/ansys/pyaedt/pull/6191>`_

        * - Add function to emit to list all component types
          - `#6210 <https://github.com/ansys/pyaedt/pull/6210>`_

        * - Toggle net type in q3d
          - `#6237 <https://github.com/ansys/pyaedt/pull/6237>`_

        * - Assign wave port in driven terminal
          - `#6358 <https://github.com/ansys/pyaedt/pull/6358>`_

        * - Control order connection between coil terminals in maxwell3d transientaphiformulation
          - `#6360 <https://github.com/ansys/pyaedt/pull/6360>`_

        * - Spisim ucie
          - `#6373 <https://github.com/ansys/pyaedt/pull/6373>`_

        * - Added a new class to customize page ports and added 2 new properties
          - `#6374 <https://github.com/ansys/pyaedt/pull/6374>`_

        * - Add new method to convert far field data to ffd
          - `#6392 <https://github.com/ansys/pyaedt/pull/6392>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - bump codecov/codecov-action from 5.4.2 to 5.4.3
          - `#6166 <https://github.com/ansys/pyaedt/pull/6166>`_

        * - bump ansys/actions from 9.0.12 to 9.0.13
          - `#6217 <https://github.com/ansys/pyaedt/pull/6217>`_

        * - Update pytest-cov requirement from <6.2,>=4.0.0 to >=4.0.0,<6.3
          - `#6292 <https://github.com/ansys/pyaedt/pull/6292>`_

        * - Update plotly requirement from <6.2,>=6.0 to >=6.0,<6.3
          - `#6356 <https://github.com/ansys/pyaedt/pull/6356>`_

        * - Update pytest-xdist requirement from <3.8,>=3.5.0 to >=3.5.0,<3.9
          - `#6393 <https://github.com/ansys/pyaedt/pull/6393>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Improving documentation of maxwell class
          - `#6150 <https://github.com/ansys/pyaedt/pull/6150>`_

        * - Update ``CONTRIBUTORS.md`` with the latest contributors
          - `#6218 <https://github.com/ansys/pyaedt/pull/6218>`_

        * - Fix docstrings to comply with numpydoc style.
          - `#6231 <https://github.com/ansys/pyaedt/pull/6231>`_

        * - Update ``contributors.md`` with the latest contributors
          - `#6330 <https://github.com/ansys/pyaedt/pull/6330>`_, `#6394 <https://github.com/ansys/pyaedt/pull/6394>`_

        * - Fix extension contribution code snippets
          - `#6384 <https://github.com/ansys/pyaedt/pull/6384>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - fix a bug in the reduce method
          - `#6204 <https://github.com/ansys/pyaedt/pull/6204>`_

        * - Improve circuit speed
          - `#6206 <https://github.com/ansys/pyaedt/pull/6206>`_

        * - LSF submission string error 6182
          - `#6208 <https://github.com/ansys/pyaedt/pull/6208>`_

        * - RefDes is a property not present in all components.
          - `#6209 <https://github.com/ansys/pyaedt/pull/6209>`_

        * - Version manager install from wheelhouse
          - `#6216 <https://github.com/ansys/pyaedt/pull/6216>`_

        * - edit_external_circuit move lists
          - `#6223 <https://github.com/ansys/pyaedt/pull/6223>`_

        * - Fixed the way to retrieve non_graphical variable
          - `#6351 <https://github.com/ansys/pyaedt/pull/6351>`_

        * - Exposed file format in plot_animated_field function
          - `#6353 <https://github.com/ansys/pyaedt/pull/6353>`_

        * - Handle zero-valued expression variables properly.
          - `#6376 <https://github.com/ansys/pyaedt/pull/6376>`_

        * - Symbolstyle return value
          - `#6378 <https://github.com/ansys/pyaedt/pull/6378>`_

        * - The method export_model_obj when a full path to an obj is passed.
          - `#6382 <https://github.com/ansys/pyaedt/pull/6382>`_

        * - Refactoring of component_array creation
          - `#6383 <https://github.com/ansys/pyaedt/pull/6383>`_

        * - Support for maxwell transient aphi solver renaming in 2025r2
          - `#6414 <https://github.com/ansys/pyaedt/pull/6414>`_

        * - Subprocess call doesn't accept check
          - `#6418 <https://github.com/ansys/pyaedt/pull/6418>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - 2025.2 compatibility
          - `#6152 <https://github.com/ansys/pyaedt/pull/6152>`_

        * - update CHANGELOG for v0.17.0
          - `#6192 <https://github.com/ansys/pyaedt/pull/6192>`_

        * - Update 0.18.dev0
          - `#6195 <https://github.com/ansys/pyaedt/pull/6195>`_

        * - Improve test efficiency
          - `#6196 <https://github.com/ansys/pyaedt/pull/6196>`_

        * - Do not check AEDT/EDB binary files with Ruff
          - `#6198 <https://github.com/ansys/pyaedt/pull/6198>`_

        * - Bump ansys actions to v9.0.12
          - `#6201 <https://github.com/ansys/pyaedt/pull/6201>`_

        * - Enforce ``ruff`` pycodestyle e rules
          - `#6203 <https://github.com/ansys/pyaedt/pull/6203>`_

        * - Update labeler permissions
          - `#6232 <https://github.com/ansys/pyaedt/pull/6232>`_

        * - Bump ansys/actions into v10.0.4
          - `#6233 <https://github.com/ansys/pyaedt/pull/6233>`_

        * - Update changelog for v0.17.5
          - `#6341 <https://github.com/ansys/pyaedt/pull/6341>`_

        * - Add deepwiki badge in readme.md
          - `#6345 <https://github.com/ansys/pyaedt/pull/6345>`_

        * - Fix visualization random failure
          - `#6346 <https://github.com/ansys/pyaedt/pull/6346>`_

        * - Update minimum python version
          - `#6352 <https://github.com/ansys/pyaedt/pull/6352>`_

        * - Add dependency check on all target
          - `#6363 <https://github.com/ansys/pyaedt/pull/6363>`_

        * - Temporary fix for vtk-osmesa
          - `#6407 <https://github.com/ansys/pyaedt/pull/6407>`_

        * - Rename numbers.py into numbers_utils.py
          - `#6412 <https://github.com/ansys/pyaedt/pull/6412>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - test_12_1_post processing
          - `#6200 <https://github.com/ansys/pyaedt/pull/6200>`_

        * - Improve primitives connect
          - `#6220 <https://github.com/ansys/pyaedt/pull/6220>`_

        * - Import nastran extension and tests
          - `#6227 <https://github.com/ansys/pyaedt/pull/6227>`_

        * - Cutout extension
          - `#6321 <https://github.com/ansys/pyaedt/pull/6321>`_

        * - Configure layout rlc on cap
          - `#6342 <https://github.com/ansys/pyaedt/pull/6342>`_

        * - Use enum instead of custom class
          - `#6354 <https://github.com/ansys/pyaedt/pull/6354>`_

        * - Point cloud extension and tests
          - `#6372 <https://github.com/ansys/pyaedt/pull/6372>`_

        * - Power map from csv extension
          - `#6388 <https://github.com/ansys/pyaedt/pull/6388>`_


`0.17.5 <https://github.com/ansys/pyaedt/releases/tag/v0.17.5>`_ - June 30, 2025
================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Create coil extension
          - `#6276 <https://github.com/ansys/pyaedt/pull/6276>`_

        * - Update create_setup method
          - `#6279 <https://github.com/ansys/pyaedt/pull/6279>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump ansys/actions from 10.0.11 to 10.0.12
          - `#6325 <https://github.com/ansys/pyaedt/pull/6325>`_

        * - Update pandas requirement from <2.3,>=1.1.0 to >=1.1.0,<2.4
          - `#6326 <https://github.com/ansys/pyaedt/pull/6326>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Add guide line on how to develop an extension
          - `#6303 <https://github.com/ansys/pyaedt/pull/6303>`_

        * - Add space between badges.
          - `#6305 <https://github.com/ansys/pyaedt/pull/6305>`_

        * - Add direct link to troubleshooting in the aedt panel installation
          - `#6320 <https://github.com/ansys/pyaedt/pull/6320>`_

        * - Fix ci cd badge in readme
          - `#6334 <https://github.com/ansys/pyaedt/pull/6334>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - The new_session was not properly populated into desktop __new__ class
          - `#6298 <https://github.com/ansys/pyaedt/pull/6298>`_

        * - Extension's unwanted desktop opening
          - `#6304 <https://github.com/ansys/pyaedt/pull/6304>`_

        * - Notify vtk for changes in the animation loop
          - `#6310 <https://github.com/ansys/pyaedt/pull/6310>`_

        * - Lsf-job-submission-failure
          - `#6318 <https://github.com/ansys/pyaedt/pull/6318>`_

        * - Dotnet use runtime spec
          - `#6324 <https://github.com/ansys/pyaedt/pull/6324>`_

        * - Skip move on circuit if it is running on linux in non-graphical mode
          - `#6332 <https://github.com/ansys/pyaedt/pull/6332>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Enforce ``ruff`` pyflakes f rules
          - `#6239 <https://github.com/ansys/pyaedt/pull/6239>`_

        * - Update changelog for v0.17.4
          - `#6306 <https://github.com/ansys/pyaedt/pull/6306>`_

        * - Skip not stable emit tests
          - `#6312 <https://github.com/ansys/pyaedt/pull/6312>`_

        * - Add cooldown for github actions
          - `#6327 <https://github.com/ansys/pyaedt/pull/6327>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Refactored settings.py to use pathlib
          - `#6291 <https://github.com/ansys/pyaedt/pull/6291>`_

        * - Configure layout
          - `#6328 <https://github.com/ansys/pyaedt/pull/6328>`_


`0.17.4 <https://github.com/ansys/pyaedt/releases/tag/v0.17.4>`_ - June 24, 2025
================================================================================

.. tab-set::


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update grpcio requirement from <1.73,>=1.50.0 to >=1.50.0,<1.74
          - `#6293 <https://github.com/ansys/pyaedt/pull/6293>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update ``contributors.md`` with the latest contributors
          - `#6295 <https://github.com/ansys/pyaedt/pull/6295>`_

        * - Fix url link after changes
          - `#6302 <https://github.com/ansys/pyaedt/pull/6302>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Parametrics fix in add_from_file for maxwell
          - `#6299 <https://github.com/ansys/pyaedt/pull/6299>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update changelog for v0.17.3
          - `#6297 <https://github.com/ansys/pyaedt/pull/6297>`_


`0.17.3 <https://github.com/ansys/pyaedt/releases/tag/v0.17.3>`_ - June 23, 2025
================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Via design extension
          - `#6222 <https://github.com/ansys/pyaedt/pull/6222>`_

        * - Configure layout
          - `#6235 <https://github.com/ansys/pyaedt/pull/6235>`_

        * - New version of point_in_polygon for higher performances
          - `#6283 <https://github.com/ansys/pyaedt/pull/6283>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update grpcio requirement from <1.71,>=1.50.0 to >=1.50.0,<1.73
          - `#6263 <https://github.com/ansys/pyaedt/pull/6263>`_

        * - Update pytest requirement from <8.4,>=7.4.0 to >=7.4.0,<8.5
          - `#6265 <https://github.com/ansys/pyaedt/pull/6265>`_

        * - Update plotly requirement from <6.1,>=6.0 to >=6.0,<6.2
          - `#6266 <https://github.com/ansys/pyaedt/pull/6266>`_

        * - Bump ansys/actions from 10.0.10 to 10.0.11
          - `#6267 <https://github.com/ansys/pyaedt/pull/6267>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Refactor move it extension with extensioncommon
          - `#6280 <https://github.com/ansys/pyaedt/pull/6280>`_

        * - Remove_galileo_reference
          - `#6281 <https://github.com/ansys/pyaedt/pull/6281>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update changelog for v0.17.2
          - `#6262 <https://github.com/ansys/pyaedt/pull/6262>`_

        * - Add numpy as default requirement
          - `#6289 <https://github.com/ansys/pyaedt/pull/6289>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Advanced field calculator extension
          - `#6261 <https://github.com/ansys/pyaedt/pull/6261>`_

        * - Configure layout
          - `#6287 <https://github.com/ansys/pyaedt/pull/6287>`_


`0.17.2 <https://github.com/ansys/pyaedt/releases/tag/v0.17.2>`_ - June 13, 2025
================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Frtm new methods and doa new features
          - `#6221 <https://github.com/ansys/pyaedt/pull/6221>`_

        * - Coordinate system in hfss 3d layout
          - `#6255 <https://github.com/ansys/pyaedt/pull/6255>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update pyvista[io] requirement from <0.45,>=0.38.0 to >=0.38.0,<0.46
          - `#6061 <https://github.com/ansys/pyaedt/pull/6061>`_

        * - Bump ansys/actions from 10.0.8 to 10.0.10
          - `#6256 <https://github.com/ansys/pyaedt/pull/6256>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Import graphic dependencies if needed
          - `#6246 <https://github.com/ansys/pyaedt/pull/6246>`_

        * - Emi receiver report
          - `#6250 <https://github.com/ansys/pyaedt/pull/6250>`_

        * - Add extension logo image anchor
          - `#6251 <https://github.com/ansys/pyaedt/pull/6251>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update changelog for v0.17.1
          - `#6245 <https://github.com/ansys/pyaedt/pull/6245>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Extension architecture using common class
          - `#6238 <https://github.com/ansys/pyaedt/pull/6238>`_


`0.17.1 <https://github.com/ansys/pyaedt/releases/tag/v0.17.1>`_ - June 09, 2025
================================================================================

.. tab-set::


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update pytest-xdist requirement from <3.7,>=3.5.0 to >=3.5.0,<3.8
          - `#6242 <https://github.com/ansys/pyaedt/pull/6242>`_

        * - Bump ansys/actions from 10.0.4 to 10.0.8
          - `#6243 <https://github.com/ansys/pyaedt/pull/6243>`_


`0.17.0 <https://github.com/ansys/pyaedt/releases/tag/v0.17.0>`_ - May 23, 2025
===============================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Added document revision to Virtual Compliance
          - `#6131 <https://github.com/ansys/pyaedt/pull/6131>`_

        * - Add circuit extension
          - `#6143 <https://github.com/ansys/pyaedt/pull/6143>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - update pytest-timeout requirement from <2.4,>=2.3.0 to >=2.3.0,<2.5
          - `#6167 <https://github.com/ansys/pyaedt/pull/6167>`_

        * - update scikit-rf requirement from <1.7,>=0.30.0 to >=0.30.0,<1.8
          - `#6172 <https://github.com/ansys/pyaedt/pull/6172>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update ``CONTRIBUTORS.md`` with the latest contributors
          - `#6168 <https://github.com/ansys/pyaedt/pull/6168>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Return None in compute power loss if no solution available
          - `#6106 <https://github.com/ansys/pyaedt/pull/6106>`_

        * - Fix small bug in VirtualCompliance which prevented the save of the reports
          - `#6165 <https://github.com/ansys/pyaedt/pull/6165>`_

        * - Improve the speed up of the cleanup of objects and delete of objects in modeler.
          - `#6170 <https://github.com/ansys/pyaedt/pull/6170>`_

        * - Image aspect ratio in VirtualCompliance
          - `#6173 <https://github.com/ansys/pyaedt/pull/6173>`_

        * - Change default report resolution on VirtualCompliance
          - `#6177 <https://github.com/ansys/pyaedt/pull/6177>`_

        * - Check if property key exist in boundary for configuration file
          - `#6180 <https://github.com/ansys/pyaedt/pull/6180>`_

        * - improved ibis pin load time
          - `#6181 <https://github.com/ansys/pyaedt/pull/6181>`_

        * - fixed the issue where the freq/time column got interchanged with y axis value for lna analysis and tdr
          - `#6185 <https://github.com/ansys/pyaedt/pull/6185>`_

        * - fixed add_pyaedt_to_aedt
          - `#6189 <https://github.com/ansys/pyaedt/pull/6189>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Setting up ruff
          - `#6157 <https://github.com/ansys/pyaedt/pull/6157>`_

        * - update CHANGELOG for v0.16.2
          - `#6164 <https://github.com/ansys/pyaedt/pull/6164>`_

        * - Update dependabot cfg and codeowners
          - `#6169 <https://github.com/ansys/pyaedt/pull/6169>`_

        * - Minor changes to update jobs name
          - `#6190 <https://github.com/ansys/pyaedt/pull/6190>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Separate extension tests
          - `#6186 <https://github.com/ansys/pyaedt/pull/6186>`_


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

        * - Add hint for toolkit icon visibility
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

        * - "Time" removed from intrinsic keys in Steady State simulations
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