# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
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
from dataclasses import field
from dataclasses import make_dataclass
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk

import ansys.aedt.core
from ansys.aedt.core import get_pyaedt_app
import ansys.aedt.core.extensions
from ansys.aedt.core.extensions.misc import ExtensionCommon
from ansys.aedt.core.extensions.misc import ExtensionCommonData
from ansys.aedt.core.extensions.misc import ExtensionMaxwell3DCommon
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.generic.numbers_utils import Quantity
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modeler.advanced_cad.coil import COIL_PARAMETERS
from ansys.aedt.core.modeler.advanced_cad.coil import Coil

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()
EXTENSION_TITLE = "Create coil"


def prettyfy(key: str) -> str:
    """Convert a parameter key to a more readable format."""
    return key.replace("_", " ").title()


def generate_extension_defaults():
    defaults = {"Is Vertical": True}

    for category in ["Common", "Vertical", "Flat"]:
        defaults[category] = {prettyfy(k): v for k, v in COIL_PARAMETERS[category].items()}
    return defaults


def build_coil_extension_data(defaults):
    fields = [("is_vertical", bool, field(default=defaults["Is Vertical"]))]
    for category in ["Common", "Vertical", "Flat"]:
        for k, v in defaults[category].items():
            fields.append((k.replace(" ", "_").lower(), type(v), field(default=v)))
    return make_dataclass("CoilExtensionData", fields, bases=(ExtensionCommonData,))


defaults = generate_extension_defaults()
CoilExtensionData = build_coil_extension_data(defaults)
DEFAULT_PADDING = {"padx": 5, "pady": 5}


class CoilExtension(ExtensionMaxwell3DCommon):
    """Extension to create coils in AEDT."""

    def __init__(self, withdraw: bool = False):
        # Initialize the common extension class with the title and theme color
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=False,
            toggle_row=18,
            toggle_column=2,
        )
        # Initialize the Coil class
        self.coil = Coil(self.aedt_application, is_vertical=True)
        # Tkinter widgets
        self.__widget = {}
        # add custom content
        self.add_extension_content()

    def on_checkbox_toggle(self):
        pass

    def show_pictures_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Coil Parameters")

        tk_image = tk.PhotoImage(file=Path(__file__).parent / "images" / "large" / "coil_parameters.png")
        label = tk.Label(popup, image=tk_image)
        label.image = tk_image
        label.pack()

    def _add_vertical_coil_checkbox(self, tab, row):
        is_vertical_label = ttk.Label(tab, text="Vertical Coil", style="PyAEDT.TLabel", width=20)
        is_vertical_label.grid(row=row, column=0, **DEFAULT_PADDING)
        is_vertical = tk.IntVar(tab, name="is_vertical", value=1)
        self.__widget["is_vertical"] = ttk.Checkbutton(
            tab,
            variable=is_vertical,
            style="PyAEDT.TCheckbutton",
            name="is_vertical",
            command=self.on_checkbox_toggle(),
        )
        self.__widget["is_vertical"].var = is_vertical
        self.__widget["is_vertical"].grid(row=row, column=1, sticky="", padx=5)
        row += 1
        return row

    def _add_parameter_row(self, tab, parameter, default_value, row):
        widget_name = parameter.replace(" ", "_").lower()
        parameter_label = ttk.Label(tab, text=parameter, style="PyAEDT.TLabel", width=20)
        parameter_label.grid(row=row, column=0, **DEFAULT_PADDING)
        self.__widget[widget_name] = tk.Text(tab, width=20, height=1, name=widget_name)
        self.__widget[widget_name].configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        self.__widget[widget_name].grid(row=row, column=1, **DEFAULT_PADDING)
        self.__widget[widget_name].insert("1.0", f"{default_value}")
        row += 1
        return row

    def _add_export_button(self, tab, row):
        export_points_button = ttk.Button(
            tab, text="Parameters", command=self.show_pictures_popup, width=10, style="PyAEDT.TButton"
        )
        export_points_button.grid(row=row, column=1, **DEFAULT_PADDING)

    def create_parameter_inputs(self, tab, tab_name):
        """Create parameter input widgets for a category."""
        row = 0
        if tab_name == "Common":
            row = self._add_vertical_coil_checkbox(tab, row)

        for parameter, default_value in defaults[tab_name].items():
            row = self._add_parameter_row(tab, parameter, default_value, row)

        if tab_name == "Common":
            self._add_export_button(tab, row)

    def add_extension_content(self):
        """Add custom content to the extension UI."""

        def callback(extension: CoilExtension):
            data = CoilExtensionData()
            for k, widget in self.__widget.items():
                val = widget.get("1.0", "end-1c") if isinstance(widget, tk.Text) else bool(widget.var.get())
                if hasattr(data, k):
                    setattr(data, k, val)
            extension.data = data
            self.root.destroy()

        master = self.root
        # Main panel
        main_frame = ttk.PanedWindow(master, orient=tk.HORIZONTAL, style="TPanedwindow")
        main_frame.grid(row=0, column=0, sticky="nsew")
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)

        # Notebook
        notebook = ttk.Notebook(master, style="TNotebook")
        main_frame.add(notebook, weight=3)

        for tab_name in ["Common", "Vertical", "Flat"]:
            tab = ttk.Frame(notebook, style="PyAEDT.TFrame")
            notebook.add(tab, text=tab_name)
            self.create_parameter_inputs(tab, tab_name)

        create_coil = ttk.Button(
            master,
            text="Create Coil",
            width=20,
            style="PyAEDT.TButton",
            name="create_coil",
            command=lambda: callback(self),
        )
        create_coil.grid(row=1, column=0, **DEFAULT_PADDING)


def main(data: CoilExtensionData):
    """Main function to create coils in AEDT."""
    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        version=VERSION,
        port=PORT,
        aedt_process_id=AEDT_PROCESS_ID,
        student_version=IS_STUDENT,
    )

    active_project = app.active_project()
    active_design = app.active_design()

    project_name = active_project.GetName()
    design_name = active_design.GetName()

    aedtapp = get_pyaedt_app(project_name, design_name)
    if aedtapp.design_type != "Maxwell 3D":
        raise AEDTRuntimeError("This extension can only be used with Maxwell 3D designs.")

    coil = Coil(aedtapp, is_vertical=data.is_vertical)

    # Create polyline shape for coil
    polyline = coil.create_vertical_path() if data.is_vertical else coil.create_flat_path()

    # Define start point based on coil orientation
    centre_x = Quantity(data.centre_x).value
    centre_y = Quantity(data.centre_y).value
    inner_y = Quantity(data.inner_length).value

    if data.is_vertical:
        centre_z = Quantity(data.centre_z).value
        inner_distance = Quantity(data.inner_distance).value
        pitch = Quantity(data.pitch).value
        turns = int(data.turns)
        start_point = [
            centre_x,
            centre_y - 0.5 * inner_y - inner_distance,
            centre_z + pitch * turns * 0.5,
        ]
    else:
        inner_x = Quantity(data.inner_width).value
        start_position = Quantity(data.looping_position).value
        start_point = [
            centre_x + 0.25 * inner_x,
            centre_y - (start_position - 0.5) * inner_y,
            0,
        ]
    # Create coil profile
    coil.create_sweep_profile(start_point, polyline)

    if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
        aedtapp.release_desktop(False, False)
    return True


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(defaults, EXTENSION_TITLE)
    default_args = False
    parameters = {}
    # Open UI
    if not args["is_batch"]:
        extension: ExtensionCommon = CoilExtension(withdraw=False)

        tk.mainloop()

        main(extension.data)
    else:
        data = CoilExtensionData()
        for key, value in args.items():
            setattr(data, key, value)
        main(data)
