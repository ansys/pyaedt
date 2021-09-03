"""
EDB  Analysis
-------------
This example shows how to use EDB to interact with a layout.
"""
# sphinx_gallery_thumbnail_path = 'Resources/edb.png'

import shutil

import os
import time
from pyaedt import generate_unique_name, examples
try:
    if os.name == "posix":
        tmpfold = os.environ["TMPDIR"]
    else:
        tmpfold = os.environ["TEMP"]
except:
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
aedt_file = targetfile[:-4] + "aedt"


###############################################################################

from pyaedt import Edb

###############################################################################
# Launch EDB
# ~~~~~~~~~~
# This example launches the :class: `pyaedt.Edb` class.
# This example uses EDB 2021.1 and uses SI units.

if os.path.exists(aedt_file): os.remove(aedt_file)
edb = Edb(edbpath=targetfile, edbversion="2021.1")

###############################################################################
# Compute Nets and Components
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example computes nets and components.
# There are queries for nets, stackups, layers, components, and geometries.

print("Nets {}".format(len(edb.core_nets.nets.keys())))
start = time.time()
print("Components {}".format(len(edb.core_components.components.keys())))
print("elapsed time = ", time.time() - start)

###############################################################################
# Get Pin Position
# ~~~~~~~~~~~~~~~~
# This example gets the position for a specific pin.
# The next example shows how to get all pins for a specific component and get
# the positions of each of them.
# Each pin is a list of ``[X, Y]`` coordinate postions.

pins = edb.core_components.get_pin_from_component("U2")
for pin in pins:
    print(edb.core_components.get_pin_position(pin))

###############################################################################
# Get All Nets Connected to a Component
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example get all nets connected to a specific component.

edb.core_components.get_component_net_connection_info("U2")

###############################################################################
# Compute Rats
# ~~~~~~~~~~~~
# This comman computes rats.

rats = edb.core_components.get_rats()

###############################################################################
# Get All DC-Connected Net Lists Through Inductance
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example gets all DC-connected net lists through inductance.
# The inputs needed are ground net lists. A list of all nets
# connected to a ground through an inductor is returned.

GROUND_NETS = ["GND", "PGND"]
dc_connected_net_list = edb.core_nets.get_dcconnected_net_list(GROUND_NETS)
print(dc_connected_net_list)

###############################################################################
# Get the Power Tree Based on a Specific Net
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example gets the power tree based on a specific net.

VRM = "U3A1"
OUTPUT_NET = "BST_V1P0_S0"
powertree_df, component_list_columns, net_group = edb.core_nets.get_powertree(
    OUTPUT_NET, GROUND_NETS)
for el in powertree_df:
    print(el)

###############################################################################
# Delete all RLCs with Only One Pin
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This command deletes all RLCs with only one pin, providing a useful way of
# removing components not needed in the simulation.

edb.core_components.delete_single_pin_rlc()

###############################################################################
# Delete a Component
# ~~~~~~~~~~~~~~~~~~
# This command can be used to manually delete one or more components.

edb.core_components.delete_component("C3B17")

###############################################################################
# Delete a Net
# ~~~~~~~~~~~~
# This command can be used to manually delete one or more nets.

edb.core_nets.delete_nets("A0_N")

###############################################################################
# Get Stackup Limits
# ~~~~~~~~~~~~~~~~~~
# This command gets the stackup limits, top and bottom layers, and elevations.

print(edb.core_stackup.stackup_limits())

###############################################################################
# Create a Coaxial Port
# ~~~~~~~~~~~~~~~~~~~~~
# This command creates a coaxial port for the HFSS simulation.

edb.core_hfss.create_coax_port_on_component("U2A5", "V1P0_S0")

###############################################################################
# Edit the Stackup and Material
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# THis example edits the stackup and the material. You can change stackup
# properties with assignment. Materials can be created and assigned to layers.

edb.core_stackup.stackup_layers.layers['TOP'].thickness = "75um"
edb.core_stackup.create_debye_material("My_Debye", 5, 3, 0.02, 0.05, 1e5, 1e9)
edb.core_stackup.stackup_layers.layers['UNNAMED_002'].material_name = "My_Debye"

###############################################################################
# Create a Circuit Port for SIwave Simulation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example creates a circuit port for SIwave simulation.

edb.core_siwave.create_circuit_port_on_net("U2A5", "DDR3_DM0")

edb.core_siwave.add_siwave_ac_analysis()

###############################################################################
# Create a Voltage Source and Siwave DC IR Simulation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example creates a Voltage Source and then setup a DCIR Analysis.

edb.core_siwave.create_voltage_source_on_net("U2A5","V1P5_S3","U2A5","GND",3.3,0,"V1")
settings = edb.core_siwave.get_siwave_dc_setup_template()
settings.accuracy_level = 0
settings.use_dc_custom_settings  = True
settings.name = "myDCIR_4"
# settings.pos_term_to_ground = "I1"
settings.neg_term_to_ground = "V1"
edb.core_siwave.add_siwave_dc_analysis(settings)

###############################################################################
# Save Modifications
# ~~~~~~~~~~~~~~~~~~
# This command saves modifications.

edb.save_edb()

###############################################################################
# Close EDB
# ~~~~~~~~~
# This command closes EDB.
# After EDB is closed, it can be opened by AEDT.

edb.close_edb()
