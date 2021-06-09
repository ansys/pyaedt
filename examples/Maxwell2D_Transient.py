"""

Maxwell 2D Analysis
--------------------------------------------
This tutorial shows how you can use PyAedt to create a project in
in Maxwell2D and run a transient simulation
"""

import os
from pyaedt import Maxwell2d
from pyaedt import generate_unique_name

# could use m2d.temp_directory ??


###############################################################################
# NonGraphical
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Change Boolean to False to open AEDT in graphical mode
NonGraphical = True

##################################################
# Insert a Maxwell design and save project

m2d=Maxwell2d(solution_type="TransientXY", specified_version="2021.1", NG=NonGraphical)
# TODO avoid the environmnent variable ? Maybe even say if the
project_dir = m2d.generate_temp_project_directory(name="Example")
m2d.save_project(os.path.join(project_dir,"M2d.aedt"))

###################################################
#  create rectangle and duplicate it

id1=m2d.modeler.primitives.create_rectangle([0,0,0],[20,10],"Rectangle1", "copper")
m2d.modeler.duplicate_along_line(id1, [14,0,0])

###################################################
#  create air region

m2d.modeler.primitives.create_region([100,100,100,100,100,100])

###################################################
#  Assign Windings to sheets and balloon to air region

m2d.assign_winding(["Rectangle1", "Rectangle1_1"], name="PHA")
m2d.assign_balloon(m2d.modeler.primitives["Region"].edges)

###############################################################################
# Add a transient Setup
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This method add a transient setup

setup = m2d.create_setup()
setup.props["StopTime"] ="0.02s"
setup.props["TimeStep"] = "0.0002s"
setup.props["SaveFieldsType"] = "Every N Steps"
setup.props["N Steps"] = "1"
setup.props["Steps From"] ="0s"
setup.props["Steps To"] = "0.002s"
setup.update()

###############################################################################
# Create AEDT Rectangular Plot
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This method add a rectangular plot to Aedt

m2d.post.create_rectangular_plot("InputCurrent(PHA)",primary_sweep_variable="Time", families_dict={"Time":["All"]}, plotname="Winding Plot 1")

##################################################
# Solve the Model

m2d.analyse_nominal()

##################################################
# Create the Output and plot it using pyvista

import time
start = time.time()
cutlist = ["Global:XY"]
face_lists = m2d.modeler.primitives.get_object_faces("Rectangle1")
face_lists += m2d.modeler.primitives.get_object_faces("Rectangle1_1")
timesteps=[str(i*1e-3)+"s" for i in range(21)]

animatedGif=m2d.post.animate_fields_from_aedtplt_2("Mag_B", face_lists, "Surface", intrinsic_dict={'Time': '0s'}, variation_variable="Time",variation_list=timesteps, off_screen=True, export_gif=True)


###############################################
# Close AEDT

m2d.close_desktop()
