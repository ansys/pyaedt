"""
EMIT: Antenna Example
---------------------
This tutorial shows how you can use PyAEDT to create a project in EMIT.
"""
# sphinx_gallery_thumbnail_path = 'Resources/emit.png'
import os
from pyaedt import Emit
from pyaedt import Desktop

###############################################################################
# Initialization Settings
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Change NonGraphical Boolean to False to open AEDT in graphical mode
# With NewThread = False, an existing instance of AEDT will be used, if
# available. This example will use AEDT 2022R2. However this example is supposed to work
# on AEDT 2022R2 and on.


non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")
NewThread = False
desktop_version = "2022.2"


###############################################################################
# Launch AEDT and EMIT Design
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Desktop class initializes AEDT and starts it on specified version and
# specified graphical mode. NewThread Boolean variable defines if a user wants
# to create a new instance of AEDT or try to connect to existing instance of
# it.
d = Desktop(desktop_version, non_graphical, NewThread)
aedtapp = Emit()


###############################################################################
# Create and Connect EMIT Components
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create 3 radios and connect an antenna to each.
rad1 = aedtapp.modeler.components.create_component("UE - Handheld")
ant1 = aedtapp.modeler.components.create_component("Antenna")
if rad1 and ant1:
    ant1.move_and_connect_to(rad1)

rad2 = aedtapp.modeler.components.create_component("GPS Receiver")
ant2 = aedtapp.modeler.components.create_component("Antenna")
if rad2 and ant2:
    ant2.move_and_connect_to(rad2)

rad3 = aedtapp.modeler.components.create_component("Bluetooth")
ant3 = aedtapp.modeler.components.create_component("Antenna")
if rad3 and ant3:
    ant3.move_and_connect_to(rad3)


###############################################################################
# Define Coupling Among the RF Systems
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This portion of the EMIT API is not yet implemented.


###############################################################################
# Run the EMIT Simulation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This portion of the EMIT API is not yet implemented.


###############################################################################
# Close Desktop
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# After the simulaton is completed user can close the desktop or release it
# (using release_desktop method). All methods give possibility to save projects
# before exit.
aedtapp.save_project()
aedtapp.release_desktop(close_projects=True, close_desktop=True)
