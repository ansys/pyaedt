"""
Circuit Example Analysis
------------------------
This example shows how you can use PyAEDT to create a Circut design 
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

desktopVersion = "2021.1"

###############################################################################
# Launch AEDT in Non-Graphical Mode
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# You can change the Boolean parameter ``NonGraphical`` to ``False`` to launch  
# AEDT in graphical mode.

NonGraphical = True
NewThread = True

###############################################################################
# Launch AEDT and Circuit
# ~~~~~~~~~~~~~~~~~~~~~~~
# The :class:`pyaedt.Desktop` class initializes AEDT and starts it on a specified version in 
# a specified graphical mode. The Boolean parameter ``NewThread`` defines whether
# to create a new instance of AEDT or try to connect to existing instance of it.

d = Desktop(desktopVersion, NonGraphical, NewThread)
aedtapp = Circuit()

###############################################################################
# Create a Circuit Setup
# ~~~~~~~~~~~~~~~~~~~~~~
# This method creates and customizes a Linear Network Analysis (LNA) setup.

setup1 = aedtapp.create_setup("MyLNA")
setup1.SweepDefinition = [('Variable', 'Freq'), ('Data', 'LINC 0GHz 4GHz 10001'), ('OffsetF1', False),
                          ('Synchronize', 0)]
setup1.update()

###############################################################################
# Create Components
# ~~~~~~~~~~~~~~~~~
# These methods create components, such as inductors, resistors, and capacitors.

myindid, myind = aedtapp.modeler.components.create_inductor("L1", 1e-9, 0, 0)
myresid, myres = aedtapp.modeler.components.create_resistor("R1", 50, 0.0254, 0)
mycapid, mycap = aedtapp.modeler.components.create_capacitor("C1", 1e-12, 0.0400, 0)

###############################################################################
# Get Component Pins
# ~~~~~~~~~~~~~~~~~~
# This method gets all pins of a specified component.

pins_res = aedtapp.modeler.components.get_pins(myres)

ind1 = aedtapp.modeler.components[myind]
res1 = aedtapp.modeler.components[myres]

###############################################################################
# Create a Port and a Ground
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# These methods create a port and a ground, which are needed for a circuit anlaysis.

portid, portname = aedtapp.modeler.components.create_iport("myport", -0.0254, 0)
gndid, gndname = aedtapp.modeler.components.create_gnd(0.0508, -0.00254)
###############################################################################
# Connect Components
# ~~~~~~~~~~~~~~~~~~
# This method connects components with wires.

aedtapp.modeler.connect_schematic_components(portid, myindid)
aedtapp.modeler.connect_schematic_components(myindid, myresid, pinnum_second=2)
aedtapp.modeler.connect_schematic_components(myresid, mycapid, pinnum_first=1)
aedtapp.modeler.connect_schematic_components(mycapid, gndid)

###############################################################################
# Add a Transient Setup
# ~~~~~~~~~~~~~~~~~~~~~
# This method adds a transient setup.

setup2 = aedtapp.create_setup("MyTransient", aedtapp.SimulationSetupTypes.NexximTransient)
setup2.TransientData = ["0.01ns", "200ns"]
setup2.update()
setup3 = aedtapp.create_setup("MyDC", aedtapp.SimulationSetupTypes.NexximDC)

###############################################################################
# Solve the Transient Setup
# ~~~~~~~~~~~~~~~~~~~~~~~~
# This method solves the transient setup.

aedtapp.analyze_setup("MyLNA")

aedtapp.export_fullwave_spice()
###############################################################################
# Close AEDT
# ~~~~~~~~~~
# After the simulaton is completed, you can close AEDT or release it using the 
# :func:`pyaedt.Desktop.release_desktop` method.
# All methods provide for saving the project before exiting.
if os.name != "posix":
    d.force_close_desktop()
