# ------------------------------------------------------------------------------
#
# This Example shows how to create a fully parametrized HeatSink in Icepak
#
# -------------------------------------------------------------------------------
import os
from pyaedt.core import Icepak
from pyaedt.core import Desktop
from pyaedt.core.generic.general_methods import generate_unique_name

project_dir = os.path.join(os.environ['TEMP'], generate_unique_name('Example', n=16))
if not os.path.exists(project_dir):
    os.makedirs(project_dir)
print('project_dir: ' + project_dir)
project_name = "Test_Exercise12"
project_file = os.path.join(project_dir, project_name + ".aedt")

desktopVersion = "2021.1"
d = Desktop(desktopVersion)
ipk = Icepak()

ipk.create_parametric_fin_heat_sink(hs_height=400, hs_width=400)
ipk.save_project(project_file)
pass
