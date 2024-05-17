import math
import os
import sys

import pyaedt
from pyaedt import Circuit
from pyaedt import Desktop
from pyaedt import TwinBuilder
from pyaedt.generic.general_methods import read_toml

if "PYAEDT_SCRIPT_PORT" in os.environ and "PYAEDT_SCRIPT_VERSION" in os.environ:
    port = int(os.environ["PYAEDT_SCRIPT_PORT"])
    version = os.environ["PYAEDT_SCRIPT_VERSION"]
else:
    port = 0
    version = "2024.1"

with Desktop(new_desktop_session=False, close_on_exit=False, specified_version=version, port=port) as d:
    proj = d.active_project()
    des = d.active_design()
    projname = proj.GetName()
    if des.GetDesignType() in ["Twin Builder"]:
        desname = des.GetName().split(";")[1]
        tb = TwinBuilder(designname=desname, projectname=projname)
    else:
        d.logger.error("An active TwinBuilder Design is needed.")
        sys.exit()
    catalog = read_toml(os.path.join(pyaedt.__path__[0], "misc", "tb_nexxim_mapping.toml"))
    scale = catalog["General"]["scale"]
    cir = Circuit(designname=tb.design_name + "_Translated")
    from pyaedt.generic.constants import unit_converter

    pins_unconnected = []
    added_components = {}
    for wire in tb.modeler.components.wires.values():
        seg_vals = list(wire.points_in_segment.values())
        for points in seg_vals:
            scaled_point = []
            for p in points:
                scaled_point.append([i * scale for i in p])
            cir.modeler.components.create_wire(scaled_point, wire.name)
    for vname, var in tb.variable_manager.independent_variables.items():
        cir[vname] = var.expression
    for vname, var in tb.variable_manager.dependent_variables.items():
        cir[vname] = var.expression
    for cmp, el in tb.modeler.components.components.items():
        if el.name in ["CompInst@FML_INIT"]:
            for k, p in el.parameters.items():
                if k.startswith("EQU"):
                    var = p.split(":=")
                    cir[var[0]] = var[1]
    for cmp, el in tb.modeler.components.components.items():
        cmp_name = el.name.split("@")[1]
        if cmp_name in catalog:
            x1 = unit_converter(catalog[cmp_name]["x_offset"] * scale, input_units="mil", output_units="meter")
            y1 = unit_converter(catalog[cmp_name]["y_offset"] * scale, input_units="mil", output_units="meter")
            offsetx = x1 * math.sin(math.pi * el.angle / 180) + y1 * math.cos(math.pi * el.angle / 180)
            offsety = +y1 * math.sin(math.pi * el.angle / 180) + x1 * math.cos(math.pi * el.angle / 180)
            refdes = ""
            if "InstanceName" in el.parameters:
                refdes = el.parameters["InstanceName"]
            cmpid = cir.modeler.components.create_component(
                refdes,
                component_library=catalog[cmp_name]["component_library"],
                component_name=catalog[cmp_name]["component_name"],
                location=[el.location[0] * scale + offsetx, el.location[1] * scale + offsety],
                angle=el.angle + catalog[cmp_name]["rotate_deg"],
            )
            if abs(offsetx) > 1e-9:
                for pin in cmpid.pins:
                    if pin.net == "":
                        origin = pin.location[:]
                        if pin.location[1] < cmpid.location[1]:
                            origin[1] = origin[1] - abs(offsetx)
                            cir.modeler.components.create_wire([pin.location[:], origin])
                        else:
                            origin[1] = origin[1] + abs(offsetx)
                            cir.modeler.components.create_wire([pin.location[:], origin])
            else:
                for pin in cmpid.pins:
                    if pin.net == "":
                        origin = pin.location[:]
                        if pin.location[0] < cmpid.location[0]:
                            origin[0] = origin[0] - abs(offsety)
                            cir.modeler.components.create_wire([pin.location[:], origin])
                        else:
                            origin[0] = origin[0] + abs(offsety)
                            cir.modeler.components.create_wire([origin, pin.location[:]])

            for p, value in catalog[cmp_name]["property_mapping"].items():
                cmpid.set_property(value, el.parameters[p])
        elif "GPort" in el.name:
            cmpid = cir.modeler.components.create_gnd([i * scale for i in el.location], el.angle)
            x1 = unit_converter(100, input_units="mil", output_units="meter")
            offsetx = x1 * math.sin(el.angle * math.pi / 180)
            offsety = x1 * math.cos(el.angle * math.pi / 180)
            cir.modeler.move(cmpid, offset=[-offsetx, offsety])
            cir.modeler.move(cmpid, offset=[offsetx, -offsety])
    for cpms in pins_unconnected:
        cir.modeler.move(cpms[0], cpms[1])
        for pin in cpms[0].pins:
            if pin.net == "":
                offsety = [-i for i in cpms[1]]
                cir.modeler.move(cpms[0], offsety)
