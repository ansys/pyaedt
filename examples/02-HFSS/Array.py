"""
HFSS: Component Antenna Array
-----------------------------
This example shows how to use pyaedt to create an example using 3d component file, setup analysis, solve it and
postprocessing functions to create plots using Matplotlib and pyvista without opening the HFSS user interface.
This examples runs only on Windows using CPython.
"""


import os
from pyaedt import Hfss
from pyaedt import examples
from pyaedt.generic.DataHandlers import json_to_dict
from pyaedt.generic.general_methods import generate_unique_name
import tempfile

##########################################################
# Set Non Graphical Mode.
# Default is False

non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")
example_path = examples.download_3dcomponent()

##########################################################
# Launch Hfss and save project.

hfss = Hfss(specified_version="2022.2", designname="Array_Simple", non_graphical=non_graphical, new_desktop_session=True)
tmpfold = tempfile.gettempdir()
name = generate_unique_name("array_demo")
hfss.save_project(os.path.join(tmpfold, name+".aedt"))

print(os.path.join(tmpfold, name+".aedt"))

##########################################################
# Read array definition from json file
# ------------------------------------
# A json file can contain all information needed to import and setup the full array in Hfss.
# If the 3d component is not available in the design then it will be loaded from the path indicated into the dictionary.
# In this example we are editing the dictionary to point to the location of the a3dcomp file.
dict_in = json_to_dict(os.path.join(example_path, "array_simple.json"))
dict_in["Circ_Patch_5GHz1"] = os.path.join(example_path, "Circ_Patch_5GHz.a3dcomp")
dict_in["cells"][(3, 3)] = {"name": "Circ_Patch_5GHz1"}
hfss.add_3d_component_array_from_json(dict_in)


##########################################################
# Simulation setup
# ----------------
# A simulation setup is created, options are changed and setup is analyzed.

setup = hfss.create_setup()
setup.props["Frequency"] = "5GHz"
setup.props["MaximumPasses"] = 3

hfss.analyze_nominal(num_cores=4)

##########################################################
# Get Far Field Data
# ------------------
# After a simualtion is completed the far field data, ports by ports is generated and stored in a data class.


ffdata = hfss.get_antenna_ffd_solution_data(sphere_name="Infinite Sphere1", setup_name=hfss.nominal_adaptive,
                                            frequencies=[5e9])

##########################################################
# Post Processing: Contour Plot
# -----------------------------
# Multiple post-processing can be performed. In this example we see the Contour plot.
# Theta scan and Phi scan can be defined as well.

ffdata.plot_farfield_contour(qty_str='RealizedGain', convert_to_db=True,
                             title='Contur at {}Hz'.format(ffdata.frequency))

##########################################################
# Post Processing: 2D Cutout
# --------------------------
# Multiple post-processing can be performed. In this example we see the 2D Cutout plots.
# Theta scan and Phi scan can be defined as well.

ffdata.plot_2d_cut(primary_sweep='theta', secondary_sweep_value=[-180, -75, 75],
                   qty_str='RealizedGain',
                   title='Azimuth at {}Hz'.format(ffdata.frequency),
                   convert_to_db=True)

ffdata.plot_2d_cut(primary_sweep="phi", secondary_sweep_value=30,
                   qty_str='RealizedGain',
                   title='Elevation',
                   convert_to_db=True)

##########################################################
# Post Processing: 3D Plot Matplotlib
# ------------------------------------
# In this example we see the 3D Polar plot computed with matplotlib.
# Theta scan and Phi scan can be defined as well.

ffdata.polar_plot_3d(qty_str='RealizedGain',
                     convert_to_db=True)

##########################################################
# Post Processing: 3D Plot Pyvista
# --------------------------------
# Pyvista postprocessing provides an easy to use interactive plot with possibility to change,
# on the fly the theta and phi scan angles.

ffdata.polar_plot_3d_pyvista(qty_str='RealizedGain',
                             convert_to_db=True,
                             export_image_path=os.path.join(hfss.working_directory, "picture.jpg"),
                             show=False)

##########################################################
# Desktop Release
# ---------------

hfss.release_desktop()
