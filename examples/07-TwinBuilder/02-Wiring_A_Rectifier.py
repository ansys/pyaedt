"""
Twin Builder: wiring a rectifier with a capacitor filter
---------------------------------------------------------
This example shows how you can use PyAEDT to create a Twin Builder design
and run a Twin Builder time-domain simulation.
"""

###############################################################################
# Perform required imputs
# ~~~~~~~~~~~~~~~~~~~~~~~
# Perform the required imports.

import os
import math
import matplotlib.pyplot as plt
from pyaedt import TwinBuilder

###############################################################################
# Select version and set launch options
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Select the Twin Builder version and set launch options. The following code
# launches Twin Builder 2022 R2 in graphical mode.
#
# You can change the Boolean parameter ``non_graphical`` to ``True`` to launch
# Twin Builder in non-graphical mode. You can also change the Boolean parameter
# ``new_thread`` to ``False`` to launch Twin Builder in an existing AEDT session
# if one is running.

desktop_version = "2022.2"
non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")
new_thread = True

###############################################################################
# Launch Twin Builder
# ~~~~~~~~~~~~~~~~~~~
# Launch Twin Builder using an implicit declaration and add a new design with
# a default setup.

tb = TwinBuilder(specified_version=desktop_version, non_graphical=non_graphical, new_desktop_session=new_thread)

###############################################################################
# Create components for bridge rectifier with capacitor filter
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create components for a bridge rectifier with a capacitor filter.
 
# Define the grid distance for ease in calculations.

G = 0.00254

# Create an AC sinosoidal source component.

source = tb.modeler.schematic.create_voltage_source("V_AC", "ESINE", 100, 50, [-1 * G, 0])

# Create the four diodes of the bridge rectifier.

diode1 = tb.modeler.schematic.create_diode("D1", [10 * G, 6 * G], 3 * math.pi / 2)
diode2 = tb.modeler.schematic.create_diode("D2", [20 * G, 6 * G], 3 * math.pi / 2)
diode3 = tb.modeler.schematic.create_diode("D3", [10 * G, -4 * G], 3 * math.pi / 2)
diode4 = tb.modeler.schematic.create_diode("D4", [20 * G, -4 * G], 3 * math.pi / 2)

# Create a capacitor filter.

capacitor = tb.modeler.schematic.create_capacitor("C_FILTER", 1e-6, [29 * G, -10 * G])

# Create a load resistor.

resistor = tb.modeler.schematic.create_resistor("RL", 100000, [39 * G, -10 * G])

# Create a ground.

gnd = tb.modeler.components.create_gnd([5 * G, -16 * G])

###############################################################################
# Connect components
# ~~~~~~~~~~~~~~~~~~
# Connect components with wires.

# Wire the diode bridge.

tb.modeler.schematic.create_wire([diode1.pins[0].location, diode3.pins[0].location])
tb.modeler.schematic.create_wire([diode2.pins[1].location, diode4.pins[1].location])
tb.modeler.schematic.create_wire([diode1.pins[1].location, diode2.pins[0].location])
tb.modeler.schematic.create_wire([diode3.pins[1].location, diode4.pins[0].location])

# Wire the AC source.

tb.modeler.schematic.create_wire([source.pins[1].location, [0, 10 * G], [15 * G, 10 * G], [15 * G, 5 * G]])
tb.modeler.schematic.create_wire([source.pins[0].location, [0, -10 * G], [15 * G, -10 * G], [15 * G, -5 * G]])

# Wire the filter capacitor and load resistor.

tb.modeler.schematic.create_wire([resistor.pins[0].location, [40 * G, 0], [22 * G, 0]])
tb.modeler.schematic.create_wire([capacitor.pins[0].location, [30 * G, 0]])

# Wire the ground.

tb.modeler.schematic.create_wire([resistor.pins[1].location, [40 * G, -15 * G], gnd.pins[0].location])
tb.modeler.schematic.create_wire([capacitor.pins[1].location, [30 * G, -15 * G]])
tb.modeler.schematic.create_wire([gnd.pins[0].location, [5 * G, 0], [8 * G, 0]])

# Zoom to fit the schematic
tb.modeler.zoom_to_fit()

###############################################################################
# Parametrize transient setup
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Parametrize the default transient setup by setting the end time.

tb.set_end_time("100ms")

###############################################################################
# Solve transient setup
# ~~~~~~~~~~~~~~~~~~~~~~~~~
# Solve the transient setup.

tb.analyze_setup("TR")


###############################################################################
# Get report data and plot using Matplotlib
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Get report data and plot it using Matplotlib. The following code gets and plots
# the values for the voltage on the pulse voltage source and the values for the
# voltage on the capacitor in the RC circuit.

E_Value = "V_AC.V"
x = tb.post.get_solution_data(E_Value, "TR", "Time")
plt.plot(x.intrinsics["Time"], x.data_real(E_Value))

R_Value = "RL.V"
x = tb.post.get_solution_data(R_Value, "TR", "Time")
plt.plot(x.intrinsics["Time"], x.data_real(R_Value))

plt.grid()
plt.xlabel("Time")
plt.ylabel("AC to DC Conversion using Rectifier")
plt.show()

###############################################################################
# Close Twin Builder
# ~~~~~~~~~~~~~~~~~~
# After the simulaton is completed, you can close Twin Builder or release it.
# All methods provide for saving the project before closing.

if os.name != "posix":
    tb.release_desktop()
