"""
Icepack: setup from Sherlock inputs
-----------------------------------
This example shows how to create an Icepak project starting from Sherlock
files (STEP and CSV) and an AEDB board.
"""
###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports and set paths.

import time
import os
import tempfile
import datetime

from pyaedt import examples, generate_unique_name

# Set paths
input_dir = examples.download_sherlock()
tmpfold = tempfile.gettempdir()


temp_folder = os.path.join(tmpfold, generate_unique_name("Example"))
if not os.path.exists(temp_folder):
    os.makedirs(temp_folder)
print(temp_folder)

##########################################################
# Set non-graphical mode
# ~~~~~~~~~~~~~~~~~~~~~~
# Set non-graphical mode. The default is ``False``.

non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")

###############################################################################
# Input variables
# ~~~~~~~~~~~~~~~
# Input variables. The following code creates all input variables that are needed
# to run this example.

material_name = "MaterialExport.csv"
component_properties = "TutorialBoardPartsList.csv"
component_step = "TutorialBoard.stp"
aedt_odb_project = "SherlockTutorial.aedt"
aedt_odb_design_name = "PCB"
stackup_thickness = 2.11836
outline_polygon_name = "poly_14188"

###############################################################################
# Import Icepak and AEDT
# ~~~~~~~~~~~~~~~~~~~~~~
# Import Icepak and AEDT.

from pyaedt import Icepak
from pyaedt import Desktop

###############################################################################
# Launch AEDT
# ~~~~~~~~~~~
# Launch AEDT 2022 R2 in graphical mode.

d = Desktop("2022.2", non_graphical=non_graphical, new_desktop_session=True)

start = time.time()
material_list = os.path.join(input_dir, material_name)
component_list = os.path.join(input_dir, component_properties)
validation = os.path.join(temp_folder, "validation.log")
file_path = os.path.join(input_dir, component_step)
project_name = os.path.join(temp_folder, component_step[:-3] + "aedt")

###############################################################################
# Create Icepak project
# ~~~~~~~~~~~~~~~~~~~~~
# Create an Icepak project.

ipk = Icepak()

###############################################################################
# Delete region to speed up import
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Delete the region and disable autosave to speed up the import.

d.disable_autosave()
ipk.modeler.delete("Region")
component_name = "from_ODB"

###############################################################################
# Import PCB from AEDB file
# ~~~~~~~~~~~~~~~~~~~~~~~~~
# Import a PCB from an AEDB file.

odb_path = os.path.join(input_dir, aedt_odb_project)
ipk.create_pcb_from_3dlayout(
    component_name, odb_path, aedt_odb_design_name, extenttype="Polygon", outlinepolygon=outline_polygon_name
)

###############################################################################
# Create offset coordinate system
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create an offset coordinate system to match ODB++ with the
# Sherlock STEP file.

ipk.modeler.create_coordinate_system([0, 0, stackup_thickness / 2], mode="view", view="XY")

###############################################################################
# Import CAD file
# ~~~~~~~~~~~~~~~
# Import a CAD file.

ipk.modeler.import_3d_cad(file_path, refresh_all_ids=False)

###############################################################################
# Save CAD file
# ~~~~~~~~~~~~~
# Save the CAD file and refresh the properties from the parsing of the AEDT file.

ipk.save_project(project_name, refresh_obj_ids_after_save=True)


###############################################################################
# Plot model
# ~~~~~~~~~~
# Plot the model.

ipk.plot(show=False, export_path=os.path.join(temp_folder, "Sherlock_Example.jpg"), plot_air_objects=False)


###############################################################################
# Delete PCB objects
# ~~~~~~~~~~~~~~~~~~
# Delete the PCB objects.

ipk.modeler.delete_objects_containing("pcb", False)

###############################################################################
# Create region
# ~~~~~~~~~~~~~
# Create an air region.

ipk.modeler.create_air_region(*[20, 20, 300, 20, 20, 300])

###############################################################################
# Assign materials
# ~~~~~~~~~~~~~~~~
# Assign materials from the the Sherlock file.

ipk.assignmaterial_from_sherlock_files(component_list, material_list)

###############################################################################
# Delete objects with no material assignments
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Delete objects with no materials assignments.

no_material_objs = ipk.modeler.get_objects_by_material("")
ipk.modeler.delete(no_material_objs)
ipk.save_project()

###############################################################################
# Assign power to component blocks
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Assign power to component blocks.

all_objects = ipk.modeler.object_names

###############################################################################
# Assign power blocks
# ~~~~~~~~~~~~~~~~~~~
# Assign power blocks from the Sherlock file.

total_power = ipk.assign_block_from_sherlock_file(component_list)


###############################################################################
# Plot model
# ~~~~~~~~~~
# Plot the model again now that materials are assigned.

ipk.plot(show=False, export_path=os.path.join(temp_folder, "Sherlock_Example.jpg"), plot_air_objects=False)


###############################################################################
# Set up boundaries
# ~~~~~~~~~~~~~~~~~
# Set up boundaries.

ipk.mesh.automatic_mesh_pcb(4)

setup1 = ipk.create_setup()
setup1.props["Solution Initialization - Y Velocity"] = "1m_per_sec"
setup1.props["Radiation Model"] = "Discrete Ordinates Model"
setup1.props["Include Gravity"] = True
setup1.props["Secondary Gradient"] = True
ipk.assign_openings(ipk.modeler.get_object_faces("Region"))

###############################################################################
# Check for intersections
# ~~~~~~~~~~~~~~~~~~~~~~~
# Check for intersections using validation and fix them by
# assigning priorities.

ipk.assign_priority_on_intersections()

###############################################################################
# Save project and release AEDT
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Save the project and release AEDT.

ipk.save_project()

end = time.time() - start
if os.name != "posix":
    ipk.release_desktop()
print("Elapsed time: {}".format(datetime.timedelta(seconds=end)))
print("Project Saved in {} ".format(temp_folder))
