"""

HFSS3DLayout  Analysis
--------------------------------------------
This Example shows how to use HFSS3DLayout combined with EDB to interact with a layout
"""



import sys
import os
import pathlib
import shutil



local_path = os.path.abspath('')
module_path = pathlib.Path(local_path)
aedt_lib_path = module_path.parent.parent
sys.path.append(os.path.join(aedt_lib_path))
from pyaedt import generate_unique_name
temp_folder = os.path.join(os.environ["TEMP"], generate_unique_name("Example"))
if not os.path.exists(temp_folder): os.makedirs(temp_folder)
print(temp_folder)
######################################
#Copying Example in Temp Folder


from pyaedt import Desktop
from pyaedt import Hfss3dLayout
from pyaedt import examples
from pyaedt.generic.general_methods import generate_unique_name



targetfile=examples.download_aedb()
print(targetfile)

######################################
# Initializing Desktop
# Launching HFSS 3DLayout



d = Desktop("2021.1")
h3d=Hfss3dLayout(targetfile)
h3d.save_project(os.path.join(temp_folder,"edb_demo.aedt"))

######################################
# Disable visibility for all Nets
# Check Setups from setups objects


h3d.setups[0].props

######################################
# Check Boundaries from setups objects


h3d.boundaries

######################################
# Hide all nets
######################################

# Enable Visibility for few nets


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
h3d.modeler.model_units

######################################

# Disable component visibility for TOP and BOTTOM
# update_stackup_layer will apply modification to layout

######################################
# Disable component visibility for TOP and BOTTOM
# update_stackup_layer will apply modification to layout

#%%

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
d.force_close_desktop()





