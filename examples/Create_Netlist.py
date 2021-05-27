"""

Netlist Example Analysis
--------------------------------------------
# This Example shows how to Import Netlist in AEDT Nexxim
Netlists supported are HSPICE (and partially Mentor)
"""



import sys
import os
import pathlib

#########################################################
#Import Packages
#Setup The local path to the Path Containing AEDTLIb


local_path = os.path.abspath('')
module_path = pathlib.Path(local_path)
aedt_lib_path = module_path.parent.parent.parent
from pyaedt import examples
netlist = examples.download_netlist()
sys.path.append(os.path.join(aedt_lib_path))
from pyaedt import generate_unique_name
temp_folder = os.path.join(os.environ["TEMP"], generate_unique_name("Example"))
if not os.path.exists(temp_folder): os.makedirs(temp_folder)
print(temp_folder)


#########################################################
# This command add AEDTLib Path to the path list to allow usage of AEDTLib



myfile = os.path.join(netlist)

#########################################################
# initializing Netlist full path. Can be changed



from pyaedt import Circuit
from pyaedt import Desktop

#########################################################
# Import of Main Classes needed: Desktop and Circuit



desktopVersion = "2021.1"
NonGraphical = False
NewThread = False

#########################################################
# Initializing version of Desktop and Graphical Options



desktop = Desktop(desktopVersion, NonGraphical, NewThread)

#########################################################
# Launching Desktop



aedtapp = Circuit()

#########################################################
# Launching Circuit. An empty circuit will be created



aedtapp.save_project(os.path.join(temp_folder, "my_firt_netlist.aedt"))

#########################################################
# Save Project to temp folder. Can be changed



aedtapp["Voltage"]="5"



aedtapp.create_schematic_from_netlist(myfile)

#########################################################
# Launch command to create Schematic



aedtapp.close_project()

#########################################################
# Close Project....or continue adding functionalities



desktop.force_close_desktop()

#########################################################





