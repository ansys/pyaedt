"""
Maxwell 2D  Coil Analysis
-------------------------
This example shows how you can use PyAEDT to create a project in
Maxwell2D and run an eddy current simulation.

To provide the advanced postprocessing features needed for this example, Matplotlib, NumPy, and
PyVista must be installed on the machine.

This examples runs only on Windows using CPython.
"""

import os
import numpy as np
import matplotlib.pyplot as plt

from pyaedt import Maxwell3d

###############################################################################
# Insert a Maxwell 3D Design
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example inserts a Maxwell 3D design.

M3D = Maxwell3d(solution_type="EddyCurrent", specified_version="2021.2", non_graphical=False, new_desktop_session=True)
M3D.modeler.model_units = "mm"

###############################################################################
# Create the Model
# ~~~~~~~~~~~~~~~~
# This example creates a box that is to be used in the simulation.

plate = M3D.modeler.primitives.create_box([0, 0, 0], [294, 294, 19], name="Plate", matname="aluminum")
hole = M3D.modeler.primitives.create_box([18, 18, 0], [108, 108, 19], name="Hole")

###############################################################################
# Perform Modeler Operations
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
# You can apply different modeler operations such as subtraction, material assignment, and solving inside.

M3D.modeler.subtract([plate], [hole])
plate.material_name = "aluminum"
plate.solve_inside = True
adaptive_frequency = "200Hz"
# Create fields postprocessing variable for loss in object Plate.
p_plate = M3D.post.volumetric_loss("Plate")

project_dir = M3D.generate_temp_project_directory("Example")
project_name = os.path.join(project_dir, "test.aedt")
# Unable to save file by passing the file name or directory as an argument.
M3D.save_project(project_name)

###############################################################################
# Create Coil
# ~~~~~~~~~~~
# This example creates a coil.

center_hole = M3D.modeler.Position(119, 25, 49)
center_coil = M3D.modeler.Position(94, 0, 49)
coil_hole = M3D.modeler.primitives.create_box(
    center_hole, [150, 150, 100], name="Coil_Hole"
)  # All positions in model units
coil = M3D.modeler.primitives.create_box(center_coil, [200, 200, 100], name="Coil")  # All positions in model units
M3D.modeler.subtract([coil], [coil_hole])
coil.material_name = "copper"
coil.solve_inside = True
p_coil = M3D.post.volumetric_loss("Coil")

###############################################################################
# Create a Relative Coordinate System
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This command creates a relative coordinate system.

M3D.modeler.create_coordinate_system(origin=[200, 100, 0], mode="view", view="XY", name="Coil_CS")

###############################################################################
# Create a Coil Terminal
# ~~~~~~~~~~~~~~~~~~~~~~
# This example creates a coil terminal.

M3D.modeler.section(["Coil"], M3D.PLANE.ZX)
M3D.modeler.separate_bodies(["Coil_Section1"])
M3D.modeler.primitives.delete("Coil_Section1_Separate1")
M3D.assign_current(["Coil_Section1"], amplitude=2472)

###############################################################################
# Draw a Region
# ~~~~~~~~~~~~~
# This command draws an air region.

M3D.modeler.create_air_region(*[300] * 6)

###############################################################################
# Set Eddy Effects
# ~~~~~~~~~~~~~~~~
# This command sets the eddy effects.

M3D.eddy_effects_on(["Plate"])

###############################################################################
# Add an Eddy Current Setup
# ~~~~~~~~~~~~~~~~~~~~~~~~~
# This example adds a transient setup and defines all settings.

Setup = M3D.create_setup()
Setup.props["MaximumPasses"] = 12
Setup.props["MinimumPasses"] = 2
Setup.props["MinimumConvergedPasses"] = 1
Setup.props["PercentRefinement"] = 30
Setup.props["Frequency"] = adaptive_frequency
Setup.props["HasSweepSetup"] = True
Setup.props["StartValue"] = "1e-08GHz"
Setup.props["StopValue"] = "1e-06GHz"
Setup.props["StepSize"] = "1e-07GHz"

Setup.update()
Setup.enable_expression_cache([p_plate, p_coil], "Fields", "Phase='0deg' ", True)

###############################################################################
# Solve the Project
# ~~~~~~~~~~~~~~~~~~
# This command solves the project.

M3D.analyze_nominal()

###############################################################################
# Get Report Data
# ~~~~~~~~~~~~~~~
# :func:`PostProcessor.get_report_data` returns a data class with all data produced from
# the simulation.

val = M3D.post.get_report_data(expression="SolidLoss")
M3D.post.report_types

###############################################################################
# Use Matplotlib to Plot Results
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example plots results using Matplotlib.

fig, ax = plt.subplots(figsize=(20, 10))

ax.set(xlabel="Frequency (Hz)", ylabel="Solid Losses (W)", title="Losses Chart")
ax.grid()
mag_data = np.array(val.data_magnitude())
freq_data = np.array([i * 1e9 for i in val.sweeps["Freq"]])
ax.plot(freq_data, mag_data)
plt.show()

###################################################
# Save the Project and Close AEDT
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example saves the project and then closes AEDT.

M3D.save_project(project_name)
M3D.release_desktop()
