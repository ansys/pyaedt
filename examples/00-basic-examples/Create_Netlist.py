"""
Netlist Example Analysis
------------------------
# This example shows how to import Netlist data into a 
# Circuit design. Supported Netlist files are HSPICE and, 
# partially, Mentor.
"""

import sys
import os

###############################################################################
# Import packages.
# Set the local path to the path for AEDTLib.

from pyaedt import examples
netlist = examples.download_netlist()
from pyaedt import generate_unique_name

if os.name == "posix":
    tmpfold = os.environ["TMPDIR"]
else:
    tmpfold = os.environ["TEMP"]

temp_folder = os.path.join(tmpfold, generate_unique_name("Example"))
if not os.path.exists(temp_folder): os.makedirs(temp_folder)
myfile = os.path.join(netlist)
print(temp_folder)

###############################################################################
# Import the main classes needed: `Desktop` and `Circuit`.

from pyaedt import Circuit
from pyaedt import Desktop

###############################################################################
# Launch AEDT and Circuit.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example launches AEDT 2021.1 in graphical mode.

# This examples uses SI units.

desktopVersion = "2021.1"


###############################################################################
# Launch AEDT in non-graphical mode.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Change the Boolean parameter ``NonGraphical`` to ``False`` to launch AEDT in 
# graphical mode.

NonGraphical = False
NewThread = True

###############################################################################
# Launch AEDT and Circuit.
# ~~~~~~~~~~~~~~~~~~~~~~~~
# The `Desktop` class initializes AEDT and starts it on a specified version in 
# a specified graphical mode. The Boolean parameter ``NewThread`` defines whether
# to create a new instance of AEDT or try to connect to existing instance of it.


desktop = Desktop(desktopVersion, NonGraphical, NewThread)
aedtapp = Circuit()

###############################################################################
# Save the project to the temp folder, which can be changed.

aedtapp.save_project(os.path.join(temp_folder, "my_firt_netlist.aedt"))


###############################################################################
# Define a design variable.
# Using a ``$`` prefix creates a project variable.

aedtapp["Voltage"]="5"


###############################################################################
# Create a schematic from a netlist file.
# This method reads the netlist file and parses it. All components will be parsed 
# but only specified categories will be mapped. In particular, R, L, C, Q, U, J, V, 
# and I components will be mapped.

aedtapp.create_schematic_from_netlist(myfile)

###############################################################################
# Close the project (after adding any other desired functionalities).

if os.name != "posix":
    aedtapp.close_project()
    desktop.force_close_desktop()
