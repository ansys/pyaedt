"""
TwinBuilder: Wiring a Rectifier with Capacitive Filter in Twin Builder
----------------------------------------------------------------------
This example shows how you can use PyAEDT to create a Twin Builder design
and run a Twin Builder time-domain simulation.
"""

###############################################################################
# Import Required Packages for Twin Builder
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import os
import math
import matplotlib.pyplot as plt
from pyaedt import TwinBuilder

###############################################################################
# Select Version and Launch Options
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example launches Twin Builder 2022R1 in graphical mode.

# You can change the Boolean parameter ``non_graphical`` to ``True`` to launch
# Twin Builder in non graphical mode.
# You can change the Boolean parameter ``new_thread`` to ``False`` to launch
# Twin Builder in existing Desktop Session, if any.

desktop_version = "2022.1"
non_graphical = False
new_thread = True

###############################################################################
# Launch Twin Builder
# ~~~~~~~~~~~~~~~~~~~
# Use implicit declaration to launch Twin Builder Application

# Add a new Twin Builder design with a default setup

tb = TwinBuilder(specified_version=desktop_version, non_graphical=non_graphical, new_desktop_session=new_thread)

###############################################################################
# Create Components for a bridge rectifier with capacitor filter
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#

# Define the Grid Distance for ease of calculations

G = 0.00254

# Place an AC sinosoidal source component

source = tb.modeler.schematic.create_voltage_source("V_AC", "ESINE", 100, 50, [-1 * G, 0])

# Place four diodes of the bridge rectifier

diode1 = tb.modeler.schematic.create_diode("D1", [10 * G, 6 * G], 3 * math.pi / 2)
diode2 = tb.modeler.schematic.create_diode("D2", [20 * G, 6 * G], 3 * math.pi / 2)
diode3 = tb.modeler.schematic.create_diode("D3", [10 * G, -4 * G], 3 * math.pi / 2)
diode4 = tb.modeler.schematic.create_diode("D4", [20 * G, -4 * G], 3 * math.pi / 2)

# Place capacitor filter

capacitor = tb.modeler.schematic.create_capacitor("C_FILTER", 1e-6, [29 * G, -10 * G])

# Place load resistor

resistor = tb.modeler.schematic.create_resistor("RL", 100000, [39 * G, -10 * G])

# Place a ground

gnd = tb.modeler.components.create_gnd([5 * G, -16 * G])

###############################################################################
# Connect Components
# ~~~~~~~~~~~~~~~~~~
# This method connects components with wires.

# Wire the diode bridge

tb.modeler.schematic.create_wire([diode1.pins[0].location, diode3.pins[0].location])
tb.modeler.schematic.create_wire([diode2.pins[1].location, diode4.pins[1].location])
tb.modeler.schematic.create_wire([diode1.pins[1].location, diode2.pins[0].location])
tb.modeler.schematic.create_wire([diode3.pins[1].location, diode4.pins[0].location])

# Wire the AC Source

tb.modeler.schematic.create_wire([source.pins[1].location, [0, 10 * G], [15 * G, 10 * G], [15 * G, 5 * G]])
tb.modeler.schematic.create_wire([source.pins[0].location, [0, -10 * G], [15 * G, -10 * G], [15 * G, -5 * G]])

# Wire the Filter Capacitor and Load Resistor

tb.modeler.schematic.create_wire([resistor.pins[0].location, [40 * G, 0], [22 * G, 0]])
tb.modeler.schematic.create_wire([capacitor.pins[0].location, [30 * G, 0]])

# Wire the ground

tb.modeler.schematic.create_wire([resistor.pins[1].location, [40 * G, -15 * G], gnd.pins[0].location])
tb.modeler.schematic.create_wire([capacitor.pins[1].location, [30 * G, -15 * G]])
tb.modeler.schematic.create_wire([gnd.pins[0].location, [5 * G, 0], [8 * G, 0]])

# Zoom to Fit the schematic
tb.modeler.zoom_to_fit()

###############################################################################
# Parametrize a Transient Setup
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This method setup the end time for the default transient setup.

tb.set_end_time("100ms")

###############################################################################
# Solve the Transient Setup
# ~~~~~~~~~~~~~~~~~~~~~~~~~
# This method solves the transient setup.

tb.analyze_setup("TR")


###############################################################################
# Get Report Data and plot it on matplotlib
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Get the values for the voltage on the Pulse voltage source
# Get the values for the voltage on the capacitor in the RC Circuit

E_Value = "V_AC.V"
x = tb.post.get_solution_data(E_Value, "TR", "Time")
plt.plot(x.sweeps["Time"], x.data_real(E_Value))

R_Value = "RL.V"
x = tb.post.get_solution_data(R_Value, "TR", "Time")
plt.plot(x.sweeps["Time"], x.data_real(R_Value))

plt.grid()
plt.xlabel("Time")
plt.ylabel("AC to DC Conversion using Rectifier")
plt.show()

###############################################################################
# Close Twin Builder
# ~~~~~~~~~~~~~~~~~~
# After the simulaton is completed, you can close Twin Builder or release it
# All methods provide for saving the project before exiting.

if os.name != "posix":
    tb.release_desktop()
