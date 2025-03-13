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
import time
from tkinter import filedialog
from tkinter import messagebox

import ansys.aedt.core
from ansys.aedt.core.edb import Edb
from ansys.aedt.core.hfss3dlayout import Hfss3dLayout
from ansys.aedt.core.hfss import Hfss
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
extension_arguments = {"working_path": "", "source_path": "", "mounting_side": "top"}
extension_description = "Arbitrary wave port creator"


def frontend():  # pragma: no cover
    import tkinter
    from tkinter import ttk

    import PIL.Image
    import PIL.ImageTk
    from ansys.aedt.core.workflows.misc import ExtensionTheme

    master = tkinter.Tk()
    master.minsize(1000, 220)
    master.maxsize(1000, 220)

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

    work_dir_path = tkinter.StringVar()
    source_file_path = tkinter.StringVar()
    mounting_side_variable = tkinter.StringVar()
    import_edb_variable = tkinter.BooleanVar()

    def browse_workdir_call_back():
        work_dir_path.set(filedialog.askdirectory())
        work_dir.delete("1.0", tkinter.END)
        work_dir.insert(tkinter.END, work_dir_path.get())

    def browse_source_file_call_back():
        if not import_edb_variable.get():
            file_type = (("odb++", "*.tgz"), ("cadence pcb", "*.brd"), (("cadence package", "*.mcm"), ("", "*.zip")))
            source_file_path.set(
                filedialog.askopenfilename(filetypes=file_type, title="Please select the source design")
            )
        else:
            source_file_path.set(filedialog.askdirectory(title="Import aedb folder"))
        source_file.delete("1.0", "end")
        source_file.insert("end", source_file_path.get())

    # Working directory
    label_work_dir = ttk.Label(master, text="Working directory", style="PyAEDT.TLabel")
    label_work_dir.grid(row=0, column=0, pady=10)

    work_dir = tkinter.Text(master, width=60, height=1)
    work_dir.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)

    # work_dir.setvar(work_dir_path, "")
    work_dir.grid(row=0, column=1, pady=10, padx=5)
    work_dir_button = ttk.Button(master, text="Browse", command=browse_workdir_call_back, style="PyAEDT.TButton")
    work_dir_button.grid(row=0, column=2, sticky="E")

    # source layout
    label_source = ttk.Label(master, text="Source layout", style="PyAEDT.TLabel")
    label_source.grid(row=1, column=0, pady=10)

    source_file = tkinter.Text(master, width=60, height=1)
    source_file.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
    source_file.setvar(source_file_path.get(), "")
    source_file.grid(row=1, column=1, pady=10, padx=5)

    source_file_button = ttk.Button(master, text="Browse", command=browse_source_file_call_back, style="PyAEDT.TButton")
    source_file_button.grid(row=1, column=2, sticky="E")

    # mounting side
    label_combobox = ttk.Label(master, text="Mounting side", style="PyAEDT.TLabel")
    label_combobox.grid(row=2, column=0)

    mounting_side_combo_box = ttk.Combobox(
        master=master, width=10, textvariable=mounting_side_variable, style="PyAEDT.TCombobox"
    )
    mounting_side_combo_box["values"] = ("top", "bottom")
    mounting_side_combo_box.grid(row=3, column=0, padx=5, pady=10)
    mounting_side_combo_box.set("top")
    mounting_side_combo_box.current()

    # checkbox import EDB
    import_edb_variable.set(True)
    ttk.Checkbutton(master=master, text="Import EDB", variable=import_edb_variable, style="PyAEDT.TCheckbutton").grid(
        row=3, column=1, padx=5, pady=10
    )

    def toggle_theme():
        if master.theme == "light":
            set_dark_theme()
            master.theme = "dark"
        else:
            set_light_theme()
            master.theme = "light"

    def set_light_theme():
        master.configure(bg=theme.light["widget_bg"])
        source_file.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
        work_dir.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
        theme.apply_light_theme(style)
        change_theme_button.config(text="\u263D")  # Sun icon for light theme

    def set_dark_theme():
        master.configure(bg=theme.dark["widget_bg"])
        source_file.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        work_dir.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        theme.apply_dark_theme(style)
        change_theme_button.config(text="\u2600")  # Moon icon for dark theme

    # Create a frame for the toggle button to position it correctly
    button_frame = ttk.Frame(master, style="PyAEDT.TFrame", relief=tkinter.SUNKEN, borderwidth=2)
    button_frame.grid(row=4, column=2, pady=10, padx=10)

    # Add the toggle theme button inside the frame
    change_theme_button = ttk.Button(
        button_frame, width=20, text="\u263D", command=toggle_theme, style="PyAEDT.TButton"
    )

    change_theme_button.grid(row=0, column=0, padx=0)

    def callback():
        master.flag = True
        master.working_path_ui = work_dir.get("1.0", tkinter.END).strip()
        master.source_path_ui = source_file.get("1.0", tkinter.END).strip()
        master.mounting_side_ui = mounting_side_combo_box.get()
        master.import_edb = import_edb_variable.get()
        master.destroy()

    # execute button
    execute_button = ttk.Button(master=master, text="Generate", command=callback, width=20, style="PyAEDT.TButton")
    execute_button.grid(row=4, column=0, padx=10, pady=10)

    tkinter.mainloop()

    working_path_ui = getattr(master, "working_path_ui", extension_arguments["working_path"])
    source_path_ui = getattr(master, "source_path_ui", extension_arguments["source_path"])
    mounting_side_ui = getattr(master, "mounting_side_ui", extension_arguments["mounting_side"])

    output_dict = {}
    if master.flag:
        output_dict = {
            "working_path": working_path_ui,
            "source_path": source_path_ui,
            "mounting_side": mounting_side_ui,
        }

    return output_dict


def main(extension_args):
    working_dir = Path(extension_args["working_path"])
    edb_file = Path(extension_args["source_path"])
    mounting_side_variable = extension_args["mounting_side"]

    edb_project = working_dir / "arbitrary_wave_port.aedb"
    out_3d_project = working_dir / "output_3d.aedt"
    component_3d_file = working_dir / "wave_port.a3dcomp"

    if working_dir.exists():
        if len(list(working_dir.iterdir())) > 0:  # pragma: no cover
            res = messagebox.askyesno(
                title="Warning",
                message="The selected working directory is not empty, "
                "the entire content will be deleted. "
                "Are you sure to continue ?",
            )
            if res == "no":
                return

    edb = Edb(edbpath=rf"{edb_file}", edbversion=version)
    if not edb.create_model_for_arbitrary_wave_ports(
        temp_directory=str(working_dir), mounting_side=mounting_side_variable, output_edb=str(edb_project)
    ):
        messagebox.showerror(
            "EDB model failure",
            "Failed to create EDB model, please make sure you "
            "selected the correct mounting side. The selected side must "
            "must contain explicit voids with pad-stack instances inside.",
        )
    edb.close()
    time.sleep(1)

    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        version=version,
        port=port,
        aedt_process_id=aedt_process_id,
        student_version=is_student,
    )

    hfss3d = Hfss3dLayout(project=str(edb_project), version=version)
    setup = hfss3d.create_setup("wave_ports")
    setup.export_to_hfss(file_fullname=str(out_3d_project), keep_net_name=True)
    time.sleep(1)
    hfss3d.close_project()

    hfss = Hfss(projectname=str(out_3d_project), specified_version=version, new_desktop_session=False)
    hfss.solution_type = "Terminal"

    # Deleting dielectric objects
    for solid_obj in [
        obj for obj in hfss.modeler.solid_objects if obj.material_name in hfss.modeler.materials.dielectrics
    ]:
        solid_obj.delete()

    # creating ports
    for sheet in hfss.modeler.sheet_objects:
        hfss.wave_port(assignment=sheet.id, reference="GND", terminals_rename=False)

    # create 3D component
    hfss.save_project(file_name=str(out_3d_project))
    hfss.modeler.create_3dcomponent(input_file=str(component_3d_file))
    hfss.logger.info(
        f"3D component with arbitrary wave ports has been generated. "
        f"You can import the file located in working directory {working_dir}"
    )
    hfss.close_project()

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
