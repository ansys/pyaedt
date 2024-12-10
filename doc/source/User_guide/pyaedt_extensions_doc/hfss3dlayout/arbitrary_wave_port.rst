Arbitrary wave port
===================

This extension automates the creation of arbitrary wave ports for PCB layouts or other design files.

Features
--------

- Provides an intuitive user interface for selecting nets, defining the cutout type, and adjusting parameters such as expansion factor.
- Supports batch processing for automated execution via command line arguments.
- Customizable options for fixing disjoint nets, selecting the cutout type, and applying expansion factors.
- Integration with Ansys EDB for layout cutout creation and post-processing.

The following image shows the extension user interface:

.. image:: ../../../_static/extensions/arbitrary_wave_port_ui.png
  :width: 800
  :alt: Arbitrary Wave Port Creator UI

It assumes that oblong voids are explicit and some pad-stack instances are inside to define terminal.
After defining the working directory and the source file used for creating wave ports, the combobox for defining
the mounting side is important. You can choose between `top` and `bottom`.
For the selected design, `top` searches for the top metal layer and `bottom` for the bottom signal layer.
If not void are found the tool shows an error message, you might have to change the mounting side.

Note: The selected working directory content is deleted once you press `Generate` button.
If this folder already exists and is not empty, user gets a warning window asking to continue or not.
The check box `Import EDB` is checked by default, when user browse for source file,
only folders are displayed since EDB is an AEDB folder.

The tool also supports other format, when the user does not check `Import EDB` box, the following file formats are available:
odb++, brd, mcm, or zip are allowed.


Using the extension
-------------------

1. Open the **Automation** tab in the HFSS 3D Layout interface.
2. Locate and click the **Layout Cutout** icon under the Extension Manager.
3. The main window displays the following elements:
   - **Working directory**: A text box to specify the directory where output files will be saved.
   - **Source layout**: A text box to specify the source layout design file (e.g., PCB files).
   - **Mounting side**: A dropdown menu to select the mounting side (top or bottom) for the wave port.
   - **Import EDB**: A checkbox to enable or disable the import of EDB files for the layout.
   - **Theme toggle**: A button to switch between light and dark modes for the UI.
4. Select the desired options and click **Generate** to create the wave ports and the corresponding 3D component.


Command line
------------

The extension can also be used directly via the command line for batch processing.

Supported arguments include:

- **working_path**: The directory where output files are saved.
- **source_path**: The path to the source layout design file.
- **mounting_side**: The side to mount the wave port on ("top" or "bottom").
- **import_edb**: Boolean flag to enable or disable EDB import.
- **is_batch**: Boolean flag to enable batch mode (skip GUI).
- **is_test**: Boolean flag to enable or disable test mode.

Use the following syntax to run the extension:

.. toctree::
   :maxdepth: 2

   ../commandline
