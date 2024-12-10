Export to 3D
============

The **Export to 3D** extension allows users to export their HFSS 3D Layout designs into various formats including HFSS,
Q3D, Maxwell 3D, and Icepak, keeping the net names.

The extension provides a graphical user interface (GUI) for configuration,
or it can be used in batch mode via command line arguments.


Features
--------

- **Support for various export formats**: Choose from `HFSS`, `Q3D`, `Maxwell 3D`, and `Icepak` export options.
- **User interface**: A simple user interface for selecting the desired export option.

The following image shows the extension user interface:

.. image:: ../../../_static/extensions/export_3d_ui.png
  :width: 800
  :alt: Parametrize Layout UI


Using the extension
-------------------

1. Open the **Automation** tab in the HFSS 3D Layout interface.
2. Locate and click the **Export to 3D** icon under the Extension Manager.
3. The main window displays a label, a combobox to choose an export option, and a button to initiate the export.
3. Click **Export** to export the design.


Command Line
------------

The extension can also be used directly via the command line for batch processing.

Supported arguments include:

- **choice**: The export option to choose (`"Export to HFSS"`, `"Export to Q3D"`, `"Export to Maxwell 3D"`,
or `"Export to Icepak"`).
- **is_batch**: Boolean flag to indicate if the extension should run in batch mode.

Use the following syntax to run the extension:

.. toctree::
   :maxdepth: 2

   ../commandline
