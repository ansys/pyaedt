"""

Circuit Example Analysis
--------------------------------------------
This tutorial shows how you can use PyAedt to create a project in
in NEXXIM Circuit and run a simulation
"""

from pyaedt import Circuit
from pyaedt import Desktop

###############################################################################
# Launch Desktop and Circuit
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This examples will use AEDT 2021.1 in Graphical mode

# This examples will use SI units.

desktopVersion = "2021.1"

###############################################################################
# NonGraphical
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Change Boolean to False to open AEDT in graphical mode

NonGraphical = True
NewThread = False

###############################################################################
# Launch AEDT and Circuit Design
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Desktop Class initialize Aedt and start it on specified version and specified graphical mode. NewThread Boolean variables defines if
# a user wants to create a new instance of AEDT or try to connect to existing instance of it
d = Desktop(desktopVersion, NonGraphical, NewThread)
aedtapp = Circuit()

###############################################################################
# Create Circuit Setup
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This method create and customize a Linear Network Analysis Setup

setup1 = aedtapp.create_setup("MyLNA")
setup1.SweepDefinition = [('Variable', 'Freq'), ('Data', 'LINC 0GHz 4GHz 10001'), ('OffsetF1', False),
                          ('Synchronize', 0)]
setup1.update()

###############################################################################
# Create Components
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This method create components. there are methods to create inductors, resistors or capacitors.

myindid, myind = aedtapp.modeler.components.create_inductor("L1", 1e-9, 0, 0)
myresid, myres = aedtapp.modeler.components.create_resistor("R1", 50, 0.0254, 0)
mycapid, mycap = aedtapp.modeler.components.create_capacitor("C1", 1e-12, 0.0400, 0)

###############################################################################
# Get Components pins
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This method allows to get all pins of specified component

pins_res = aedtapp.modeler.components.get_pins(myres)

ind1 = aedtapp.modeler.components[myind]
res1 = aedtapp.modeler.components[myres]

###############################################################################
# Create Ports
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This method create ports and Ground. those are needed for a circuit anlaysis

portid, portname = aedtapp.modeler.components.create_iport("myport", -0.0254, 0)
gndid, gndname = aedtapp.modeler.components.create_gnd(0.0508, -0.00254)
###############################################################################
# Connect Components
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This method connect components with wires

aedtapp.modeler.connect_schematic_components(portid, myindid)
aedtapp.modeler.connect_schematic_components(myindid, myresid, pinnum_second=2)
aedtapp.modeler.connect_schematic_components(myresid, mycapid, pinnum_first=1)
aedtapp.modeler.connect_schematic_components(mycapid, gndid)

###############################################################################
# Add a transient Setup
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This method add a transient setup

setup2 = aedtapp.create_setup("MyTransient", aedtapp.SimulationSetupTypes.NexximTransient)
setup2.TransientData = ["0.01ns", "200ns"]
setup2.update()
setup3 = aedtapp.create_setup("MyDC", aedtapp.SimulationSetupTypes.NexximDC)

###############################################################################
# Solve Setup
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This method solve transient setup

aedtapp.analyze_setup("MyLNA")

###############################################################################
# Close Desktop
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# After the simulaton is completed user can close the desktop or release it (using release_desktop method).
# All methods give possibility to save projects before exit

d.force_close_desktop()
