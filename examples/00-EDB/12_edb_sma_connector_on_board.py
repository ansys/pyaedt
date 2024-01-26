"""
# EDB: geometry creation

This example shows how to
1. Create a parameterized PCB with an SMA connector footprint for a single-ended
   SMA connector launch footprint..
22 Place 3D component on PCB.
3. Create HFSS setup and frequency sweep with a mesh operation.
4. Create return loss plot
"""
######################################################################
# ## The Finished Project
#
# <img src="_static\edb_example_12_sma_connector_on_board.png" width="450">

######################################################################
# ## Create parameterized PCB
#
# Import dependencies.

import os
import numpy as np
import pyaedt
import tempfile

###############################################################################
# Create the EDB.

ansys_version = "2023.2"
temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")
working_folder = temp_dir.name

aedb_path = os.path.join(working_folder, "pcb.aedb")
edb = pyaedt.Edb(edbpath=aedb_path, edbversion=ansys_version)
print("EDB is located at {}".format(aedb_path))

#####################
# Defne the FR4 dielectric for the PCB.

edb.materials.add_dielectric_material("ANSYS_FR4", 3.5, 0.005)

###############################################################################
# ## Create Stackup
#
# The stackup is defined explicitly here, but also can be imported
# from a from a csv or xml file using the method
# ``Edb.stackup.import_stackup()``.

edb.add_design_variable("$DIEL_T", "0.15mm")
edb.stackup.add_layer("BOT")
edb.stackup.add_layer("D5", "GND", layer_type="dielectric", thickness="$DIEL_T", material="ANSYS_FR4")
edb.stackup.add_layer("L5", "Diel", thickness="0.05mm")
edb.stackup.add_layer("D4", "GND", layer_type="dielectric", thickness="$DIEL_T", material="ANSYS_FR4")
edb.stackup.add_layer("L4", "Diel", thickness="0.05mm")
edb.stackup.add_layer("D3", "GND", layer_type="dielectric", thickness="$DIEL_T", material="ANSYS_FR4")
edb.stackup.add_layer("L3", "Diel", thickness="0.05mm")
edb.stackup.add_layer("D2", "GND", layer_type="dielectric", thickness="$DIEL_T", material="ANSYS_FR4")
edb.stackup.add_layer("L2", "Diel", thickness="0.05mm")
edb.stackup.add_layer("D1", "GND", layer_type="dielectric", thickness="$DIEL_T", material="ANSYS_FR4")
edb.stackup.add_layer("TOP", "Diel", thickness="0.05mm")

######################
# Create ground conductors.

edb.add_design_variable("PCB_W", "20mm")
edb.add_design_variable("PCB_L", "20mm")

gnd_dict = {}
for layer_name in edb.stackup.signal_layers.keys():
    gnd_dict[layer_name] = edb.modeler.create_rectangle(layer_name, "GND", [0, "PCB_W/-2"], ["PCB_L", "PCB_W/2"])

###############################################################################
# ## Create signal net
#
# Create signal net on layer 3, and add clearance to the ground plane.

edb.add_design_variable("SIG_L", "10mm")
edb.add_design_variable("SIG_W", "0.1mm")
edb.add_design_variable("SIG_C", "0.3mm")

signal_path = (["5mm", 0], ["SIG_L+5mm", 0])
signal_trace = edb.modeler.create_trace(signal_path, "L3", "SIG_W", "SIG", "Flat", "Flat")

signal_path = (["5mm", 0], ["PCB_L", 0])
clr = edb.modeler.create_trace(signal_path, "L3", "SIG_C*2+SIG_W", "SIG", "Flat", "Flat")
gnd_dict["L3"].add_void(clr)

####################
# ## Signal Vias
#
# Create via padstack definition. Place the signal vias.

edb.add_design_variable("SG_VIA_D", "1mm")
edb.add_design_variable("$VIA_AP_D", "1.2mm")
edb.padstacks.create("ANSYS_VIA", "0.3mm", "0.5mm", "$VIA_AP_D")
edb.padstacks.place(["5mm", 0], "ANSYS_VIA", "SIG")

######################################
# Create ground vias around the SMA
# connector launch footprint. The vas
# are placed around the circumference
# of the launch from 35 degrees to 325
# degrees.

for i in np.arange(30, 326, 35):
    px = np.cos(i / 180 * np.pi)
    py = np.sin(i / 180 * np.pi)
    edb.padstacks.place(["{}*{}+5mm".format("SG_VIA_D", px), "{}*{}".format("SG_VIA_D", py)], "ANSYS_VIA", "GND")

#######################################
# Create ground vias along signal trace.

for i in np.arange(2e-3, edb.variables["SIG_L"].value - 2e-3, 2e-3):
    edb.padstacks.place(["{}+5mm".format(i), "1mm"], "ANSYS_VIA", "GND")
    edb.padstacks.place(["{}+5mm".format(i), "-1mm"], "ANSYS_VIA", "GND")

###################################################
# Create a wave port at the end of the signal trace.

signal_trace.create_edge_port("port_1", "End", "Wave", horizontal_extent_factor=10)

###############################################################################
# ## HFSS Simulation Setup
#
# The named argument ``max_num_passes`` sets an upper limit on the
# number of adaptive passes for mesh refinement.
#
# For broadband applications when the simulation results may be used
# to generate a SPICE model, the outer domain boundary can be
# located roughly $$ d=\lambda/8 $$ from the internal structures
# in the model.

extend_domain = 3E11/5E9/8.0  # Quarter wavelength at 4 GHz.
edb.design_options.antipads_always_on = True
edb.hfss.hfss_extent_info.air_box_horizontal_extent = extend_domain
edb.hfss.hfss_extent_info.air_box_positive_vertical_extent = extend_domain
edb.hfss.hfss_extent_info.air_box_negative_vertical_extent = extend_domain

setup = edb.create_hfss_setup("Setup1")
setup.set_solution_single_frequency("5GHz", max_num_passes=8, max_delta_s="0.02")
setup.hfss_solver_settings.order_basis = "first"

#############################
# Add a mesh operation to the setup.

edb.setups["Setup1"].add_length_mesh_operation({"SIG": ["L3"]}, "m1", max_length="0.1mm")

##############################
# Add frequency sweep to setup.
#
# When the simulation results will
# be used for transient SPICE analysis, it is advisible
# to use the following strategy.
#
# - DC point
# - Logarithmic sweep from 1 kHz to 100 MHz
# - Linear scale for higher frequencies.

setup.add_frequency_sweep(
    "Sweep1",
    frequency_sweep=[
        ["linear count", "0", "1KHz", 1],
        ["log scale", "1KHz", "100MHz", 10],
        ["linear scale", "0.1GHz", "5GHz", "0.1GHz"],
    ],
)

####################
# Save and close EDB.

edb.save_edb()
edb.close_edb()

#####################
# Launch Hfss3dLayout.

h3d = pyaedt.Hfss3dLayout(aedb_path, specified_version=ansys_version, new_desktop_session=True)

####################
# Place a 3D component.

full_comp_name = pyaedt.downloads.download_file("component_3d",
                                                filename="SMA_RF_SURFACE_MOUNT.a3dcomp",
                                                destination=working_folder)
comp = h3d.modeler.place_3d_component(
    component_path=full_comp_name, number_of_terminals=1, 
    placement_layer="TOP", component_name="my_connector", 
    pos_x="5mm", pos_y=0.000)

###############################################################################
# ## Run Simulation

h3d.analyze(num_cores=4)

#########################
# Visualize the return loss.
h3d.post.create_report("dB(S(port_1, port_1))")

############################
# Save and close the project.
h3d.save_project()
print("Project is saved to {}".format(h3d.project_path))
h3d.release_desktop(True, True)

###############################################################################
# Clean up the temporary folder.

temp_dir.cleanup()
