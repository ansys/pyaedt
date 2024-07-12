# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
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


import logging
import os.path

from pyaedt import Desktop
from pyaedt import Hfss
from pyaedt import Icepak
from pyaedt import Maxwell3d
from pyaedt import Q3d
from pyaedt import settings
from pyaedt.application.design_solutions import solutions_types
from pyaedt.generic.design_types import get_pyaedt_app
from pyaedt.generic.filesystem import search_files
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.workflows.misc import get_aedt_version
from pyaedt.workflows.misc import get_arguments
from pyaedt.workflows.misc import get_port
from pyaedt.workflows.misc import get_process_id
from pyaedt.workflows.misc import is_student

settings.use_grpc_api = True
settings.use_multi_desktop = True
non_graphical = True
extension_arguments = {"password": "", "application": "HFSS", "solution": "Modal", "file_path": ""}
extension_description = "Convert File from 22R2"
port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()
is_student = is_student()


def frontend():  # pragma: no cover

    import tkinter
    from tkinter import filedialog
    from tkinter import ttk

    master = tkinter.Tk()

    master.geometry("750x250")

    master.title("Convert File from 22R2")

    # Configure style for ttk buttons
    style = ttk.Style()
    style.configure("Toolbutton.TButton", padding=6, font=("Helvetica", 8))

    var2 = tkinter.StringVar()
    label2 = tkinter.Label(master, textvariable=var2)
    var2.set("Browse file or folder:")
    label2.grid(row=0, column=0, pady=10)
    text = tkinter.Text(master, width=40, height=1)
    text.grid(row=0, column=1, pady=10, padx=5)

    def edit_sols(self):
        sol["values"] = tuple(solutions_types[appl.get()].keys())
        sol.current(0)

    var = tkinter.StringVar()
    label = tkinter.Label(master, textvariable=var)
    var.set("Password (Encrypted 3D Component Only):")
    label.grid(row=1, column=0, pady=10)
    pwd = tkinter.Entry(master, width=20, show="*")
    pwd.insert(tkinter.END, "")
    pwd.grid(row=1, column=1, pady=10, padx=5)

    var = tkinter.StringVar()
    label = tkinter.Label(master, textvariable=var)
    var.set("Application (3D Component Only):")
    label.grid(row=2, column=0, pady=10)
    appl = ttk.Combobox(master, width=40, validatecommand=edit_sols)  # Set the width of the combobox
    appl["values"] = ("HFSS", "Q3D Extractor", "Maxwell 3D", "Icepak")
    appl.current(0)
    appl.bind("<<ComboboxSelected>>", edit_sols)
    appl.grid(row=2, column=1, pady=10, padx=5)

    var = tkinter.StringVar()
    label = tkinter.Label(master, textvariable=var)
    var.set("Solution (3D Component Only):")
    label.grid(row=3, column=0, pady=10)
    sol = ttk.Combobox(master, width=40)  # Set the width of the combobox
    sol["values"] = ttk.Combobox(master, width=40)  # Set the width of the combobox
    sol["values"] = tuple(solutions_types["HFSS"].keys())
    sol.current(0)
    sol.grid(row=3, column=1, pady=10, padx=5)

    def browseFiles():
        filename = filedialog.askopenfilename(
            initialdir="/",
            title="Select a Electronics File",
            filetypes=(("AEDT", ".aedt *.a3dcomp"), ("all files", "*.*")),
        )
        text.insert(tkinter.END, filename)

    b1 = tkinter.Button(master, text="...", width=10, command=browseFiles)
    b1.grid(row=0, column=2, pady=10)

    def callback():
        applications = {"HFSS": 0, "Icepak": 1, "Maxwell 3D": 2, "Q3D Extractor": 3}
        master.password_ui = pwd.get()
        master.application_ui = applications[appl.get()]
        master.solution_ui = sol.get()
        master.file_path_ui = text.get("1.0", tkinter.END).strip()
        master.destroy()

    b3 = tkinter.Button(master, text="Ok", width=40, command=callback)
    b3.grid(row=5, column=1, pady=10, padx=10)

    tkinter.mainloop()

    password_ui = getattr(master, "password_ui", extension_arguments["password"])
    application_ui = getattr(master, "application_ui", extension_arguments["application"])
    solution_ui = getattr(master, "solution_ui", extension_arguments["solution"])
    file_path_ui = getattr(master, "file_path_ui", extension_arguments["file_path"])

    output_dict = {
        "password": password_ui,
        "application": application_ui,
        "solution": solution_ui,
        "file_path": file_path_ui,
    }
    return output_dict


def check_missing(input_object, output_object, file_path):
    if output_object.design_type not in [
        "HFSS",
        "Icepak",
        "Q3d",
        "2D Extractor",
        "Maxwell 3D",
        "Maxwell 2D",
        "Mechanical",
    ]:
        return
    object_list = input_object.modeler.object_names[::]
    new_object_list = output_object.modeler.object_names[::]
    un_classified_objects = output_object.modeler.unclassified_names[::]
    unclassified = [i for i in object_list if i not in new_object_list and i in un_classified_objects]
    disappeared = [i for i in object_list if i not in new_object_list and i not in un_classified_objects]
    list_of_suppressed = [["Design", "Object", "Operation"]]
    for obj_name in unclassified:
        if obj_name in output_object.modeler.object_names:
            continue
        hist = output_object.modeler[obj_name].history()
        for el_name, el in list(hist.children.items())[::-1]:
            if "Suppress Command" in el.props:
                el.props["Suppress Command"] = True
                list_of_suppressed.append([output_object.design_name, obj_name, el_name])
            if obj_name in output_object.modeler.object_names:
                break
    for obj_name in disappeared:
        input_object.export_3d_model(
            file_name=obj_name,
            file_format=".x_t",
            file_path=input_object.working_directory,
            assignment_to_export=[obj_name],
        )
        output_object.modeler.import_3d_cad(os.path.join(input_object.working_directory, obj_name + ".x_t"))
        list_of_suppressed.append([output_object.design_name, obj_name, "History"])
    from pyaedt.generic.general_methods import read_csv
    from pyaedt.generic.general_methods import write_csv

    if file_path.split(".")[1] == "a3dcomp":
        output_csv = os.path.join(file_path[:-8], "Import_Errors.csv")[::-1].replace("\\", "_", 1)[::-1]
    else:
        output_csv = os.path.join(file_path[:-5], "Import_Errors.csv")[::-1].replace("\\", "_", 1)[::-1]
    if os.path.exists(output_csv):
        data_read = read_csv(output_csv)
        list_of_suppressed = data_read + list_of_suppressed[1:]
    write_csv(output_csv, list_of_suppressed)
    print(f"Errors saved in {output_csv}")
    return output_csv, True


def convert_3d_component(
    extension_args,
    output_desktop,
    input_desktop,
):

    file_path = extension_args["file_path"]
    password = extension_args["password"]
    solution = extension_args["solution"]
    application = extension_args["application"]

    output_path = file_path[:-8] + f"_{version}.a3dcomp"

    if os.path.exists(output_path):
        output_path = file_path[:-8] + generate_unique_name(f"_version", n=2) + ".a3dcomp"
    app = Hfss
    if application == 1:
        app = Icepak
    elif application == 2:
        app = Maxwell3d
    elif application == 3:
        app = Q3d
    app1 = app(aedt_process_id=input_desktop.aedt_process_id, solution_type=solution)
    cmp = app1.modeler.insert_3d_component(file_path, password=password)
    app_comp = cmp.edit_definition(password=password)
    design_name = app_comp.design_name
    app_comp.oproject.CopyDesign(design_name)
    project_name2 = generate_unique_name("Proj_convert")
    output_app = app(aedt_process_id=output_desktop.aedt_process_id, solution_type=solution, project=project_name2)

    output_app.oproject.Paste()
    output_app = get_pyaedt_app(desktop=output_desktop, project_name=project_name2, design_name=design_name)
    check_missing(app_comp, output_app, file_path)
    output_app.modeler.create_3dcomponent(
        output_path,
        is_encrypted=True if password else False,
        edit_password=password,
        hide_contents=False,
        allow_edit=True if password else False,
        password_type="InternalPassword" if password else "UserSuppliedPassword",
    )
    try:
        output_desktop.DeleteProject(project_name2)
        print(f"Project successfully deleted")
    except Exception:
        print(f"Error project was not closed")
    print(f"3D Component {output_path} has been created.")


def convert_aedt(
    extension_args,
    output_desktop,
    input_desktop,
):

    file_path = extension_args["file_path"]

    file_path = str(file_path)
    a3d_component_path = str(file_path)
    output_path = a3d_component_path[:-5] + f"_{version}.aedt"
    if os.path.exists(output_path):
        output_path = a3d_component_path[:-5] + generate_unique_name(f"_{version}", n=2) + ".aedt"

    input_desktop.load_project(file_path)
    project_name = os.path.splitext(os.path.split(file_path)[-1])[0]
    oproject2 = output_desktop.odesktop.NewProject(output_path)
    project_name2 = os.path.splitext(os.path.split(output_path)[-1])[0]

    for design in input_desktop.design_list():

        app1 = get_pyaedt_app(desktop=input_desktop, project_name=project_name, design_name=design)
        app1.oproject.CopyDesign(app1.design_name)
        oproject2.Paste()
        output_app = get_pyaedt_app(desktop=output_desktop, project_name=project_name2, design_name=design)
        check_missing(app1, output_app, file_path)
        output_app.save_project()
    input_desktop.odesktop.CloseProject(os.path.splitext(os.path.split(file_path)[-1])[0])


def convert(args):
    logger = logging.getLogger("Global")
    if os.path.isdir(args["file_path"]):
        files_path = search_files(args["file_path"], "*.a3dcomp")
        files_path += search_files(args["file_path"], "*.aedt")
    else:
        files_path = [args["file_path"]]
    output_desktop = Desktop(
        new_desktop=True,
        version=version,
        port=port,
        aedt_process_id=aedt_process_id,
        student_version=is_student,
    )
    input_desktop = Desktop(new_desktop=True, version=222, non_graphical=non_graphical)
    for file in files_path:
        try:
            args["file_path"] = file
            if args["file_path"].endswith("a3dcomp"):
                convert_3d_component(args, output_desktop, input_desktop)
            else:
                convert_aedt(args, output_desktop, input_desktop)
        except Exception:
            logger.error(f"Failed to convert {file}")
    input_desktop.release_desktop()
    output_desktop.release_desktop(False, False)


if __name__ == "__main__":
    args = get_arguments(extension_arguments, extension_description)
    # Open UI
    if not args["is_batch"]:  # pragma: no cover
        output = frontend()
        if output:
            for output_name, output_value in output.items():
                if output_name in extension_arguments:
                    args[output_name] = output_value
    convert(args)
