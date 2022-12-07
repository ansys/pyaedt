"""
EDB: Siwave analysis from EDB setup
-----------------------------------
This example shows how you can use EDB to interact with a layout.
"""
###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports.

import shutil

import os
import time
from pyaedt import examples, generate_unique_folder_name

temp_folder = generate_unique_folder_name()
example_path = examples.download_aedb(temp_folder)

targetfile = os.path.dirname(example_path)

siwave_file = os.path.join(os.path.dirname(targetfile), "Galileo.siw")
print(targetfile)
aedt_file = targetfile[:-4] + "aedt"

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
# The inputs needed are ground net lists. The returned list contains all nets
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
# Get the stackup limits (top and bottom layers and elevations).

print(edb.core_stackup.stackup_limits())

###############################################################################
# Create coaxial port
# ~~~~~~~~~~~~~~~~~~~
# Create a coaxial port for the HFSS simulation.

edb.core_hfss.create_coax_port_on_component("U2A5", "V1P0_S0")

###############################################################################
# Edit stackup layers and material
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Edit the stackup layers and material. You can change stackup layer
# properties with assignment and create materials and assign them to layers.

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
setup = edb.core_siwave.add_siwave_dc_analysis("myDCIR_4")
setup.use_dc_custom_settings = True
setup.dc_slider_position = 0
setup.add_source_terminal_to_ground("V1", 1)



###############################################################################
# Save modifications
# ~~~~~~~~~~~~~~~~~~
# Save modifications.

edb.save_edb()
edb.core_nets.plot(None, "TOP")

siw_file = edb.solve_siwave()

###############################################################################
# Export Siwave Reports
# ~~~~~~~~~~~~~~~~~~~~~
# Export all DC Reports quantities.
outputs = edb.export_siwave_dc_results(siw_file, setup.name, )

###############################################################################
# Close EDB
# ~~~~~~~~~
# Close EDB. After EDB is closed, it can be opened by AEDT.

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
