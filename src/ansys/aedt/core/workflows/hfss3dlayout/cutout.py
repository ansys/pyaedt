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
from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core.generic.general_methods import generate_unique_name
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
    "choice": "ConvexHull",
    "signals": [],
    "reference": [],
    "expansion_factor": 3,
    "fix_disjoints": True,
}
extension_description = "Layout Cutout"


def frontend():  # pragma: no cover
    import tkinter
    from tkinter import ttk

    import PIL.Image
    import PIL.ImageTk
    from ansys.aedt.core.workflows.misc import ExtensionTheme

    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        version=version,
        port=port,
        aedt_process_id=aedt_process_id,
        student_version=is_student,
    )

    active_project = app.active_project()
    active_design = app.active_design()

    if active_design.GetDesignType() in ["HFSS 3D Layout Design"]:
        design_name = active_design.GetName().split(";")[1]
    else:  # pragma: no cover
        app.logger.debug("HFSS 3D Layout project is needed.")
        app.release_desktop(False, False)
        raise Exception("HFSS 3D Layout designs needed.")

    project_name = active_project.GetName()
    h3d = ansys.aedt.core.Hfss3dLayout(project=project_name, design=design_name)

    objs_net = {}
    for net in h3d.oeditor.GetNets():
        objs_net[net] = h3d.modeler.objects_by_net(net)

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

    label = ttk.Label(master, text="Cutout Type:", style="PyAEDT.TLabel")
    label.grid(row=0, column=0, pady=10, padx=10)

    combo = ttk.Combobox(master, width=40, style="PyAEDT.TCombobox")  # Set the width of the combobox
    combo["values"] = ("ConvexHull", "Bounding", "Conforming")
    combo.current(0)
    combo.grid(row=0, column=1, pady=10, padx=10)

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
    label2 = ttk.Label(master, textvariable=var2, style="PyAEDT.TLabel")
    var2.set("Select")
    label2.grid(row=1, column=2, pady=10, padx=10)

    b_sig = ttk.Button(
        master, text="Select signal nets in layout and Apply", width=40, command=apply_signal, style="PyAEDT.TButton"
    )
    b_sig.grid(row=1, column=1, pady=10, padx=10)

    var3 = tkinter.StringVar()
    label3 = ttk.Label(master, textvariable=var3, style="PyAEDT.TLabel")
    var3.set("Select")
    label3.grid(row=2, column=2, pady=10, padx=10)

    b_ref = ttk.Button(master, text="Apply Reference Nets", width=40, command=apply_reference, style="PyAEDT.TButton")
    b_ref.grid(row=2, column=1, pady=10)

    label_exp = ttk.Label(master, text="Expansion factor (mm):", style="PyAEDT.TLabel")
    label_exp.grid(row=3, column=0, pady=10, padx=10)

    expansion = tkinter.Text(master, width=20, height=1)
    expansion.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
    expansion.insert(tkinter.END, "3")
    expansion.grid(row=3, column=1, pady=10, padx=10)

    label_disj = ttk.Label(master, text="Fix disjoint nets:", style="PyAEDT.TLabel")
    label_disj.grid(row=4, column=0, pady=10)

    disjoint_check = tkinter.IntVar()
    check2 = ttk.Checkbutton(master, variable=disjoint_check, style="PyAEDT.TCheckbutton")
    check2.grid(row=4, column=1, pady=10)

    def toggle_theme():
        if master.theme == "light":
            set_dark_theme()
            master.theme = "dark"
        else:
            set_light_theme()
            master.theme = "light"

    def set_light_theme():
        master.configure(bg=theme.light["widget_bg"])
        expansion.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
        theme.apply_light_theme(style)
        change_theme_button.config(text="\u263D")  # Sun icon for light theme

    def set_dark_theme():
        master.configure(bg=theme.dark["widget_bg"])
        expansion.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        theme.apply_dark_theme(style)
        change_theme_button.config(text="\u2600")  # Moon icon for dark theme

    # Create a frame for the toggle button to position it correctly
    button_frame = ttk.Frame(master, style="PyAEDT.TFrame", relief=tkinter.SUNKEN, borderwidth=2)
    button_frame.grid(row=6, column=2, pady=10, padx=10)

    # Add the toggle theme button inside the frame
    change_theme_button = ttk.Button(
        button_frame, width=20, text="\u263D", command=toggle_theme, style="PyAEDT.TButton"
    )

    change_theme_button.grid(row=0, column=0, padx=0)

    def callback():
        master.flag = True
        master.choice_ui = combo.get()
        master.disjoints_ui = True if disjoint_check.get() == 1 else False
        master.expansion_ui = expansion.get("1.0", tkinter.END).strip()
        master.destroy()

    b = ttk.Button(master, text="Create Cutout", width=40, command=callback, style="PyAEDT.TButton")
    b.grid(row=6, column=1, pady=10)

    tkinter.mainloop()

    choice_ui = getattr(master, "choice_ui", extension_arguments["choice"])
    disjoints_ui = getattr(master, "disjoints_ui", extension_arguments["fix_disjoints"])
    expansion_ui = getattr(master, "expansion_ui", extension_arguments["expansion_factor"])
    signal_ui = getattr(master, "signal_ui", extension_arguments["signals"])
    reference_ui = getattr(master, "reference_ui", extension_arguments["reference"])
    output_dict = {}
    app.release_desktop(False, False)
    if master.flag:
        output_dict = {
            "choice": choice_ui,
            "signals": signal_ui,
            "reference": reference_ui,
            "expansion_factor": expansion_ui,
            "fix_disjoints": disjoints_ui,
        }
    return output_dict


def main(extension_args):
    choice = extension_args["choice"]
    signal = extension_args["signals"]
    reference = extension_args["reference"]
    expansion = extension_args["expansion_factor"]
    disjoint = extension_args["fix_disjoints"]
    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        version=version,
        port=port,
        aedt_process_id=aedt_process_id,
        student_version=is_student,
    )

    active_project = app.active_project()
    active_design = app.active_design()
    aedb_path = Path(active_project.GetPath()) / f"{active_project.GetName()}.aedb"
    new_path = aedb_path.with_stem(aedb_path.stem + generate_unique_name("_cutout", n=2))
    edb = Edb(str(aedb_path), active_design.GetName().split(";")[1], edbversion=version)
    edb.save_edb_as(str(new_path))
    edb.cutout(
        signal_list=signal,
        reference_list=reference,
        extent_type=choice,
        expansion_size=float(expansion) / 1000,
        use_round_corner=False,
        output_aedb_path=str(new_path),
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

    # Open layout in HFSS 3D Layout
    Hfss3dLayout(str(new_path))

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
    else:
        main(args)
