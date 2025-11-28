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
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modeler.advanced_cad.coil import COIL_PARAMETERS
from ansys.aedt.core.modeler.advanced_cad.coil import Coil

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()
EXTENSION_TITLE = "Create coil"


def generate_extension_defaults():
    defaults = {"is_vertical": True}

    for category in ["Common", "Vertical", "Flat"]:
        defaults[category].update(COIL_PARAMETERS[category])
    return defaults


EXTENSION_DEFAULT_ARGUMENTS = generate_extension_defaults()


@dataclass
class CoilExtensionData(ExtensionCommonData):
    """Data class containing parameters to create coils."""

    is_vertical: str = EXTENSION_DEFAULT_ARGUMENTS["is_vertical"]
    # Common parameters
    name: str = EXTENSION_DEFAULT_ARGUMENTS["Common"]["name"]
    centre_x: str = EXTENSION_DEFAULT_ARGUMENTS["Common"]["centre_x"]
    centre_y: str = EXTENSION_DEFAULT_ARGUMENTS["Common"]["centre_y"]
    turns: str = EXTENSION_DEFAULT_ARGUMENTS["Common"]["turns"]
    inner_distance: str = EXTENSION_DEFAULT_ARGUMENTS["Common"]["inner_distance"]
    inner_width: str = EXTENSION_DEFAULT_ARGUMENTS["Common"]["inner_width"]
    inner_length: str = EXTENSION_DEFAULT_ARGUMENTS["Common"]["inner_length"]
    wire_radius: str = EXTENSION_DEFAULT_ARGUMENTS["Common"]["wire_radius"]
    arc_segmentation: str = EXTENSION_DEFAULT_ARGUMENTS["Common"]["arc_segmentation"]
    section_segmentation: str = EXTENSION_DEFAULT_ARGUMENTS["Common"]["section_segmentation"]
    # Vertical parameters
    centre_z: str = EXTENSION_DEFAULT_ARGUMENTS["Vertical"]["centre_z"]
    direction: str = EXTENSION_DEFAULT_ARGUMENTS["Vertical"]["direction"]
    pitch: str = EXTENSION_DEFAULT_ARGUMENTS["Vertical"]["pitch"]
    # Flat parameters
    distance_turns: str = EXTENSION_DEFAULT_ARGUMENTS["Flat"]["distance_turns"]
    looping_position: str = EXTENSION_DEFAULT_ARGUMENTS["Flat"]["looping_position"]


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

    def create_parameter_inputs(self, tab, tab_name):
        """Create parameter input widgets for a category."""
        group_frame = ttk.LabelFrame(
            tab,
            text=tab_name,
            style="PyAEDT.TLabelframe",
        )
        group_frame.pack(fill=ttk.X, padx=10, pady=5)
        is_vertical = tk.IntVar(self.root, name="is_vertical", value=1)
        self.__widget["check"] = ttk.Checkbutton(
            group_frame,
            variable=is_vertical,
            style="PyAEDT.TCheckbutton",
            name="is_vertical",
            command=self.on_checkbox_toggle(),
        )
        self.__widget["check"].pack(anchor=ttk.W, padx=5)

    def add_extension_content(self):
        """Add custom content to the extension UI."""
        master = self.root
        # Main panel
        main_frame = ttk.PanedWindow(master, orient=tk.HORIZONTAL, style="TPanedwindow")
        main_frame.grid(row=0, column=0, sticky="nsew")
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)

        for tab_name in ["Common", "Vertical", "Flat"]:
            tab = ttk.Frame(main_frame, style="PyAEDT.TFrame")
            main_frame.add(tab, text=tab_name)
            self.create_parameter_inputs(tab, tab_name)


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

    # coil = Coil(aedtapp, is_vertical=data.is_vertical)

    # Create polyline shape for coil
    # polyline = coil.create_vertical_path() if data.is_vertical else coil.create_flat_path()

    if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
        aedtapp.release_desktop(False, False)
    return True


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)
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
