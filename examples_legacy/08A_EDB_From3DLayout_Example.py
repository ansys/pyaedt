# ------------------------------------------------------------------------------
#
# This Example shows how to use HFSS3DLayout to do basic layout operations. To be noted how slower it is compared to examples 08B
#
# -------------------------------------------------------------------------------
import os
import shutil
import time
# from pyaedt.EDB import EDB  # EDB class is part of modeler Module and edb_core is opened in Readonly
from pyaedt import Hfss3dLayout
from pyaedt import Desktop
from pyaedt.generic.general_methods import generate_unique_name

project_dir = os.path.join(os.environ['TEMP'], generate_unique_name('Example', n=16))
if not os.path.exists(project_dir):
    os.makedirs(project_dir)
print('project_dir: ' + project_dir)

desktopVersion = "2021.1"
oDesktop = None
NonGraphical = False
NewThread = False
project_name = "Galileo"
project = os.path.join(os.path.dirname(__file__), "Examples_Files", project_name)
aedtproject = os.path.join(project_dir, "Galileo.aedt")
aedbproject = os.path.join(project_dir, "Galileo.aedb")
shutil.copy2(project + ".aedt", project_dir)
if not os.path.exists(aedbproject):
    os.mkdir(aedbproject)
shutil.copy2(os.path.join(project + ".aedb", "edb.def"), os.path.join(aedbproject, "edb.def"))
start = time.time()
print("Example Using HFSS3DLayout")
with Desktop(desktopVersion, NonGraphical, NewThread):
    desktop_time = time.time() -start  # Layout class. EDB class is part of modeler Module and edb_core is opened in Readonly
    hfss3dlayout = Hfss3dLayout(aedtproject)
    load_time = time.time() - start - desktop_time
    comp = hfss3dlayout.modeler.edb.get_component_by_name("J1")
    pin = hfss3dlayout.modeler.edb.get_pin_from_component(comp, pinName="1")
    myvianame = hfss3dlayout.modeler.edb.create_padstack()
    hfss3dlayout.modeler.edb.save_edb()
    stackup = hfss3dlayout.modeler.edb.stackup_layers
    component_list = hfss3dlayout.modeler.edb.components
    component_info = hfss3dlayout.modeler.edb.get_component_info("J1")
    vias = hfss3dlayout.modeler.edb.padstacks
    viasinfo = hfss3dlayout.modeler.edb.get_padstack_info()
    signalnets = hfss3dlayout.modeler.edb.signal_nets
    powernets = hfss3dlayout.modeler.edb.power_nets
    # I close the project in aedt before creating the padstack with EDB
    hfss3dlayout.close_project(hfss3dlayout.project_name, False)
    endtime = time.time() - start - desktop_time
print("Destok Launch Time " + str(desktop_time))
print("Process Time" + str(endtime))
print("Total Time" + str(endtime+desktop_time))

# os.remove(os.path.join(project_dir, project_name+".aedt"))
# os.remove(os.path.join(project_dir, project_name+".aedb", "edb.def"))

