"""

EDB  Analysis
--------------------------------------------
This Example shows how to use EDB co to interact with a layout
"""
# sphinx_gallery_thumbnail_path = 'Resources/edb.png'

import shutil

import os
import time
from pyaedt import generate_unique_name, examples

if os.name == "posix":
    tmpfold = os.environ["TMPDIR"]
else:
    tmpfold = os.environ["TEMP"]

temp_folder = os.path.join(tmpfold, generate_unique_name("Example"))
if not os.path.exists(temp_folder): os.makedirs(temp_folder)
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
# Get the stackup limits, top and bottom layers and elevations

print(edb.core_stackup.stackup_limits())

#################################
# Create a new Coaxial port for HFSS Simulation
edb.core_hfss.create_coax_port_on_component("U2A5", "V1P0_S0")

#################################
# Edit stackup and material
# User can change stackup properties with assignment
# Materials can be created and assigned to layers


edb.core_stackup.stackup_layers.layers['TOP'].thickness = "75um"
edb.core_stackup.create_debye_material("My_Debye", 5, 3, 0.02, 0.05, 1e5, 1e9)
edb.core_stackup.stackup_layers.layers['UNNAMED_002'].material_name = "My_Debye"


#################################
# Create a new Circuit Port for Siwave Simulation
edb.core_siwave.create_circuit_port("U2A5", "DDR3_DM0")


edb.core_siwave.add_siwave_ac_analysis()

edb.core_siwave.add_siwave_dc_analysis()



#################################
# Save Modification

edb.save_edb()

#################################
# Close edb. After edb is closed it can be opened by AEDT


edb.close_edb()

#################################


