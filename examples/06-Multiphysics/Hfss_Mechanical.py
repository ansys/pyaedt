"""
Multiphysics: HFSS-Mechanical multiphysics analysis
---------------------------------------------------
This example shows how to use PyAEDT to create a multiphysics workflow that includes Circuit, HFSS, and Mechanical.
"""

###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports.

import tempfile
import os
import shutil

from pyaedt import examples, generate_unique_name
from pyaedt import Hfss, Circuit, Mechanical


##########################################################
# Set non-graphical mode
# ~~~~~~~~~~~~~~~~~~~~~~
# Set non-graphical mode. The default is ``False``.

non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")

###############################################################################
# Download and open project
# ~~~~~~~~~~~~~~~~~~~~~~~~~
# Download and open the project. Save it to the temporary folder.

project_full_name = examples.download_via_wizard()
tmpfold = tempfile.gettempdir()
temp_folder = os.path.join(tmpfold, generate_unique_name("Example"))
project_temp_name = os.path.join(temp_folder, "via_wizard.aedt")
if not os.path.exists(temp_folder):
    os.makedirs(temp_folder)
shutil.copy2(project_full_name, project_temp_name)


###############################################################################
# Start HFSS
# ~~~~~~~~~~
# Start HFSS and initialize the PyAEDT object.

version = "2022.2"
hfss = Hfss(project_temp_name, specified_version=version, non_graphical=non_graphical)
pin_names = hfss.excitations

###############################################################################
# Start Circuit
# ~~~~~~~~~~~~~~
# Start Circuit and add the HFSS dynamic link component to it.

circuit = Circuit()
hfss_comp = circuit.modeler.schematic.add_subcircuit_dynamic_link(hfss)

###############################################################################
# Set up dynamic link options
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Set up the dynamic link options. The argument for ``set_sim_option_on_hfss_subcircuit``
# can be the component name, component ID, or component object.

circuit.modeler.schematic.refresh_dynamic_link(hfss_comp.composed_name)
circuit.modeler.schematic.set_sim_option_on_hfss_subcircuit(hfss_comp)
hfss_setup_name = hfss.setups[0].name + " : " + hfss.setups[0].sweeps[0].name
circuit.modeler.schematic.set_sim_solution_on_hfss_subcircuit(hfss_comp.composed_name, hfss_setup_name)

###############################################################################
# Create ports and excitations
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create ports and excitations. Find component pin locations and create interface
# ports on them. Define the voltage source on the input port.


circuit.modeler.schematic.create_interface_port(
    "Excitation_1", [hfss_comp.pins[0].location[0], hfss_comp.pins[0].location[1]]
)
circuit.modeler.schematic.create_interface_port(
    "Excitation_2", [hfss_comp.pins[1].location[0], hfss_comp.pins[1].location[1]]
)
circuit.modeler.schematic.create_interface_port(
    "Port_1", [hfss_comp.pins[2].location[0], hfss_comp.pins[2].location[1]]
)
circuit.modeler.schematic.create_interface_port(
    "Port_2", [hfss_comp.pins[3].location[0], hfss_comp.pins[3].location[1]]
)

voltage = 1
phase = 0
excitation_settings = [str(voltage) + " V", str(phase) + " deg", "0V", "0V", "0V", "1GHz", "0s", "0", "0deg", "0Hz"]
ports_list = ["Excitation_1", "Excitation_2"]
circuit.assign_voltage_sinusoidal_excitation_to_ports(ports_list, excitation_settings)

###############################################################################
# Create setup
# ~~~~~~~~~~~~~~
# Create a setup.

setup_name = "MySetup"
LNA_setup = circuit.create_setup(setupname=setup_name)
bw_start = 4.3
bw_stop = 4.4
n_points = 1001
unit = "GHz"
sweep_list = ["LINC", str(bw_start) + unit, str(bw_stop) + unit, str(n_points)]
LNA_setup.props["SweepDefinition"]["Data"] = " ".join(sweep_list)

###############################################################################
# Solve and push excitations
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Solve the circuit and push excitations to the HFSS model to calculate the
# correct value of losses.

circuit.analyze_nominal()

circuit.push_excitations(instance_name="S1", setup_name=setup_name)


###############################################################################
# Start Mechanical
# ~~~~~~~~~~~~~~~~~
# Start Mechanical and copy bodies from the HFSS project.

mech = Mechanical()
mech.copy_solid_bodies_from(hfss)


###############################################################################
# Get losses from HFSS and assign convection to Mechanical
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Get losses from HFSS and assign the convection to Mechanical.


mech.assign_em_losses(
    hfss.design_name,
    hfss.setups[0].name,
    "LastAdaptive",
    hfss.setups[0].props["Frequency"],
    surface_objects=hfss.get_all_conductors_names(),
)
diels = ["1_pd", "2_pd", "3_pd", "4_pd", "5_pd"]
for el in diels:
    mech.assign_uniform_convection([mech.modeler[el].top_face_y, mech.modeler[el].bottom_face_y], 3)


###############################################################################
# Plot model
# ~~~~~~~~~~
# Plot the model.

mech.plot(show=False, export_path=os.path.join(mech.working_directory, "Mech.jpg"), plot_air_objects=False)

###############################################################################
# Solve and plot thermal results
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Solve and plot the thermal results.

mech.create_setup()
mech.save_project()
mech.analyze_nominal()
surfaces = []
for name in mech.get_all_conductors_names():
    surfaces.extend(mech.modeler.get_object_faces(name))
mech.post.create_fieldplot_surface(surfaces, "Temperature")


###############################################################################
# Release AEDT
# ~~~~~~~~~~~~
# Release AEDT.

mech.release_desktop(True, True)
