"""
Choke
--------------
This example shows how you can use PyAEDT to create an choke setup in HFSS.
"""

import json
import sys

from pyaedt import Desktop
from pyaedt import Hfss

###############################################################################
# Rules and information of use
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The dictionary values is containing the different parameters of the core and the windings which composed the choke.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The main structure of the dictionary must not be changed, i.e the dictionary has primary keys ("Number of Windings",
# "Layer", "Layer Type", etc...) which have dictionaries as values, these dictionaries keys are the secondary keys of
# the dictionary values ("1", "2", "3", "4", "Simple", etc...). Neither the primary nor the secondary keys
# must be modified, only their values.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The value type must be unchanged. For the dictionary from "Number of Windings" to "Wire Section" included,
# values must be boolean. Only one value by dictionary must be "True". If all values are "True" only the first one will
# remain so. If all values are "False", the first value will be choose as the correct one by default".
# For the dictionary from "Core" to "Inner Winding" included, values must be string or float or int.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# "Occupation(%)" is only an informative parameter, it is useless to modify it.
# If you have doubt you can let parameters like they are it will work.

values = {
    "Number of Windings": {"1": False, "2": True, "3": False, "4": False},
    "Layer": {"Simple": False, "Double": True, "Triple": False},
    "Layer Type": {"Separate": False, "Linked": True},
    "Similar Layer": {"Similar": False, "Different": True},
    "Mode": {"Differential": False, "Common": True},
    "Wire Section": {"None": False, "Hexagon": True, "Octagon": False, "Circle": False},
    "Core": {"Name": "Core", "Material": "iron", "Inner Radius": 20, "Outer Radius": 30, "Height": 10, "Chamfer": 0.8},
    "Outer Winding": {"Name": "Winding", "Material": "copper", "Inner Radius": 20, "Outer Radius": 30, "Height": 10,
                      "Wire Diameter": 1.5, "Turns": 20, "Coil Pit(deg)": 0.1, "Occupation(%)": 0},
    "Mid Winding": {"Turns": 25, "Coil Pit(deg)": 0.1, "Occupation(%)": 0},
    "Inner Winding": {"Turns": 4, "Coil Pit(deg)": 0.1, "Occupation(%)": 0}
}

###############################################################################
# Convert dictionary to json file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The PyAEDT methods ask the path of the json file as argument, so you can convert this dictionary in json file
# thanks to the following command. Please write your own path where you want to put the json file.


with open("C:/Users/jmichel/PycharmProjects/json_file/choke_demonstration.json", "w") as outfile:
    json.dump(values, outfile)

###############################################################################
# Launch AEDT in Graphical Mode
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This examples launches AEDT 2021.2 in graphical mode.


desktop = Desktop("2021.2", non_graphical=False, new_desktop_session=True)

###############################################################################
# Launch HFSS in Graphical Mode
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This examples launches HFSS 2021.2 in graphical mode.

hfss = Hfss(solution_type="Modal")

###############################################################################
# Verify the parameter of the json file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The first method "check_choke_values" will take the json file path in argument and:
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# - Check if the json file is correctly written (as it is explained in the rules)
# - Check inequations on windings parameters to avoid to have unintended intersection

dictionary_values = hfss.modeler.check_choke_values(
    "C:/Users/jmichel/PycharmProjects/json_file/choke_demonstration.json",
    create_another_file=False)
print(dictionary_values)

###############################################################################
# Generate the choke
# ~~~~~~~~~~~~~~~~~~
# This second method "create_choke" will take the json file path in argument and generate the choke.

list_object = hfss.modeler.create_choke(
    "C:/Users/jmichel/PycharmProjects/json_file/choke_demonstration.json")
