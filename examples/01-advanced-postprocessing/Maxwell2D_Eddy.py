"""

Maxwell 2D  Coil Analysis
--------------------------------------------
This tutorial shows how you can use PyAedt to create a project in
in Maxwell2D and run an Eddy Current Simulation
This Example needs PyVista, numpy and matplotlib,  to be installed on the machine to provide advanced post processing features
"""

import os
import numpy as np
import matplotlib.pyplot as plt

from pyaedt import Maxwell3d

###############################################################################
# NonGraphical
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Change Boolean to False to open AEDT in graphical mode

NonGraphical = False


#########################################
# Insert a Maxwell design and instantiate Geometry modeler.

M3D = Maxwell3d(solution_type="EddyCurrent", specified_version="2021.1", NG=NonGraphical)
project_dir = M3D.generate_temp_project_directory(name="Example")
project_name = os.path.join(project_dir, 'test.aedt')
M3D.modeler.model_units = "mm"
CS = M3D.modeler.coordinate_system
primitives = M3D.modeler.primitives

#############################
# Create the Model
# create box that will be used in simulation

plate = primitives.create_box([0, 0, 0], [294, 294, 19], name="Plate", matname="aluminum")
hole = primitives.create_box([18, 18, 0], [108, 108, 19], name="Hole")

#############################
# Modeler Operation
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# different modeler operation can be applied using subtract, material assignment, solve_inside


primitives.subtract([plate], [hole])
M3D.assignmaterial(plate, "aluminum")
M3D.solve_inside("Plate")
adaptive_frequency = "200Hz"
p_plate = M3D.post.volumetric_loss("Plate")  # Create fields postprocessing variable for loss in object Plate
M3D.save_project(project_name)  # unable to save file by passing the file name or directory as an argument.

########################
# Create coil

center_hole = M3D.modeler.Position(119, 25, 49)
center_coil = M3D.modeler.Position(94, 0, 49)
coil_hole = primitives.create_box(center_hole, [150, 150, 100], name="Coil_Hole")  # All positions in model units
coil = primitives.create_box(center_coil, [200, 200, 100], name="Coil")  # All positions in model units
primitives.subtract([coil], [coil_hole])
M3D.assignmaterial(coil, "copper")
M3D.solve_inside("Coil")
p_coil = M3D.post.volumetric_loss("Coil")

########################################
# Create relative coordinate system

CS.create([200, 100, 0], view="XY", name="Coil_CS")

##############################
# Create coil terminal

primitives.section(["Coil"], M3D.CoordinateSystemPlane.ZXPlane)
primitives.separate_bodies(["Coil_Section1"])
primitives.delete("Coil_Section1_Separate1")
M3D.assign_current(["Coil_Section1"], amplitude=2472)

#################################
# draw region

M3D.modeler.create_air_region(*[300] * 6)
#############################
# set eddy effects

M3D.eddy_effects_on(['Plate'])

###############################################################################
# Add an Eddy Current Setup
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This method add a transient setup and defines all the setup settings

Setup = M3D.create_setup()
Setup.props["MaximumPasses"] = 12
Setup.props["MinimumPasses"] = 2
Setup.props["MinimumConvergedPasses"] = 1
Setup.props["PercentRefinement"] = 30
Setup.props["Frequency"] = adaptive_frequency
Setup.props["HasSweepSetup"] = True
Setup.props["StartValue"] = "1e-08GHz"
Setup.props["StopValue"] = "1e-06GHz"
Setup.props["StepSize"] = "2e-08GHz"

Setup.update()
Setup.enable_expression_cache([p_plate, p_coil], "Fields", "Phase=\'0deg\' ", True)


###################################################
#  Solve

M3D.analyse_nominal()


###################################################
#  get_report_data returns a data class with all data produced from the simulation

val = M3D.post.get_report_data(expression="SolidLoss")
M3D.post.report_types

###################################################
# Plot Results using matplotlib

fig, ax = plt.subplots(figsize=(20, 10))

ax.set(xlabel='Frequency (Hz)', ylabel='Solid Losses (W)', title='Losses Chart')
ax.grid()
mag_data = np.array(val.data_magnitude())
freq_data = np.array([i * 1e9 for i in val.sweeps["Freq"]])
ax.plot(freq_data, mag_data)
plt.show()

###################################################
# Savethe project and release the desktop object

M3D.save_project(project_name)
M3D.close_desktop()



