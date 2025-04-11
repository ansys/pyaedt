Transformer loss distribution
=============================

With this extension you can export transformer loss distribution to generic formats such as .csv, .tab or .npy.

You can access the extension from the icon created on the **Automation** tab using the Extension Manager.

The following image shows the extension user interface:

.. image:: ../../../_static/extensions/transformer_loss_distribution.png
  :width: 800
  :alt: Transformer Loss Distribution UI

You can export ohmic loss distribution or surface force density on a specific object surface or
on surfaces of multiple objects.

If a sample points file (.pts) is not provided, the field values are automatically computed on mesh nodes.

With the button "Preview" you can visualize the field distribution on the selected object surface with pyvista.

You can also launch the extension user interface from the terminal. An example can be found here:


.. toctree::
   :maxdepth: 2

   ../commandline