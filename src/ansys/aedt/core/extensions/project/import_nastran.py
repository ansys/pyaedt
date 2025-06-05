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

from dataclasses import asdict
from dataclasses import dataclass
import os
from pathlib import Path
import tkinter

import ansys.aedt.core
from ansys.aedt.core import get_pyaedt_app
import ansys.aedt.core.extensions
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.visualization.advanced.misc import nastran_to_stl


@dataclass
class ExtensionData:
    decimate: float = 0.0
    lightweight: bool = False
    planar: bool = True
    file_path: str = ""


PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()
EXTENSION_TITLE = "Import Nastran or STL file"
EXTENSION_DEFAULT_ARGUMENTS = {"decimate": 0.0, "lightweight": False, "planar": True, "file_path": ""}

result = None


def create_ui(withdraw=False):
    from tkinter import filedialog
    from tkinter import ttk

    from ansys.aedt.core.extensions.misc import create_default_ui

    root, theme, style = create_default_ui(EXTENSION_TITLE, withdraw=withdraw)

    label2 = ttk.Label(root, text="Browse file:", style="PyAEDT.TLabel")
    label2.grid(row=0, column=0, pady=10)

    text = tkinter.Text(root, width=40, height=1, name="file_path_text")
    text.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
    text.grid(row=0, column=1, pady=10, padx=5)

    def browseFiles():
        filename = filedialog.askopenfilename(
            initialdir="/",
            title="Select a Nastran or stl File",
            filetypes=(("Nastran", "*.nas"), ("STL", "*.stl"), ("all files", "*.*")),
        )
        text.insert(tkinter.END, filename)

    b1 = ttk.Button(root, text="...", width=10, command=browseFiles, style="PyAEDT.TButton", name="browse_button")
    b1.grid(row=0, column=2, pady=10)

    label = ttk.Label(root, text="Decimation factor (0-0.9). It may affect results:", style="PyAEDT.TLabel")
    label.grid(row=1, column=0, pady=10)

    check = tkinter.Text(root, width=20, height=1, name="decimation_text")
    check.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
    check.insert(tkinter.END, "0.0")
    check.grid(row=1, column=1, pady=10, padx=5)

    label = ttk.Label(root, text="Import as lightweight (only HFSS):", style="PyAEDT.TLabel")
    label.grid(row=2, column=0, pady=10)
    light = tkinter.IntVar(root, name="var_lightweight")
    check2 = ttk.Checkbutton(root, variable=light, style="PyAEDT.TCheckbutton", name="check_lightweight")
    check2.grid(row=2, column=1, pady=10, padx=5)

    label = ttk.Label(root, text="Enable planar merge:", style="PyAEDT.TLabel")
    label.grid(row=3, column=0, pady=10)
    planar = tkinter.IntVar(root, value=1)
    check3 = ttk.Checkbutton(root, variable=planar, style="PyAEDT.TCheckbutton", name="check_planar_merge")
    check3.grid(row=3, column=1, pady=10, padx=5)

    def toggle_theme():
        if root.theme == "light":
            set_dark_theme()
            root.theme = "dark"
        else:
            set_light_theme()
            root.theme = "light"

    def set_light_theme():
        root.configure(bg=theme.light["widget_bg"])
        text.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
        check.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
        theme.apply_light_theme(style)
        change_theme_button.config(text="\u263d")  # Sun icon for light theme

    def set_dark_theme():
        root.configure(bg=theme.dark["widget_bg"])
        text.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        check.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        theme.apply_dark_theme(style)
        change_theme_button.config(text="\u2600")  # Moon icon for dark theme

    # Create a frame for the toggle button to position it correctly
    button_frame = ttk.Frame(
        root, style="PyAEDT.TFrame", relief=tkinter.SUNKEN, borderwidth=2, name="theme_button_frame"
    )
    button_frame.grid(row=5, column=2, pady=10, padx=10)

    # Add the toggle theme button inside the frame
    change_theme_button = ttk.Button(
        button_frame, width=20, text="\u263d", command=toggle_theme, style="PyAEDT.TButton", name="theme_toggle_button"
    )

    change_theme_button.grid(row=0, column=0, padx=0)

    def callback():
        global result
        result = ExtensionData(
            decimate=float(check.get("1.0", tkinter.END).strip()),
            lightweight=True if light.get() == 1 else False,
            planar=True if planar.get() == 1 else False,
            file_path=text.get("1.0", tkinter.END).strip(),
        )
        root.destroy()

    def preview():
        decimate_ui = float(check.get("1.0", tkinter.END).strip())
        file_path_ui = text.get("1.0", tkinter.END).strip()
        if not file_path_ui:
            raise ValueError("Incorrect file path. Please select a valid file.")

        if not Path(file_path_ui).is_file():
            raise FileNotFoundError(f"File ({file_path_ui}) not found")

        if file_path_ui.endswith(".nas"):
            nastran_to_stl(file_path_ui, decimation=decimate_ui, preview=True)
        else:
            from ansys.aedt.core.visualization.advanced.misc import simplify_stl

            simplify_stl(file_path_ui, decimation=decimate_ui, preview=True)

    b2 = ttk.Button(root, text="Preview", width=40, command=preview, style="PyAEDT.TButton", name="preview_button")
    b2.grid(row=5, column=0, pady=10, padx=10)

    b3 = ttk.Button(root, text="Ok", width=40, command=callback, style="PyAEDT.TButton", name="ok_button")
    b3.grid(row=5, column=1, pady=10, padx=10)

    return root


def main(extension_args):
    file_path = Path(extension_args["file_path"])
    lightweight = extension_args["lightweight"]
    decimate = extension_args["decimate"]
    planar = extension_args["planar"]

    if file_path.is_file():
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

        if file_path.suffix == ".nas":
            aedtapp.modeler.import_nastran(
                str(file_path), import_as_light_weight=lightweight, decimation=decimate, enable_planar_merge=str(planar)
            )
        else:
            from ansys.aedt.core.visualization.advanced.misc import simplify_stl

            outfile = simplify_stl(str(file_path), decimation=decimate)
            aedtapp.modeler.import_3d_cad(
                outfile, healing=False, create_lightweigth_part=lightweight, merge_planar_faces=planar
            )
        app.logger.info("Geometry imported correctly.")
    else:
        app = ansys.aedt.core.Desktop(
            new_desktop=False,
            version=VERSION,
            port=PORT,
            aedt_process_id=AEDT_PROCESS_ID,
            student_version=IS_STUDENT,
        )
        app.logger.debug("Wrong file selected. Select a .nas or .stl file")

    if "PYTEST_CURRENT_TEST" not in os.environ:
        app.release_desktop(False, False)
    return True


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)

    # Open UI
    if not args["is_batch"]:  # pragma: no cover
        root = create_ui()

        tkinter.mainloop()

        if result:
            args.update(asdict(result))
            main(args)
    else:
        main(args)
