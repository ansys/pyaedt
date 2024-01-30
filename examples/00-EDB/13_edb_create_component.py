# # EDB: Layout Creation and Setup
#
# This example demonstrates how to to
#
# 1. Create a layout layer stackup.
# 2. Define padstacks.
# 3. Place padstack instances in the layout where the connectors are located.
# 4. Create primitives such as polygons and traces.
# 5. Create "components" from the padstack definitions using "pins".
#  >The "component" in EDB acts as a placeholder to enable automatic
#   >placement of electrical models, or
#   >as in this example to assign ports.  In many
#   >cases the EDB is imported from a 3rd party layout, in which case the
#   >concept of a "component" as a placeholder is needed to map
#   >models to the components on the PCB for later use in the
#   >simulation.
# 7. Create the HFSS simulation setup and assign ports where the connectors are located.

# ## PCB Trace Model
#
# Here is an image of the model that will be created in this example.
#
# <img src="_static/connector_example.png" width="600">
#
# The rectangular sheets at each end of the PCB enable placement of ports where the connectors are located.

# Initialize the EDB layout object.

import os
import pyaedt
import tempfile
from pyaedt import Edb

temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")
aedb_path = os.path.join(temp_dir.name, "component_example.aedb")

edb = Edb(edbpath=aedb_path, edbversion="2023.2")
print("EDB is located at {}".format(aedb_path))

# Initialize variables

layout_count = 12
diel_material_name = "FR4_epoxy"
diel_thickness = "0.15mm"
cond_thickness_outer = "0.05mm"
cond_thickness_inner = "0.017mm"
soldermask_thickness = "0.05mm"
trace_in_layer = "TOP"
trace_out_layer = "L10"
trace_width = "200um"
connector_size = 2e-3
conectors_position = [[0, 0], [10e-3, 0]]

# Create the stackup

edb.stackup.create_symmetric_stackup(layer_count=layout_count, inner_layer_thickness=cond_thickness_inner,
                                     outer_layer_thickness=cond_thickness_outer,
                                     soldermask_thickness=soldermask_thickness, dielectric_thickness=diel_thickness,
                                     dielectric_material=diel_material_name)

# Create ground planes

ground_layers = [layer_name for layer_name in edb.stackup.signal_layers.keys() if layer_name not in
                 [trace_in_layer, trace_out_layer]]
plane_shape = edb.modeler.Shape("rectangle", pointA=["-3mm", "-3mm"], pointB=["13mm", "3mm"])
for i in ground_layers:
    edb.modeler.create_polygon(plane_shape, i, net_name="VSS")

# ### Design Parameters
#
# Parameters that are preceeded by a _"$"_ character have project-wide scope. 
# Therefore, the padstack **definition** and hence all instances of that padstack rely on the parameters.
#
# Parameters such as _"trace_in_width"_ and _"trace_out_width"_ have local scope and
# are only used in in the design.

edb.add_design_variable("$via_hole_size", "0.3mm")
edb.add_design_variable("$antipaddiam", "0.7mm")
edb.add_design_variable("$paddiam", "0.5mm")
edb.add_design_variable("trace_in_width", "0.2mm", is_parameter=True)
edb.add_design_variable("trace_out_width", "0.1mm", is_parameter=True)

# ### Create the Connector Component
#
# The component definition is used to place the connector on the PCB. First define the padstacks.

edb.padstacks.create_padstack(padstackname="Via", holediam="$via_hole_size", antipaddiam="$antipaddiam",
                              paddiam="$paddiam")

# Create the first connector

component1_pins = [edb.padstacks.place_padstack(conectors_position[0], "Via", net_name="VDD", fromlayer=trace_in_layer,
                                                tolayer=trace_out_layer),
                   edb.padstacks.place_padstack([conectors_position[0][0] - connector_size / 2,
                                                 conectors_position[0][1] - connector_size / 2],
                                                "Via", net_name="VSS"),
                   edb.padstacks.place_padstack([conectors_position[0][0] + connector_size / 2,
                                                 conectors_position[0][1] - connector_size / 2],
                                                "Via", net_name="VSS"),
                   edb.padstacks.place_padstack([conectors_position[0][0] + connector_size / 2,
                                                 conectors_position[0][1] + connector_size / 2],
                                                "Via", net_name="VSS"),
                   edb.padstacks.place_padstack([conectors_position[0][0] - connector_size / 2,
                                                 conectors_position[0][1] + connector_size / 2],
                                                "Via", net_name="VSS")]

# Create the 2nd connector

component2_pins = [
    edb.padstacks.place_padstack(conectors_position[-1], "Via", net_name="VDD", fromlayer=trace_in_layer,
                                 tolayer=trace_out_layer),
    edb.padstacks.place_padstack([conectors_position[1][0] - connector_size / 2,
                                  conectors_position[1][1] - connector_size / 2],
                                 "Via", net_name="VSS"),
    edb.padstacks.place_padstack([conectors_position[1][0] + connector_size / 2,
                                  conectors_position[1][1] - connector_size / 2],
                                 "Via", net_name="VSS"),
    edb.padstacks.place_padstack([conectors_position[1][0] + connector_size / 2,
                                  conectors_position[1][1] + connector_size / 2],
                                 "Via", net_name="VSS"),
    edb.padstacks.place_padstack([conectors_position[1][0] - connector_size / 2,
                                  conectors_position[1][1] + connector_size / 2],
                                 "Via", net_name="VSS")]

# ### Define "Pins"
#
# Pins are fist defined to allow a component to subsequently connect to the remainder 
# of the model. In this case, ports will be assigned at the connector instances using the "pins".

for padstack_instance in list(edb.padstacks.instances.values()):
    padstack_instance.is_pin = True

# Create components from he pins

edb.components.create(component1_pins, 'connector_1')
edb.components.create(component2_pins, 'connector_2')

# Creating ports on the pins and insert a simulation setup using the ``SimulationConfiguration`` class.

sim_setup = edb.new_simulation_configuration()
sim_setup.solver_type = sim_setup.SOLVER_TYPE.Hfss3dLayout
sim_setup.batch_solve_settings.cutout_subdesign_expansion = 0.01
sim_setup.batch_solve_settings.do_cutout_subdesign = False
sim_setup.batch_solve_settings.signal_nets = ["VDD"]
sim_setup.batch_solve_settings.components = ["connector_1", "connector_2"]
sim_setup.batch_solve_settings.power_nets = ["VSS"]
sim_setup.ac_settings.start_freq = "0GHz"
sim_setup.ac_settings.stop_freq = "5GHz"
sim_setup.ac_settings.step_freq = "1GHz"
edb.build_simulation_project(sim_setup)

# Save the EDB and open it in the 3D Layout editor. If ``non_graphical==False``
# there may be a delay while AEDT started.

edb.save_edb()
edb.close_edb()
h3d = pyaedt.Hfss3dLayout(specified_version="2023.2",
                          projectname=aedb_path,
                          non_graphical=False,  # Set non_graphical = False to launch AEDT in graphical mode.
                          new_desktop_session=True)

# ### Release the application from the Python kernel
#
# It is important to release the application from the Python kernel after 
# execution of the script. The default behavior of the ``release_desktop()`` method closes all open
# projects and closes the application.
#
# If you want to conintue working on the project in graphical mode
# after script execution, call the following method with both arguments set to ``False``.

h3d.release_desktop(close_projects=True, close_desktop=True)

# ### Clean up the Temporary Directory
#
# The following command cleans up the temporary directory, thereby removing all 
# project files. If you'd like to save this project, save it to a folder of your choice 
# prior to running the following cell.

temp_dir.cleanup()
