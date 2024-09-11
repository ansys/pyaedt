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

import ansys.aedt.core
from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core import generate_unique_name
import ansys.aedt.core.workflows.hfss3dlayout
from ansys.aedt.core.workflows.misc import get_aedt_version
from ansys.aedt.core.workflows.misc import get_arguments
from ansys.aedt.core.workflows.misc import get_port
from ansys.aedt.core.workflows.misc import get_process_id
from ansys.aedt.core.workflows.misc import is_student
from pyedb import Edb

port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()
is_student = is_student()

# Extension batch arguments
extension_arguments = {
    "aedb_path": "",
    "design_name": "",
    "parametrize_layers": True,
    "parametrize_materials": True,
    "parametrize_padstacks": True,
    "parametrize_traces": True,
    "nets_filter": [],
    "expansion_polygon_mm": 0,
    "expansion_void_mm": 0,
    "relative_parametric": True,
    "project_name": "",
}
extension_description = "Layout Parametrization"


def frontend():  # pragma: no cover
    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        version=version,
        port=port,
        aedt_process_id=aedt_process_id,
        student_version=is_student,
    )
    active_project = app.active_project()
    active_design = app.active_design()
    aedb_path = os.path.join(active_project.GetPath(), active_project.GetName() + ".aedb")
    edb = Edb(aedb_path, active_design.GetName().split(";")[1], edbversion=version)

    import tkinter
    from tkinter import ttk

    import PIL.Image
    import PIL.ImageTk

    master = tkinter.Tk()

    master.geometry("900x600")

    master.title("Parametrize Layout")

    # Load the logo for the main window
    icon_path = os.path.join(os.path.dirname(ansys.aedt.core.workflows.__file__), "images", "large", "logo.png")
    im = PIL.Image.open(icon_path)
    photo = PIL.ImageTk.PhotoImage(im)

    # Set the icon for the main window
    master.iconphoto(True, photo)

    # Configure style for ttk buttons
    style = ttk.Style()
    style.configure("Toolbutton.TButton", padding=6, font=("Helvetica", 10))

    var9 = tkinter.StringVar()
    label9 = tkinter.Label(master, textvariable=var9)
    var9.set("New project name: ")
    label9.grid(row=0, column=0, pady=10)
    project_name = tkinter.Entry(master, width=30)
    project_name.insert(tkinter.END, generate_unique_name(active_project.GetName(), n=2))
    project_name.grid(row=0, column=1, pady=10, padx=5)

    var10 = tkinter.StringVar()
    label10 = tkinter.Label(master, textvariable=var10)
    var10.set("Use relative parameters: ")
    label10.grid(row=0, column=2, pady=10)
    relative = tkinter.IntVar()
    check5 = tkinter.Checkbutton(master, width=30, variable=relative)
    check5.grid(row=0, column=3, pady=10, padx=5)
    relative.set(1)

    var1 = tkinter.StringVar()
    label1 = tkinter.Label(master, textvariable=var1)
    var1.set("Parametrize Layers:")
    label1.grid(row=1, column=0, pady=10)
    layers = tkinter.IntVar()
    check1 = tkinter.Checkbutton(master, width=30, variable=layers)
    check1.grid(row=1, column=1, pady=10, padx=5)
    layers.set(1)

    var2 = tkinter.StringVar()
    label2 = tkinter.Label(master, textvariable=var2)
    var2.set("Parametrize Materials:")
    label2.grid(row=1, column=2, pady=10)
    materials = tkinter.IntVar()
    check2 = tkinter.Checkbutton(master, width=30, variable=materials)
    check2.grid(row=1, column=3, pady=10, padx=5)
    materials.set(1)

    var3 = tkinter.StringVar()
    label3 = tkinter.Label(master, textvariable=var3)
    var3.set("Parametrize Padstacks:")
    label3.grid(row=2, column=0, pady=10)
    padstacks = tkinter.IntVar()
    check3 = tkinter.Checkbutton(master, width=30, variable=padstacks)
    check3.grid(row=2, column=1, pady=10, padx=5)
    padstacks.set(1)

    var5 = tkinter.StringVar()
    label5 = tkinter.Label(master, textvariable=var5)
    var5.set("Extend Polygons (mm): ")
    label5.grid(row=3, column=0, pady=10)
    polygons = tkinter.Entry(master, width=30)
    polygons.insert(tkinter.END, "0")
    polygons.grid(row=3, column=1, pady=10, padx=5)

    var6 = tkinter.StringVar()
    label6 = tkinter.Label(master, textvariable=var6)
    var6.set("Extend Voids (mm): ")
    label6.grid(row=3, column=2, pady=10)
    voids = tkinter.Entry(master, width=30)
    voids.insert(tkinter.END, "0")
    voids.grid(row=3, column=3, pady=10, padx=5)

    var7 = tkinter.StringVar()
    label7 = tkinter.Label(master, textvariable=var7)
    var7.set("Parametrize Nets:")
    label7.grid(row=4, column=0, pady=10)
    nets = tkinter.IntVar()
    check4 = tkinter.Checkbutton(master, width=30, variable=nets)
    check4.grid(row=4, column=1, pady=10, padx=5)
    nets.set(1)

    var8 = tkinter.StringVar()
    label8 = tkinter.Label(master, textvariable=var8)
    var8.set("Select Nets(None for all):")
    label8.grid(row=4, column=2, pady=10)
    net_list = tkinter.Listbox(master, height=20, width=30, selectmode=tkinter.MULTIPLE)
    net_list.grid(row=4, column=3, pady=5)

    idx = 1
    for net in edb.nets.nets.keys():
        net_list.insert(idx, net)
        idx += 1

    def callback():
        master.layers_ui = layers.get()
        master.materials_ui = materials.get()
        master.padstacks_ui = padstacks.get()
        master.nets_ui = nets.get()
        master.voids_ui = voids.get().strip()
        master.poly_ui = polygons.get().strip()
        master.project_name_ui = project_name.get().strip()
        master.relative_ui = relative.get()
        master.net_list_ui = []
        for i in net_list.curselection():
            master.net_list_ui.append(net_list.get(i))
        master.destroy()

    b = tkinter.Button(master, text="Create Parametric Model", width=40, command=callback)
    b.grid(row=5, column=1, pady=10)

    tkinter.mainloop()

    layers_ui = getattr(master, "layers_ui", extension_arguments["parametrize_layers"])
    materials_ui = getattr(master, "materials_ui", extension_arguments["parametrize_materials"])
    padstacks_ui = getattr(master, "padstacks_ui", extension_arguments["parametrize_padstacks"])
    nets_ui = getattr(master, "nets_ui", extension_arguments["parametrize_traces"])
    nets_filter_ui = getattr(master, "nets_filter", extension_arguments["nets_filter"])
    poly_ui = getattr(master, "poly_ui", extension_arguments["expansion_polygon_mm"])
    voids_ui = getattr(master, "voids_ui", extension_arguments["expansion_void_mm"])
    project_name_ui = getattr(master, "project_name_ui", extension_arguments["project_name"])
    relative_ui = getattr(master, "relative_ui", extension_arguments["relative_parametric"])

    output_dict = {
        "aedb_path": os.path.join(active_project.GetPath(), active_project.GetName() + ".aedb"),
        "design_name": active_design.GetName().split(";")[1],
        "parametrize_layers": layers_ui,
        "parametrize_materials": materials_ui,
        "parametrize_padstacks": padstacks_ui,
        "parametrize_traces": nets_ui,
        "nets_filter": nets_filter_ui,
        "expansion_polygon_mm": float(poly_ui),
        "expansion_void_mm": float(voids_ui),
        "relative_parametric": relative_ui,
        "project_name": project_name_ui,
    }
    edb.close_edb()
    app.release_desktop(False, False)
    return output_dict


def main(extension_arguments):
    layers_ui = extension_arguments.get("parametrize_layers", True)
    materials_ui = extension_arguments.get("parametrize_materials", True)
    padstacks_ui = extension_arguments.get("parametrize_padstacks", True)
    nets_ui = extension_arguments.get("parametrize_traces", True)
    nets_filter_ui = extension_arguments.get("nets_filter", [])
    poly_ui = extension_arguments.get("expansion_polygon_mm", 0.0)
    voids_ui = extension_arguments.get("expansion_void_mm", 0.0)
    project_name_ui = extension_arguments.get("project_name", generate_unique_name("Parametric", n=2))
    relative_ui = extension_arguments.get("relative_parametric", True)
    design_name_ui = extension_arguments.get("design_name", "")
    aedb_path_ui = extension_arguments.get("aedb_path", "")
    if not aedb_path_ui:
        app = ansys.aedt.core.Desktop(
            new_desktop=False,
            version=version,
            port=port,
            aedt_process_id=aedt_process_id,
            student_version=is_student,
        )
        active_project = app.active_project()
        active_design = app.active_design()
        aedb_path_ui = os.path.join(active_project.GetPath(), active_project.GetName() + ".aedb")
        design_name_ui = active_design.GetName().split(";")[1]
    edb = Edb(aedb_path_ui, design_name_ui, edbversion=version)

    try:
        poly_ui = float(poly_ui) * 0.001
    except:
        poly_ui = None
    try:
        voids_ui = float(voids_ui) * 0.001
    except:
        voids_ui = None
    new_project_aedb = os.path.join(os.path.dirname(aedb_path_ui), project_name_ui + ".aedb")
    edb.auto_parametrize_design(
        layers=layers_ui,
        materials=materials_ui,
        via_holes=padstacks_ui,
        pads=padstacks_ui,
        antipads=padstacks_ui,
        traces=nets_ui,
        layer_filter=None,
        material_filter=None,
        padstack_definition_filter=None,
        trace_net_filter=nets_filter_ui,
        use_single_variable_for_padstack_definitions=True,
        use_relative_variables=relative_ui,
        output_aedb_path=new_project_aedb,
        open_aedb_at_end=False,
        expand_polygons_size=poly_ui,
        expand_voids_size=voids_ui,
    )
    edb.close_edb()
    if not extension_arguments["is_test"]:  # pragma: no cover
        h3d = Hfss3dLayout(new_project_aedb)
        h3d.logger.info("Project generated correctly.")
        h3d.release_desktop(False, False)
    return True


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(extension_arguments, extension_description)
    import pyedb

    if pyedb.__version__ < "0.21.0":
        raise Exception("PyEDB 0.21.0 or recent needs to run this extension.")
    # Open UI
    if not args["is_batch"]:  # pragma: no cover
        output = frontend()
        if output:
            for output_name, output_value in output.items():
                if output_name in extension_arguments:
                    args[output_name] = output_value

    main(args)
