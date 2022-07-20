"""
Twin Builder: RC circuit design anaysis
---------------------------------------
This example shows how you can use PyAEDT to create a Twin Builder design
and run a Twin Builder time-domain simulation.
"""

###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports.

import os
from pyaedt import TwinBuilder

###############################################################################
# Select version and set launch options
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
# Create components for RC circuit driven by pulse voltage source
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create components for an RC circuit driven by a pulse voltage source. Define
# the grid distance for ease in calculations.

G = 0.00254

# Create components, such as a voltage source, resistor, and capacitor.

source = tb.modeler.schematic.create_voltage_source("E1", "EPULSE", 10, 10, [0, 0])
resistor = tb.modeler.schematic.create_resistor("R1", 10000, [10 * G, 10 * G], 90)
capacitor = tb.modeler.schematic.create_capacitor("C1", 1e-6, [20 * G, 0])

###############################################################################
# Create ground
# ~~~~~~~~~~~~~
# Create a ground, which is needed for analog analysis.

gnd = tb.modeler.components.create_gnd([0, -10 * G])

###############################################################################
# Connect components
# ~~~~~~~~~~~~~~~~~~
# Connects components with pins.

source.pins[1].connect_to_component(resistor.pins[0])
resistor.pins[1].connect_to_component(capacitor.pins[0])
capacitor.pins[1].connect_to_component(source.pins[0])
source.pins[0].connect_to_component(gnd.pins[0])

###############################################################################
# Parametrize transient setup
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Parametrize the default transient setup by setting the end time.

tb.set_end_time("300ms")

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

E_Value = "E1.V"
C_Value = "C1.V"

x = tb.post.get_solution_data([E_Value, C_Value], "TR", "Time")
x.plot([E_Value, C_Value], xlabel="Time", ylabel="Capacitor Voltage vs Input Pulse")


###############################################################################
# Close Twin Builder
# ~~~~~~~~~~~~~~~~~~
# After the simulaton completes, you can close Twin Builder or release it.
# All methods provide for saving the project before closing.

if os.name != "posix":
    tb.release_desktop()
