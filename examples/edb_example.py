"""

EDB  Analysis
--------------------------------------------
This Example shows how to use EDB co to interact with a layout
"""

import os
import sys
import pathlib
import glob
import shutil
local_path = os.path.abspath('')
module_path = pathlib.Path(local_path)
aedt_lib_path = module_path.parent.parent.parent
sys.path.append(os.path.join(aedt_lib_path))
import os
import time
from pyaedt import generate_unique_name, examples
temp_folder = os.path.join(os.environ["TEMP"], generate_unique_name("Example"))
example_path = examples.download_aedb()
targetfolder = os.path.join(temp_folder,'Galileo.aedb')
if os.path.exists(targetfolder):
    shutil.rmtree(targetfolder)
shutil.copytree(example_path[:-8], targetfolder)
targetfile=os.path.join(targetfolder)
print(targetfile)
aedt_file = targetfile[:-12]+"aedt"


#################################

from pyaedt import Edb

###############################################################################
# Launch Edb Class
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This examples will use Edb 2021.1

# This examples will use SI units.

if os.path.exists(aedt_file): os.remove(aedt_file)
edb = Edb(edbpath=targetfile)

#################################
# Compute Nets and Components
# there are queries for nets, stackup, layer, components, geometries

print("Nets {}".format(len(edb.core_nets.nets.keys())))
start = time.time()
print("Components {}".format(len(edb.core_components.components.keys())))
print("elapsed time = ", time.time() - start)

#################################
# Get Pin Position
# with next instructions user can get all pins for a specific component and get position of each of them
# every pin position will be a list of x, y postions

pins = edb.core_components.get_pin_from_component("U2")
for pin in pins:
    print(edb.core_components.get_pin_position(pin))


#################################
# Get all Nets connected to a specific Component

edb.core_components.get_component_net_connection_info("U2")

#################################
# Compute Rats

rats = edb.core_components.get_rats()

#################################
# Get all dc connected netlist through inductance
# Input needed are ground nets list. it will return all the list of nets connected to groun thorugh an inductor

GROUND_NETS = ["GND", "PGND"]
dc_connected_net_list = edb.core_nets.get_dcconnected_net_list(GROUND_NETS)
print(dc_connected_net_list)

#################################
# Get Power Tree based on a speficifi net

VRM = "U3A1"
OUTPUT_NET = "BST_V1P0_S0"
powertree_df, power_nets = edb.core_nets.get_powertree(OUTPUT_NET, GROUND_NETS)
for el in powertree_df:
    print(el)



#################################
# Delete all RLC with 1 pin only
# this method is useful to remove components not needed into the simulation


edb.core_components.delete_single_pin_rlc()

#################################
# Delete component
# User can still delete manually one or multiple components

edb.core_components.delete_component("C3B17")

#################################
# Delete one or more net
# User can still delete manually one or multiple net

edb.core_nets.delete_nets("A0_N")

#################################
# Save Modification

edb.save_edb()

#################################
# Close edb. After edb is closed it can be opened by AEDT


edb.close_edb()

#################################


