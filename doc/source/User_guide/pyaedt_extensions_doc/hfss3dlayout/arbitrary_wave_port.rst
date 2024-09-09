Parametrize Layout
==================

This extension is used to generate arbitrary wave ports.

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

The extension is accessible through the icon created by the Extension Manager in the **Automation** tab.

The available arguments are: ``working_path``, ``source_path``, ``mounting_side``.

``working_path`` and ``source_path`` define the working path and ECAD project path.
``mounting_side`` defines the port orientation in the layout.

The extension user interface can also be launched from the terminal. An example can be found here:


.. toctree::
   :maxdepth: 2

   ../commandline
