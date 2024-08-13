# # Icepak: setup from Sherlock inputs

# This example shows how you can create an Icepak project from Sherlock
# files (STEP and CSV) and an AEDB board.

# ## Perform required imports
#
# Perform required imports and set paths.

# +
import os
import tempfile

import matplotlib.pyplot as plt
import pyaedt
from IPython.display import Image

# -

# Set constant values

AEDT_VERSION = "2024.1"
NG_MODE = False  # Open Electronics UI when the application is launched.


# ## Define input files and variables.
#
# Set paths.

temp_folder = tempfile.TemporaryDirectory(suffix=".ansys")
input_dir = pyaedt.downloads.download_sherlock(destination=temp_folder.name)

# Define input files names.

material_name = "MaterialExport.csv"
component_properties = "TutorialBoardPartsList.csv"
component_step = "TutorialBoard.stp"
aedt_odb_project = "SherlockTutorial.aedt"

# Define variables that will be needed later.

aedt_odb_design_name = "PCB"
outline_polygon_name = "poly_14188"

# Define input files with path

material_list = os.path.join(input_dir, material_name)
component_list = os.path.join(input_dir, component_properties)
validation = os.path.join(temp_folder.name, "validation.log")
file_path = os.path.join(input_dir, component_step)
project_name = os.path.join(temp_folder.name, component_step[:-3] + "aedt")

# ## Create Icepak model

ipk = pyaedt.Icepak(project=project_name, version=AEDT_VERSION, non_graphical=NG_MODE)

# Disable autosave to speed up the import.

ipk.autosave_disable()


# Import a PCB from an AEDB file.

odb_path = os.path.join(input_dir, aedt_odb_project)
ipk.create_pcb_from_3dlayout(
    component_name="Board", project_name=odb_path, design_name=aedt_odb_design_name
)

# Create an offset coordinate system to match ODB++ with the Sherlock STEP file.
# The thickness is computed from the ``"Board"`` component (``"Board1"`` is the
# instance name of the ``"Board"`` native component) and used to offset the coordinate system.

bb = ipk.modeler.user_defined_components["Board1"].bounding_box
stackup_thickness = bb[-1] - bb[2]
ipk.modeler.create_coordinate_system(
    origin=[0, 0, stackup_thickness / 2], mode="view", view="XY"
)

# Import the board components from a MCAD file and remove the PCB object as it is already
# imported with the ECAD.

ipk.modeler.import_3d_cad(file_path, refresh_all_ids=False)
ipk.modeler.delete_objects_containing("pcb", False)

# Modify the air region. Padding values are passed in this order: [+X, -X, +Y, -Y, +Z, -Z]

ipk.mesh.global_mesh_region.global_region.padding_values = [20, 20, 20, 20, 300, 300]

# ## Assign materials and power dissipation conditions from Sherlock
#
# Use Sherlock file to assign materials.

ipk.assignmaterial_from_sherlock_files(
    component_file=component_list, material_file=material_list
)

# Delete objects with no materials assignments.

no_material_objs = ipk.modeler.get_objects_by_material(material="")
ipk.modeler.delete(assignment=no_material_objs)

# Assign power blocks from the Sherlock file.

total_power = ipk.assign_block_from_sherlock_file(csv_name=component_list)

# ## Plot model

ipk.plot(
    show=False,
    output_file=os.path.join(temp_folder.name, "Sherlock_Example.jpg"),
    plot_air_objects=False,
    plot_as_separate_objects=False
)

# ## Create simulation setup
# ### Mesh settings
# Set global mesh settings

ipk.mesh.global_mesh_region.manual_settings = True
ipk.mesh.global_mesh_region.settings["MaxElementSizeX"] = 30
ipk.mesh.global_mesh_region.settings["MaxElementSizeY"] = 30
ipk.mesh.global_mesh_region.settings["MaxElementSizeZ"] = 30
ipk.mesh.global_mesh_region.settings["BufferLayers"] = 2
ipk.mesh.global_mesh_region.settings["EnableMLM"] = True
ipk.mesh.global_mesh_region.settings["UniformMeshParametersType"] = "Average"
ipk.mesh.global_mesh_region.settings["MaxLevels"] = 3
ipk.mesh.global_mesh_region.update()

# Add PCB mesh with 2D multi-level meshing

mesh_region = ipk.mesh.assign_mesh_region(assignment="Board1")
mesh_region.manual_settings = True
mesh_region.settings["MaxElementSizeX"] = 10
mesh_region.settings["MaxElementSizeY"] = 10
mesh_region.settings["MaxElementSizeZ"] = 10
mesh_region.settings["EnableMLM"] = True
mesh_region.settings["UniformMeshParametersType"] = "Average"
mesh_region.settings["EnforeMLMType"] = "2D"
mesh_region.settings["2DMLMType"] = "2DMLM_Auto"
mesh_region.settings["MaxLevels"] = 1
mesh_region.update()


# ### Boundary conditions
# assign free opening at all the region faces

ipk.assign_pressure_free_opening(assignment=ipk.modeler.get_object_faces("Region"))

# ### Add post-processing object
# Create point monitor

point1 = ipk.monitor.assign_point_monitor(
    point_position=ipk.modeler["COMP_U10"].top_face_z.center, monitor_name="Point1"
)

# Create line for reporting after the simulation

line = ipk.modeler.create_polyline(
    points=[
        ipk.modeler["COMP_U10"].top_face_z.vertices[0].position,
        ipk.modeler["COMP_U10"].top_face_z.vertices[2].position,
    ],
    non_model=True,
)

# ### Solve
# Max iterations are set to 10 for quick demonstration, please increase to at
# least 100 for better accuracy.

setup1 = ipk.create_setup()
setup1.props["Solution Initialization - Y Velocity"] = "1m_per_sec"
setup1.props["Radiation Model"] = "Discrete Ordinates Model"
setup1.props["Include Gravity"] = True
setup1.props["Secondary Gradient"] = True
setup1.props["Convergence Criteria - Max Iterations"] = 10

# Check for intersections using validation and fix them by
# assigning priorities.

ipk.assign_priority_on_intersections()

# Analyze the model

ipk.analyze(cores=4, tasks=4)
ipk.save_project()

# ## Post-Processing
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

# ## Save project and release AEDT

ipk.save_project()
ipk.release_desktop()

# ## Cleanup
#
# All project files are saved in the folder ``temp_dir.name``.
# If you've run this example as a Jupyter notebook you
# can retrieve those project files. The following cell
# removes all temporary files, including the project folder.

temp_folder.cleanup()