"""
HFSS: Choke
-----------
This example shows how you can use PyAEDT to create an choke setup in HFSS.
"""

import json
import tempfile
import os

from pyaedt import generate_unique_name
from pyaedt import Hfss
from pyaedt.modules.Mesh import Mesh

tmpfold = tempfile.gettempdir()

temp_folder = os.path.join(tmpfold, generate_unique_name("Example"))
if not os.path.exists(temp_folder):
    os.mkdir(temp_folder)

##########################################################
# Set Non Graphical Mode.
# Default is False

non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")

###############################################################################
# Launch HFSS in Graphical Mode
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This examples launches HFSS 2022.2 in graphical mode.

hfss = Hfss(specified_version="2022.2", non_graphical=non_graphical, new_desktop_session=True, solution_type="Terminal")

###############################################################################
# Rules and information of use
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The dictionary values is containing the different parameters of the core and the windings which compose
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
    "Number of Windings": {"1": False, "2": True, "3": False, "4": False},
    "Layer": {"Simple": False, "Double": True, "Triple": False},
    "Layer Type": {"Separate": False, "Linked": True},
    "Similar Layer": {"Similar": False, "Different": True},
    "Mode": {"Differential": False, "Common": True},
    "Wire Section": {"None": False, "Hexagon": True, "Octagon": False, "Circle": False},
    "Core": {
        "Name": "Core",
        "Material": "ferrite",
        "Inner Radius": 20,
        "Outer Radius": 30,
        "Height": 10,
        "Chamfer": 0.8,
    },
    "Outer Winding": {
        "Name": "Winding",
        "Material": "copper",
        "Inner Radius": 20,
        "Outer Radius": 30,
        "Height": 10,
        "Wire Diameter": 1.5,
        "Turns": 20,
        "Coil Pit(deg)": 0.1,
        "Occupation(%)": 0,
    },
    "Mid Winding": {"Turns": 25, "Coil Pit(deg)": 0.1, "Occupation(%)": 0},
    "Inner Winding": {"Turns": 4, "Coil Pit(deg)": 0.1, "Occupation(%)": 0},
}

###############################################################################
# Convert dictionary to json file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The PyAEDT methods ask the path of the json file as argument, so you can convert this dictionary in json file
# thanks to the following command.

json_path = os.path.join(hfss.working_directory, "choke_example.json")

with open(json_path, "w") as outfile:
    json.dump(values, outfile)

###############################################################################
# Verify the parameter of the json file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The first method "check_choke_values" will take the json file path in argument and:
# - Check if the json file is correctly written (as it is explained in the rules)
# - Check inequations on windings parameters to avoid to have unintended intersection

dictionary_values = hfss.modeler.check_choke_values(json_path, create_another_file=False)
print(dictionary_values)

###############################################################################
# Generate the choke
# ~~~~~~~~~~~~~~~~~~
# This second method "create_choke" will take the json file path in argument and generate the choke.

list_object = hfss.modeler.create_choke(json_path)
print(list_object)
core = list_object[1]
first_winding_list = list_object[2]
second_winding_list = list_object[3]


###############################################################################
# Create Ground
# -------------

ground_radius = 1.2 * dictionary_values[1]["Outer Winding"]["Outer Radius"]
ground_position = [0, 0, first_winding_list[1][0][2] - 2]
ground = hfss.modeler.create_circle("XY", ground_position, ground_radius, name="GND", matname="copper")
coat = hfss.assign_coating(ground, isinfgnd=True)

###############################################################################
# Create Lumped Ports
# -------------------

port_position_list = [
    [first_winding_list[1][0][0], first_winding_list[1][0][1], first_winding_list[1][0][2] - 1],
    [first_winding_list[1][-1][0], first_winding_list[1][-1][1], first_winding_list[1][-1][2] - 1],
    [second_winding_list[1][0][0], second_winding_list[1][0][1], second_winding_list[1][0][2] - 1],
    [second_winding_list[1][-1][0], second_winding_list[1][-1][1], second_winding_list[1][-1][2] - 1],
]
port_dimension_list = [2, dictionary_values[1]["Outer Winding"]["Wire Diameter"]]
for position in port_position_list:
    sheet = hfss.modeler.create_rectangle("XZ", position, port_dimension_list, name="sheet_port")
    sheet.move([-dictionary_values[1]["Outer Winding"]["Wire Diameter"] / 2, 0, -1])
    hfss.create_lumped_port_to_sheet(
        sheet.name, portname="port_" + str(port_position_list.index(position) + 1), reference_object_list=[ground]
    )

###############################################################################
# Create Mesh Operation
# ---------------------

cylinder_height = 2.5 * dictionary_values[1]["Outer Winding"]["Height"]
cylinder_position = [0, 0, first_winding_list[1][0][2] - 4]
mesh_operation_cylinder = hfss.modeler.create_cylinder(
    "XY", cylinder_position, ground_radius, cylinder_height, numSides=36, name="mesh_cylinder"
)
mesh = Mesh(hfss)
mesh.assign_length_mesh([mesh_operation_cylinder], maxlength=15, maxel=None, meshop_name="choke_mesh")


###############################################################################
# Create Boundaries
# -----------------
# A region with openings is needed to run the analysis.

region = hfss.modeler.create_region(pad_percent=1000)


###############################################################################
# Create the Setup
# ----------------
# A setup with a sweep will be used to run the simulation. Depending on your computing machine,
# simulation can take time.

setup = hfss.create_setup("MySetup")
setup.props["Frequency"] = "50MHz"
setup.props["MaximumPasses"] = 10
hfss.create_linear_count_sweep(
    setupname=setup.name,
    unit="MHz",
    freqstart=0.1,
    freqstop=100,
    num_of_freq_points=100,
    sweepname="sweep1",
    sweep_type="Interpolating",
    save_fields=False,
)

###############################################################################
# Save the project
# ----------------

hfss.save_project(os.path.join(temp_folder, "My_HFSS_Choke.aedt"))
hfss.modeler.fit_all()
hfss.plot(show=False, export_path=os.path.join(hfss.working_directory, "Image.jpg"), plot_air_objects=True)


###############################################################################
# Close AEDT
# ~~~~~~~~~~
# After the simulaton is completed, you can close AEDT or release it using the
# :func:`pyaedt.Desktop.release_desktop` method.
# All methods provide for saving the project before exiting.


if os.name != "posix":
    hfss.release_desktop()

