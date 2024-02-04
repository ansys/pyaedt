# # Twin Builder: wiring a rectifier with a capacitor filter
#
# This example shows how you can use PyAEDT to create a Twin Builder design
# and run a Twin Builder time-domain simulation.
#
# <img src="_static/rectifier.png" width="500">

# ## Perform required imports
#
# Perform required imports.

import math
import matplotlib.pyplot as plt
import pyaedt
import tempfile
import os

# ## Select version and set launch options
#
# Select the Twin Builder version and set the launch options. The following code
# launches Twin Builder 2023 R2 in graphical mode.
#
# You can change the Boolean parameter ``non_graphical`` to ``True`` to launch
# Twin Builder in non-graphical mode. You can also change the Boolean parameter
# ``new_thread`` to ``False`` to launch Twin Builder in an existing AEDT session
# if one is running.

desktop_version = "2023.2"
non_graphical = False
new_thread = True
temp_dir = tempfile.TemporaryDirectory(suffix=".ansys")

# ## Launch Twin Builder
#
# Launch Twin Builder using an implicit declaration and add a new design with
# a default setup.

tb = pyaedt.TwinBuilder(projectname=os.path.join(temp_dir.name, "TB_Rectifier_Demo"),
                        specified_version=desktop_version,
                        non_graphical=non_graphical,
                        new_desktop_session=new_thread
                        )

# ## Create components for bridge rectifier
#
# Place components for a bridge rectifier and a capacitor filter in the schematic editor.
#
# Specify the grid spacing to use for placement
# of components in the schematic editor. Components are placed using the named
# argument ``location`` as a list of ``[x, y]`` values in mm.

G = 0.00254

# Create an AC sinosoidal voltage source.

source = tb.modeler.schematic.create_voltage_source("V_AC", "ESINE", 100, 50, location=[-1 * G, 0])

# Place the four diodes of the bridge rectifier. The named argument ``angle`` is the rotation angle
# of the component in radians.

diode1 = tb.modeler.schematic.create_diode(compname="D1", location=[10 * G, 6 * G], angle=3 * math.pi / 2)
diode2 = tb.modeler.schematic.create_diode(compname="D2", location=[20 * G, 6 * G], angle=3 * math.pi / 2)
diode3 = tb.modeler.schematic.create_diode(compname="D3", location=[10 * G, -4 * G], angle=3 * math.pi / 2)
diode4 = tb.modeler.schematic.create_diode(compname="D4", location=[20 * G, -4 * G], angle=3 * math.pi / 2)

# Place a capacitor filter.

capacitor = tb.modeler.schematic.create_capacitor(compname="C_FILTER", value=1e-6, location=[29 * G, -10 * G])

# Place a load resistor.

resistor = tb.modeler.schematic.create_resistor(compname="RL", value=100000, location=[39 * G, -10 * G])

# Place the ground component.

gnd = tb.modeler.components.create_gnd(location=[5 * G, -16 * G])

# ## Connect components
#
# Connect components with wires.

# Connect the diode pins to create the bridge.

tb.modeler.schematic.create_wire(points_array=[diode1.pins[0].location, diode3.pins[0].location])
tb.modeler.schematic.create_wire(points_array=[diode2.pins[1].location, diode4.pins[1].location])
tb.modeler.schematic.create_wire(points_array=[diode1.pins[1].location, diode2.pins[0].location])
tb.modeler.schematic.create_wire(points_array=[diode3.pins[1].location, diode4.pins[0].location])

# Connect the voltage source to the bridge.

tb.modeler.schematic.create_wire(points_array=[source.pins[1].location, [0, 10 * G], [15 * G, 10 * G], [15 * G, 5 * G]])
tb.modeler.schematic.create_wire(points_array=[source.pins[0].location, [0, -10 * G], [15 * G, -10 * G], [15 * G, -5 * G]])

# Connect the filter capacitor and load resistor.

tb.modeler.schematic.create_wire(points_array=[resistor.pins[0].location, [40 * G, 0], [22 * G, 0]])
tb.modeler.schematic.create_wire(points_array=[capacitor.pins[0].location, [30 * G, 0]])

# Add the ground connection.

tb.modeler.schematic.create_wire(points_array=[resistor.pins[1].location, [40 * G, -15 * G], gnd.pins[0].location])
tb.modeler.schematic.create_wire(points_array=[capacitor.pins[1].location, [30 * G, -15 * G]])
tb.modeler.schematic.create_wire(points_array=[gnd.pins[0].location, [5 * G, 0], [8 * G, 0]])

# Zoom to fit the schematic
tb.modeler.zoom_to_fit()

# The circuit schematic will now be visible in the Twin Builder schematic editor and should look like
# the image shown at the beginning of the example.
#
# ## Run the Simulation
#
# Update the total time to be simulated and run the analysis

tb.set_end_time("100ms")
tb.analyze_setup("TR")

# ## Get report data and plot using Matplotlib
#
# Get report data and plot it using Matplotlib. The following code gets and plots
# the values for the voltage on the pulse voltage source and the values for the
# voltage on the capacitor in the RC circuit.

src_name = source.InstanceName + ".V"
x = tb.post.get_solution_data(src_name, tb.analysis_setup, "Time")
plt.plot(x.intrinsics["Time"], x.data_real(src_name))
plt.grid()
plt.xlabel("Time")
plt.ylabel("AC Voltage")
plt.show()

r_voltage = resistor.InstanceName + ".V"
x = tb.post.get_solution_data(r_voltage, tb.analysis_setup, "Time")
plt.plot(x.intrinsics["Time"], x.data_real(r_voltage))
plt.grid()
plt.xlabel("Time")
plt.ylabel("AC to DC Conversion using Rectifier")
plt.show()

# ## Close Twin Builder
#
# After the simulation is completed, you can close Twin Builder or release it.
# All methods provide for saving the project before closing.

tb.release_desktop()

# ## Cleanup
#
# Remove the project and temporary folder. The project files can be retrieved from the
# temporary directory, ``temp_dir.name``, prior to executing the following cell, if desired.

temp_dir.cleanup()  # Cleans up all files and removes the project directory.
