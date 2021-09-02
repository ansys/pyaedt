"""
HFSS 3D Layout Analysis
-----------------------
This example shows how to use HFSS 3D Layout combined with EDB to interact with a layout.
"""
# sphinx_gallery_thumbnail_path = 'Resources/edb2.png'


import os

from pyaedt import generate_unique_name

if os.name == "posix":
    tmpfold = os.environ["TMPDIR"]
else:
    tmpfold = os.environ["TEMP"]

temp_folder = os.path.join(tmpfold, generate_unique_name("Example"))
if not os.path.exists(temp_folder): os.makedirs(temp_folder)
print(temp_folder)

###############################################################################
# Copy an Example in the Temp Folder
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This exammple copies an example in the temp folder.

from pyaedt import Desktop
from pyaedt import Hfss3dLayout
from pyaedt import examples


targetfile=examples.download_aedb()
print(targetfile)
aedt_file = targetfile[:-12]+"aedt"


###############################################################################
# Launch AEDT
# ~~~~~~~~~~~
# This example launches AEDT 2021.1 in graphical model.

# This example uses SI units.

desktopVersion = "2021.1"


###############################################################################
# Launch AEDT in Non-Graphical Mode
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Change the Boolean parameter ``NonGraphical`` to ``False`` to launch AEDT in
# graphical mode.

NonGraphical = True
NewThread = False

###############################################################################
# Initialize AEDT
# ~~~~~~~~~~~~~~~
# Launch HFSS 3D Layout.
# The `h3d` object will contain the :class: `pyaedt.Edb` class query methods.

d = Desktop(desktopVersion, NonGraphical, NewThread)
if os.path.exists(aedt_file): os.remove(aedt_file)
h3d = Hfss3dLayout(targetfile)
h3d.save_project(os.path.join(temp_folder,"edb_demo.aedt"))

###############################################################################
# Print Setups
# ~~~~~~~~~~~~
# The example prints setups from the `setups` object.

h3d.setups[0].props

###############################################################################
# Print boundaries from the `setups` object.

h3d.boundaries

###############################################################################
# Hide All Nets
# ~~~~~~~~~~~~~
# This example hides all nets.

h3d.modeler.primitives.change_net_visibility(visible=False)

###############################################################################
# Show Only Two Nets
# ~~~~~~~~~~~~~~~~~~
# This examples shows only the two specified nets.

h3d.modeler.primitives.change_net_visibility(["A0_GPIO", "A0_MUX"], visible=True)

###############################################################################
# Show All Layers
# ~~~~~~~~~~~~~~~
# This example shows all layers.

layers = h3d.modeler.layers.all_signal_layers
for lay in layers:
    layer = h3d.modeler.layers.layers[h3d.modeler.layers.layer_id(lay)]
    layer.IsVisible = True
    layer.update_stackup_layer()

###############################################################################
# Change the Layer Color
# ~~~~~~~~~~~~~~~~~~~~~~
# This examples changes the layer color.

layer = h3d.modeler.layers.layers[h3d.modeler.layers.layer_id("TOP")]
layer.set_layer_color(0,255,0)
h3d.modeler.fit_all()

###############################################################################
# Disable Component Visibility
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The example disable component visibility for ``"TOP"`` and ``"BOTTOM"``.
# The :func:`pyaedt.modules.LayerStackup.Layer.update_stackup_layer` method
# will apply modifications to the layout.

top = h3d.modeler.layers.layers[h3d.modeler.layers.layer_id("TOP")]
top.IsVisibleComponent = False
top.update_stackup_layer()

bot = h3d.modeler.layers.layers[h3d.modeler.layers.layer_id("BOTTOM")]
bot.IsVisibleComponent = False
bot.update_stackup_layer()

###############################################################################

# Fit All
# ~~~~~~~
# This method fits all so that you can visualize all.

h3d.modeler.fit_all()

###############################################################################
# Close AEDT
# ~~~~~~~~~~
# After the simulaton is completed, you can close AEDT or release it using the
# :func:`pyaedt.Desktop.release_desktop` method.
# All methods provide for saving the project before exiting.

if os.name != "posix":
    h3d.close_project()
    d.force_close_desktop()
