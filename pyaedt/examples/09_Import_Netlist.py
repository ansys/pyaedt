# ------------------------------------------------------------------------------
#
# This Example shows how to import an HSPICE Netlist using pyaedt
#
# -------------------------------------------------------------------------------
import os
from pyaedt.core import Circuit
from pyaedt.core import Desktop
from pyaedt.core.generic.general_methods import generate_unique_name

project_dir = os.path.join(os.environ['TEMP'], generate_unique_name('Example', n=16))
if not os.path.exists(project_dir):
    os.makedirs(project_dir)
print('project_dir: ' + project_dir)
project_name = "Test_Exercise09"
project_file = os.path.join(project_dir, project_name + ".aedt")


local_path = os.path.dirname(os.path.realpath(__file__))
desktopVersion = "2021.1"


NonGraphical = False
NewThread = False
myfile = os.path.join(local_path, "Examples_Files", "netlist_small.cir")
with Desktop(desktopVersion, NonGraphical, NewThread):
    aedtapp = Circuit()
    aedtapp["definire"] = "0.01"
    aedtapp.save_project(project_file)
    aedtapp.create_schematic_from_netlist(myfile)
    aedtapp.modeler.oeditor.ZoomToFit()
    # simpapp = Simplorer()
    # simpapp.create_schematic_from_netlist(myfile)
    # aedtapp.close_project()

pass
