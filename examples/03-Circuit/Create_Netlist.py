"""
Circuit: netlist to schematic iport
------------------------------------
# This example shows how to import netlist data into a circuit design.
# HSPICE files are supported. Mentor files are partially supported.
"""

###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports and set paths.

# sphinx_gallery_thumbnail_path = 'Resources/schematic.png'
import os

# Import required modules
from pyaedt import examples
import tempfile

netlist = examples.download_netlist()
from pyaedt import generate_unique_name

# Set local path to path for PyAEDT
tmpfold = tempfile.gettempdir()
temp_folder = os.path.join(tmpfold, generate_unique_name("Example"))
if not os.path.exists(temp_folder):
    os.makedirs(temp_folder)
myfile = os.path.join(netlist)
print(temp_folder)


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


##########################################################
# Set non-graphical mode
# ~~~~~~~~~~~~~~~~~~~~~~
# Set non-graphical mode. The default is ``False``.

non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")
NewThread = True

###############################################################################
# Launch AEDT with Circuit
# ~~~~~~~~~~~~~~~~~~~~~~~
# Launch AEDT with Circuit. The :class:`pyaedt.Desktop` class initializes AEDT
# and starts it on the specified version in the specified graphical mode. The Boolean
# parameter ``NewThread`` defines whether to create a new instance of AEDT or try
# to connect to an existing instance of it.

desktop = Desktop(desktopVersion, non_graphical, NewThread)
aedtapp = Circuit()

###############################################################################
# Save project to temporary folder
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Save the project to the temporary folder. You can change this folder.

aedtapp.save_project(os.path.join(temp_folder, "my_firt_netlist.aedt"))

###############################################################################
# Define design variable
# ~~~~~~~~~~~~~~~~~~~~~~
# Define a design variable by using a ``$`` prefix.

aedtapp["Voltage"] = "5"

###############################################################################
# Create schematic from netlist file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a schematic from a netlist file. The ``create_schematic_from_netlist``
# method reads the netlist file and parses it. All components are parsed
# but only these specified categories are mapped: R, L, C, Q, U, J, V, and I.

aedtapp.create_schematic_from_netlist(myfile)

###############################################################################
# Close project and release AEDT
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# After adding any other desired functionalities, close the project and release
# AEDT.

if os.name != "posix":
    desktop.release_desktop()
