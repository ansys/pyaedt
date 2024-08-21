"""
Icepak: setup from Sherlock inputs
-----------------------------------
This example shows how you can create an Icepak project from Sherlock
files (STEP and CSV) and an AEDB board.
"""
###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports and set paths.

import time
import os
import ansys.aedt.core
import datetime
import matplotlib.pyplot as plt

# Set paths
project_folder = ansys.aedt.core.generate_unique_folder_name()
input_dir = ansys.aedt.core.downloads.download_sherlock(destination=project_folder)

##########################################################
# Set AEDT version
# ~~~~~~~~~~~~~~~~
# Set AEDT version.

aedt_version = "2024.2"

###############################################################################
# Set non-graphical mode
# ~~~~~~~~~~~~~~~~~~~~~~
# Set non-graphical mode. 
# You can set ``non_graphical`` value either to ``True`` or ``False``.

non_graphical = False

###############################################################################
# Define variables
# ~~~~~~~~~~~~~~~~
# Define input variables. The following code creates all input variables that are needed
# to run this example.

material_name = "MaterialExport.csv"
component_properties = "TutorialBoardPartsList.csv"
component_step = "TutorialBoard.stp"
aedt_odb_project = "SherlockTutorial.aedt"
aedt_odb_design_name = "PCB"
stackup_thickness = 2.11836
outline_polygon_name = "poly_14188"

###############################################################################
# Launch AEDT
# ~~~~~~~~~~~
# Launch AEDT 2024 R2 in graphical mode.

d = ansys.aedt.core.launch_desktop(version=aedt_version, non_graphical=non_graphical, new_desktop=True)

start = time.time()
material_list = os.path.join(input_dir, material_name)
component_list = os.path.join(input_dir, component_properties)
validation = os.path.join(project_folder, "validation.log")
file_path = os.path.join(input_dir, component_step)
project_name = os.path.join(project_folder, component_step[:-3] + "aedt")

###############################################################################
# Create Icepak project
# ~~~~~~~~~~~~~~~~~~~~~
# Create an Icepak project.

ipk = ansys.aedt.core.Icepak(project=project_name)

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
ipk.create_pcb_from_3dlayout(component_name=component_name, project_name=odb_path, design_name=aedt_odb_design_name,
                             extenttype="Polygon")

###############################################################################
# Create offset coordinate system
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create an offset coordinate system to match ODB++ with the
# Sherlock STEP file.

bb = ipk.modeler.user_defined_components["Board1"].bounding_box
stackup_thickness = bb[-1] - bb[2]
ipk.modeler.create_coordinate_system(
    origin=[0, 0, stackup_thickness / 2], mode="view", view="XY"
)

###############################################################################
# Import CAD file
# ~~~~~~~~~~~~~~~
# Import a CAD file and delete the CAD "pcb" object as the ECAD is already in the design.

ipk.modeler.import_3d_cad(file_path, refresh_all_ids=False)
ipk.modeler.delete_objects_containing("pcb", False)

###############################################################################
# Create region
# ~~~~~~~~~~~~~
# Create an air region.

ipk.mesh.global_mesh_region.global_region.padding_values = [20, 20, 20, 20, 300, 300]

###############################################################################
# Assign materials
# ~~~~~~~~~~~~~~~~
# Assign materials from Sherlock file.

ipk.assignmaterial_from_sherlock_files(
    component_file=component_list, material_file=material_list
)

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

total_power = ipk.assign_block_from_sherlock_file(csv_name=component_list)

###############################################################################
# Plot model
# ~~~~~~~~~~
# Plot the model again now that materials are assigned.

ipk.plot(
    show=False,
    output_file=os.path.join(project_folder.name, "Sherlock_Example.jpg"),
    plot_air_objects=False,
    plot_as_separate_objects=False
)

###############################################################################
# Set up boundaries
# ~~~~~~~~~~~~~~~~~
# Set up boundaries.

# Mesh settings that is tailored for PCB
# Max iterations is set to 20 for quick demonstration, please increase to at least 100 for better accuracy.

ipk.globalMeshSettings(3, gap_min_elements='1', noOgrids=True, MLM_en=True,
                            MLM_Type='2D', edge_min_elements='2', object='Region')

setup1 = ipk.create_setup()
setup1.props["Solution Initialization - Y Velocity"] = "1m_per_sec"
setup1.props["Radiation Model"] = "Discrete Ordinates Model"
setup1.props["Include Gravity"] = True
setup1.props["Secondary Gradient"] = True
setup1.props["Convergence Criteria - Max Iterations"] = 10
ipk.assign_openings(ipk.modeler.get_object_faces("Region"))

###############################################################################
# Create point monitor
# ~~~~~~~~~~~~~~~~~~~~

point1 = ipk.assign_point_monitor(ipk.modeler["COMP_U10"].top_face_z.center, monitor_name="Point1")
ipk.modeler.set_working_coordinate_system("Global")
line = ipk.modeler.create_polyline(
    [ipk.modeler["COMP_U10"].top_face_z.vertices[0].position, ipk.modeler["COMP_U10"].top_face_z.vertices[2].position],
    non_model=True)
ipk.post.create_report(expressions="Point1.Temperature", primary_sweep_variable="X")

###############################################################################
# Check for intersections
# ~~~~~~~~~~~~~~~~~~~~~~~
# Check for intersections using validation and fix them by
# assigning priorities.

ipk.assign_priority_on_intersections()

###############################################################################
# Compute power budget
# ~~~~~~~~~~~~~~~~~~~~

power_budget, total = ipk.post.power_budget("W" )
print(total)

###############################################################################
# Analyze the model
# ~~~~~~~~~~~~~~~~~

ipk.analyze(cores=4, tasks=4)
ipk.save_project()

###############################################################################
# Get solution data and plots
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Get monitor point result

pt_monitor_result = ipk.monitor.all_monitors[point1].value()
print(pt_monitor_result)

# Create a report on the previously defined line and get data from it

report = ipk.post.create_report(
    expressions=["Temperature", "Speed"],
    context=line.name,
    primary_sweep_variable="Distance",
    report_category="Fields",
    polyline_points=500,
)
report_data = report.get_solution_data()
distance = [
    k[0] for k, _ in report_data.full_matrix_mag_phase[0]["Temperature"].items()
]
temperature = [
    v for _, v in report_data.full_matrix_mag_phase[0]["Temperature"].items()
]
speed = [v for _, v in report_data.full_matrix_mag_phase[0]["Speed"].items()]

# Plot the data

fig, ax = plt.subplots(1, 1)
sc = ax.scatter(distance, speed, c=temperature)
ax.grid()
ax.set_xlabel("Distance [mm]")
ax.set_ylabel("Speed [m/s]")
cbar = fig.colorbar(sc)
cbar.set_label("Temperature [cel]")

# Plot contours. The plot can be performed within AEDT...

plot1 = ipk.post.create_fieldplot_surface(
    assignment=ipk.modeler["COMP_U10"].faces, quantity="SurfTemperature"
)
path = plot1.export_image(
    full_path=os.path.join(temp_folder.name, "temperature.png"), show_region=False
)
Image(filename=path)  # Display the image

# ... or using pyvista integration

ipk.post.plot_field(
    quantity="SurfPressure",
    assignment=ipk.modeler["COMP_U10"].faces,
    export_path=ipk.working_directory,
    show=False,
)

###############################################################################
# Save project and release AEDT
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Save the project and release AEDT.

ipk.save_project()

end = time.time() - start
print("Elapsed time: {}".format(datetime.timedelta(seconds=end)))
print("Project Saved in {} ".format(ipk.project_file))
ipk.release_desktop()


