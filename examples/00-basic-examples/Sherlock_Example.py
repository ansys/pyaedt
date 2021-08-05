"""
Icepack Setup from Sherlock Inputs
----------------------------------
This example shows how to create an Icepak project starting from Sherlock files (STEP and CSV) and AEDB board.
"""
# sphinx_gallery_thumbnail_path = 'Resources/sherlock.png'

import time
import os
import datetime

from pyaedt import examples, generate_unique_name
input_dir = examples.download_sherlock()
if os.name == "posix":
    tmpfold = os.environ["TMPDIR"]
else:
    tmpfold = os.environ["TEMP"]

temp_folder = os.path.join(tmpfold, generate_unique_name("Example"))
if not os.path.exists(temp_folder): os.makedirs(temp_folder)
print(temp_folder)

###############################################################################
# Input variables.
# This lists all input variables needed to run the example.

material_name = 'MaterialExport.csv'
component_properties =  'TutorialBoardPartsList.csv'
component_step = 'TutorialBoard.stp'
aedt_odb_project = 'SherlockTutorial.aedt'
aedt_odb_design_name = "PCB"
stackup_thickness = 2.11836
outline_polygon_name = "poly_14188"

###############################################################################
# Import PyAEDT and launch AEDT.
# This example launches AEDT 2021.1 in graphical mode.

from pyaedt import Icepak
from pyaedt import Desktop

###############################################################################
# Launch AEDT in Non-Graphical mode
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Change the Boolean parameter ``NonGraphical`` to ``False`` to launch AEDT in 
# graphical mode.

NonGraphical = False

d=Desktop("2021.1", NG=NonGraphical)

start = time.time()
material_list = os.path.join(input_dir, material_name)
component_list = os.path.join(input_dir, component_properties)
validation = os.path.join(temp_folder, "validation.log")
file_path = os.path.join(input_dir, component_step)
project_name = os.path.join(temp_folder, component_step[:-3] + "aedt")

###############################################################################
# Create an Icepak project and delete the region to improve performance.

ipk = Icepak()

###############################################################################
# Remove the region and disable autosave to speed up the import.

d.disable_autosave()
ipk.modeler.primitives.delete("Region")
component_name = "from_ODB"

###############################################################################
# Import a PCB from AEDB file.

odb_path = os.path.join(input_dir, aedt_odb_project)
ipk.create_pcb_from_3dlayout(component_name, odb_path, aedt_odb_design_name, extenttype="Polygon",
                               outlinepolygon=outline_polygon_name)

###############################################################################
# Create an offset coordinate system to match odb++ with the Sherlock STEP file.

ipk.modeler.create_coordinate_system([0, 0, stackup_thickness/2], mode="view", view="XY")

###############################################################################
# Import a CAD file.

ipk.modeler.import_3d_cad(file_path, refresh_all_ids=False)

###############################################################################
# Save the CAD file and refresh properties from AEDT file parsing.

ipk.save_project(project_name, refresh_obj_ids_after_save=True)

###############################################################################
# Remove PCB objects.

ipk.modeler.primitives.delete_objects_containing("pcb", False)

###############################################################################
# Create a region.

ipk.modeler.create_air_region(*[20,20,300,20,20,300])

###############################################################################
# Assign materials.

ipk.assignmaterial_from_sherlock_files(component_list, material_list)

###############################################################################
# Delete objects with no material assignments.

no_material_objs = ipk.modeler.primitives.get_objects_by_material("")
ipk.modeler.primitives.delete(no_material_objs)
ipk.save_project()

###############################################################################
# Assign power to component blocks.

all_objects = ipk.modeler.primitives.object_names

###############################################################################
# Assign power blocks.

total_power = ipk.assign_block_from_sherlock_file(component_list)

###############################################################################
# Set up boundaries

ipk.mesh.automatic_mesh_pcb(4)

setup1 = ipk.create_setup()
setup1.props["Solution Initialization - Y Velocity"] =  "1m_per_sec"
setup1.props["Radiation Model"] ="Discrete Ordinates Model"
setup1.props["Include Gravity"] =True
setup1.props["Secondary Gradient"] =True
setup1.update()
ipk.assign_openings(ipk.modeler.primitives.get_object_faces("Region"))

###############################################################################
# Check for intersection using validation and fix it by assigning priorities.

ipk.assign_priority_on_intersections()

###############################################################################
# Save and close the project.

ipk.save_project()


end = time.time()-start
if os.name != "posix":
    ipk.close_desktop()
print("Elapsed time: {}".format(datetime.timedelta(seconds=end)))
print("Project Saved in {} ".format(temp_folder))
