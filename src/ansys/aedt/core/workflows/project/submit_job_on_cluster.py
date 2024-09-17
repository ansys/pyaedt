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
extension_arguments = {
    "cluster_name": "",
    "project_path": "",
    "aedt_path": "",
    "num_nodes": 1,
    "num_cores": 32,
    "wait_for_license": True,
}
extension_description = "Scheduler job submission"


def frontend():  # pragma: no cover
    import tkinter
    from tkinter import ttk

    import PIL.Image
    import PIL.ImageTk

    master = tkinter.Tk()

    master.geometry("750x220")

    master.minsize(750, 220)
    master.maxsize(750, 220)

    master.title("LSF job submission")

    # Load the logo for the main window
    icon_path = os.path.join(os.path.dirname(ansys.aedt.core.workflows.__file__), "images", "large", "logo.png")
    im = PIL.Image.open(icon_path)
    photo = PIL.ImageTk.PhotoImage(im)

    # Set the icon for the main window
    master.iconphoto(True, photo)

    # Configure style for ttk buttons
    style = ttk.Style()
    style.configure("Toolbutton.TButton", padding=6, font=("Helvetica", 10))

    ansys_path_var = tkinter.StringVar()
    project_path_var = tkinter.StringVar()
    cluster_name_var = tkinter.StringVar()
    wait_for_license_var = tkinter.BooleanVar()
    num_core_var = tkinter.IntVar()
    num_node_var = tkinter.IntVar()

    def browse_project_file_call_back():
        project_path_var.set(filedialog.askopenfilename(title="Select project to solve"))

    def browse_aedt_exe_path_call_back():
        ansys_path_var.set(filedialog.askopenfilename(title="AEDT exe path"))

    # Project path
    var1 = tkinter.StringVar()
    label_project_path = tkinter.Label(master, textvariable=var1)
    var1.set("Project path")
    label_project_path.grid(row=0, column=0, pady=10)
    project_path = tkinter.Text(master, width=60, height=1)
    # work_dir.setvar(work_dir_path, "")
    project_path.grid(row=0, column=1, pady=10, padx=5)
    project_path_button = tkinter.Button(master, text="Browse", command=browse_project_file_call_back)
    project_path_button.grid(row=0, column=2, sticky="E")

    # AEDT path
    var2 = tkinter.StringVar()
    label_source = tkinter.Label(master, textvariable=var2)
    var2.set("AEDT exe path")
    label_source.grid(row=1, column=0, pady=10)
    aedt_exe_path = tkinter.Text(master, width=60, height=1)
    aedt_exe_path.grid(row=1, column=1, pady=10, padx=5)
    aedt_exe_button = tkinter.Button(master, text="Browse", command=browse_aedt_exe_path_call_back)
    aedt_exe_button.grid(row=1, column=2, sticky="E")

    # cluster name
    var3 = tkinter.StringVar()
    label_cluster_name = tkinter.Label(master, textvariable=var3)
    var3.set("Cluster name")
    label_cluster_name.grid(row=2, column=0, pady=10)
    cluster_name = tkinter.Text(master, width=10, height=1)
    cluster_name.grid(row=3, column=0, pady=10, padx=5)

    # num nodes
    var4 = tkinter.StringVar()
    label_number_node = tkinter.Label(master, textvariable=var4)
    var4.set("Number nodes")
    label_number_node.grid(row=2, column=1, pady=10)
    number_nodes = tkinter.Text(master, width=10, height=1)
    number_nodes.grid(row=3, column=1, pady=10, padx=5)

    # num cores
    var5 = tkinter.StringVar()
    label_number_cores = tkinter.Label(master, textvariable=var5)
    var5.set("Number cores")
    label_number_cores.grid(row=2, column=2, pady=10)
    number_cores = tkinter.Text(master, width=10, height=1)
    number_cores.grid(row=3, column=2, pady=10, padx=5)

    # checkbox wait for license
    wait_for_license_var.set(True)
    ttk.Checkbutton(master=master, text="Wait for license", variable=wait_for_license_var).grid(
        row=4, column=1, padx=5, pady=10
    )

    def callback():
        master.project_path_ui = project_path_var.get("1.0", tkinter.END).strip()
        master.aedt_path_ui = ansys_path_var.get("1.0", tkinter.END).strip()
        master.wait_for_license_ui = wait_for_license_var.get()
        master.destroy()

    # execute button
    execute_button = tkinter.Button(master=master, text="Submit", command=callback)
    execute_button.grid(row=4, column=0, padx=5, pady=10)

    tkinter.mainloop()

    project_path_ui = getattr(master, "project_path_ui", extension_arguments["project_path"])
    aedt_path_ui = getattr(master, "aedt_path_ui", extension_arguments["aedt_path"])

    output_dict = {
        "project_path": project_path_ui,
        "aedt_path": aedt_path_ui,
    }

    return output_dict


def main(extension_args):
    working_dir = extension_args["working_path"]
    edb_file = extension_args["source_path"]
    mounting_side_variable = extension_args["mounting_side"]

    edb_project = os.path.join(working_dir, "arbitrary_wave_port.aedb")
    out_3d_project = os.path.join(working_dir, "output_3d.aedt")
    component_3d_file = os.path.join(working_dir, "wave_port.a3dcomp")
    if os.path.exists(working_dir):
        if len(os.listdir(working_dir)) > 0:  # pragma: no cover
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
        temp_directory=working_dir, mounting_side=mounting_side_variable, output_edb=edb_project
    ):
        messagebox.showerror(
            "EDB model failure",
            "Failed to create EDB model, please make sure you "
            "selected the correct mounting side. The selected side must "
            "must contain explicit voids with pad-stack instances inside.",
        )
    signal_nets = list(edb.nets.signal.keys())
    edb.close()
    time.sleep(1)

    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        version=version,
        port=port,
        aedt_process_id=aedt_process_id,
        student_version=is_student,
    )

    hfss3d = Hfss3dLayout(project=edb_project, version=version)
    setup = hfss3d.create_setup("wave_ports")
    setup.export_to_hfss(file_fullname=out_3d_project, keep_net_name=True)
    time.sleep(1)
    hfss3d.close_project()

    hfss = Hfss(projectname=out_3d_project, specified_version=version, new_desktop_session=False)
    hfss.solution_type = "Modal"

    # Deleting dielectric objects
    [obj.delete() for obj in hfss.modeler.solid_objects if obj.material_name in hfss.modeler.materials.dielectrics]

    # creating ports
    sheets_for_ports = hfss.modeler.sheet_objects
    terminal_faces = []
    terminal_objects = [obj for obj in hfss.modeler.object_list if obj.name in signal_nets]
    for obj in terminal_objects:
        if mounting_side_variable == "bottom":
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
    hfss.modeler.create_3dcomponent(input_file=component_3d_file)
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
