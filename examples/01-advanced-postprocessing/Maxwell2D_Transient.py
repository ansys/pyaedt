"""

Maxwell 2D Analysis
-------------------
This example shows how you can use PyAEDT to create a project in Maxwell 2D
and run a transient simulation. It runs only on Windows using CPython.

The following libraries are required for the advanced postprocessing features
used in this example:

- `Matplotlib <https://pypi.org/project/matplotlib/>`_
- `Numpty <https://pypi.org/project/numpy/>`_
- `PyVista <https://pypi.org/project/pyvista/>`_

Install these with:

.. code::

   pip install numpy pyvista matplotlib

"""

import os
from pyaedt import Maxwell2d

###############################################################################
# Launch AEDT in Graphical Mode
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# You change the Boolean parameter ``non_graphical`` to ``False`` to launch
# AEDT in graphical mode.

non_graphical = True

###############################################################################
# Insert a Maxwell 2D Design and Save the Project
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example inserts a Maxwell 2D design and then saves the project.

maxwell_2d=Maxwell2d(solution_type="TransientXY", specified_version="2021.1", NG=non_graphical)
project_dir = maxwell_2d.generate_temp_project_directory("Example")
maxwell_2d.save_project(os.path.join(project_dir,"M2d.aedt"))

###############################################################################
# Create a Rectangle and Duplicate It
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example creates a rectangle and then duplicates it.

rect1 = maxwell_2d.modeler.primitives.create_rectangle([0, 0, 0],[20, 10], "Rectangle1", "copper")
added = rect1.duplicate_along_line([14,0,0])
rect2 = maxwell_2d.modeler.primitives[added[0]]

###############################################################################
# Create an Air Region
# ~~~~~~~~~~~~~~~~~~~
# This command creates an air region.

region = maxwell_2d.modeler.primitives.create_region([100, 100, 100, 100, 100, 100])

###############################################################################
# Assign Windings to Sheets and a Balloon to the Air Region
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example assigns windings to shhets and a balloon too the air region.

maxwell_2d.assign_winding([rect1.name, rect2.name], name="PHA")
maxwell_2d.assign_balloon(region.edges)

###############################################################################
# Add a Transient Setup
# ~~~~~~~~~~~~~~~~~~~~~
# This example adds a transient setup.

setup = maxwell_2d.create_setup()
setup.props["StopTime"] ="0.02s"
setup.props["TimeStep"] = "0.0002s"
setup.props["SaveFieldsType"] = "Every N Steps"
setup.props["N Steps"] = "1"
setup.props["Steps From"] ="0s"
setup.props["Steps To"] = "0.002s"
setup.update()

###############################################################################
# Create a Rectangular Plot
# ~~~~~~~~~~~~~~~~~~~~~~~~~
# This command creates a rectangular plot.

maxwell_2d.post.create_rectangular_plot("InputCurrent(PHA)",primary_sweep_variable="Time", families_dict={
                                        "Time":["All"]}, plotname="Winding Plot 1")

###############################################################################
# Solve the Model
# ~~~~~~~~~~~~~~~
# This command solves the model.

maxwell_2d.analyze_nominal()

###############################################################################
# Create the Output and Plot It Using PyVista
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This example creates the output and then plots it using PyVista.

import time
start = time.time()
cutlist = ["Global:XY"]
face_lists = rect1.faces
face_lists += rect2.faces
timesteps=[str(i*1e-3)+"s" for i in range(21)]
id_list = [f.id for f in face_lists]
#animatedGif=maxwell_2d.post.animate_fields_from_aedtplt_2("Mag_B", id_list, "Surface", intrinsic_dict={'Time': '0s'}, variation_variable="Time",variation_list=timesteps, off_screen=True, export_gif=True)


###############################################
# Close AEDT
# ~~~~~~~~~~
# This command closes AEDT.

maxwell_2d.close_desktop()
