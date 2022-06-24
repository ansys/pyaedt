"""
Circuit: Schematic Subcircuit Management
----------------------------------------
This example shows how you can use PyAEDT to add a subcircuit to a Circuit design.
 Push down into the child subcircuit and pop up to the parent design.
"""

import os

##########################################################
# Set Non Graphical Mode.
# Default is False

non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")

###############################################################################
# Launch AEDT and Circuit
# ~~~~~~~~~~~~~~~~~~~~~~~
# This examples launches AEDT 2022R2 in graphical mode.

from pyaedt import Circuit
circuit = Circuit(specified_version="2022.2", non_graphical=non_graphical, new_desktop_session=True)

###############################################################################
# Add new subcircuit
# ~~~~~~~~~~~~~~~~~~
# This example adds a new subcircuit to the previously created Circuit design
# becoming the child circuit.
# Then it pushes down into the child subcircuit.

subcircuit = circuit.modeler.schematic.create_subcircuit([0.0, 0.0])
subcircuit_name = subcircuit.composed_name
circuit.push_down(subcircuit)

###############################################################################
# Subcircuit parameterization
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This method parameterizes the subcircuit and adds a resistor, inductor,
# and a capacitor with the value given by the parameters.
# They are then connected in series.
# The ``pop_up`` method provides for getting back to the parent design.

circuit.variable_manager.set_variable("R_val", "35ohm")
circuit.variable_manager.set_variable("L_val", "1e-7H")
circuit.variable_manager.set_variable("C_val", "5e-10F")
p1 = circuit.modeler.schematic.create_interface_port("In")
r1 = circuit.modeler.schematic.create_resistor(value="R_val")
l1 = circuit.modeler.schematic.create_inductor(value="L_val")
c1 = circuit.modeler.schematic.create_capacitor(value="C_val")
p2 = circuit.modeler.schematic.create_interface_port("Out")
circuit.modeler.schematic.connect_components_in_series([p1, r1, l1, c1, p2])
circuit.pop_up()

###############################################################################
# Subcircuit duplication
# ~~~~~~~~~~~~~~~~~~~~~~
# The formerly created subcircuit is duplicated, and a new parameter value is set.
# It works only in graphical mode.

if not non_graphical:
    new_comp = circuit.modeler.schematic.duplicate(subcircuit_name, [0.0512, 0])
    new_comp.parameters["R_val"] = "75ohm"

circuit.release_desktop(True, True)
