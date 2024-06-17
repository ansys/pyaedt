# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import math
import os
import sys

import pyaedt
from pyaedt.generic.general_methods import read_toml
from pyaedt.generic.settings import is_linux
import pyaedt.workflows
from pyaedt.workflows.misc import get_aedt_version
from pyaedt.workflows.misc import get_arguments
from pyaedt.workflows.misc import get_port
from pyaedt.workflows.misc import get_process_id
from pyaedt.workflows.misc import is_student

port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()
is_student = is_student()

# Extension batch arguments
extension_arguments = None
extension_description = "Create Circuit design from Twin Builder design"


def main(extension_args):

    app = pyaedt.Desktop(
        new_desktop=False,
        version=version,
        port=port,
        aedt_process_id=aedt_process_id,
        student_version=is_student,
    )

    if is_linux:  # pragma: no cover
        app.logger.error("This extension is not compatible with Linux.")
        if not extension_args["is_test"]:
            app.release_desktop(False, False)
        return True

    active_project = app.active_project()
    active_design = app.active_design()

    project_name = active_project.GetName()

    if active_design.GetDesignType() in ["Twin Builder"]:
        design_name = active_design.GetName().split(";")[1]
        tb = pyaedt.TwinBuilder(design=design_name, project=project_name)
    else:  # pragma: no cover
        app.logger.error("An active TwinBuilder Design is needed.")
        sys.exit()

    catalog = read_toml(os.path.join(pyaedt.__path__[0], "misc", "tb_nexxim_mapping.toml"))
    scale = catalog["General"]["scale"]
    cir = pyaedt.Circuit(design=tb.design_name + "_Translated")

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

    if not extension_args["is_test"]:  # pragma: no cover
        app.release_desktop(False, False)
    return True


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(extension_arguments, extension_description)
    main(args)
