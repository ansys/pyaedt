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

import csv
import os
import re

import pyaedt
from pyaedt.workflows.misc import get_aedt_version
from pyaedt.workflows.misc import get_arguments
from pyaedt.workflows.misc import get_port
from pyaedt.workflows.misc import get_process_id
from pyaedt.workflows.misc import is_student

port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()
is_student = is_student()

cad_format_mapping = {
    "GDSII": "gds",
    "AutoCAD": "dxf",
    "Gerber": "gerber",
    "AWRMicrowaveOffice": "awr",
    "Cadence": "brd",
    "IPC2581": "ipc2581",
    "ODB++": "odb++",
}


def main_code(ipc_path, cad_format, csv_file, cs_name, color_networks):
    hfss3dl = pyaedt.Hfss3dLayout(version=version)

    dn = hfss3dl.design_name

    hfss3dl._import_cad(
        ipc_path, cad_format=cad_format_mapping[cad_format], set_as_active=True, close_active_project=False
    )
    dn2 = hfss3dl.design_name

    hfss3dl.oproject.CopyDesign(hfss3dl.design_name)
    ipk.oproject.Paste()

    ipk.delete_design(dn)
    hfss3dl.close_project(save=False)

    pcb = ipk.create_ipk_3dcomponent_pcb(
        re.sub(r"\W", "", os.path.split(ipc_path)[-1].split(".")[0]),
        [None, dn2, "<--EDB Layout Data-->", True, True],
        "",
        2,
    )

    if csv_file:
        pcb.auto_update = False
        pcb.included_parts = "Device"
        with open(csv_file, "r") as f:
            csv_dictreader = csv.DictReader(f)
            for row in csv_dictreader:
                pcb.included_parts.override_definition(
                    row["Package"],
                    row["Part"],
                    filter_component=False,
                    power=f"{str(row['Power(W)'])}W",
                    r_jb=f"{str(row['ThetaJb(Kel_per_w)'])}Kel_per_w",
                    r_jc=f"{str(row['ThetaJb(Kel_per_w)'])}Kel_per_w",
                    height=f"{str(row['Height(m)'])}m",
                )
        pcb.update()
        pcb.auto_update = True
        network_color = (233, 248, 48)
        objects = ["NAME:PropServers"]
        if color_networks:
            for p in ipk.modeler.user_defined_components[pcb.name].parts.values():
                if not p.solve_inside:
                    objects.append(p.name)
            if len(objects) > 1:
                ipk.oeditor.ChangeProperty(
                    [
                        "NAME:AllTabs",
                        [
                            "NAME:Geometry3DAttributeTab",
                            objects,
                            [
                                "NAME:ChangedProps",
                                [
                                    "NAME:Color",
                                    "R:=",
                                    network_color[0],
                                    "G:=",
                                    network_color[1],
                                    "B:=",
                                    network_color[2],
                                ],
                            ],
                        ],
                    ]
                )

    ipk.modeler.user_defined_components[pcb.name].target_coordinate_system = cs_name
    ipk.modeler.user_defined_components[pcb.name].update()

    ipk.release_desktop(False, False)


def frontend(available_coordinate_systems):
    import tkinter as tk
    import tkinter.filedialog as filedialog
    import tkinter.ttk as ttk

    import PIL.Image
    import PIL.ImageTk

    # Interface
    root = tk.Tk()

    # Load the logo for the main window
    icon_path = os.path.join(os.path.dirname(pyaedt.workflows.__file__), "images", "large", "logo.png")
    im = PIL.Image.open(icon_path)
    photo = PIL.ImageTk.PhotoImage(im)

    # Set the icon for the main window
    root.iconphoto(True, photo)

    ipc_path = tk.StringVar()
    csv_file = tk.StringVar()
    cs_name = tk.StringVar()
    cad_format = tk.StringVar()
    color = tk.IntVar()

    def browse_file1():
        ipc_path.set(filedialog.askopenfilename())

    def browse_file2():
        csv_file.set(filedialog.askopenfilename())

    py = 5

    tk.Label(root, text="ECAD Format").grid(row=0, column=0, pady=py, padx=(50, 0))
    dropdown1 = ttk.Combobox(root, textvariable=cad_format, values=list(cad_format_mapping.keys()))
    dropdown1.grid(row=0, column=1, columnspan=2, padx=(10, 50), pady=py)
    dropdown1.current(0)

    tk.Label(root, text="ECAD Path").grid(row=1, column=0, padx=(50, 0), pady=(py * 2, py))  # ipc_path_label
    tk.Entry(root, textvariable=ipc_path).grid(row=1, column=1)  # ipc_path_entry
    tk.Button(root, text="Browse", command=browse_file1).grid(
        row=1, column=2, padx=(10, 50), pady=py
    )  # ipc_path_browse

    tk.Label(root, text="CSV Path").grid(row=2, column=0, padx=(50, 0))  # csv_file_label
    tk.Entry(root, textvariable=csv_file).grid(row=2, column=1)  # csv_file_entry
    tk.Button(root, text="Browse", command=browse_file2).grid(
        row=2, column=2, padx=(10, 50), pady=py
    )  # csv_file_browse

    tk.Label(root, text="Coord Sys").grid(row=3, column=0, pady=py, padx=(50, 0))
    dropdown = ttk.Combobox(root, textvariable=cs_name, values=available_coordinate_systems)
    dropdown.grid(row=3, column=1, columnspn=2, padx=(10, 50), pady=py)
    dropdown.current(0)

    checkbox = tk.Checkbutton(root, text="Change color for 2R components", variable=color)
    checkbox.grid(row=4, column=0, columnspn=3, pady=py, padx=(50, 50))

    sub_btn = tk.Button(
        root,
        text="Run",
        command=main_code(ipc_path.get(), cad_format.get(), csv_file.get(), cs_name.get(), color.get()),
    )
    sub_btn.grid(row=5, column=1, pady=(py, py * 2))

    root.mainloop()


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(None, "Import ECAD in Icepak")

    ipk = pyaedt.Icepak(version=version)

    # Open UI
    if not args["is_batch"]:  # pragma: no cover
        cs = ["Global"] + [cs.name for cs in ipk.modeler.coordinate_systems]
        frontend(cs)
    else:
        main_code(args["ipc_path"], args["cad_format"], args["csv_file"], args["cs_name"], args["color_networks"])
