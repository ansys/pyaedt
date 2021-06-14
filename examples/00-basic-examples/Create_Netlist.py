"""

Netlist Example Analysis
--------------------------------------------
# This Example shows how to Import Netlist in AEDT Nexxim
Netlists supported are HSPICE and, partially, Mentor
"""



import sys
import os
import pathlib

#########################################################
# Import Packages
# Setup The local path to the Path Containing AEDTLIb


local_path = os.path.abspath('')
module_path = pathlib.Path(local_path)
aedt_lib_path = module_path.parent.parent.parent
from pyaedt import examples
netlist = examples.download_netlist()
sys.path.append(os.path.join(aedt_lib_path))
from pyaedt import generate_unique_name
temp_folder = os.path.join(os.environ["TEMP"], generate_unique_name("Example"))
if not os.path.exists(temp_folder): os.makedirs(temp_folder)
myfile = os.path.join(netlist)
print(temp_folder)


#########################################################
# Import of Main Classes needed: Desktop and Circuit


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




desktop = Desktop(desktopVersion, NonGraphical, NewThread)
aedtapp = Circuit()


#########################################################
# Save Project to temp folder. Can be changed

aedtapp.save_project(os.path.join(temp_folder, "my_firt_netlist.aedt"))



#########################################################
# Define a design variable
# using $ prefix user will create a project variable

aedtapp["Voltage"]="5"


#########################################################
# Launch command to create Schematic
# This method will read the netlist and parse it. All components will be parsed but only speficied
# categories will be mapped. In particular : R, L, C, Q, U, J, V, I components will be mapped

aedtapp.create_schematic_from_netlist(myfile)



#########################################################
# Close Project....or continue adding functionalities

aedtapp.close_project()




desktop.force_close_desktop()

#########################################################





