Extensions
==========

Extensions provide a simplified graphical user interface (GUI) to perform automated workflows in AEDT, they are generally tool-specific and are therefore only accessible given the appropriate context.
In AEDT, you can use the `Extension manager <https://aedt.docs.pyansys.com/version/stable/Getting_started/Installation.html#extension-manager>`_ to add or remove extensions.
The Extension manager allows the user to install three different types of extensions:

- **Pre-installed extensions** available at project level.
- **Open source PyAEDT toolkits** available at application level.
- **Custom extensions** installable both at project and application level.

The following sections provide further clarification.

You can launch extensions in standalone mode from the console or a Python script.


Pre-installed extensions
------------------------

Project extensions
~~~~~~~~~~~~~~~~~~

Pre-installed extensions are available at project level so they are available for all AEDT applications.
They are small automated workflows with a simple GUI.

.. grid:: 2

   .. grid-item-card:: Import Nastran
            :link: pyaedt_extensions_doc/project/import_nastran
            :link-type: doc
            :margin: 2 2 0 0

            Import a Nastran or STL file in any 3D modeler application.


   .. grid-item-card:: Configure Layout
            :link: pyaedt_extensions_doc/project/configure_layout
            :link-type: doc
            :margin: 2 2 0 0

            Configure layout for PCB & package analysis.


   .. grid-item-card:: Advanced Fields Calculator
            :link: pyaedt_extensions_doc/project/advanced_fields_calculator
            :link-type: doc
            :margin: 2 2 0 0

            Lear how to use the Advanced Fields Calculator extension.


   .. grid-item-card:: Kernel converter
            :link: pyaedt_extensions_doc/project/kernel_convert
            :link-type: doc
            :margin: 2 2 0 0

            Lear how to convert projects from 2022R2 to newer versions.


   .. grid-item-card:: Point cloud generator
            :link: pyaedt_extensions_doc/project/point_cloud_generator
            :link-type: doc
            :margin: 2 2 0 0

            Generate and import points list from a geometry.

   .. grid-item-card:: Via design
            :link: pyaedt_extensions_doc/project/via_design
            :link-type: doc
            :margin: 2 2 0 0

            Generate a parameterized via design.

HFSS 3D Layout extensions
~~~~~~~~~~~~~~~~~~~~~~~~~

Pre-installed extensions are available at HFSS 3D Layout level.
They are small automated workflows with a simple GUI.

.. grid:: 2

   .. grid-item-card:: Parametrize Layout
            :link: pyaedt_extensions_doc/hfss3dlayout/parametrize_edb
            :link-type: doc
            :margin: 2 2 0 0

            Parametrize a full layout design.


   .. grid-item-card:: Generate arbitrary wave ports
            :link: pyaedt_extensions_doc/hfss3dlayout/arbitrary_wave_port
            :link-type: doc
            :margin: 2 2 0 0

            Generate arbitrary wave ports in HFSS.

   .. grid-item-card:: Push excitation from file
            :link: pyaedt_extensions_doc/hfss3dlayout/push_excitation
            :link-type: doc
            :margin: 2 2 0 0

            Edit a source from file data in HFSS 3D Layout.

   .. grid-item-card:: Cutout
            :link: pyaedt_extensions_doc/hfss3dlayout/cutout
            :link-type: doc
            :margin: 2 2 0 0

            Advanced layout cutout.

   .. grid-item-card:: Export layout
            :link: pyaedt_extensions_doc/hfss3dlayout/export_layout
            :link-type: doc
            :margin: 2 2 0 0

            Export layout.

   .. grid-item-card:: Export to 3D
            :link: pyaedt_extensions_doc/hfss3dlayout/export_3d
            :link-type: doc
            :margin: 2 2 0 0

            Export layout to 3D.

   .. grid-item-card:: Layout design toolkit
            :link: pyaedt_extensions_doc/hfss3dlayout/layout_design_toolkit
            :link-type: doc
            :margin: 2 2 0 0

            Layout design toolkit.

HFSS extensions
~~~~~~~~~~~~~~~

Pre-installed extensions are available at HFSS level.
They are small automated workflows with a simple GUI.

.. grid:: 2

   .. grid-item-card:: Choke designer
            :link: pyaedt_extensions_doc/hfss/choke_designer
            :link-type: doc
            :margin: 2 2 0 0

            Design a choke and import it in HFSS.

   .. grid-item-card:: Push excitation from file
            :link: pyaedt_extensions_doc/hfss/push_excitation
            :link-type: doc
            :margin: 2 2 0 0

            Edit a source from file data in HFSS.

   .. grid-item-card:: Shielding effectiveness
            :link: pyaedt_extensions_doc/hfss/shielding
            :link-type: doc
            :margin: 2 2 0 0

            Shielding effectiveness automated workflow HFSS.

   .. grid-item-card:: Move it
            :link: pyaedt_extensions_doc/hfss/move_it
            :link-type: doc
            :margin: 2 2 0 0

            From a line generate the parameters needed to simulate a trajectory.


Icepak extensions
~~~~~~~~~~~~~~~~~

Pre-installed extensions are available at Icepak level.
They are small automated workflows with a simple GUI.

.. grid:: 2

   .. grid-item-card:: Create power map
            :link: pyaedt_extensions_doc/icepak/create_power_map
            :link-type: doc
            :margin: 2 2 0 0

            Import a CSV file containing sources layout and power dissipation information.


Circuit extensions
~~~~~~~~~~~~~~~~~~

Pre-installed extensions are available at Circuit level.
They are small automated workflows with a simple GUI.

.. grid:: 2

   .. grid-item-card:: Schematic import
            :link: pyaedt_extensions_doc/circuit/import_schematic
            :link-type: doc
            :margin: 2 2 0 0

            Import different schematic files (ACS, SP, CIR, QCV) into Circuit.


   .. grid-item-card:: Circuit configuration
            :link: pyaedt_extensions_doc/circuit/circuit_configuration
            :link-type: doc
            :margin: 2 2 0 0

            Apply simulation configuration to a Circuit design.


Twin Builder extensions
~~~~~~~~~~~~~~~~~~~~~~~

Pre-installed extensions are available at Twin Builder level.
They are small automated workflows with a simple GUI.

.. grid:: 2

   .. grid-item-card:: Convert to Circuit
            :link: pyaedt_extensions_doc/twinbuilder/convert_to_circuit
            :link-type: doc
            :margin: 2 2 0 0

            Convert Twin Builder design to Circuit.

Maxwell extensions
~~~~~~~~~~~~~~~~~~

Pre-installed extensions are available at Maxwell level.
They are small automated workflows with a simple GUI.

.. grid:: 2

   .. grid-item-card:: Fields Loss Distribution
            :link: pyaedt_extensions_doc/maxwell/fields_distribution
            :link-type: doc
            :margin: 2 2 0 0

            Export fields loss distribution to a generic format (CSV, TAB or NPY).

   .. grid-item-card:: Vertical and flat coil geometries
            :link: pyaedt_extensions_doc/maxwell/vertical_flat_coil
            :link-type: doc
            :margin: 2 2 0 0

            Automation of vertical and flat coil geometries.

Templates
~~~~~~~~~
Templates to show how to build an extension consisting of a small automated workflow with a simple UI.

.. grid:: 2

   .. grid-item-card:: Extension template
            :link: pyaedt_extensions_doc/templates/getting_started
            :link-type: doc
            :margin: 2 2 0 0

            Simple extension template to get started.

.. toctree::
   :hidden:
   :maxdepth: 1

   pyaedt_extensions_doc/project/index
   pyaedt_extensions_doc/hfss3dlayout/index
   pyaedt_extensions_doc/hfss/index
   pyaedt_extensions_doc/icepak/index
   pyaedt_extensions_doc/circuit/index
   pyaedt_extensions_doc/twinbuilder/index
   pyaedt_extensions_doc/maxwell/index
   pyaedt_extensions_doc/templates/index


Open source toolkits
--------------------

Open source toolkits are available at application level.
They are advanced workflows where backend and frontend are split.
They are also fully documented and tested.

Here are some links to existing toolkits:
- Hfss: `Antenna Wizard <https://github.com/ansys/pyaedt-toolkits-antenna>`_.
- Maxwell 3D: `Magnet Segmentation Wizard <https://github.com/ansys/magnet-segmentation-toolkit>`_.

Now, you need to download the installer from the Releases section of each toolkit.
You can access it by clicking the "Install" button in the corresponding repository.

After installing it, you can add the toolkit to AEDT as a Custom extension by pointing to the .exe file.

.. image:: ../Resources/toolkit_manager_3.png
  :width: 500
  :alt: PyAEDT toolkit manager 3


Custom extensions
-----------------

Custom extensions are custom workflows (Python script) that can be installed both at project and application level.
From the Extension manager select the target destination:

.. image:: ../Resources/toolkit_manager_1.png
  :width: 500
  :alt: PyAEDT toolkit manager 1

Select `Custom` as the extension type.
Provide the path of the Python script containing the workflow.
Enter the extension name. This is the name that appears beneath the button in the Automation tab after a successful installation.

.. image:: ../Resources/my_custom_extension.png
  :width: 500
  :alt: Custom Extension

After the normal completion of the installation a new button appears:

.. image:: ../Resources/my_custom_extension_1.png
  :width: 500
  :alt: Custom Extension 1

The example below is a simple example of custom extension.
The Python script requires a common initial part to define the port and the version of the AEDT session to connect to.

.. code:: python

    import ansys.aedt.core
    import os

    # common part
    if "PYAEDT_SCRIPT_PORT" in os.environ and "PYAEDT_SCRIPT_VERSION" in os.environ:
        port = os.environ["PYAEDT_SCRIPT_PORT"]
        version = os.environ["PYAEDT_SCRIPT_VERSION"]
    else:
        port = 0
        version = "2025.1"

    # your pyaedt script
    app = ansys.aedt.core.Desktop(new_desktop_session=False, specified_version=version, port=port)

    active_project = app.active_project()
    active_design = app.active_design(active_project)

    # no need to hardcode your application since get_pyaedt_app detects it for you
    aedtapp = ansys.aedt.core.get_pyaedt_app(design_name=active_design.GetName(), desktop=app)

    # your workflow
    aedtapp.modeler.create_sphere([0, 0, 0], 20)

    app.release_desktop(False, False)
