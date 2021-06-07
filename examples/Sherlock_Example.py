"""

Icepack Setup From Sherlock Inputs
--------------------------------------------
This Example shows how to create an Icepak Project starting from Sherlock Files (step and csv) and aedb board 
"""



import time
import os
import datetime
import pathlib
import sys

local_path = os.path.abspath('')
module_path = pathlib.Path(local_path)
aedt_lib_path = module_path.parent
sys.path.append(os.path.join(aedt_lib_path))
from pyaedt import examples, generate_unique_name
input_dir = examples.download_sherlock()
temp_folder = os.path.join(os.environ["TEMP"], generate_unique_name("Example"))
if not os.path.exists(temp_folder): os.makedirs(temp_folder)
print(temp_folder)

######################################
# Input Variables
# this lists all input variables needed to the example to run

material_name = 'MaterialExport.csv'
component_properties =  'TutorialBoardPartsList.csv'
component_step = 'TutorialBoard.stp'
aedt_odb_project = 'SherlockTutorial.aedt'
aedt_odb_design_name = "PCB"
stackup_thickness = 2.11836
outline_polygon_name = "poly_14188"

######################################
# Import pyaedt and start AEDT
# AEDT will run in nongraphical mode

from pyaedt import Icepak
from pyaedt import Desktop

###############################################################################
# NonGraphical
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Change Boolean to False to open AEDT in graphical mode

NonGraphical = True

d=Desktop("2021.1", NG=NonGraphical)

start = time.time()
material_list = os.path.join(input_dir, material_name)
component_list = os.path.join(input_dir, component_properties)
validation = os.path.join(temp_folder, "validation.log")
file_path = os.path.join(input_dir, component_step)
project_name = os.path.join(temp_folder, component_step[:-3] + "aedt")


############################################################################
# Create an Icepak project and delete Region to improve performances

ipk = Icepak()

############################################################################
# Removing region and disabling autosave to speedup import

d.disable_autosave()
ipk.modeler.primitives.delete("Region")
component_name = "from_ODB"

######################################
# Import PCB from aedb file

odb_path = os.path.join(input_dir, aedt_odb_project)
ipk.create_pcb_from_3dlayout(component_name, odb_path, aedt_odb_design_name,extenttype="Polygon",
                               outlinepolygon=outline_polygon_name)

############################################################################
# create an offset Coordinate system to match odb++ with sherlock step file


ipk.modeler.coordinate_system.create([0,0,stackup_thickness/2],view="XY")

######################################
# import cad


ipk.modeler.import_3d_cad(file_path, refresh_all_ids=False)

############################################################################
#save cad and refresh properties from aedt file parsing

ipk.save_project(project_name, refresh_obj_ids_after_save=True)

######################################
# removing pcb objects

ipk.modeler.primitives.delete_objects_containing("pcb", False)

######################################
# Creating Region

ipk.modeler.create_air_region(*[20,20,300,20,20,300])

######################################
# assigning Materials

ipk.assignmaterial_from_sherlock_files(component_list, material_list)

############################################################################
# Deleting Object with no material Assignment

no_material_objs = ipk.modeler.primitives.get_objects_by_material("")
ipk.modeler.primitives.delete(no_material_objs)
ipk.save_project()

######################################
# Assign Power to Component Blocks


all_objects = ipk.modeler.primitives.get_all_objects_names()

######################################
# Assign Power blocks
total_power = ipk.assign_block_from_sherlock_file(component_list)

######################################
# Setup and Boundaries

ipk.mesh.automatic_mesh_pcb(4)

setup1 = ipk.create_setup()
setup1.props["Solution Initialization - Y Velocity"] =  "1m_per_sec"
setup1.props["Radiation Model"] ="Discrete Ordinates Model"
setup1.props["Include Gravity"] =True
setup1.props["Secondary Gradient"] =True
setup1.update()
ipk.assign_openings(ipk.modeler.primitives.get_object_faces("Region"))

############################################################################
# Check for intersection using Validation and fix it by assigning Priorities


ipk.assign_priority_on_intersections()

######################################
# Saving and closing
ipk.save_project()


end = time.time()-start
ipk.close_desktop()
print("Elapsed time: {}".format(datetime.timedelta(seconds=end)))
print("Project Saved in {} ".format(temp_folder))




