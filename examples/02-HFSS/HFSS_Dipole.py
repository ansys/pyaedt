"""
Hfss: Dipole Antenna
--------------------
This example shows how you can use PyAEDT to create an antenna setup in HFSS and postprocess results.
"""

import os
import tempfile
from pyaedt import Hfss
from pyaedt import Desktop
from pyaedt import generate_unique_name

tmpfold = tempfile.gettempdir()

temp_folder = os.path.join(tmpfold, generate_unique_name("Example"))
if not os.path.exists(temp_folder):
    os.mkdir(temp_folder)

###############################################################################
# Launch AEDT in Graphical Mode
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This examples launches AEDT 2022R1 in graphical mode.

nongraphical = False
d = Desktop("2022.1", non_graphical=nongraphical, new_desktop_session=True)

###############################################################################
# Launch HFSS in Graphical Mode
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This examples launches HFSS 2022R1 in graphical mode.

hfss = Hfss(solution_type="Modal")

###############################################################################
# Define a Dipole Length Variable
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This command defines a dipole length variable.

hfss["l_dipole"] = "13.5cm"

###############################################################################
# Get a 3D Component from the `syslib` Directory
# ----------------------------------------------
# To run this example correctly, you must get all geometry parameters of the
# 3D component or, in case of an encrypted 3D component, create a dictionary
# of the parameters.

compfile = hfss.components3d["Dipole_Antenna_DM"]
geometryparams = hfss.get_components3d_vars("Dipole_Antenna_DM")
geometryparams["dipole_length"] = "l_dipole"
hfss.modeler.insert_3d_component(compfile, geometryparams)

###############################################################################
# Create Boundaries
# -----------------
# A region with openings is needed to run the analysis.

hfss.create_open_region(Frequency="1GHz")

###############################################################################
# Plot the model
# ~~~~~~~~~~~~~~

my_plot = hfss.plot(show=False, plot_air_objects=False)
my_plot.show_axes = False
my_plot.show_grid = False
my_plot.isometric_view = False
my_plot.plot(
    os.path.join(hfss.working_directory, "Image.jpg"),
)

###############################################################################
# Create the Setup
# ----------------
# A setup with a sweep will be used to run the simulation.

setup = hfss.create_setup("MySetup")
setup.props["Frequency"] = "1GHz"
setup.props["MaximumPasses"] = 1
hfss.create_linear_count_sweep(
    setupname=setup.name,
    unit="GHz",
    freqstart=0.5,
    freqstop=1.5,
    num_of_freq_points=251,
    sweepname="sweep1",
    sweep_type="Interpolating",
    interpolation_tol=3,
    interpolation_max_solutions=255,
    save_fields=False,
)

###############################################################################
# Save and Run the Simulation
# ---------------------------
# A setup with a sweep will be used to run the simulation.

hfss.save_project(os.path.join(temp_folder, "MyDipole.aedt"))
hfss.analyze_setup("MySetup")

###############################################################################
# Postprocessing
# --------------
# Generate a scattering plot and a far fields plot.

hfss.create_scattering("MyScattering")
variations = hfss.available_variations.nominal_w_values_dict
variations["Freq"] = ["1GHz"]
variations["Theta"] = ["All"]
variations["Phi"] = ["All"]
hfss.post.create_report(
    "db(GainTotal)",
    hfss.nominal_adaptive,
    variations,
    primary_sweep_variable="Theta",
    context="3D",
    report_category="Far Fields",
)

###############################################################################
# Postprocessing
# --------------
# Create post processing variable and assign to new coordinate system.
# A post processing variable can be created directly from setter
# using "post" prefix or with arbitrary name using set_variable method.

hfss["post_x"] = 2
hfss.variable_manager.set_variable("y_post", 1, postprocessing=True)
hfss.modeler.create_coordinate_system(["post_x", "y_post", 0], name="CS_Post")
hfss.insert_infinite_sphere(custom_coordinate_system="CS_Post", name="Sphere_Custom")
###############################################################################
# Postprocessing
# --------------
# The same report can be obtained outside electronic desktop with the
# following commands.

solutions = hfss.post.get_solution_data(
    "GainTotal",
    hfss.nominal_adaptive,
    variations,
    primary_sweep_variable="Theta",
    context="3D",
    report_category="Far Fields",
)

solutions_custom = hfss.post.get_solution_data(
    "GainTotal",
    hfss.nominal_adaptive,
    variations,
    primary_sweep_variable="Theta",
    context="Sphere_Custom",
    report_category="Far Fields",
)

###############################################################################
# 3D Plot
# -------
# plot_3d method created a 3d plot using matplotlib.

solutions.plot_3d()

###############################################################################
# 3D Plot
# -------
# plot_3d method created a 3d plot using matplotlib.

solutions_custom.plot_3d()

###############################################################################
# 2D Plot
# -------
# plot method created a 2d plot using matplotlib. is_polar boolean let you
# decide if a polar plot or rectangular plot has to be created.

solutions.plot(math_formula="db20", is_polar=True)

###############################################################################
# Close AEDT
# ~~~~~~~~~~
# After the simulaton is completed, you can close AEDT or release it using the
# :func:`pyaedt.Desktop.release_desktop` method.
# All methods provide for saving the project before exiting.

if os.name != "posix":
    d.release_desktop()
