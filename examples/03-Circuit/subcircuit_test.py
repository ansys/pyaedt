from pyaedt import Circuit

cir = Circuit(specified_version="2021.2")

comp = cir.modeler.schematic.add_new_subcircuit([0.0, 0.0])
comp_name = comp.composed_name
cir.push_down(comp)

cir.variable_manager.set_variable("R_val", "35ohm", circuit_parameter=True)
cir.variable_manager.set_variable("L_val", "1e-7H", circuit_parameter=True)
cir.variable_manager.set_variable("C_val", "5e-10F", circuit_parameter=True)
p1 = cir.modeler.schematic.create_interface_port("In")
r1 = cir.modeler.schematic.create_resistor(value="R_val")
l1 = cir.modeler.schematic.create_inductor(value="L_val")
c1 = cir.modeler.schematic.create_capacitor(value="C_val")
p2 = cir.modeler.schematic.create_interface_port("Out")
cir.modeler.schematic.connect_components_in_series([p1, r1, l1, c1, p2])
cir.pop_up()

new_comp = cir.modeler.schematic.duplicate(comp_name, [0.0512, 0])
new_comp.parameters["R_val"] = "75ohm"

cir.release_desktop(False, False)