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

from pyedb import Edb

import pyaedt
from pyaedt import Hfss3dLayout
from pyaedt import generate_unique_name
import pyaedt.workflows.hfss3dlayout
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
extension_arguments = {
    "choice": "ConvexHull",
    "signals": [],
    "reference": [],
    "expansion_factor": 3,
    "fix_disjoints": True,
}
extension_description = "Layout Cutout"


def frontend():  # pragma: no cover
    app = pyaedt.Desktop(
        new_desktop=False,
        version=version,
        port=port,
        aedt_process_id=aedt_process_id,
        student_version=is_student,
    )
    h3d = Hfss3dLayout()
    objs_net = {}
    for net in h3d.oeditor.GetNets():
        objs_net[net] = h3d.modeler.objects_by_net(net)
    import tkinter
    from tkinter import ttk

    import PIL.Image
    import PIL.ImageTk

    master = tkinter.Tk()

    master.geometry("700x450")

    master.title("Advanced Cutout")

    # Load the logo for the main window
    icon_path = os.path.join(os.path.dirname(pyaedt.workflows.__file__), "images", "large", "logo.png")
    im = PIL.Image.open(icon_path)
    photo = PIL.ImageTk.PhotoImage(im)

    # Set the icon for the main window
    master.iconphoto(True, photo)

    # Configure style for ttk buttons
    style = ttk.Style()
    style.configure("Toolbutton.TButton", padding=6, font=("Helvetica", 10))

    var = tkinter.StringVar()
    label = tkinter.Label(master, textvariable=var)
    var.set("Cutout Type:")
    label.grid(row=0, column=0, pady=10)
    combo = ttk.Combobox(master, width=40)  # Set the width of the combobox
    combo["values"] = ("ConvexHull", "Bounding", "Conforming")
    combo.current(0)
    combo.grid(row=0, column=1, pady=10)

    combo.focus_set()
    master.signal_ui = [i for i in h3d.modeler.signal_nets.keys()]
    master.reference_ui = [i for i in h3d.modeler.power_nets.keys()]

    def get_selection():
        sels = h3d.oeditor.GetSelections()
        selection = []
        for sel in sels:
            for net, net_list in objs_net.items():
                if sel in net_list:
                    selection.append(net)
                    break
        return selection

    def apply_signal():
        selection = get_selection()
        master.signal_ui = list(set(selection))
        if selection:
            var2.set("OK")
        else:
            var2.set("Empty selection. Select nets from layout and retry.")

    def apply_reference():
        selection = get_selection()
        master.reference_ui = list(set(selection))
        if selection:
            var3.set("OK")
        else:
            var3.set("Empty selection. Select nets from layout and retry.")

    var2 = tkinter.StringVar()
    label2 = tkinter.Label(master, textvariable=var2, relief=tkinter.RAISED)
    var2.set("Select")
    label2.grid(row=1, column=2, pady=10)
    b_sig = tkinter.Button(master, text="Select signal nets in layout and Apply", width=40, command=apply_signal)
    b_sig.grid(row=1, column=1, pady=10)
    var3 = tkinter.StringVar()
    label3 = tkinter.Label(master, textvariable=var3, relief=tkinter.RAISED)
    var3.set("Select")
    label3.grid(row=2, column=2, pady=10)
    b_ref = tkinter.Button(master, text="Apply Reference Nets", width=40, command=apply_reference)
    b_ref.grid(row=2, column=1, pady=10)

    var_exp = tkinter.StringVar()
    label_exp = tkinter.Label(master, textvariable=var_exp)
    var_exp.set("Expansion factor(mm):")
    label_exp.grid(row=3, column=0, pady=10)
    expansion = tkinter.Text(master, width=20, height=1)
    expansion.insert(tkinter.END, "3")
    expansion.grid(row=3, column=1, pady=10, padx=5)
    var_disj = tkinter.StringVar()
    label_disj = tkinter.Label(master, textvariable=var_disj)
    var_disj.set("Fix disjoint nets:")
    label_disj.grid(row=4, column=0, pady=10)
    disjoint_check = tkinter.IntVar()
    check2 = tkinter.Checkbutton(master, width=30, variable=disjoint_check)
    check2.grid(row=4, column=1, pady=10, padx=5)

    def callback():
        master.choice_ui = combo.get()
        master.disjoints_ui = True if disjoint_check.get() == 1 else False
        master.expansion_ui = expansion.get("1.0", tkinter.END).strip()
        master.destroy()

    b = tkinter.Button(master, text="Create Cutout", width=40, command=callback)
    b.grid(row=6, column=1, pady=10)

    tkinter.mainloop()

    choice_ui = getattr(master, "choice_ui", extension_arguments["choice"])
    disjoints_ui = getattr(master, "disjoints_ui", extension_arguments["fix_disjoints"])
    expansion_ui = getattr(master, "expansion_ui", extension_arguments["expansion_factor"])
    signal_ui = getattr(master, "signal_ui", extension_arguments["signals"])
    reference_ui = getattr(master, "reference_ui", extension_arguments["reference"])

    output_dict = {
        "choice": choice_ui,
        "signals": signal_ui,
        "reference": reference_ui,
        "expansion_factor": expansion_ui,
        "fix_disjoints": disjoints_ui,
    }
    app.release_desktop(False, False)
    return output_dict


def main(extension_args):
    choice = extension_args["choice"]
    signal = extension_args["signals"]
    reference = extension_args["reference"]
    expansion = extension_args["expansion_factor"]
    disjoint = extension_args["fix_disjoints"]
    app = pyaedt.Desktop(
        new_desktop=False,
        version=version,
        port=port,
        aedt_process_id=aedt_process_id,
        student_version=is_student,
    )

    active_project = app.active_project()
    active_design = app.active_design()
    aedb_path = os.path.join(active_project.GetPath(), active_project.GetName() + ".aedb")
    new_path = aedb_path[:-5] + generate_unique_name("_cutout", n=2) + ".aedb"
    edb = Edb(aedb_path, active_design.GetName().split(";")[1], edbversion=version)
    edb.save_edb_as(new_path)
    edb.cutout(
        signal_list=signal,
        reference_list=reference,
        extent_type=choice,
        expansion_size=float(expansion) / 1000,
        use_round_corner=False,
        output_aedb_path=new_path,
        open_cutout_at_end=True,
        use_pyaedt_cutout=True,
        number_of_threads=4,
        use_pyaedt_extent_computing=True,
        extent_defeature=0,
        remove_single_pin_components=True if disjoint else False,
        custom_extent=None,
        custom_extent_units="mm",
        include_partial_instances=False,
        keep_voids=True,
        check_terminals=False,
        include_pingroups=False,
        expansion_factor=0,
        maximum_iterations=10,
        preserve_components_with_model=False,
        simple_pad_check=True,
        keep_lines_as_path=False,
    )
    if disjoint:
        edb.nets.find_and_fix_disjoint_nets(reference)
    edb.close_edb()
    h3d = Hfss3dLayout(new_path)
    if not extension_args["is_test"]:  # pragma: no cover
        app.logger.info("Project generated correctly.")
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
