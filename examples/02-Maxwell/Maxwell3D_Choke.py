"""
Maxwell3d: Choke
----------------
This example shows how you can use PyAEDT to create an choke setup in Maxwell3D.
"""

import json
import tempfile
import os

from pyaedt import generate_unique_name
from pyaedt import Desktop
from pyaedt import Maxwell3d
from pyaedt.modules.Mesh import Mesh

tmpfold = tempfile.gettempdir()

temp_folder = os.path.join(tmpfold, generate_unique_name("Example"))
if not os.path.exists(temp_folder):
    os.mkdir(temp_folder)

###############################################################################
# Launch AEDT in Graphical Mode
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This examples launches AEDT 2022.1 in graphical mode.
version = "2022.1"
non_graphical = True

###############################################################################
# Launch HFSS in Graphical Mode
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This examples launches HFSS 2021.2 in graphical mode.

m3d = Maxwell3d(solution_type="EddyCurrent", specified_version=version, non_graphical=non_graphical,
                new_desktop_session=True)

###############################################################################
# Rules and information of use
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The dictionary values is containing the different parameters of the core and the windings which composed
# the choke. The main structure of the dictionary must not be changed, i.e the dictionary has primary keys
# ("Number of Windings", "Layer", "Layer Type", etc...) which have dictionaries as values, these dictionaries
# keys are the secondary keys of the dictionary values ("1", "2", "3", "4", "Simple", etc...).
# Neither the primary nor the secondary keys must be modified, only their values.
# The value type must be unchanged. For the dictionary from "Number of Windings" to "Wire Section" included,
# values must be boolean. Only one value by dictionary must be "True". If all values are "True" only the first one
# will remain so. If all values are "False", the first value will be choose as the correct one by default".
# For the dictionary from "Core" to "Inner Winding" included, values must be string or float or int.
# "Number of Windings" is to choose the number of windings around the core.
# "Layer" is to choose the number of layers of all windings.
# "Layer Type" is to choose if the layers of a winding are linked to each other or not.
# "Similar Layer" is to choose if the layers of a winding have the number of turns and
# the same spacing between turns or not.
# "Mode" is only useful for 2 windings to choose if they are in common or differential mode.
# "Wire Section" is to choose the wire section type and number of segments.
# "Core" is to design the core.
# "Outer Winding" is to design the first layer or outer layer of a winding and
# select the common parameter for all layers.
# "Mid Winding" is to select the turns and the turns spacing ("Coil Pit")
# for the second or mid layer if it is necessary.
# "Inner Winding" is to select the turns and the turns spacing ("Coil Pit")
# for the third or inner layer if it is necessary.
# "Occupation(%)" is only an informative parameter, it is useless to modify it.
# If you have doubt you can let parameters like they are it will work.

values = {
    "Number of Windings": {"1": False, "2": False, "3": True, "4": False},
    "Layer": {"Simple": False, "Double": False, "Triple": True},
    "Layer Type": {"Separate": False, "Linked": True},
    "Similar Layer": {"Similar": False, "Different": True},
    "Mode": {"Differential": True, "Common": False},
    "Wire Section": {"None": False, "Hexagon": False, "Octagon": True, "Circle": False},
    "Core": {
        "Name": "Core",
        "Material": "ferrite",
        "Inner Radius": 100,
        "Outer Radius": 143,
        "Height": 25,
        "Chamfer": 0.8,
    },
    "Outer Winding": {
        "Name": "Winding",
        "Material": "copper",
        "Inner Radius": 100,
        "Outer Radius": 143,
        "Height": 25,
        "Wire Diameter": 5,
        "Turns": 2,
        "Coil Pit(deg)": 4,
        "Occupation(%)": 0,
    },
    "Mid Winding": {"Turns": 7, "Coil Pit(deg)": 4, "Occupation(%)": 0},
    "Inner Winding": {"Turns": 10, "Coil Pit(deg)": 4, "Occupation(%)": 0},
}

###############################################################################
# Convert dictionary to json file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The PyAEDT methods ask the path of the json file as argument, so you can convert this dictionary in json file
# thanks to the following command.

json_path = os.path.join(m3d.working_directory, "choke_example.json")

with open(json_path, "w") as outfile:
    json.dump(values, outfile)

###############################################################################
# Verify the parameter of the json file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The first method "check_choke_values" will take the json file path in argument and:
# - Check if the json file is correctly written (as it is explained in the rules)
# - Check inequations on windings parameters to avoid to have unintended intersection

dictionary_values = m3d.modeler.check_choke_values(json_path, create_another_file=False)
print(dictionary_values)

###############################################################################
# Generate the choke
# ~~~~~~~~~~~~~~~~~~
# This second method "create_choke" will take the json file path in argument and generate the choke.

list_object = m3d.modeler.create_choke(json_path)
print(list_object)
core = list_object[1]
first_winding_list = list_object[2]
second_winding_list = list_object[3]
third_winding_list = list_object[4]

###############################################################################
# Assign Excitation
# -----------------

first_winding_faces = m3d.modeler.get_object_faces(first_winding_list[0].name)
second_winding_faces = m3d.modeler.get_object_faces(second_winding_list[0].name)
third_winding_faces = m3d.modeler.get_object_faces(third_winding_list[0].name)
m3d.assign_current([first_winding_faces[-1]], amplitude=1000, phase="0deg", swap_direction=False, name="phase_1_in")
m3d.assign_current([first_winding_faces[-2]], amplitude=1000, phase="0deg", swap_direction=True, name="phase_1_out")
m3d.assign_current([second_winding_faces[-1]], amplitude=1000, phase="120deg", swap_direction=False, name="phase_2_in")
m3d.assign_current([second_winding_faces[-2]], amplitude=1000, phase="120deg", swap_direction=True, name="phase_2_out")
m3d.assign_current([third_winding_faces[-1]], amplitude=1000, phase="240deg", swap_direction=False, name="phase_3_in")
m3d.assign_current([third_winding_faces[-2]], amplitude=1000, phase="240deg", swap_direction=True, name="phase_3_out")

###############################################################################
# Assign Matrix
# -------------

m3d.assign_matrix(["phase_1_in", "phase_2_in", "phase_3_in"], matrix_name="current_matrix")

###############################################################################
# Create Mesh Operation
# ---------------------

mesh = Mesh(m3d)
mesh.assign_skin_depth(
    [first_winding_list[0], second_winding_list[0], third_winding_list[0]],
    0.20,
    triangulation_max_length="10mm",
    meshop_name="skin_depth",
)
mesh.assign_surface_mesh_manual(
    [first_winding_list[0], second_winding_list[0], third_winding_list[0]],
    surf_dev=None,
    normal_dev="30deg",
    meshop_name="surface_approx",
)

###############################################################################
# Create Boundaries
# -----------------
# A region with openings is needed to run the analysis.

region = m3d.modeler.create_air_region(x_pos=100, y_pos=100, z_pos=100, x_neg=100, y_neg=100, z_neg=0)

###############################################################################
# Create the Setup
# ----------------
# A setup with a sweep will be used to run the simulation. Depending on your computing machine,
# simulation can take time.

setup = m3d.create_setup("MySetup")
print(setup.props)
setup.props["Frequency"] = "100kHz"
setup.props["PercentRefinement"] = 15
setup.props["MaximumPasses"] = 10
setup.props["HasSweepSetup"] = True
setup.add_eddy_current_sweep(range_type="LinearCount", start=100, end=1000, count=12, units="kHz", clear=True)


###############################################################################
# Save the project
# ----------------

m3d.save_project(os.path.join(temp_folder, "My_Maxwell3d_Choke.aedt"))
m3d.modeler.fit_all()
m3d.plot(os.path.join(m3d.working_directory, "Image.jpg"))


###############################################################################
# Close AEDT
# ~~~~~~~~~~
# After the simulaton is completed, you can close AEDT or release it using the
# :func:`pyaedt.Desktop.release_desktop` method.
# All methods provide for saving the project before exiting.


if os.name != "posix":
    m3d.release_desktop()
