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

import os

import pathlib
import ansys.aedt.core
from ansys.aedt.core.hfss3dlayout import Hfss3dLayout
from ansys.aedt.core.edb import Edb
from  ansys.aedt.core.hfss import Hfss
from ansys.aedt.core.workflows.misc import get_arguments
from ansys.aedt.core.workflows.misc import get_aedt_version
from ansys.aedt.core.workflows.misc import get_port
from ansys.aedt.core.workflows.misc import get_process_id
from ansys.aedt.core.workflows.misc import is_student

from tkinter import filedialog
import tkinter
from tkinter import messagebox
from tkinter import ttk
import PIL.Image
import PIL.ImageTk

port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()
is_student = is_student()

# Extension batch arguments
extension_arguments = {}
extension_description = "Arbitrary wave port creator"


def frontend():  # pragma: no cover
    master = tkinter.Tk()
    master.geometry("680x220")
    master.minsize(680, 220)
    master.maxsize(680, 220)
    master.title("Arbitrary wave-port generator")

    work_dir_path = tkinter.StringVar()
    source_file_path = tkinter.StringVar()
    mounting_side_variable = tkinter.StringVar()
    import_edb_variable = tkinter.BooleanVar()
    import_3d_component_variable = tkinter.BooleanVar()

    # Load the logo for the main window
    icon_path = os.path.join(os.path.dirname(ansys.aedt.core.workflows.__file__), "images", "large", "logo.png")
    im = PIL.Image.open(icon_path)
    photo = PIL.ImageTk.PhotoImage(im)

    # Set the icon for the main window
    master.iconphoto(True, photo)

    # Configure style for ttk buttons
    style = ttk.Style()
    style.configure("Toolbutton.TButton", padding=6, font=("Helvetica", 10))

    def browse_workdir_call_back():
        work_dir_path.set(filedialog.askdirectory())
        work_dir.delete("1.0", "end")
        work_dir.insert("end", work_dir_path.get())

    def browse_source_file_call_back():
        if not import_edb_variable.get():
            file_type = (('odb++', '*.tgz'), ('cadence pcb', '*.brd'), (('cadence package', '*.mcm'),
                                                                    ('', '*.zip')))
            source_file_path.set(filedialog.askopenfilename(filetypes=file_type, title="Please select the source design"))
        else:
            source_file_path.set(filedialog.askdirectory(title="Import aedb folder"))
        source_file.delete("1.0", "end")
        source_file.insert("end", source_file_path.get())

    def create_3d_component():
        edb_file = source_file.get("1.0", "end-1c")
        _wdir = work_dir.get("1.0", "end-1c")
        edb_project = os.path.join(_wdir, "arbitrary_wave_port.aedb")
        out_3d_project = os.path.join(_wdir, "output_3d.aedt")
        component_3d_file = os.path.join(_wdir, "wave_port.a3dcomp")
        if os.path.exists(_wdir):
            if len(os.listdir(_wdir)) > 0:
                res = messagebox.askyesno(title="Warning", message="The selected working directory is not empty, "
                                                                   "he entire content will be deleted. "
                                                                   "Are you sure to continue ?")
                if res == "no":
                    return
        edb = Edb(edbpath=rf"{edb_file}", edbversion=version)
        if not edb.create_model_for_arbitrary_wave_ports(temp_directory=_wdir,
                                                  mounting_side=mounting_side_variable.get(),
                                                  output_edb=edb_project):
            messagebox.showerror("EDB model failure", "Failed to create EDB model, please make sure you "
                                                      "selected the correct mounting side. The selected side must "
                                                      "must contain explicit voids with pad-stack instances inside.")
        signal_nets = list(edb.nets.signal.keys())
        edb.close()
        hfss3d = Hfss3dLayout(projectname=edb_project, specified_version=version)
        setup = hfss3d.create_setup("wave_ports")
        setup.export_to_hfss(file_fullname=out_3d_project, keep_net_name=True)
        hfss3d.release_desktop(close_projects=True, close_desktop=False)
        hfss = Hfss(projectname=out_3d_project, specified_version=version, new_desktop_session=False)

        # deleting dielectric objects
        [obj.delete() for obj in hfss.modeler.solid_objects if obj.material_name in hfss.modeler.materials.dielectrics]

        # creating ports
        sheets_for_ports = hfss.modeler.sheet_objects
        terminal_faces = []
        terminal_objects = [obj for obj in hfss.modeler.object_list if obj.name in signal_nets]
        for obj in terminal_objects:
            if mounting_side_variable.get() == "bottom":
                face = obj.bottom_face_z
            else:
                face = obj.top_face_z
            terminal_face = hfss.modeler.create_object_from_face(face.id, non_model=False)
            hfss.assign_perfecte_to_sheets(terminal_face.name)
            name = obj.name
            terminal_faces.append(terminal_face)
            obj.delete()
            terminal_face.name = name
        for sheet in sheets_for_ports:
            hfss.wave_port(assignment=sheet.id, reference="GND", terminals_rename=False)

        # create 3D component
        hfss.save_project(file_name=out_3d_project)
        hfss.modeler.create_3dcomponent(component_file=component_3d_file)
        hfss.release_desktop(close_projects=True, close_desktop=False)
        if import_3d_component_variable.get():
            app = ansys.aedt.core.Desktop(
                new_desktop=False,
                version=version,
                port=port,
                aedt_process_id=aedt_process_id,
                student_version=is_student,
            )

            app.active_design().modeler.insert_3d_component(component_3d_file)


    # workdir
    var1 = tkinter.StringVar()
    label_work_dir = tkinter.Label(master, textvariable=var1)
    var1.set("Working directory")
    label_work_dir.grid(row=0, column=0, pady=10)
    work_dir = tkinter.Text(master, width=60, height=1)
    # work_dir.setvar(work_dir_path, "")
    work_dir.grid(row=0, column=1, pady=10, padx=5)
    work_dir_button = tkinter.Button(master, text="Browse", command=browse_workdir_call_back)
    work_dir_button.grid(row=0, column=2, sticky="E")

    # source layout
    var2 = tkinter.StringVar()
    label_source = tkinter.Label(master, textvariable=var2)
    var2.set("Source layout")
    label_source.grid(row=1, column=0, pady=10)
    source_file = tkinter.Text(master, width=60, height=1)
    source_file.setvar(source_file_path.get(), "")
    source_file.grid(row=1, column=1, pady=10, padx=5)
    source_file_button = tkinter.Button(master, text="Browse", command=browse_source_file_call_back)
    source_file_button.grid(row=1, column=2, sticky="E")

    # mounting side
    var3 = tkinter.StringVar()
    label_combobox = tkinter.Label(master, textvariable=var3)
    var3.set("Mounting side")
    label_combobox.grid(row=2, column=0)
    mounting_side_combo_box = ttk.Combobox(master=master, width=10, textvariable=mounting_side_variable)
    mounting_side_combo_box["values"] = ("top", "bottom")
    mounting_side_combo_box.grid(row=3, column=0, padx=5, pady=10)
    mounting_side_combo_box.set("top")
    mounting_side_combo_box.current()

    # checkbox import EDB
    import_edb_variable.set(True)
    ttk.Checkbutton(master=master, text="Import EDB",
                                               variable=import_edb_variable).grid(row=2, column=1, padx=5, pady=10)


    # checkbox import 3D component
    import_3d_component_variable.set(True)
    ttk.Checkbutton(master=master, text="Import 3D component",
                    variable=import_3d_component_variable).grid(row=3, column=1, padx=5, pady=10)

    # execute button
    execute_button = tkinter.Button(master=master, text="Generate", command=create_3d_component)
    execute_button.grid(row=4, column=0, padx=5, pady=10)

    # quit button
    execute_button = tkinter.Button(master=master, text="Quit", command=master.quit)
    execute_button.grid(row=4, column=1, padx=5, pady=10)
    master.mainloop()


def main():
    frontend()


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(extension_arguments, extension_description)
    # Open UI
    if not args["is_batch"]:  # pragma: no cover
        main()
