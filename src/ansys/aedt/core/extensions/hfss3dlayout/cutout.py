# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
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
from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field
import os
from pathlib import Path
import tkinter
from tkinter import ttk
from typing import List

from pyedb import Edb

import ansys.aedt.core
from ansys.aedt.core import Hfss3dLayout
import ansys.aedt.core.extensions.hfss3dlayout
from ansys.aedt.core.extensions.misc import DEFAULT_PADDING
from ansys.aedt.core.extensions.misc import SUN
from ansys.aedt.core.extensions.misc import ExtensionCommonData
from ansys.aedt.core.extensions.misc import ExtensionHFSS3DLayoutCommon
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.internal.errors import AEDTRuntimeError

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()
CUTOUT_TYPES = ("ConvexHull", "Bounding", "Conforming")
EXTENSION_DEFAULT_ARGUMENTS = {
    "cutout_type": "ConvexHull",
    "signals": [],
    "references": [],
    "expansion_factor": 3.0,
    "fix_disjoints": False,
}
EXTENSION_TITLE = "Layout cutout"
EXTENSION_NB_ROW = 5
EXTENSION_NB_COLUMN = 2
SELECTION_PERFORMED = "Selection performed."
WAITING_FOR_SELECTION = "Waiting for selection..."


@dataclass
class CutoutData(ExtensionCommonData):
    """Data class containing user input and computed data."""

    cutout_type: str = EXTENSION_DEFAULT_ARGUMENTS["cutout_type"]
    signals: List[str] = field(default_factory=lambda: EXTENSION_DEFAULT_ARGUMENTS["signals"])
    references: List[str] = field(default_factory=lambda: EXTENSION_DEFAULT_ARGUMENTS["references"])
    expansion_factor: float = EXTENSION_DEFAULT_ARGUMENTS["expansion_factor"]
    fix_disjoints: bool = EXTENSION_DEFAULT_ARGUMENTS["fix_disjoints"]


class CutoutExtension(ExtensionHFSS3DLayoutCommon):
    """Class to create a cutout in an HFSS 3D Layout design."""

    def __init__(self, withdraw: bool = False):
        # Initialize the common extension class with the title and theme color
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=False,
        )
        self.data: CutoutData = CutoutData()
        # NOTE: Objects net are loaded only once, if a new project/design is opened
        # the extension has to be opened again or this value will not refresh.
        self.__objects_net = self.__load_objects_net()
        self.__widgets = {}
        self.__execute_cutout = False
        self.add_extension_content()

    def add_extension_content(self):
        """Add custom content to the extension UI."""
        upper_frame = ttk.Frame(self.root, style="PyAEDT.TFrame")
        upper_frame.grid(row=0, column=0, columnspan=EXTENSION_NB_COLUMN)

        label = ttk.Label(upper_frame, text="Cutout type:", style="PyAEDT.TLabel")
        label.grid(row=0, column=0, **DEFAULT_PADDING)

        combo = ttk.Combobox(upper_frame, style="PyAEDT.TCombobox", values=CUTOUT_TYPES, state="readonly")
        combo.grid(row=0, column=1, **DEFAULT_PADDING)
        combo.current(0)
        self.__widgets["cutout_type"] = combo

        label_exp = ttk.Label(upper_frame, text="Expansion factor (mm):", style="PyAEDT.TLabel")
        label_exp.grid(row=1, column=0, **DEFAULT_PADDING)

        expansion = tkinter.Text(upper_frame, width=15, height=1)
        expansion.insert(tkinter.END, str(EXTENSION_DEFAULT_ARGUMENTS["expansion_factor"]))
        expansion.grid(row=1, column=1, **DEFAULT_PADDING)
        self.__widgets["expansion_factor"] = expansion

        label_disj = ttk.Label(upper_frame, text="Fix disjoint nets:", style="PyAEDT.TLabel")
        label_disj.grid(row=2, column=0, **DEFAULT_PADDING)

        check_variable = tkinter.IntVar()
        check_variable.set(EXTENSION_DEFAULT_ARGUMENTS["fix_disjoints"])
        check = ttk.Checkbutton(upper_frame, variable=check_variable, style="PyAEDT.TCheckbutton")
        check.grid(row=2, column=1, **DEFAULT_PADDING)
        self.__widgets["fix_disjoints"] = check_variable

        selection_button_width = 20

        signal_button = ttk.Button(
            upper_frame,
            text="Select signal nets in layout",
            command=lambda: self.__select("signal"),
            style="PyAEDT.TButton",
            width=selection_button_width,
        )
        signal_button.grid(row=3, column=0, **DEFAULT_PADDING)
        self.__widgets["signal_nets"] = signal_button

        signal_nets_variable = tkinter.StringVar()
        signal_nets_label = ttk.Label(upper_frame, textvariable=signal_nets_variable, style="PyAEDT.TLabel")
        signal_nets_variable.set(WAITING_FOR_SELECTION)
        signal_nets_label.grid(row=3, column=1, **DEFAULT_PADDING)
        self.__widgets["signal_nets_variable"] = signal_nets_variable

        reference_button = ttk.Button(
            upper_frame,
            text="Select reference nets",
            command=lambda: self.__select("reference"),
            style="PyAEDT.TButton",
            width=selection_button_width,
        )
        reference_button.grid(row=4, column=0, **DEFAULT_PADDING)
        self.__widgets["reference_nets"] = reference_button

        reference_nets_variable = tkinter.StringVar()
        reference_nets_label = ttk.Label(upper_frame, textvariable=reference_nets_variable, style="PyAEDT.TLabel")
        reference_nets_variable.set(WAITING_FOR_SELECTION)
        reference_nets_label.grid(row=4, column=1, **DEFAULT_PADDING)
        self.__widgets["reference_nets_variable"] = reference_nets_variable

        lower_frame_1 = ttk.Frame(self.root, style="PyAEDT.TFrame")
        lower_frame_1.grid(row=2, column=0, columnspan=EXTENSION_NB_COLUMN)

        reset_button = ttk.Button(
            lower_frame_1,
            text="Reset selection",
            command=lambda: self.__reset_selection(),
            style="PyAEDT.TButton",  # noqa
        )
        reset_button.grid(row=1, column=0, **DEFAULT_PADDING)
        self.__widgets["reset"] = reset_button

        create_cutout = ttk.Button(
            lower_frame_1,
            text="Create Cutout",
            command=lambda: self.__output_data(),
            style="PyAEDT.TButton",  # noqa
        )
        create_cutout.grid(row=1, column=1, **DEFAULT_PADDING)
        self.__widgets["create_cutout"] = create_cutout

        change_theme_button = ttk.Button(
            lower_frame_1,
            width=10,
            text=SUN,
            command=self.toggle_theme,
            style="PyAEDT.TButton",
            name="theme_toggle_button",
        )
        change_theme_button.grid(row=1, column=2, **DEFAULT_PADDING)

    @property
    def objects_net(self):
        """Get objects by net from the EDB modeler."""
        return self.__objects_net

    @property
    def widgets(self):
        """Get mapping to the extension's widgets"""
        return self.__widgets

    @property
    def execute_cutout(self):
        """Get whether the cutout should be executed."""
        return self.__execute_cutout

    def __load_objects_net(self):
        """Load objects by net from the EDB modeler."""
        res = defaultdict(list)
        if not self.aedt_application.modeler.edb:
            self.release_desktop()
            raise AEDTRuntimeError("Extension cannot be used with an empty HFSS 3D Layout design.")
        for net, net_objs in self.aedt_application.modeler.edb.modeler.primitives_by_net.items():
            res[net].extend(obj.aedt_name for obj in net_objs)
        for net_obj in self.aedt_application.modeler.edb.padstacks.instances.values():
            res[net_obj.net_name].append(net_obj.aedt_name)
        self.aedt_application.modeler.edb.close_edb()
        res = dict(res)
        return res

    # Callbacks for the extension's buttons

    def __get_selection(self):
        """Get the selected nets from the layout."""
        selections = self.aedt_application.oeditor.GetSelections()
        if not selections:
            raise AEDTRuntimeError("No nets selected. Please select nets from the layout.")
        selection = set()
        for sel in selections:
            for net, net_list in self.objects_net.items():
                if sel in net_list:
                    selection.add(net)
                    break
        selection = list(selection)
        return selection

    def __select(self, selection_type: str):
        """Select nets from the layout."""
        selection = self.__get_selection()
        if not selection:
            raise AEDTRuntimeError("Empty selection. Select nets from layout and retry.")
        self.aedt_application.logger.debug(f"Selected nets: {selection}")
        if selection_type == "signal":
            self.data.signals = selection
            variable = self.__widgets["signal_nets_variable"]
            variable.set(SELECTION_PERFORMED)
        elif selection_type == "reference":
            self.data.references = selection
            variable = self.__widgets["reference_nets_variable"]
            variable.set(SELECTION_PERFORMED)
        else:  # pragma: no cover
            raise AEDTRuntimeError(f"Unknown selection type: {selection_type}")

    def __reset_selection(self):
        """Reset the selected nets."""
        if self.data is not None:
            self.data.signals = []
            variable = self.__widgets["signal_nets_variable"]
            variable.set(WAITING_FOR_SELECTION)
            self.data.references = []
            variable = self.__widgets["reference_nets_variable"]
            variable.set(WAITING_FOR_SELECTION)

    def __output_data(self):
        """"""
        if not self.data.signals or not self.data.references:
            raise AEDTRuntimeError("Please select signal and reference nets before creating a cutout.")
        self.data.cutout_type = self.__widgets["cutout_type"].get()
        self.data.expansion_factor = float(self.__widgets["expansion_factor"].get("1.0", tkinter.END).strip())
        self.data.fix_disjoints = self.__widgets["fix_disjoints"].get() == 1
        self.__execute_cutout = True
        self.root.destroy()


def main(data: CutoutData) -> Path:
    """Main function to execute the cutout operation."""
    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        version=VERSION,
        port=PORT,
        aedt_process_id=AEDT_PROCESS_ID,
        student_version=IS_STUDENT,
    )

    active_project = app.active_project()
    active_design = app.active_design()

    aedb_path = Path(active_project.GetPath()) / f"{active_project.GetName()}.aedb"
    new_path = aedb_path.with_stem(aedb_path.stem + generate_unique_name("_cutout", n=2))

    edb = Edb(str(aedb_path), active_design.GetName().split(";")[1], edbversion=VERSION)
    edb.save_edb_as(str(new_path))
    edb.cutout(
        signal_list=data.signals,
        reference_list=data.references,
        extent_type=data.cutout_type,
        expansion_size=float(data.expansion_factor) / 1000,
        use_round_corner=False,
        output_aedb_path=str(new_path),
        open_cutout_at_end=True,
        use_pyaedt_cutout=True,
        number_of_threads=4,
        use_pyaedt_extent_computing=True,
        extent_defeature=0,
        remove_single_pin_components=data.fix_disjoints,
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
    if data.fix_disjoints:
        edb.nets.find_and_fix_disjoint_nets(data.references)
    edb.close_edb()

    if "PYTEST_CURRENT_TEST" not in os.environ:
        Hfss3dLayout(str(new_path))
        app.logger.info("Project generated correctly.")
        app.release_desktop(False, False)
    return new_path


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)

    # Open UI
    if not args["is_batch"]:
        extension = CutoutExtension(withdraw=False)

        tkinter.mainloop()

        if extension.execute_cutout:
            main(extension.data)
    else:
        data = CutoutData()
        for key, value in args.items():
            setattr(data, key, value)
        main(data)
