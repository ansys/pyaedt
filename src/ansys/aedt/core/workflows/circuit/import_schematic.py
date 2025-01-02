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

from pathlib import Path

import ansys.aedt.core
from ansys.aedt.core import Circuit
import ansys.aedt.core.workflows
from ansys.aedt.core.workflows.misc import get_aedt_version
from ansys.aedt.core.workflows.misc import get_arguments
from ansys.aedt.core.workflows.misc import get_port
from ansys.aedt.core.workflows.misc import get_process_id
from ansys.aedt.core.workflows.misc import is_student

port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()
is_student = is_student()

# Extension batch arguments
extension_arguments = {"asc_file": ""}
extension_description = "Import schematic to Circuit"


def frontend():  # pragma: no cover
    import tkinter
    from tkinter import filedialog
    from tkinter import ttk

    import PIL.Image
    import PIL.ImageTk
    from ansys.aedt.core.workflows.misc import ExtensionTheme

    master = tkinter.Tk()
    master.title(extension_description)

    # Detect if user closes the UI
    master.flag = False

    # Load the logo for the main window
    icon_path = Path(ansys.aedt.core.workflows.__path__[0]) / "images" / "large" / "logo.png"
    im = PIL.Image.open(icon_path)
    photo = PIL.ImageTk.PhotoImage(im)

    # Set the icon for the main window
    master.iconphoto(True, photo)

    # Configure style for ttk buttons
    style = ttk.Style()
    theme = ExtensionTheme()

    # Apply light theme initially
    theme.apply_light_theme(style)
    master.theme = "light"

    # Set background color of the window (optional)
    master.configure(bg=theme.light["widget_bg"])

    label2 = ttk.Label(master, text="Browse file:", style="PyAEDT.TLabel")
    label2.grid(row=0, column=0, pady=10, padx=10)

    text = tkinter.Text(master, width=40, height=1)
    text.grid(row=0, column=1, pady=10, padx=5)
    text.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)

    def browse_asc_folder():
        inital_dir = text.get("1.0", tkinter.END).strip()
        filename = filedialog.askopenfilename(
            initialdir=Path(inital_dir).parent if inital_dir else "/",
            title="Select configuration file",
            filetypes=(("LTSPice file", "*.asc"), ("Spice file", "*.cir *.sp"), ("Qcv file", "*.qcv")),
        )
        text.insert(tkinter.END, filename)

    b1 = ttk.Button(master, text="...", width=10, command=browse_asc_folder, style="PyAEDT.TButton")
    b1.grid(row=0, column=2, pady=10)

    def toggle_theme():
        if master.theme == "light":
            set_dark_theme()
            master.theme = "dark"
        else:
            set_light_theme()
            master.theme = "light"

    def set_light_theme():
        master.configure(bg=theme.light["widget_bg"])
        text.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
        theme.apply_light_theme(style)
        change_theme_button.config(text="\u263D")  # Sun icon for light theme

    def set_dark_theme():
        master.configure(bg=theme.dark["widget_bg"])
        text.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        theme.apply_dark_theme(style)
        change_theme_button.config(text="\u2600")  # Moon icon for dark theme

    # Create a frame for the toggle button to position it correctly
    button_frame = ttk.Frame(master, style="PyAEDT.TFrame", relief=tkinter.SUNKEN, borderwidth=2)
    button_frame.grid(row=1, column=2, pady=10, padx=10)  # Place it in the second row, third column

    # Add the toggle theme button inside the frame
    change_theme_button = ttk.Button(button_frame, text="\u263D", command=toggle_theme, style="PyAEDT.TButton")
    change_theme_button.grid(row=0, column=0, padx=0)

    def callback():
        master.flag = True
        master.asc_path_ui = text.get("1.0", tkinter.END).strip()
        master.destroy()

    b3 = ttk.Button(master, text="Import", width=40, command=callback, style="PyAEDT.TButton")
    b3.grid(row=1, column=1, pady=10, padx=10)

    tkinter.mainloop()

    asc_file_ui = getattr(master, "asc_path_ui", extension_arguments["asc_file"])

    output_dict = {}
    if master.flag:
        output_dict = {
            "asc_file": asc_file_ui,
        }
    return output_dict


def main(extension_args):
    asc_file = Path(extension_args["asc_file"])
    if not asc_file.exists():
        raise Exception("File does not exist.")

    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        version=version,
        port=port,
        aedt_process_id=aedt_process_id,
        student_version=is_student,
    )

    cir = Circuit(design=asc_file.stem)

    if asc_file.suffix == ".asc":
        cir.create_schematic_from_asc_file(str(asc_file))
    elif asc_file.suffix in {".sp", ".cir"}:
        cir.create_schematic_from_netlist(str(asc_file))
    elif asc_file.suffix == ".qcv":
        cir.create_schematic_from_mentor_netlist(str(asc_file))
    if not extension_args["is_test"]:  # pragma: no cover
        app.release_desktop(False, False)
    return True


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(extension_arguments, extension_description)

    # Open UI
    if not args["is_batch"]:  # pragma: no cover
        output = frontend()
        if output:
            for output_name, output_value in output.items():
                if output_name in extension_arguments:
                    args[output_name] = output_value
            main(args)
    else:
        main(args)
