"""
Circuit Example Analysis
------------------------
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
# This examples launches AEDT 2021.1 in graphical mode.

# This examples uses SI units.

desktop_version = "2021.1"

###############################################################################
# Launch AEDT in Non-Graphical Mode
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# You can change the Boolean parameter ``non_graphical`` to ``False`` to launch
# AEDT in graphical mode.

non_graphical = True
new_thread = True

###############################################################################
# Launch AEDT and Circuit
# ~~~~~~~~~~~~~~~~~~~~~~~
# The :class: `pyaedt.Desktop` class initializes AEDT and starts it on a specified version in
# a specified graphical mode. The Boolean parameter ``new_thread`` defines whether
# to create a new instance of AEDT or try to connect to existing instance of it.

desktop = Desktop(desktop_version, non_graphical, new_thread)
aedt_app = Circuit()

###############################################################################
# Create a Circuit Setup
# ~~~~~~~~~~~~~~~~~~~~~~
# This method creates and customizes a Linear Network Analysis (LNA) setup.

setup1 = aedt_app.create_setup("MyLNA")
setup1.SweepDefinition = [('Variable', 'Freq'), ('Data', 'LINC 0GHz 4GHz 10001'), ('OffsetF1', False),
                          ('Synchronize', 0)]
setup1.update()

###############################################################################
# Create Components
# ~~~~~~~~~~~~~~~~~
# These methods create components, such as inductors, resistors, and capacitors.

inductor_id, inductor = aedt_app.modeler.components.create_inductor("L1", 1e-9, 0, 0)
resistor_id, resistor = aedt_app.modeler.components.create_resistor("R1", 50, 0.0254, 0)
capacitor_id, capacitor = aedt_app.modeler.components.create_capacitor("C1", 1e-12, 0.0400, 0)

###############################################################################
# Get Component Pins
# ~~~~~~~~~~~~~~~~~~
# This method gets all pins of a specified component.

pins_resistor = aedt_app.modeler.components.get_pins(resistor)

inductor_component = aedt_app.modeler.components[inductor]
resistor_component = aedt_app.modeler.components[resistor]

###############################################################################
# Create a Port and a Ground
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# These methods create a port and a ground, which are needed for a circuit anlaysis.

port_id, port_name = aedt_app.modeler.components.create_iport("myport", -0.0254, 0)
gnd_id, gnd_name = aedt_app.modeler.components.create_gnd(0.0508, -0.00254)
###############################################################################
# Connect Components
# ~~~~~~~~~~~~~~~~~~
# This method connects components with wires.

aedt_app.modeler.connect_schematic_components(port_id, inductor_id)
aedt_app.modeler.connect_schematic_components(inductor_id, resistor_id, pinnum_second=2)
aedt_app.modeler.connect_schematic_components(resistor_id, capacitor_id, pinnum_first=1)
aedt_app.modeler.connect_schematic_components(capacitor_id, gnd_id)

###############################################################################
# Add a Transient Setup
# ~~~~~~~~~~~~~~~~~~~~~
# This method adds a transient setup.

setup2 = aedt_app.create_setup("MyTransient", aedt_app.SimulationSetupTypes.NexximTransient)
setup2.TransientData = ["0.01ns", "200ns"]
setup2.update()
setup3 = aedt_app.create_setup("MyDC", aedt_app.SimulationSetupTypes.NexximDC)

###############################################################################
# Solve the Transient Setup
# ~~~~~~~~~~~~~~~~~~~~~~~~
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
    desktop.force_close_desktop()
