"""

HFSS3DLayout Analysis
--------------------------------------------
This Example shows how to use HFSS3DLayout combined with EDB to interact with a layout
"""



import sys
import os
import pathlib
import shutil




from pyaedt import generate_unique_name
temp_folder = os.path.join(os.environ["TEMP"], generate_unique_name("Example"))
if not os.path.exists(temp_folder): os.makedirs(temp_folder)
print(temp_folder)
######################################
#Copying Example in Temp Folder


from pyaedt import Desktop
from pyaedt import Hfss3dLayout
from pyaedt import examples



targetfile=examples.download_aedb()
print(targetfile)
aedt_file = targetfile[:-12]+"aedt"



###############################################################################
# Initializing Desktop
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This examples will use version 2021.1

# This examples will use SI units.

desktopVersion = "2021.1"


###############################################################################
# NonGraphical
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Change Boolean to False to open AEDT in graphical mode
NonGraphical = True
NewThread = False

######################################
# Initializing Desktop
# Launching HFSS 3DLayout
# h3d object will contain also Edb Class query methods

d = Desktop(desktopVersion, NonGraphical, NewThread)
if os.path.exists(aedt_file): os.remove(aedt_file)
h3d=Hfss3dLayout(targetfile)
h3d.save_project(os.path.join(temp_folder,"edb_demo.aedt"))

######################################
# Print Setups from setups objects

h3d.setups[0].props

######################################
# Print Boundaries from setups objects


h3d.boundaries

######################################
# Hide all nets
######################################


h3d.modeler.primitives.change_net_visibility(visible=False)


######################################
# Show only 2 nets


h3d.modeler.primitives.change_net_visibility(["A0_GPIO", "A0_MUX"], visible=True)

######################################
# Show all layers
######################################
# Show all the layers


layers = h3d.modeler.layers.all_signal_layers
for lay in layers:
    layer=h3d.modeler.layers.layers[h3d.modeler.layers.layer_id(lay)]
    layer.IsVisible = True
    layer.update_stackup_layer()


######################################
# Change Layer Color

layer=h3d.modeler.layers.layers[h3d.modeler.layers.layer_id("TOP")]
layer.set_layer_color(0,255,0)
h3d.modeler.fit_all()

######################################

# Disable component visibility for TOP and BOTTOM
# update_stackup_layer will apply modification to layout

top = h3d.modeler.layers.layers[h3d.modeler.layers.layer_id("TOP")]
top.IsVisibleComponent = False
top.update_stackup_layer()

bot = h3d.modeler.layers.layers[h3d.modeler.layers.layer_id("BOTTOM")]
bot.IsVisibleComponent = False
bot.update_stackup_layer()

######################################

# Fit All to visualize all


h3d.modeler.fit_all()


######################################

# Enable and run the following command to close the desktop
h3d.close_project()

###############################################################################
# Close Desktop
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# After the simulaton is completed user can close the desktop or release it (using release_desktop method).
# All methods give possibility to save projects before exit

d.force_close_desktop()





