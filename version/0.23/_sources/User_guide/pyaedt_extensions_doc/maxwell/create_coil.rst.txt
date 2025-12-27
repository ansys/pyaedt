Create coil design geometries
=============================

This extension aims to create vertical or flat coil geometries in Maxwell 3D using specific parameters.
It supports more complex shapes than simple cylinders because it allows the segmentation of the coil profile as well as
the segmentation of corners.
The segmentation features are designed to optimize AEDT meshing operations.

You can access the extension from the icon created on the **Automation** tab using the Extension Manager.

The following image shows the extension user interface:

.. image:: ../../../_static/extensions/create_coil.png
   :width: 600
   :alt: Create coil UI

The user can select the coil type by checking the **Vertical Coil** checkbox, define the coil parameters that are common
to both types, and then define the parameters that are specific to each type. Depending on the coil type (checkbox),
some entries are enabled or disabled.

Finally, with one simple button click, the user can create the coil geometry in AEDT.

You can also launch the extension user interface from the terminal. An example can be found here:


.. toctree::
   :maxdepth: 2

   ../commandline