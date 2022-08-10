"""
Circuit: netlist to schematic import
------------------------------------
This example shows how you can import netlist data into a circuit design.
HSPICE files are fully supported. Mentor files are partially supported.
"""

###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports and set paths.

import os

# Import required modules
from pyaedt import examples
from pyaedt import generate_unique_project_name
netlist = examples.download_netlist()

project_name = generate_unique_project_name()
print(project_name)


###############################################################################
# Import main classes
# ~~~~~~~~~~~~~~~~~~~
# Import the main classes that are needed: :class:`pyaedt.Desktop` and :class:`pyaedt.Circuit`.

from pyaedt import Circuit
from pyaedt import Desktop

###############################################################################
# Launch AEDT
# ~~~~~~~~~~~
# Launch AEDT 2022 R2 in graphical mode. This example uses SI units.

desktopVersion = "2022.2"


###############################################################################
# Set non-graphical mode
# ~~~~~~~~~~~~~~~~~~~~~~
# Set non-graphical mode. ``"PYAEDT_NON_GRAPHICAL"`` is needed to generate
# documentation only.
# You can set ``non_graphical`` either to ``True`` or ``False``.
# The Boolean parameter ``NewThread`` defines whether to create a new instance
# of AEDT or try to connect to an existing instance of it.

non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")
NewThread = True

###############################################################################
# Launch AEDT with Circuit
# ~~~~~~~~~~~~~~~~~~~~~~~
# Launch AEDT with Circuit. The :class:`pyaedt.Desktop` class initializes AEDT
# and starts it on the specified version in the specified graphical mode.

desktop = Desktop(desktopVersion, non_graphical, NewThread)
aedtapp = Circuit(projectname=project_name)

###############################################################################
# Define variable
# ~~~~~~~~~~~~~~~
# Define a design variable by using a ``$`` prefix.

aedtapp["Voltage"] = "5"

###############################################################################
# Create schematic from netlist file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a schematic from a netlist file. The ``create_schematic_from_netlist``
# method reads the netlist file and parses it. All components are parsed
# but only these categories are mapped: R, L, C, Q, U, J, V, and I.

aedtapp.create_schematic_from_netlist(netlist)

###############################################################################
# Close project and release AEDT
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# After adding any other desired functionalities, close the project and release
# AEDT.

if os.name != "posix":
    desktop.release_desktop()
