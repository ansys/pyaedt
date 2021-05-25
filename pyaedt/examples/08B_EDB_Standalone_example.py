# ------------------------------------------------------------------------------
#
# This Example shows how to use EDB to do basic layout operations. To be noted how fast it is compared to example 08A
#
# -------------------------------------------------------------------------------
import os
import shutil
import time
from pyaedt.core import Edb
from pyaedt.core.generic.general_methods import generate_unique_name

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

# This example runs without HFSS3DLayout class. EDB class is opened directly and edb_core is opened in WriteMode
edb = Edb(aedbproject, 'Galileo_G87173_204', isreadonly=False)
comp = edb.get_component_by_name("J1")
pin = edb.get_pin_from_component(comp.GetName(), pinName="1")
stackup = edb.stackup_layers
component_list = edb.components
component_info = edb.get_component_info("J1")
edb.create_padstack()
vias = edb.padstacks
viasinfo = edb.get_padstack_info()
signalnets = edb.signal_nets
powernets = edb.power_nets
edb.save_edb()
edb.close_edb()

endtime = time.time() - start
print("Process Time"+str(endtime))
