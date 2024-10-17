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
extension_description = "Import schematic to Circuit."


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
    icon_path = os.path.join(ansys.aedt.core.workflows.__path__[0], "images", "large", "logo.png")
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

    def browse_asc_folder():
        inital_dir = text.get("1.0", tkinter.END).strip()
        filename = filedialog.askopenfilename(
            initialdir=os.path.dirname(inital_dir) if inital_dir else "/",
            title="Select configuration file",
            filetypes=(("LTSPice file", "*.asc"), ("Spice file", "*.cir *.sp"), ("Qcv file", "*.qcv")),
        )
        text.insert(tkinter.END, filename)

    b1 = tkinter.Button(master, text="...", width=10, command=browse_asc_folder)
    b1.grid(row=0, column=2, pady=10)

    def callback():
        master.asc_path_ui = text.get("1.0", tkinter.END).strip()
        master.destroy()

    b3 = tkinter.Button(master, text="Ok", width=40, command=callback)
    b3.grid(row=1, column=1, pady=10, padx=10)

    tkinter.mainloop()

    asc_file_ui = getattr(master, "asc_path_ui", extension_arguments["asc_file"])

    output_dict = {
        "asc_file": asc_file_ui,
    }
    return output_dict


def main(extension_args):
    asc_file = extension_args["asc_file"]
    if not os.path.exists(asc_file):
        raise Exception("Error. File doesn't exists.")
    cir = Circuit(design=os.path.split(asc_file)[-1][:-4])
    if asc_file.endswith(".asc"):
        cir.create_schematic_from_asc_file(asc_file)
    elif asc_file.endswith(".sp") or asc_file.endswith(".cir"):
        cir.create_schematic_from_netlist(asc_file)
    elif asc_file.endswith(".qcv"):
        cir.create_schematic_from_mentor_netlist(asc_file)
    if not extension_args["is_test"]:  # pragma: no cover
        cir.release_desktop(False, False)
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
