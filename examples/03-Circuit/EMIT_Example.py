"""
EMIT: antenna
---------------------
This tutorial shows how you can use PyAEDT to create a project in EMIT for
a simulation of an attenna.
"""
###############################################################################
# sphinx_gallery_thumbnail_path = 'Resources/emit.png'
# Perform required inputs
# ~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports.

import os
from pyaedt import Emit
from pyaedt import Desktop

###############################################################################
# Specify initialization settings
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Change the ``non_graphical`` Boolean variable to ``False`` to open AEDT in
# graphical mode. With ``NewThread = False``, an existing instance of AEDT
# is used if one is available. The following code uses AEDT 2022 R2.

non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")
NewThread = False
desktop_version = "2022.2"


###############################################################################
# Launch AEDT with EMIT
# ~~~~~~~~~~~~~~~~~~~~~
# Launch AEDT with EMIT. The ``Desktop`` class initializes AEDT and starts it
# on the specified version and in the specified graphical mode. The ``NewThread``
# Boolean variable defines whether to create a new instance of AEDT or try to
# connect to existing instance of it if one is available.

d = Desktop(desktop_version, non_graphical, NewThread)
aedtapp = Emit()


###############################################################################
# Create and connect EMIT components
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create three radios and connect an antenna to each one.

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
# Define coupling among RF systems
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Define the coupling among the RF systems. This portion of the EMIT API is not
# yet implemented.


###############################################################################
# Run EMIT simulation
# ~~~~~~~~~~~~~~~~~~~
# Run the EMIT simulation. This portion of the EMIT API is not yet implemented.


###############################################################################
# Save project and close AEDT
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# After the simulaton completes, you can close AEDT or release it using the
# :func:`pyaedt.Desktop.force_close_desktop` method.
# All methods provide for saving the project before closing.

aedtapp.save_project()
aedtapp.release_desktop(close_projects=True, close_desktop=True)
