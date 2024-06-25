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

import os.path

from pyedb import Edb

import pyaedt
from pyaedt import Hfss3dLayout
from pyaedt import generate_unique_name
from pyaedt.generic.filesystem import search_files
import pyaedt.workflows
from pyaedt.workflows.misc import get_aedt_version
from pyaedt.workflows.misc import get_arguments
from pyaedt.workflows.misc import get_port
from pyaedt.workflows.misc import get_process_id
from pyaedt.workflows.misc import is_student

port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()
is_student = is_student()

# Extension batch arguments
extension_arguments = {"aedb_path": "", "configuration_path": ""}
extension_description = "Configure project from aedb file"


def frontend():  # pragma: no cover

    import tkinter
    from tkinter import filedialog
    from tkinter import ttk

    import PIL.Image
    import PIL.ImageTk

    master = tkinter.Tk()

    master.geometry("750x250")

    master.title(extension_description)

    # Load the logo for the main window
    icon_path = os.path.join(pyaedt.workflows.__path__[0], "images", "large", "logo.png")
    im = PIL.Image.open(icon_path)
    photo = PIL.ImageTk.PhotoImage(im)

    # Set the icon for the main window
    master.iconphoto(True, photo)

    # Configure style for ttk buttons
    style = ttk.Style()
    style.configure("Toolbutton.TButton", padding=6, font=("Helvetica", 8))

    var2 = tkinter.StringVar()
    label2 = tkinter.Label(master, textvariable=var2)
    var2.set("Browse file:")
    label2.grid(row=0, column=0, pady=10)
    text = tkinter.Text(master, width=40, height=1)
    text.grid(row=0, column=1, pady=10, padx=5)

    def browse_aedb():
        filename = filedialog.askopenfilename(
            initialdir="/",
            title="Select a layout folder or file",
            filetypes=(("aedb file", "*.def"), ("brd", "*.brd"), ("all files", "*.*")),
        )
        if filename.endswith(".def"):
            filename = os.path.dirname(filename)
        text.insert(tkinter.END, filename)

    b1 = tkinter.Button(master, text="...", width=10, command=browse_aedb)
    b1.grid(row=0, column=2, pady=10)

    var3 = tkinter.StringVar()
    label3 = tkinter.Label(master, textvariable=var3)
    var3.set("Browse configuration file or folder:")
    label3.grid(row=1, column=0, pady=10)
    text2 = tkinter.Text(master, width=40, height=1)
    text2.grid(row=1, column=1, pady=10, padx=5)

    def browse_config():
        inital_dir = text.get("1.0", tkinter.END).strip()
        filename = filedialog.askopenfilename(
            initialdir=os.path.dirname(inital_dir) if inital_dir else "/",
            title="Select configuration file",
            filetypes=(("Configuration file", "*.json"), ("Configuration file", "*.toml")),
        )
        text2.insert(tkinter.END, filename)

    b2 = tkinter.Button(master, text="...", width=10, command=browse_config)
    b2.grid(row=1, column=2, pady=10)

    def callback():
        master.aedb_path_ui = text.get("1.0", tkinter.END).strip()
        master.configuration_path_ui = text2.get("1.0", tkinter.END).strip()
        master.destroy()

    b3 = tkinter.Button(master, text="Ok", width=40, command=callback)
    b3.grid(row=25, column=1, pady=10, padx=10)

    tkinter.mainloop()

    aedb_path_ui = getattr(master, "aedb_path_ui", extension_arguments["aedb_path"])

    configuration_path_ui = getattr(master, "configuration_path_ui", extension_arguments["configuration_path"])

    output_dict = {
        "configuration_path": configuration_path_ui,
        "aedb_path": aedb_path_ui,
    }
    return output_dict


def main(extension_args):
    aedb_path = extension_args["aedb_path"]
    config = extension_args["configuration_path"]
    if os.path.isdir(config):
        configs = search_files(config, "*.json")
        configs += search_files(config, "*.toml")
    else:
        configs = [config]
    app = pyaedt.Desktop(
        new_desktop_session=False,
        specified_version=version,
        port=port,
        aedt_process_id=aedt_process_id,
        student_version=is_student,
    )
    if aedb_path == "":
        project_name = app.active_project().GetName()
        aedb_path = os.path.join(app.active_project().GetPath(), project_name + ".aedb")
    else:
        project_name = os.path.splitext(os.path.split(aedb_path)[-1])[0]
    if project_name in app.project_list():
        app.odesktop.CloseProject(project_name)
    for config in configs:
        edbapp = Edb(aedb_path, edbversion=version)
        config_name = os.path.splitext(os.path.split(config)[-1])[0]
        output_path = aedb_path[:-5] + f"_{config_name}.aedb"
        if os.path.exists(output_path):
            new_name = generate_unique_name(config_name, n=2)
            output_path = aedb_path[:-5] + f"_{new_name}.aedb"
        edbapp.configuration.load(config_file=config)
        edbapp.configuration.run()
        edbapp.save_edb_as(output_path)
        edbapp.close()
        h3d = Hfss3dLayout(output_path)
        h3d.save_project()
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
