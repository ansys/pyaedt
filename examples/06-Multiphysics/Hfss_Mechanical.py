"""
Multiphysics Simulation
---------------------------
This example shows how to use Pyaedt to create a multiphysics workflow that includes Circuit, Hfss and Mechanical.
"""
# sphinx_gallery_thumbnail_path = 'Resources/Mechanical.png'

###############################################################################
# Import packages
# ~~~~~~~~~~~~~~~
# Import needed packages.
import tempfile
import os
import shutil

from pyaedt import examples, generate_unique_name
from pyaedt import Hfss, Circuit, Mechanical


###############################################################################
# Open Project
# ~~~~~~~~~~~~
# Download Project, opens it and save to TEMP Folder.
project_full_name = examples.download_via_wizard()
tmpfold = tempfile.gettempdir()
temp_folder = os.path.join(tmpfold, generate_unique_name("Example"))
project_temp_name = os.path.join(temp_folder, "via_wizard.aedt")
if not os.path.exists(temp_folder):
    os.makedirs(temp_folder)
shutil.copy2(project_full_name, project_temp_name)


###############################################################################
# Starts HFSS
# ~~~~~~~~~~~
# Starts Hfss and initialize the Pyaedt object.

version = "2021.2"
hfss = Hfss(project_temp_name, specified_version=version)
pin_names = hfss.modeler.get_excitations_name()


###############################################################################
# Starts Circuit
# ~~~~~~~~~~~~~~
# Starts Circuit and add Hfss dynamic link component to it.

circuit = Circuit()
hfss_comp = circuit.modeler.schematic.add_subcircuit_hfss_link("MyHfss", pin_names, hfss.project_file,
                                                                              hfss.design_name)

###############################################################################
# Dynamic Link Options
# ~~~~~~~~~~~~~~~~~~~~
# Setup Dynamic Link Options
# argument of set_sim_option_on_hfss_subcircuit can be the component name, the component id or
# the component object.

circuit.modeler.schematic.refresh_dynamic_link("MyHfss")
circuit.modeler.schematic.set_sim_option_on_hfss_subcircuit(hfss_comp)
hfss_setup_name = hfss.setups[0].name + " : " + hfss.setups[0].sweeps[0].name
circuit.modeler.schematic.set_sim_solution_on_hfss_subcircuit(hfss_comp.composed_name, hfss_setup_name)

###############################################################################
# Create Ports and Excitations
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Find Component pins locations adnd place interface port on it. Defines
# Voltage source on input port.


circuit.modeler.schematic.create_interface_port("Excitation_1",
                                                 [hfss_comp.pins[0].location[0], hfss_comp.pins[0].location[1]])
circuit.modeler.schematic.create_interface_port("Excitation_2",
                                                 [hfss_comp.pins[1].location[0], hfss_comp.pins[1].location[1]])
circuit.modeler.schematic.create_interface_port("Port_1",
                                                 [hfss_comp.pins[2].location[0], hfss_comp.pins[2].location[1]])
circuit.modeler.schematic.create_interface_port("Port_2",
                                                 [hfss_comp.pins[3].location[0], hfss_comp.pins[3].location[1]])

voltage = 1
phase = 0
excitation_settings = [str(voltage) + " V", str(phase) + " deg", "0V", "0V", "0V", "1GHz", "0s", "0", "0deg", "0Hz"]
ports_list = ["Excitation_1", "Excitation_2"]
circuit.assign_voltage_sinusoidal_excitation_to_ports(ports_list, excitation_settings)

###############################################################################
# Setup
# ~~~~~
# Define Simulation Setup

setup_name = "MySetup"
LNA_setup = circuit.create_setup(setupname=setup_name)
bw_start = 4.3
bw_stop = 4.4
n_points = 1001
unit = "GHz"
sweep_list = ["LINC", str(bw_start) + unit, str(bw_stop) + unit, str(n_points)]
LNA_setup.props["SweepDefinition"]["Data"] = " ".join(sweep_list)
LNA_setup.update()

###############################################################################
# Solve and Push Excitation
# ~~~~~~~~~~~~~~~~~~~~~~~~~
# Solve Circuit and Push Excitations to Hfss model to get right value of losses.

circuit.analyze_nominal()

circuit.push_excitations(instance_name="S1", setup_name=setup_name)


###############################################################################
# Starts Mechanical
# ~~~~~~~~~~~~~~~~~
# Starts Mechanical and copy bodies from Hfss Project.


mech = Mechanical()
mech.copy_solid_bodies_from(hfss)


###############################################################################
# Boundaries and Excitations
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Get losses from Hfss and assign Convection to Mechanical.


mech.assign_em_losses(hfss.design_name, hfss.setups[0].name, "LastAdaptive", hfss.setups[0].props["Frequency"],
                      surface_objects=hfss.get_all_conductors_names())
diels = ["1_pd", "2_pd", "3_pd", "4_pd", "5_pd"]
for el in diels:
    mech.assign_uniform_convection([mech.modeler.primitives[el].top_face_y, mech.modeler.primitives[el].bottom_face_y],
                                   3)

###############################################################################
# Solution
# ~~~~~~~~
# Solve and Plot Thermal results
mech.create_setup()
mech.save_project()
mech.analyze_nominal()
surfaces = []
for name in mech.get_all_conductors_names():
    surfaces.extend(mech.modeler.primitives.get_object_faces(name))
mech.post.create_fieldplot_surface(surfaces, "Temperature")


###############################################################################
# Exit
# ~~~~
# Release Desktop and Exit.


mech.release_desktop(True, True)
