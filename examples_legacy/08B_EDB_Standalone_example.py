# ------------------------------------------------------------------------------
#
# This Example shows how to use EDB to do basic layout operations. To be noted how fast it is compared to examples 08A
#
# -------------------------------------------------------------------------------
import os
import shutil
import time
from pyaedt import Edb
from pyaedt.generic.general_methods import generate_unique_name

project_dir = os.path.join(os.environ['TEMP'], generate_unique_name('Example', n=16))
if not os.path.exists(project_dir):
    os.makedirs(project_dir)
print('project_dir: ' + project_dir)

print("Example Using EDB")

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

# This examples runs without HFSS3DLayout class. EDB class is opened directly and edb_core is opened in WriteMode
edb = Edb(aedbproject, 'Galileo_G87173_204', isreadonly=False)
comp = edb.core_components.get_component_by_name("J1")
pin = edb.core_components.get_pin_from_component(comp.GetName(), pinName="1")
stackup = edb.core_components.stackup_layers
component_list = edb.core_components.components
component_info = edb.core_components.get_component_info("J1")
edb.core_padstack.create_padstack()
vias = edb.core_padstack.padstacks
viasinfo = edb.core_padstack.get_padstack_info()
signalnets = edb.core_nets.signal_nets
powernets = edb.core_nets.power_nets
edb.save_edb()
edb.close_edb()

endtime = time.time() - start
print("Process Time"+str(endtime))
