"""
EDB: Siwave analysis from EDB setup
-----------------------------------
Use EDB to interact with a layout.
"""

import shutil

import os
import time
import tempfile
from pyaedt import generate_unique_name, examples

tmpfold = tempfile.gettempdir()
temp_folder = os.path.join(tmpfold, generate_unique_name("Example"))
if not os.path.exists(temp_folder):
    os.makedirs(temp_folder)
example_path = examples.download_aedb()
targetfolder = os.path.join(temp_folder, "Galileo.aedb")
if os.path.exists(targetfolder):
    shutil.rmtree(targetfolder)
shutil.copytree(example_path[:-8], targetfolder)
targetfile = os.path.join(targetfolder)
siwave_file = os.path.join(temp_folder, "Galileo.siw")
print(targetfile)
aedt_file = targetfile[:-4] + "aedt"


###############################################################################

from pyaedt import Edb

###############################################################################
# Launch EDB
# ~~~~~~~~~~
# Launch the :class:`pyaedt.Edb` class, using EDB 2022 R2 and SI units.

if os.path.exists(aedt_file):
    os.remove(aedt_file)
edb = Edb(edbpath=targetfile, edbversion="2022.2")

###############################################################################
# Compute nets and components
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Computes nets and components.
# There are queries for nets, stackups, layers, components, and geometries.

print("Nets {}".format(len(edb.core_nets.nets.keys())))
start = time.time()
print("Components {}".format(len(edb.core_components.components.keys())))
print("elapsed time = ", time.time() - start)

###############################################################################
# Get pin position
# ~~~~~~~~~~~~~~~~
# Get the position for a specific pin.
# The next section shows how to get all pins for a specific component and
# the positions of each of them.
# Each pin is a list of ``[X, Y]`` coordinate positions.

pins = edb.core_components.get_pin_from_component("U2")
for pin in pins:
    print(edb.core_components.get_pin_position(pin))

###############################################################################
# Get all nets connected to a component
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Get all nets connected to a specific component.

edb.core_components.get_component_net_connection_info("U2")

###############################################################################
# Compute rats
# ~~~~~~~~~~~~
# Computes rats.

rats = edb.core_components.get_rats()

###############################################################################
# Get all DC-connected net lists through inductance
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Get all DC-connected net lists through inductance.
# The inputs needed are ground net lists. The returned list is of all nets
# connected to a ground through an inductor.

GROUND_NETS = ["GND", "PGND"]
dc_connected_net_list = edb.core_nets.get_dcconnected_net_list(GROUND_NETS)
print(dc_connected_net_list)

###############################################################################
# Get power tree based on a specific net
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Get the power tree based on a specific net.

VRM = "U3A1"
OUTPUT_NET = "BST_V1P0_S0"
powertree_df, component_list_columns, net_group = edb.core_nets.get_powertree(OUTPUT_NET, GROUND_NETS)
for el in powertree_df:
    print(el)

###############################################################################
# Delete all RLCs with only one pin
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Delete all RLCs with only one pin. This method provides a useful way of
# removing components not needed in the simulation.

edb.core_components.delete_single_pin_rlc()

###############################################################################
# Delete components
# ~~~~~~~~~~~~~~~~~
# Delete manually one or more components.

edb.core_components.delete_component("C3B17")

###############################################################################
# Delete nets
# ~~~~~~~~~~~
# Delete manually one or more nets.

edb.core_nets.delete_nets("A0_N")

###############################################################################
# Get stackup limits
# ~~~~~~~~~~~~~~~~~~
# Get the stackup limits, top and bottom layers, and elevations.

print(edb.core_stackup.stackup_limits())

###############################################################################
# Create coaxial port
# ~~~~~~~~~~~~~~~~~~~
# Create a coaxial port for the HFSS simulation.

edb.core_hfss.create_coax_port_on_component("U2A5", "V1P0_S0")

###############################################################################
# Edit stackup and material
# ~~~~~~~~~~~~~~~~~~~~~~~~~
# Edit the stackup and the material. You can change stackup
# properties with assignment and create materials and assign to layers.

edb.core_stackup.stackup_layers.layers["TOP"].thickness = "75um"
# edb.core_stackup.stackup_layers.layers["Diel1"].material_name = "Fr4_epoxy"
edb.core_stackup.create_debye_material("My_Debye", 5, 3, 0.02, 0.05, 1e5, 1e9)
# edb.core_stackup.stackup_layers.layers['BOTTOM'].material_name = "My_Debye"
# edb.core_stackup.stackup_layers.remove_layer("Signal3")
# edb.core_stackup.stackup_layers.remove_layer("Signal1")


###############################################################################
# Create voltage source and Siwave DCIR analysis
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a voltage source and then set up a DCIR analysis.

edb.core_siwave.create_voltage_source_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 3.3, 0, "V1")
edb.core_siwave.create_current_source_on_net("U1B5", "V1P5_S3", "U1B5", "GND", 1.0, 0, "I1")
settings = edb.core_siwave.get_siwave_dc_setup_template()
settings.accuracy_level = 0
settings.use_dc_custom_settings = True
settings.name = "myDCIR_4"
# settings.pos_term_to_ground = "I1"
settings.neg_term_to_ground = "V1"
edb.core_siwave.add_siwave_dc_analysis(settings)

###############################################################################
# Save modifications
# ~~~~~~~~~~~~~~~~~~
# Save modifications.

edb.save_edb()
edb.core_nets.plot(None, "TOP")

edb.solve_siwave()

###############################################################################
# Close EDB
# ~~~~~~~~~
# Closes EDB. After EDB is closed, it can be opened by AEDT.

edb.close_edb()

###############################################################################
# Postprocess in Siwave
# ~~~~~~~~~~~~~~~~~~~~~
# Open Siwave and generate a report. This works on Window only.

# from pyaedt import Siwave
# siwave = Siwave("2022.2")
# siwave.open_project(siwave_file)
# report_file = os.path.join(temp_folder,'Galileo.htm')
#
# siwave.export_siwave_report("myDCIR_4", report_file)
# siwave.close_project()
# siwave.quit_application()
