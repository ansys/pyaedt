"""
HFSS: FSS Unitcell Simulation
--------------------
This example shows how you can use PyAEDT to create a FSS unitcell simulations in HFSS and postprocess results.
"""

###############################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform required imports.

import os
import pyaedt

project_name = pyaedt.generate_unique_project_name(project_name="FSS")

###############################################################################
# Set non-graphical mode
# ~~~~~~~~~~~~~~~~~~~~~~
# Set non-graphical mode. `
# You can set ``non_graphical`` either to ``True`` or ``False``.

non_graphical = False

###############################################################################
# Launch AEDT
# ~~~~~~~~~~~
# Launch AEDT 2023 R2 in graphical mode.

d = pyaedt.launch_desktop("2023.2", non_graphical=non_graphical, new_desktop_session=True)

###############################################################################
# Launch HFSS
# ~~~~~~~~~~~
# Launch HFSS 2023 R2 in graphical mode.

hfss = pyaedt.Hfss(projectname=project_name, solution_type="Modal")

###############################################################################
# Define variable
# ~~~~~~~~~~~~~~~
# Define a variable for the 3D-component.

hfss["patch_dim"] = "10mm"

###############################################################################
# Get 3D component from system library
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# downaload the 3D component from the example data

unitcell_3d_component_path = pyaedt.downloads.download_FSS_3dcomponent() # download path of 3D component
unitcell_path = os.path.join(unitcell_3d_component_path, "FSS_unitcell.3dcomp")

comp = hfss.modeler.insert_3d_component(unitcell_3d_component_path) # inserting 3D component
component_name = hfss.modeler.user_defined_component_names
hfss.modeler.user_defined_components[component_name[0]].parameters["a"] = "patch_dim" # assigning variable to the parameter

###############################################################################
# Create boundary setup
# ~~~~~~~~~~~~~~~~~
# Create boundaries. A region with openings is needed to run the analysis.
bounding_dimensions = hfss.modeler.get_bounding_dimension()
periodicity_x = bounding_dimensions[0]
periodicity_y = bounding_dimensions[1]

# Create open region along +z direction for unitcell analysis
region = hfss.modeler.create_air_region(
        z_pos=10 * bounding_dimensions[2],
        is_percentage=False,
    )

# Assigning Master, Slave boundary conditions along x and y-directions
[x_min, y_min, z_min, x_max, y_max, z_max] = region.bounding_box

# get the face id's
id_x_neg = region.bottom_face_x
id_x_pos = region.top_face_x

# assign primary for pair-1
primary_1 = hfss.assign_primary(
    id_x_neg,
    [x_min, y_min, z_min],
    [x_min, y_max, z_min],
    reverse_v= False,
    coord_name="Global",
    primary_name="P1",
)
# assign secondary for pair-1
secondary_1 = hfss.assign_secondary(
    id_x_pos,
    "P1",
    [x_max, y_min, z_min],
    [x_max, y_max, z_min],
    reverse_v= True,
    coord_name="Global",
    secondary_name="S1",
)

# get the face_ids
id_y_neg = region.bottom_face_y
id_y_pos = region.top_face_y

# assign primary for pair-2
primary_2 = hfss.assign_primary(
    id_y_neg,
    [x_min, y_min, z_min],
    [x_max, y_min, z_min],
    reverse_v=True,
    coord_name="Global",
    primary_name="P2",
)
# assign secondary for pair-2
secondary_2 = hfss.assign_secondary(
    id_y_pos,
    "P2",
    [x_min, y_max, z_min],
    [x_max, y_max, z_min],
    reverse_v= False,
    coord_name="Global",
    secondary_name="S2",
)


hfss.create_open_region(Frequency="1GHz")

###############################################################################
# Assign Floquet port excitation along +z direction
# ~~~~~~~~~~~~~~~~~
# lattice directions: [0, y_max, z_max], [x_max, 0, z_max]
id_z_pos = region.top_face_z
hfss.create_floquet_port(id_z_pos, [0, 0, z_max], [0, y_max, z_max], [x_max, 0, z_max],
                                     portname='port_z_max', deembed_dist=10 * bounding_dimensions[2])

###############################################################################
# Plot model
# ~~~~~~~~~~
# Plot the model.

my_plot = hfss.plot(show=False, plot_air_objects=False)
my_plot.show_axes = False
my_plot.show_grid = False
my_plot.isometric_view = False
my_plot.plot(
    os.path.join(hfss.working_directory, "Image.jpg"),
)

###############################################################################
# Create setup
# ~~~~~~~~~~~~
# Create a setup with a sweep to run the simulation.

setup = hfss.create_setup("MySetup")
setup.props["Frequency"] = "10GHz"
setup.props["MaximumPasses"] = 10
hfss.create_linear_count_sweep(
    setupname=setup.name,
    unit="GHz",
    freqstart=6,
    freqstop=15,
    num_of_freq_points=201,
    sweepname="sweep1",
    sweep_type="Interpolating",
    interpolation_tol=6,
    save_fields=False,
)

###############################################################################
# Create parameteric sweep
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create parameteric sweep by varying "patch_dim", start:8 mm, stop: 11mm, step: 0.5

hfss.parametrics.add("patch_dim", 8, 11, 0.5, variation_type = "LinearStep", parametricname="sweep_para")

###############################################################################
# Create S-parameter report using report objects
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create S-parameter reports using create report,
# which gives you more freedom.

# Create a report
all_quantities = hfss.post.available_report_quantities()
str_mag = []
str_ang = []

variation = {"Freq": ["All"]}
variation["patch_dim"] = ["All"]

for i in all_quantities:
    str_mag.append("mag(" + i + ")")
    str_ang.append("ang_deg("+ i+")")

hfss.post.create_report(
    expressions=str_mag,
    variations=variation,
    plotname="magnitude_plot",
)
hfss.post.create_report(
    expressions=str_ang,
    variations=variation,
    plotname="phase_plot",
)

# create a report angle vs sweep parameters
variation_2 = {"Freq": ["10.05GHz"]}
variation_2["patch_dim"] = ["All"]

hfss.post.create_report(
    expressions=str_ang,
    primary_sweep_variable = "patch_dim",
    variations=variation_2,
    plotname="phase_plot_vs_dim",
)


###############################################################################
# Save and run simulation
# ~~~~~~~~~~~~~~~~~~~~~~~
# Save and run the simulation.
hfss.analyze_all()

###############################################################################
# Close AEDT
# ~~~~~~~~~~
# After the simulation completes, you can close AEDT or release it using the
# :func:`pyaedt.Desktop.release_desktop` method.
# All methods provide for saving the project before closing.

hfss.release_desktop()
