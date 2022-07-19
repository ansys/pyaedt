"""
Circuit: schematic subcircuit management
----------------------------------------
This example shows how you can use PyAEDT to add a subcircuit to a circuit design.
It pushes down the child subcircuit and pops up to the parent design.
"""
##########################################################
# Perform required import
# ~~~~~~~~~~~~~~~~~~~~~~~
# Perform the required import.

import os

##########################################################
# Set non-graphical mode
# ~~~~~~~~~~~~~~~~~~~~~~
# Set non-graphical mode. The default is ``False``.

non_graphical = os.getenv("PYAEDT_NON_GRAPHICAL", "False").lower() in ("true", "1", "t")

###############################################################################
# Launch AEDT with Circuit
# ~~~~~~~~~~~~~~~~~~~~~~~
# Launch AEDT 2022 R2 in graphical mode with Circuit.

from pyaedt import Circuit
circuit = Circuit(specified_version="2022.2", non_graphical=non_graphical, new_desktop_session=True)

###############################################################################
# Add subcircuit
# ~~~~~~~~~~~~~~
# Add a new subcircuit to the previously created circuit design, creating a
# child circuit. Push this child circuit down into the child subcircuit.

subcircuit = circuit.modeler.schematic.create_subcircuit([0.0, 0.0])
subcircuit_name = subcircuit.composed_name
circuit.push_down(subcircuit)

###############################################################################
# Parameterize subcircuit
# ~~~~~~~~~~~~~~~~~~~~~~~
# Parameterize the subcircuit and add a resistor, inductor, and a capacitor with
# the given parameter values. Connect them in series and then use the ``pop_up``
# method to get back to the parent design.

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
# Duplicate subcircuit
# ~~~~~~~~~~~~~~~~~~~~
# Duplicate the previously created subcircuit and set a new parameter value.
# This works only in graphical mode.

if not non_graphical:
    new_comp = circuit.modeler.schematic.duplicate(subcircuit_name, [0.0512, 0])
    new_comp.parameters["R_val"] = "75ohm"

# Release AEDT
# ~~~~~~~~~~~~
# Release AEDT.

circuit.release_desktop(True, True)
