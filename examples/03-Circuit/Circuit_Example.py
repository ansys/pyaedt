"""
Schematic Creation and Analysis
-------------------------------
This example shows how you can use PyAEDT to create a Circuit design
and run a Nexxim time-domain simulation.
"""
# sphinx_gallery_thumbnail_path = 'Resources/circuit.png'

from pyaedt import Circuit
from pyaedt import Desktop
import os

###############################################################################
# Launch AEDT and Circuit
# ~~~~~~~~~~~~~~~~~~~~~~~
# This examples launches AEDT 2021.2 in graphical mode.

# This examples uses SI units.

desktop_version = "2021.2"

###############################################################################
# Launch AEDT in Non-Graphical Mode
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# You can change the Boolean parameter ``non_graphical`` to ``False`` to launch
# AEDT in graphical mode.
# You can change the Boolean parameter ``new_thread`` to ``False`` to launch
# AEDT in existing Desktop Session, if any.

non_graphical = False
new_thread = True

###############################################################################
# Launch AEDT and Circuit
# ~~~~~~~~~~~~~~~~~~~~~~~
# The :class:`pyaedt.Desktop` class initializes AEDT and starts it on a specified version in
# a specified graphical mode. The Boolean parameter ``new_thread`` defines whether
# to create a new instance of AEDT or try to connect to existing instance of it.

desktop = Desktop(desktop_version, non_graphical, new_thread)
aedt_app = Circuit()

###############################################################################
# Create a Circuit Setup
# ~~~~~~~~~~~~~~~~~~~~~~
# This method creates and customizes a Linear Network Analysis (LNA) setup.

setup1 = aedt_app.create_setup("MyLNA")
setup1.SweepDefinition = [
    ("Variable", "Freq"),
    ("Data", "LINC 0GHz 4GHz 10001"),
    ("OffsetF1", False),
    ("Synchronize", 0),
]
setup1.update()

###############################################################################
# Create Components
# ~~~~~~~~~~~~~~~~~
# These methods create components, such as inductors, resistors, and capacitors.

inductor = aedt_app.modeler.schematic.create_inductor("L1", 1e-9, [0, 0])
resistor = aedt_app.modeler.schematic.create_resistor("R1", 50, [0.0254, 0])
capacitor = aedt_app.modeler.schematic.create_capacitor("C1", 1e-12)

###############################################################################
# Get Component Pins
# ~~~~~~~~~~~~~~~~~~
# This method gets all pins of a specified component.

pins_resistor = resistor.pins


###############################################################################
# Create a Port and a Ground
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# These methods create a port and a ground, which are needed for a circuit anlaysis.

port = aedt_app.modeler.components.create_interface_port("myport")
gnd = aedt_app.modeler.components.create_gnd()
###############################################################################
# Connect Components
# ~~~~~~~~~~~~~~~~~~
# This method connects components with wires.

port.pins[0].connect_to_component(inductor.pins[0])
inductor.pins[1].connect_to_component(resistor.pins[0])
resistor.pins[1].connect_to_component(capacitor.pins[0])
capacitor.pins[1].connect_to_component(gnd.pins[0])

###############################################################################
# Add a Transient Setup
# ~~~~~~~~~~~~~~~~~~~~~
# This method adds a transient setup.

setup2 = aedt_app.create_setup("MyTransient", aedt_app.SETUPS.NexximTransient)
setup2.TransientData = ["0.01ns", "200ns"]
setup2.update()
setup3 = aedt_app.create_setup("MyDC", aedt_app.SETUPS.NexximDC)

###############################################################################
# Solve the Transient Setup
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# This method solves the transient setup.

aedt_app.analyze_setup("MyLNA")

aedt_app.export_fullwave_spice()
###############################################################################
# Close AEDT
# ~~~~~~~~~~
# After the simulaton is completed, you can close AEDT or release it using the
# :func:`pyaedt.Desktop.force_close_desktop` method.
# All methods provide for saving the project before exiting.
if os.name != "posix":
    desktop.release_desktop()
