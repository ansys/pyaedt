"""
TwinBuilder: RC Circuit Design in Twin Builder
----------------------------------------------
This example shows how you can use PyAEDT to create a Twin Builder design
and run a Twin Builder time-domain simulation.
"""

###############################################################################
# Import Required Packages for Twin Builder
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import os
from pyaedt import TwinBuilder

###############################################################################
# Select Version and Launch Options
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example launches Twin Builder 2022R2 in graphical mode.

# You can change the Boolean parameter ``non_graphical`` to ``True`` to launch
# Twin Builder in non graphical mode.
# You can change the Boolean parameter ``new_thread`` to ``False`` to launch
# Twin Builder in existing Desktop Session, if any.

desktop_version = "2022.2"

non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")
new_thread = True

###############################################################################
# Launch Twin Builder
# ~~~~~~~~~~~~~~~~~~~
# Use implicit declaration to launch Twin Builder Application

# Add a new Twin Builder design with a default setup

tb = TwinBuilder(specified_version=desktop_version, non_graphical=non_graphical, new_desktop_session=new_thread)

###############################################################################
# Create Components for a RC circuit driven by a pulse voltage source
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#

# Define the Grid Distance for ease in calculations

G = 0.00254

# These methods create components, such as voltage source, resistors, and capacitors.

source = tb.modeler.schematic.create_voltage_source("E1", "EPULSE", 10, 10, [0, 0])
resistor = tb.modeler.schematic.create_resistor("R1", 10000, [10 * G, 10 * G], 90)
capacitor = tb.modeler.schematic.create_capacitor("C1", 1e-6, [20 * G, 0])

###############################################################################
# Create a Ground
# ~~~~~~~~~~~~~~~
# This method creates a ground, which is needed for a twin builder analog analysis.

gnd = tb.modeler.components.create_gnd([0, -10 * G])

###############################################################################
# Connect Components
# ~~~~~~~~~~~~~~~~~~
# This method connects components with pageports.

source.pins[1].connect_to_component(resistor.pins[0])
resistor.pins[1].connect_to_component(capacitor.pins[0])
capacitor.pins[1].connect_to_component(source.pins[0])
source.pins[0].connect_to_component(gnd.pins[0])

###############################################################################
# Parametrize a Transient Setup
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This method setup the end time for the default transient setup.

tb.set_end_time("300ms")

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

E_Value = "E1.V"
C_Value = "C1.V"

x = tb.post.get_solution_data([E_Value, C_Value], "TR", "Time")
x.plot([E_Value, C_Value], xlabel="Time", ylabel="Capacitor Voltage vs Input Pulse")


###############################################################################
# Close Twin Builder
# ~~~~~~~~~~~~~~~~~~
# After the simulaton is completed, you can close Twin Builder or release it
# All methods provide for saving the project before exiting.

if os.name != "posix":
    tb.release_desktop()
