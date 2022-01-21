"""
RC Circuit Schematic Creation and Analysis
-------------------------------
This example shows how you can use PyAEDT to create a Twin Builder design
and run a Twin Builder time-domain simulation.
"""

from pyaedt import TwinBuilder
from pyaedt import Desktop
import os
import matplotlib.pyplot as plt

###############################################################################
# Launch Twin Builder
# ~~~~~~~~~~~~~~~~~~~~~~~
# This example launches Twin Builder 2021.2 in graphical mode.

# This example uses SI units.

desktop_version = "2021.2"

###############################################################################
# Launch Twin Builder in Non-Graphical Mode
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# You can change the Boolean parameter ``non_graphical`` to ``False`` to launch
# Twin Builder in graphical mode.
# You can change the Boolean parameter ``new_thread`` to ``False`` to launch
# Twin Builder in existing Desktop Session, if any.

non_graphical = False
new_thread = True

###############################################################################
# Launch Twin Builder
# ~~~~~~~~~~~~~~~~~~~~~~~
# The :class:`pyaedt.Desktop` class initializes AEDT and starts it on a specified version in
# a specified graphical mode. The Boolean parameter ``new_thread`` defines whether
# to create a new instance of AEDT or try to connect to existing instance of it.

desktop = Desktop(desktop_version, non_graphical, new_thread)

# Add a new Twin Builder design with a default setup

tb = TwinBuilder()


###############################################################################
# Create Components for a RC circuit driven by a pulse voltage source
# ~~~~~~~~~~~~~~~~~

# Define the Grid Distance

G = 0.00254

# These methods create components, such as voltage source, resistors, and capacitors.

source = tb.modeler.schematic.create_voltage_source("E1", "EPULSE", 10, 10, [0, 0])
resistor = tb.modeler.schematic.create_resistor("R1", 10000, [10 * G, 10 * G], 90)
capacitor = tb.modeler.schematic.create_capacitor("C1", 1e-6, [20 * G, 0])

###############################################################################
# Create a Ground
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# This method create a ground, which is needed for a twin builder analog analysis.

gnd = tb.modeler.components.create_gnd([0, -10 * G])

###############################################################################
# Connect Components
# ~~~~~~~~~~~~~~~~~~
# This method connects components with wires.

source.pins[1].connect_to_component(resistor.pins[0])
resistor.pins[1].connect_to_component(capacitor.pins[0])
capacitor.pins[1].connect_to_component(source.pins[0])
source.pins[0].connect_to_component(gnd.pins[0])

###############################################################################
# Parametrize a Transient Setup
# ~~~~~~~~~~~~~~~~~~~~~
# This method setup the end time for the default transient setup.

tb.set_end_time("300ms")

###############################################################################
# Solve the Transient Setup
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# This method solves the transient setup.

tb.analyze_setup("TR")


################################################################
# Get Report Data and plot it on matplotlib.

# Get the values for the voltage on the Pulse voltage source
E_Value = "E1.V"
x = tb.post.get_report_data(E_Value, "TR", "Time", {"Time": ["All"]})
plt.plot(x.sweeps["Time"], x.data_real(E_Value))

# Get the values for the voltage on the capacitor in the RC Circuit
C_Value = "C1.V"
x = tb.post.get_report_data(C_Value, "TR", "Time", {"Time": ["All"]})
plt.plot(x.sweeps["Time"], x.data_real(C_Value))


plt.grid()
plt.xlabel("Time")
plt.ylabel("C1.V vs E1.V")
plt.show()

plt.clf()

###############################################################################
# Close Twin Builder
# ~~~~~~~~~~
# After the simulaton is completed, you can close Twin Builder or release it using the
# :func:`pyaedt.Desktop.force_close_desktop` method.
# All methods provide for saving the project before exiting.
if os.name != "posix":
    desktop.release_desktop()
