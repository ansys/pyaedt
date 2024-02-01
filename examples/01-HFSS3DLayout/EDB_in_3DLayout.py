# # HFSS 3D Layout: PCB and EDB in 3D layout
#
# This example shows how you can use HFSS 3D Layout combined with EDB to
# interact with a 3D layout.

import os
import tempfile
import pyaedt

temp_dir = tempfile.TemporaryDirectory(suffx=".ansys")
project_folder = os.path.join(temp_dir.name, "Example")
if not os.path.exists(project_folder):
    os.makedirs(project_folder)
print(project_folder)

# Copy an example into the temporary project folder.

targetfile = pyaedt.downloads.download_aedb()
print(targetfile)
aedt_file = targetfile[:-12] + "aedt"

# Set ``non_graphical`` to ``True`` in order to run in non-graphical mode.
# The example is currently set up to run in graphical mode.

non_graphical = False
NewThread = True

# Launch AEDT 2023R2 in graphical mode. Units are SI.

desktopVersion = "2023.2"

# ## Initialize AEDT and launch HFSS 3D Layout
#
# Initialize AEDT and launch HFSS 3D Layout.
# The ``h3d`` object contains the `pyaedt.Edb` class query methods.

d = pyaedt.launch_desktop(desktopVersion, non_graphical, NewThread)
if os.path.exists(aedt_file):
    os.remove(aedt_file)
h3d = pyaedt.Hfss3dLayout(targetfile)
h3d.save_project(os.path.join(project_folder, "edb_demo.aedt"))

# ## Print boundaries
#
# Print boundaries from the ``setups`` object.

h3d.boundaries

# Hide all nets.

h3d.modeler.change_net_visibility(visible=False)

# Show only two specified nets.

h3d.modeler.change_net_visibility(["A0_GPIO", "A0_MUX"], visible=True)
edb = h3d.modeler.edb
edb.nets.plot(["A0_GPIO", "A0_MUX"])

# Show all layers.

for layer in h3d.modeler.layers.all_signal_layers:
    layer.is_visible = True

# Change the layer color.

layer = h3d.modeler.layers.layers[h3d.modeler.layers.layer_id("TOP")]
layer.set_layer_color(0, 255, 0)
h3d.modeler.fit_all()

# ## Disable component visibility
#
# Disable component visibility for ``"TOP"`` and ``"BOTTOM"`` layers.
# The `pyaedt.modules.LayerStackup.Layer.update_stackup_layer` method
# applies modifications to the layout.

top = h3d.modeler.layers.layers[h3d.modeler.layers.layer_id("TOP")]
top.is_visible_component = False

bot = h3d.modeler.layers.layers[h3d.modeler.layers.layer_id("BOTTOM")]
bot.is_visible_component = False

# ## Display the Layout
#
# Fit all so that you can visualize all.

h3d.modeler.fit_all()

# ## Close AEDT
#
# After the simulation completes, you can close AEDT or release it using the
# `pyaedt.Desktop.release_desktop` method.
# All methods provide for saving the project before closing.

h3d.close_project()
d.release_desktop()

# Clean up the temporary directory and remove all files.

temp_dir.cleanup()
