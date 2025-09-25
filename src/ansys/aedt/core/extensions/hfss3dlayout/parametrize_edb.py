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

from dataclasses import dataclass
import os
from pathlib import Path
import tkinter
from tkinter import ttk

from pyedb import Edb

import ansys.aedt.core
from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core.extensions.misc import ExtensionCommonData
from ansys.aedt.core.extensions.misc import ExtensionHFSS3DLayoutCommon
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.internal.errors import AEDTRuntimeError

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()

# Extension batch arguments
EXTENSION_DEFAULT_ARGUMENTS = {
    "aedb_path": "",
    "design_name": "",
    "parametrize_layers": True,
    "parametrize_materials": True,
    "parametrize_padstacks": True,
    "parametrize_traces": True,
    "nets_filter": [],
    "expansion_polygon_mm": 0.0,
    "expansion_void_mm": 0.0,
    "relative_parametric": True,
    "project_name": "",
}
EXTENSION_TITLE = "Layout Parametrization"


@dataclass
class ParametrizeEdbExtensionData(ExtensionCommonData):
    """Data class containing user input and computed data."""

    aedb_path: str = EXTENSION_DEFAULT_ARGUMENTS["aedb_path"]
    design_name: str = EXTENSION_DEFAULT_ARGUMENTS["design_name"]
    parametrize_layers: bool = EXTENSION_DEFAULT_ARGUMENTS["parametrize_layers"]
    parametrize_materials: bool = EXTENSION_DEFAULT_ARGUMENTS["parametrize_materials"]
    parametrize_padstacks: bool = EXTENSION_DEFAULT_ARGUMENTS["parametrize_padstacks"]
    parametrize_traces: bool = EXTENSION_DEFAULT_ARGUMENTS["parametrize_traces"]
    nets_filter: list = None
    expansion_polygon_mm: float = EXTENSION_DEFAULT_ARGUMENTS["expansion_polygon_mm"]
    expansion_void_mm: float = EXTENSION_DEFAULT_ARGUMENTS["expansion_void_mm"]
    relative_parametric: bool = EXTENSION_DEFAULT_ARGUMENTS["relative_parametric"]
    project_name: str = EXTENSION_DEFAULT_ARGUMENTS["project_name"]

    def __post_init__(self):
        if self.nets_filter is None:
            self.nets_filter = EXTENSION_DEFAULT_ARGUMENTS["nets_filter"].copy()


class ParametrizeEdbExtension(ExtensionHFSS3DLayoutCommon):
    """Extension for parametrizing EDB layouts in AEDT."""

    def __init__(self, withdraw: bool = False):
        # Initialize the common extension class with the title and theme color
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=False,
        )
        # Initialize data object
        self.data = ParametrizeEdbExtensionData()

        # Private attributes
        self.__active_project_path = None
        self.__active_project_name = None
        self.__aedb_path = None
        self.__active_design_name = None
        self.__available_nets = []

        # Load AEDT info
        self.__load_aedt_info()

        # Tkinter widgets
        self.project_name_entry = None
        self.relative_var = None
        self.relative_checkbox = None
        self.layers_var = None
        self.layers_checkbox = None
        self.materials_var = None
        self.materials_checkbox = None
        self.padstacks_var = None
        self.padstacks_checkbox = None
        self.traces_var = None
        self.traces_checkbox = None
        self.polygons_entry = None
        self.voids_entry = None
        self.nets_listbox = None
        self.generate_button = None

        # Trigger manually since add_extension_content requires loading info first
        self.add_extension_content()

    def __load_aedt_info(self):
        """Load AEDT information for the extension."""
        try:
            app = ansys.aedt.core.Desktop(
                new_desktop=False,
                version=VERSION,
                port=PORT,
                aedt_process_id=AEDT_PROCESS_ID,
                student_version=IS_STUDENT,
            )
            active_project = app.active_project()
            if not active_project:
                raise AEDTRuntimeError("No active project found in AEDT.")

            active_design = app.active_design()
            if not active_design:
                raise AEDTRuntimeError("No active design found in AEDT.")

            self.__active_project_path = active_project.GetPath()
            self.__active_project_name = active_project.GetName()
            self.__aedb_path = Path(self.__active_project_path) / (self.__active_project_name + ".aedb")
            self.__active_design_name = active_design.GetName().split(";")[1]

            app.release_desktop(False, False)

            # Load EDB to get nets information
            edb = Edb(str(self.__aedb_path), self.__active_design_name, edbversion=VERSION)
            self.__available_nets = list(edb.nets.nets.keys())
            edb.close_edb()

        except Exception as e:
            raise AEDTRuntimeError(f"Failed to load AEDT information: {str(e)}")

    def add_extension_content(self):
        """Add extension content to the UI."""
        # Project name
        ttk.Label(self.root, text="New project name:", style="PyAEDT.TLabel").grid(row=0, column=0, pady=10, sticky="w")
        self.project_name_entry = tkinter.Entry(self.root, width=30)
        self.project_name_entry.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        default_name = generate_unique_name(self.__active_project_name, n=2)
        self.project_name_entry.insert(tkinter.END, default_name)
        self.project_name_entry.grid(row=0, column=1, pady=10, padx=5, sticky="w")

        # Relative parameters checkbox
        ttk.Label(self.root, text="Use relative parameters:", style="PyAEDT.TLabel").grid(
            row=0, column=2, pady=10, sticky="w"
        )
        self.relative_var = tkinter.IntVar()
        self.relative_checkbox = ttk.Checkbutton(self.root, variable=self.relative_var, style="PyAEDT.TCheckbutton")
        self.relative_checkbox.grid(row=0, column=3, pady=10, padx=5, sticky="w")
        self.relative_var.set(1)

        # Parametrization options
        ttk.Label(self.root, text="Parametrize Layers:", style="PyAEDT.TLabel").grid(
            row=1, column=0, pady=10, sticky="w"
        )
        self.layers_var = tkinter.IntVar()
        self.layers_checkbox = ttk.Checkbutton(self.root, variable=self.layers_var, style="PyAEDT.TCheckbutton")
        self.layers_checkbox.grid(row=1, column=1, pady=10, padx=5, sticky="w")
        self.layers_var.set(1)

        ttk.Label(self.root, text="Parametrize Materials:", style="PyAEDT.TLabel").grid(
            row=1, column=2, pady=10, sticky="w"
        )
        self.materials_var = tkinter.IntVar()
        self.materials_checkbox = ttk.Checkbutton(self.root, variable=self.materials_var, style="PyAEDT.TCheckbutton")
        self.materials_checkbox.grid(row=1, column=3, pady=10, padx=5, sticky="w")
        self.materials_var.set(1)

        ttk.Label(self.root, text="Parametrize Padstacks:", style="PyAEDT.TLabel").grid(
            row=2, column=0, pady=10, sticky="w"
        )
        self.padstacks_var = tkinter.IntVar()
        self.padstacks_checkbox = ttk.Checkbutton(self.root, variable=self.padstacks_var, style="PyAEDT.TCheckbutton")
        self.padstacks_checkbox.grid(row=2, column=1, pady=10, padx=5, sticky="w")
        self.padstacks_var.set(1)

        ttk.Label(self.root, text="Parametrize Traces:", style="PyAEDT.TLabel").grid(
            row=2, column=2, pady=10, sticky="w"
        )
        self.traces_var = tkinter.IntVar()
        self.traces_checkbox = ttk.Checkbutton(self.root, variable=self.traces_var, style="PyAEDT.TCheckbutton")
        self.traces_checkbox.grid(row=2, column=3, pady=10, padx=5, sticky="w")
        self.traces_var.set(1)

        # Expansion options
        ttk.Label(self.root, text="Extend Polygons (mm):", style="PyAEDT.TLabel").grid(
            row=3, column=0, pady=10, sticky="w"
        )
        self.polygons_entry = tkinter.Text(self.root, width=20, height=1)
        self.polygons_entry.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        self.polygons_entry.insert(tkinter.END, "0.0")
        self.polygons_entry.grid(row=3, column=1, pady=10, padx=5, sticky="w")

        ttk.Label(self.root, text="Extend Voids (mm):", style="PyAEDT.TLabel").grid(
            row=3, column=2, pady=10, sticky="w"
        )
        self.voids_entry = tkinter.Text(self.root, width=20, height=1)
        self.voids_entry.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )
        self.voids_entry.insert(tkinter.END, "0.0")
        self.voids_entry.grid(row=3, column=3, pady=10, padx=5, sticky="w")

        # Nets selection
        ttk.Label(self.root, text="Select Nets (None for all):", style="PyAEDT.TLabel").grid(
            row=4, column=0, pady=10, sticky="w"
        )

        # Create a frame for the listbox and scrollbar
        nets_frame = ttk.Frame(self.root, style="PyAEDT.TFrame")
        nets_frame.grid(row=4, column=1, columnspan=3, pady=5, padx=5, sticky="w")

        self.nets_listbox = tkinter.Listbox(nets_frame, height=8, width=50, selectmode=tkinter.MULTIPLE)
        self.nets_listbox.configure(
            bg=self.theme.light["pane_bg"], foreground=self.theme.light["text"], font=self.theme.default_font
        )

        # Add scrollbar for nets listbox
        nets_scrollbar = ttk.Scrollbar(nets_frame, orient=tkinter.VERTICAL)
        self.nets_listbox.configure(yscrollcommand=nets_scrollbar.set)
        nets_scrollbar.configure(command=self.nets_listbox.yview)

        self.nets_listbox.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        nets_scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        # Populate nets listbox
        for idx, net in enumerate(self.__available_nets):
            self.nets_listbox.insert(idx, net)

        # Generate button
        self.generate_button = ttk.Button(
            self.root,
            text="Generate Parametric Model",
            command=self.generate_callback,
            style="PyAEDT.TButton",
            name="generate",
        )
        self.generate_button.grid(row=5, column=1, columnspan=2, pady=20)

    def generate_callback(self):
        """Generate callback function."""
        try:
            # Validate expansion values
            polygon_expansion = float(self.polygons_entry.get("1.0", tkinter.END).strip())
            if polygon_expansion < 0:
                raise ValueError("Polygon expansion cannot be negative")

            void_expansion = float(self.voids_entry.get("1.0", tkinter.END).strip())
            if void_expansion < 0:
                raise ValueError("Void expansion cannot be negative")

            # Get project name
            project_name = self.project_name_entry.get().strip()
            if not project_name:
                raise ValueError("Project name cannot be empty")

            # Get selected nets
            selected_nets = []
            for i in self.nets_listbox.curselection():
                selected_nets.append(self.nets_listbox.get(i))

            # Create data object
            self.data = ParametrizeEdbExtensionData(
                aedb_path=str(self.__aedb_path),
                design_name=self.__active_design_name,
                parametrize_layers=bool(self.layers_var.get()),
                parametrize_materials=bool(self.materials_var.get()),
                parametrize_padstacks=bool(self.padstacks_var.get()),
                parametrize_traces=bool(self.traces_var.get()),
                nets_filter=selected_nets,
                expansion_polygon_mm=polygon_expansion,
                expansion_void_mm=void_expansion,
                relative_parametric=bool(self.relative_var.get()),
                project_name=project_name,
            )

            self.root.destroy()

        except ValueError as e:
            self.show_error_message(f"Invalid input: {str(e)}")
        except Exception as e:
            self.show_error_message(f"Error: {str(e)}")

    def show_error_message(self, message):
        """Show error message."""
        import tkinter.messagebox

        tkinter.messagebox.showerror("Error", message)


def main(data: ParametrizeEdbExtensionData):
    """Main function to run the parametrize EDB extension."""
    if data.expansion_polygon_mm < 0:
        raise AEDTRuntimeError("Polygon expansion cannot be negative.")

    if data.expansion_void_mm < 0:
        raise AEDTRuntimeError("Void expansion cannot be negative.")

    if not data.project_name.strip():
        raise AEDTRuntimeError("Project name cannot be empty.")

    # Get AEDT application
    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        version=VERSION,
        port=PORT,
        aedt_process_id=AEDT_PROCESS_ID,
        student_version=IS_STUDENT,
    )

    # Get project and design information
    aedb_path = data.aedb_path
    design_name = data.design_name

    if not aedb_path:
        active_project = app.active_project()
        if not active_project:
            raise AEDTRuntimeError("No active project found in AEDT.")

        active_design = app.active_design()
        if not active_design:
            raise AEDTRuntimeError("No active design found in AEDT.")

        project_path = active_project.GetPath()
        project_name = active_project.GetName()
        aedb_path = str(Path(project_path) / (project_name + ".aedb"))
        design_name = active_design.GetName().split(";")[1]

    # Open EDB
    edb = Edb(str(aedb_path), design_name, edbversion=VERSION)

    # Convert expansion values from mm to meters
    poly_expansion_m = data.expansion_polygon_mm * 0.001 if data.expansion_polygon_mm > 0 else None
    voids_expansion_m = data.expansion_void_mm * 0.001 if data.expansion_void_mm > 0 else None

    # Create output path for new parametric project
    new_project_aedb = Path(aedb_path).parent / (data.project_name + ".aedb")

    # Parametrize the design
    edb.auto_parametrize_design(
        layers=data.parametrize_layers,
        materials=data.parametrize_materials,
        via_holes=data.parametrize_padstacks,
        pads=data.parametrize_padstacks,
        antipads=data.parametrize_padstacks,
        traces=data.parametrize_traces,
        layer_filter=None,
        material_filter=None,
        padstack_definition_filter=None,
        trace_net_filter=(data.nets_filter if data.nets_filter else None),
        use_single_variable_for_padstack_definitions=True,
        use_relative_variables=data.relative_parametric,
        output_aedb_path=str(new_project_aedb),
        open_aedb_at_end=False,
        expand_polygons_size=poly_expansion_m,
        expand_voids_size=voids_expansion_m,
    )

    edb.close_edb()

    # Open the new parametric design in HFSS 3D Layout
    if "PYTEST_CURRENT_TEST" not in os.environ:
        h3d = Hfss3dLayout(str(new_project_aedb))
        h3d.logger.info("Parametric project generated successfully.")
        h3d.desktop_class.release_desktop(False, False)

    return True


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)

    # Check PyEDB version requirement
    import pyedb

    if pyedb.__version__ < "0.21.0":
        raise Exception("PyEDB 0.21.0 or newer is required to run this extension.")

    # Open UI
    if not args["is_batch"]:
        extension = ParametrizeEdbExtension(withdraw=False)

        # Start the main loop - this will block until the UI is closed
        tkinter.mainloop()

        # Check if user completed the form and data is available
        if hasattr(extension, "data") and extension.data.project_name.strip():
            main(extension.data)
    else:
        # Create data object from arguments
        data = ParametrizeEdbExtensionData(
            aedb_path=args.get("aedb_path", ""),
            design_name=args.get("design_name", ""),
            parametrize_layers=args.get("parametrize_layers", True),
            parametrize_materials=args.get("parametrize_materials", True),
            parametrize_padstacks=args.get("parametrize_padstacks", True),
            parametrize_traces=args.get("parametrize_traces", True),
            nets_filter=args.get("nets_filter", []),
            expansion_polygon_mm=args.get("expansion_polygon_mm", 0.0),
            expansion_void_mm=args.get("expansion_void_mm", 0.0),
            relative_parametric=args.get("relative_parametric", True),
            project_name=args.get("project_name", generate_unique_name("Parametric", n=2)),
        )
        main(data)
