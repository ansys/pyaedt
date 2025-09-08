# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
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

from dataclasses import dataclass
import math
import os
import tkinter
from tkinter import ttk

import ansys.aedt.core
from ansys.aedt.core import get_pyaedt_app
from ansys.aedt.core.extensions.misc import ExtensionCommonData
from ansys.aedt.core.extensions.misc import ExtensionTwinBuilderCommon
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.generic.file_utils import read_toml
from ansys.aedt.core.generic.settings import is_linux
from ansys.aedt.core.internal.errors import AEDTRuntimeError

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()

# Extension batch arguments
EXTENSION_DEFAULT_ARGUMENTS = {"design_name": ""}
EXTENSION_TITLE = "Convert to Circuit"


@dataclass
class ConvertToCircuitExtensionData(ExtensionCommonData):
    """Data class containing user input and computed data."""

    design_name: str = EXTENSION_DEFAULT_ARGUMENTS["design_name"]


class ConvertToCircuitExtension(ExtensionTwinBuilderCommon):
    """Extension for converting TwinBuilder designs to Circuit."""

    def __init__(self, withdraw: bool = False):
        # Initialize extension class with title and theme
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=False,
            toggle_row=2,
            toggle_column=1,
        )

        # Add private attributes and initialize them
        self.__tb_designs = None
        self.__load_aedt_info()

        # Tkinter widgets
        self.combo_design = None

        # Add extension content manually
        self.add_extension_content()

    def __load_aedt_info(self):
        """Load Twin Builder design information."""
        try:
            designs = []
            for design in self.desktop.design_list():
                design_object = get_pyaedt_app(design_name=design)
                if design_object.design_type == "Twin Builder":
                    designs.append(design)
            if not designs:
                raise AEDTRuntimeError("No Twin Builder designs found in the active project.")

            self.__tb_designs = designs
        except Exception as e:
            raise AEDTRuntimeError(f"Failed to load Twin Builder designs: {str(e)}")

    def add_extension_content(self):
        """Add custom content to the extension UI."""
        # Design selection
        label = ttk.Label(self.root, text="Select Twin Builder Design:", width=30, style="PyAEDT.TLabel")
        label.grid(row=0, column=0, padx=15, pady=10)
        self._widgets["label"] = label

        # Dropdown menu for designs
        self.combo_design = ttk.Combobox(
            self.root, width=30, style="PyAEDT.TCombobox", name="combo_design", state="readonly"
        )
        self.combo_design["values"] = self.__tb_designs
        if self.__tb_designs:
            self.combo_design.current(0)
        self.combo_design.grid(row=0, column=1, padx=15, pady=10)
        self.combo_design.focus_set()
        self._widgets["combo_design"] = self.combo_design

        # Information label
        info_label = ttk.Label(
            self.root,
            text="This will create a new Circuit design with converted components.",
            width=50,
            style="PyAEDT.TLabel",
        )
        info_label.grid(row=1, column=0, columnspan=2, padx=15, pady=5)
        self._widgets["info_label"] = info_label

        def callback(extension: ConvertToCircuitExtension):
            data = ConvertToCircuitExtensionData()
            data.design_name = extension.combo_design.get()
            extension.data = data
            extension.root.quit()

        ok_button = ttk.Button(
            self.root,
            text="Convert",
            width=20,
            command=lambda: callback(self),
            style="PyAEDT.TButton",
            name="convert",
        )
        ok_button.grid(row=2, column=0, padx=15, pady=10)
        self._widgets["ok_button"] = ok_button


def main(data: ConvertToCircuitExtensionData):
    """Main function to run the convert to circuit extension."""
    if not data.design_name:
        raise AEDTRuntimeError("No design provided to the extension.")

    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        version=VERSION,
        port=PORT,
        aedt_process_id=AEDT_PROCESS_ID,
        student_version=IS_STUDENT,
    )

    if is_linux:  # pragma: no cover
        app.logger.error("This extension is not compatible with Linux.")
        if "PYTEST_CURRENT_TEST" not in os.environ:
            app.release_desktop(False, False)
        return True

    active_project = app.active_project()
    project_name = active_project.GetName()

    # Get the specific TwinBuilder design
    tb = get_pyaedt_app(project_name, data.design_name)

    try:
        # Read the catalog for component mapping
        catalog_path = os.path.join(ansys.aedt.core.__path__[0], "misc", "tb_nexxim_mapping.toml")
        catalog = read_toml(catalog_path)
        scale = catalog["General"]["scale"]

        # Create new Circuit design
        cir = ansys.aedt.core.Circuit(design=tb.design_name + "_Translated")

        from ansys.aedt.core.generic.constants import unit_converter

        pins_unconnected = []

        # Convert wires
        for wire in tb.modeler.components.wires.values():
            seg_vals = list(wire.points_in_segment.values())
            for points in seg_vals:
                scaled_point = []
                for p in points:
                    scaled_point.append([i * scale for i in p])
                cir.modeler.components.create_wire(scaled_point, wire.name)

        # Copy variables
        for vname, var in tb.variable_manager.independent_variables.items():  # noqa: E501
            cir[vname] = var.expression
        for vname, var in tb.variable_manager.dependent_variables.items():  # noqa: E501
            cir[vname] = var.expression

        # Process equations from FML_INIT components
        for cmp, el in tb.modeler.components.components.items():
            if el.name in ["CompInst@FML_INIT"]:
                for k, p in el.parameters.items():
                    if k.startswith("EQU"):
                        var = p.split(":=")
                        cir[var[0]] = var[1]

        # Convert components
        for cmp, el in tb.modeler.components.components.items():
            cmp_name = el.name.split("@")[1]

            if cmp_name in catalog:
                # Calculate offsets based on scaling and rotation
                x1 = unit_converter(catalog[cmp_name]["x_offset"] * scale, input_units="mil", output_units="meter")
                y1 = unit_converter(catalog[cmp_name]["y_offset"] * scale, input_units="mil", output_units="meter")
                offsetx = x1 * math.sin(math.pi * el.angle / 180) + y1 * math.cos(math.pi * el.angle / 180)
                offsety = y1 * math.sin(math.pi * el.angle / 180) + x1 * math.cos(math.pi * el.angle / 180)

                # Get reference designator
                refdes = ""
                if "InstanceName" in el.parameters:
                    refdes = el.parameters["InstanceName"]

                # Create component in Circuit
                cmpid = cir.modeler.components.create_component(
                    refdes,
                    component_library=catalog[cmp_name]["component_library"],
                    component_name=catalog[cmp_name]["component_name"],
                    location=[el.location[0] * scale + offsetx, el.location[1] * scale + offsety],
                    angle=el.angle + catalog[cmp_name]["rotate_deg"],
                )

                # Create wires for unconnected pins
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
                    for pin in cmpid.pins:  # pragma: no cover
                        if pin.net == "":
                            origin = pin.location[:]
                            if pin.location[0] < cmpid.location[0]:
                                origin[0] = origin[0] - abs(offsety)
                                cir.modeler.components.create_wire([pin.location[:], origin])
                            else:
                                origin[0] = origin[0] + abs(offsety)
                                cir.modeler.components.create_wire([origin, pin.location[:]])

                # Map component properties
                prop_mapping = catalog[cmp_name]["property_mapping"]
                for p, value in prop_mapping.items():
                    cmpid.set_property(value, el.parameters[p])

            elif "GPort" in el.name:
                # Create ground component
                cmpid = cir.modeler.components.create_gnd([i * scale for i in el.location], el.angle)
                x1 = unit_converter(100, input_units="mil", output_units="meter")
                offsetx = x1 * math.sin(el.angle * math.pi / 180)
                offsety = x1 * math.cos(el.angle * math.pi / 180)
                cir.modeler.move(cmpid, offset=[-offsetx, offsety])
                cir.modeler.move(cmpid, offset=[offsetx, -offsety])

        # Handle unconnected pins
        for cpms in pins_unconnected:  # pragma: no cover
            cir.modeler.move(cpms[0], cpms[1])
            for pin in cpms[0].pins:
                if pin.net == "":
                    offsety = [-i for i in cpms[1]]
                    cir.modeler.move(cpms[0], offsety)

        app.logger.info(f"Successfully converted '{tb.design_name}' to Circuit design '{cir.design_name}'")

    except Exception as e:  # pragma: no cover
        app.logger.error(f"Error during conversion: {str(e)}")
        raise AEDTRuntimeError(f"Failed to convert design: {str(e)}")

    if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
        app.release_desktop(False, False)
    return True


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)

    # Open UI
    if not args["is_batch"]:
        extension = ConvertToCircuitExtension(withdraw=False)

        tkinter.mainloop()

        if extension.data is not None:
            main(extension.data)

    else:
        data = ConvertToCircuitExtensionData()
        for key, value in args.items():
            if hasattr(data, key):
                setattr(data, key, value)
        main(data)
