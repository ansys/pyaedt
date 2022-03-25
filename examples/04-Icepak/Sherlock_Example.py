"""
Icepack: Setup from Sherlock Inputs
-----------------------------------
This example shows how to create an Icepak project starting from Sherlock
# files (STEP and CSV) and an AEDB board.
"""

import time
import os
import tempfile
import datetime

from pyaedt import examples, generate_unique_name

input_dir = examples.download_sherlock()
tmpfold = tempfile.gettempdir()


temp_folder = os.path.join(tmpfold, generate_unique_name("Example"))
if not os.path.exists(temp_folder):
    os.makedirs(temp_folder)
print(temp_folder)

###############################################################################
# Input Variables
# ~~~~~~~~~~~~~~~
# This example creates all input variables needed to run the example.

material_name = "MaterialExport.csv"
component_properties = "TutorialBoardPartsList.csv"
component_step = "TutorialBoard.stp"
aedt_odb_project = "SherlockTutorial.aedt"
aedt_odb_design_name = "PCB"
stackup_thickness = 2.11836
outline_polygon_name = "poly_14188"

###############################################################################
# Import PyAEDT and Launch AEDT
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example launches AEDT 2022R1 in graphical mode.

from pyaedt import Icepak
from pyaedt import Desktop

###############################################################################
# Launch AEDT in Non-Graphical Mode
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# You can change the Boolean parameter ``NonGraphical`` to ``False`` to launch
# AEDT in graphical mode.

NonGraphical = False

d = Desktop("2022.1", non_graphical=NonGraphical, new_desktop_session=True)

start = time.time()
material_list = os.path.join(input_dir, material_name)
component_list = os.path.join(input_dir, component_properties)
validation = os.path.join(temp_folder, "validation.log")
file_path = os.path.join(input_dir, component_step)
project_name = os.path.join(temp_folder, component_step[:-3] + "aedt")

###############################################################################
# Create an Icepak Project
# ~~~~~~~~~~~~~~~~~~~~~~~~
# This command create an Icepak project

ipk = Icepak()

###############################################################################
# Delete the Region to Improve Performance
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example remove the region and disables autosave to speed up the import.

d.disable_autosave()
ipk.modeler.delete("Region")
component_name = "from_ODB"

###############################################################################
# Import a PCB from an AEDB File
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example imports a PCB from an AEDB file.

odb_path = os.path.join(input_dir, aedt_odb_project)
ipk.create_pcb_from_3dlayout(
    component_name, odb_path, aedt_odb_design_name, extenttype="Polygon", outlinepolygon=outline_polygon_name
)

###############################################################################
# Create an Offset Ccoordinate System
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This command create an offset coordinate system to match odb++ with the
# Sherlock STEP file.

ipk.modeler.create_coordinate_system([0, 0, stackup_thickness / 2], mode="view", view="XY")

###############################################################################
# Import a CAD File
# ~~~~~~~~~~~~~~~~~
# This command imports a CAD file.

ipk.modeler.import_3d_cad(file_path, refresh_all_ids=False)

###############################################################################
# Save the CAD File
# ~~~~~~~~~~~~~~~~~
# This command saves the CAD file and refreshes properties from AEDT file
# parsing.

ipk.save_project(project_name, refresh_obj_ids_after_save=True)


###############################################################################
# Plot the model
# ~~~~~~~~~~~~~~

ipk.plot(show=False, export_path=os.path.join(temp_folder, "Sherlock_Example.jpg"), plot_air_objects=False)


###############################################################################
# Remove PCB Objects
# ~~~~~~~~~~~~~~~~~~
# This command removes the PCB objects.

ipk.modeler.delete_objects_containing("pcb", False)

###############################################################################
# Create a Region
# ~~~~~~~~~~~~~~~
# This command creates an air region.

ipk.modeler.create_air_region(*[20, 20, 300, 20, 20, 300])

###############################################################################
# Assign Materials
# ~~~~~~~~~~~~~~~~
# This command assigns materials from Sherlock files.

ipk.assignmaterial_from_sherlock_files(component_list, material_list)

###############################################################################
# Delete Objects With No Material Assignments
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example deletes objects that have no materials assigned.

no_material_objs = ipk.modeler.get_objects_by_material("")
ipk.modeler.delete(no_material_objs)
ipk.save_project()

###############################################################################
# Assign Power to Component Blocks
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This command assigns power to component blocks.

all_objects = ipk.modeler.object_names

###############################################################################
# Assign Power Blocks
# ~~~~~~~~~~~~~~~~~~~
# This command assigns power blocks from the Sherlock file.

total_power = ipk.assign_block_from_sherlock_file(component_list)


###############################################################################
# Plot the model
# ~~~~~~~~~~~~~~
# We do the same plot after the material assignment

ipk.plot(show=False, export_path=os.path.join(temp_folder, "Sherlock_Example.jpg"), plot_air_objects=False)


###############################################################################
# Set Up Boundaries
# ~~~~~~~~~~~~~~~~~
# This example sets up boundaries.

ipk.mesh.automatic_mesh_pcb(4)

setup1 = ipk.create_setup()
setup1.props["Solution Initialization - Y Velocity"] = "1m_per_sec"
setup1.props["Radiation Model"] = "Discrete Ordinates Model"
setup1.props["Include Gravity"] = True
setup1.props["Secondary Gradient"] = True
ipk.assign_openings(ipk.modeler.get_object_faces("Region"))

###############################################################################
# Check for Intersection
# ~~~~~~~~~~~~~~~~~~~~~~
# This command checks for intersection using validation and fixes it by
# assigning priorities.

ipk.assign_priority_on_intersections()

###############################################################################
# Save and Close the Project
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example saves and closes the project.

ipk.save_project()


end = time.time() - start
if os.name != "posix":
    ipk.release_desktop()
print("Elapsed time: {}".format(datetime.timedelta(seconds=end)))
print("Project Saved in {} ".format(temp_folder))
