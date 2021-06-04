"""

Maxwell 2D Analysis
--------------------------------------------
This tutorial shows how you can use PyAedt to create a project in
in Maxwell2D and run a simulation
"""

import sys
import os
import pathlib
import shutil
import time
import numpy as np
import matplotlib.pyplot as plt
import shutil
local_path = os.path.abspath('')
module_path = pathlib.Path(local_path)
root_path = module_path.parent.parent
root_path2 = root_path.parent
sys.path.append(os.path.join(root_path))
sys.path.append(os.path.join(root_path2))
example_path =os.path.join(module_path.parent,"Examples","Examples_Files")
from pyaedt import Desktop
from pyaedt import Maxwell2d
from pyaedt import generate_unique_name
project_dir = os.path.join(os.environ["TEMP"], generate_unique_name("Example"))
if not os.path.exists(project_dir): os.makedirs(project_dir)
print(project_dir)
###############################################################################
# NonGraphical
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Change Boolean to False to open AEDT in graphical mode
NonGraphical = True

if not "oDesk" in dir():
    oDesk = Desktop(specified_version="2021.1", NG=NonGraphical, AlwaysNew=False)

##################################################
# 2. Insert a Maxwell design and instantiate Geometry modeler.

m2d=Maxwell2d(solution_type="TransientXY")
m2d.save_project(os.path.join(project_dir,"M2d.aedt"))
id1=m2d.modeler.primitives.create_rectangle([0,0,0],[20,10],"Rectangle1", "copper")
m2d.modeler.duplicate_along_line(id1, [14,0,0])

m2d.modeler.primitives.create_region([100,100,100,100,100,100])
m2d.assign_winding(["Rectangle1", "Rectangle1_1"], name="PHA")
m2d.assign_balloon(m2d.modeler.primitives["Region"].edges)

setup = m2d.create_setup()
setup.props["StopTime"] ="0.02s"
setup.props["TimeStep"] = "0.0002s"
setup.props["SaveFieldsType"] = "Every N Steps"
setup.props["N Steps"] = "1"
setup.props["Steps From"] ="0s"
setup.props["Steps To"] = "0.002s"
setup.update()
m2d.post.create_rectangular_plot("InputCurrent(PHA)",primary_sweep_variable="Time", families_dict={"Time":["All"]}, plotname="Winding Plot 1")
##################################################
# 3. Solve the Model

m2d.analyse_nominal()

##################################################
# 3. Create the Output


import time
start = time.time()
cutlist = ["Global:XY"]
face_lists = m2d.modeler.primitives.get_object_faces("Rectangle1")
face_lists += m2d.modeler.primitives.get_object_faces("Rectangle1_1")
timesteps=[str(i*1e-3)+"s" for i in range(21)]

animatedGif=m2d.post.animate_fields_from_aedtplt_2("Mag_B", face_lists, "Surface", intrinsic_dict={'Time': '0s'}, variation_variable="Time",variation_list=timesteps, off_screen=True, export_gif=True)



###########################################################################
# Save the project and close it.

oDesk.force_close_desktop()
