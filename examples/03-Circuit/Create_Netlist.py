"""
Circuit: Netlist to Schematic Import
------------------------------------
# This example shows how to import Netlist data into a
# Circuit design. Supported Netlist files are HSPICE and,
# partially, Mentor.
"""
# sphinx_gallery_thumbnail_path = 'Resources/schematic.png'

import os

###############################################################################
# Import Packages
# ~~~~~~~~~~~~~~~
# Set the local path to the path for PyAEDT.

from pyaedt import examples
import tempfile

netlist = examples.download_netlist()
from pyaedt import generate_unique_name

tmpfold = tempfile.gettempdir()
temp_folder = os.path.join(tmpfold, generate_unique_name("Example"))
if not os.path.exists(temp_folder):
    os.makedirs(temp_folder)
myfile = os.path.join(netlist)
print(temp_folder)


###############################################################################
# Import the main classes needed: :class:`pyaedt.Desktop` and :class:`pyaedt.Circuit`.

from pyaedt import Circuit
from pyaedt import Desktop

###############################################################################
# Launch AEDT and Circuit
# ~~~~~~~~~~~~~~~~~~~~~~~
# This example launches AEDT 2022R2 in graphical mode.

# This examples uses SI units.

desktopVersion = "2022.2"



##########################################################
# Set Non Graphical Mode.
# Default is False

non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")
NewThread = True

###############################################################################
# Launch AEDT and Circuit
# ~~~~~~~~~~~~~~~~~~~~~~~
# The :class:`pyaedt.Desktop` class initializes AEDT and starts it on a specified version in
# a specified graphical mode. The Boolean parameter ``NewThread`` defines whether
# to create a new instance of AEDT or try to connect to existing instance of it.


desktop = Desktop(desktopVersion, non_graphical, NewThread)
aedtapp = Circuit()

###############################################################################
# Save the Project to the Temp Folder
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The temp folder can be changed.

aedtapp.save_project(os.path.join(temp_folder, "my_firt_netlist.aedt"))

###############################################################################
# Define a Design Variable
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Using a ``$`` prefix creates a project variable.

aedtapp["Voltage"] = "5"

###############################################################################
# Create a Schematic from a Netlist File
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This method reads the netlist file and parses it. All components will be parsed
# but only specified categories will be mapped. In particular, R, L, C, Q, U, J, V,
# and I components will be mapped.

aedtapp.create_schematic_from_netlist(myfile)

###############################################################################
# Close the Project
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# After adding any other desired functionalities, close the project.

if os.name != "posix":
    desktop.release_desktop()
