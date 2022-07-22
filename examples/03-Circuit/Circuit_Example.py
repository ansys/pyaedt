"""
Circuit: schematic creation and analysis
----------------------------------------
This example shows how you can use PyAEDT to create a circuit design
and run a Nexxim time-domain simulation.
"""
###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports.

# sphinx_gallery_thumbnail_path = 'Resources/circuit.png'

from pyaedt import Circuit
from pyaedt import Desktop
import os

###############################################################################
# Launch AEDT
# ~~~~~~~~~~~
# Launch AEDT 2022 R2 in graphical mode. This example uses SI units.

desktop_version = "2022.2"

##########################################################
# Set non-graphical mode
# ~~~~~~~~~~~~~~~~~~~~~~
# Set non-graphical mode. The default is ``False``.

non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")
new_thread = True

###############################################################################
# Launch AEDT and Circuit
# ~~~~~~~~~~~~~~~~~~~~~~~
# The :class:`pyaedt.Desktop` class initializes AEDT and starts the specified version in
# the specified mode. The Boolean parameter ``new_thread`` defines whether
# to create a new instance of AEDT or try to connect to an existing instance of it.

desktop = Desktop(desktop_version, non_graphical, new_thread)
aedt_app = Circuit()

###############################################################################
# Create circuit setup
# ~~~~~~~~~~~~~~~~~~~~
# Create and customize an LNA (linear network analysis) setup.

setup1 = aedt_app.create_setup("MyLNA")
setup1.props["SweepDefinition"]["Data"] = "LINC 0GHz 4GHz 10001"

###############################################################################
# Create components
# ~~~~~~~~~~~~~~~~~
# Create components, such as an inductor, resistor, and capacitor.

inductor = aedt_app.modeler.schematic.create_inductor("L1", 1e-9, [0, 0])
resistor = aedt_app.modeler.schematic.create_resistor("R1", 50, [0.0254, 0])
capacitor = aedt_app.modeler.schematic.create_capacitor("C1", 1e-12)

###############################################################################
# Get all pins
# ~~~~~~~~~~~~
# Get all pins of a specified component.

pins_resistor = resistor.pins


###############################################################################
# Create port and ground
# ~~~~~~~~~~~~~~~~~~~~~~
# Create a port and a ground, which are needed for the circuit analysis.

port = aedt_app.modeler.components.create_interface_port("myport")
gnd = aedt_app.modeler.components.create_gnd()

###############################################################################
# Connect components
# ~~~~~~~~~~~~~~~~~~
# Connect components with wires.

port.pins[0].connect_to_component(inductor.pins[0])
inductor.pins[1].connect_to_component(resistor.pins[0])
resistor.pins[1].connect_to_component(capacitor.pins[0])
capacitor.pins[1].connect_to_component(gnd.pins[0])

###############################################################################
# Create transient setup
# ~~~~~~~~~~~~~~~~~~~~~~
# Create a transient setup.

setup2 = aedt_app.create_setup("MyTransient", aedt_app.SETUPS.NexximTransient)
setup2.props["TransientData"] = ["0.01ns", "200ns"]
setup3 = aedt_app.create_setup("MyDC", aedt_app.SETUPS.NexximDC)

###############################################################################
# Solve transient setup
# ~~~~~~~~~~~~~~~~~~~~~
# Solve the transient setup.

aedt_app.analyze_setup("MyLNA")

aedt_app.export_fullwave_spice()


###############################################################################
# Create report
# ~~~~~~~~~~~~~
# Create a report that plots solution data.

solutions = aedt_app.post.get_solution_data(
    expressions=aedt_app.get_traces_for_plot(category="S"),
)
fig = solutions.plot()


###############################################################################
# Close AEDT
# ~~~~~~~~~~
# After the simulation completes, you can close AEDT or release it using the
# :func:`pyaedt.Desktop.force_close_desktop` method.
# All methods provide for saving the project before closing.

if os.name != "posix":
    desktop.release_desktop()
