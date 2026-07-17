# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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
from typing import Any
from typing import cast

import ansys.aedt.core
from ansys.aedt.core import Edb
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
"""Port used by the extension."""
VERSION = get_aedt_version()
"""AEDT version used by the extension."""
AEDT_PROCESS_ID = get_process_id()
"""AEDT process identifier."""
IS_STUDENT = is_student()
"""Flag indicating whether the student version is used."""
CUTOUT_TYPES = ("ConvexHull", "Bounding", "Conforming")
"""Available cutout types."""
EXTENSION_DEFAULT_ARGUMENTS = {
    "cutout_type": "ConvexHull",
    "signals": [],
    "references": [],
    "expansion_factor": 3.0,
    "fix_disjoints": False,
}
"""Default arguments for the extension."""
EXTENSION_TITLE = "Layout cutout"
"""Title displayed for the extension."""
EXTENSION_NB_ROW = 5
"""Number of rows used by the extension UI."""
EXTENSION_NB_COLUMN = 2
"""Number of columns used by the extension UI."""
SELECTION_PERFORMED = "Selection performed."
"""Message displayed after a selection is performed."""
WAITING_FOR_SELECTION = "Waiting for selection..."
"""Message displayed while waiting for a selection."""


@dataclass
class CutoutData(ExtensionCommonData):
    """Data class containing user input and computed data.

    Examples
    --------
    >>> from ansys.aedt.core.extensions.hfss3dlayout.cutout import CutoutData
    >>> data = CutoutData(signals=["SIG1"], references=["GND"], expansion_factor=3.0)

    """

    cutout_type: str = "ConvexHull"
    """Value for cutout type."""
    signals: list[str] = field(default_factory=list)
    """Value for signals."""
    references: list[str] = field(default_factory=list)
    """Value for references."""
    expansion_factor: float = 3.0
    """Value for expansion factor."""
    fix_disjoints: bool = False
    """Value for fix disjoints."""


class CutoutExtension(ExtensionHFSS3DLayoutCommon):
    """Class to create a cutout in an HFSS 3D Layout design.

    Examples
    --------
    >>> from ansys.aedt.core.extensions.hfss3dlayout.cutout import CutoutExtension
    >>> extension = CutoutExtension(withdraw=True)

    """

    def __init__(self, withdraw: bool = False) -> None:
        # Initialize the common extension class with the title and theme color
        super().__init__(EXTENSION_TITLE, withdraw=withdraw, add_custom_content=False, use_edb=True)
        self.data: CutoutData = CutoutData()
        # NOTE: Objects net are loaded only once, if a new project/design is opened
        # the extension has to be opened again or this value will not refresh.
        self.__objects_net = self.__load_objects_net()
        self.__widgets = {}
        self.__execute_cutout = False
        self.add_extension_content()

    @property
    def cutout_data(self) -> CutoutData:
        return cast(CutoutData, self.data)

    @property
    def hfss3dlayout_app(self) -> Any:
        return cast(Any, self.aedt_application)

    def add_extension_content(self) -> None:
        """Add custom content to the extension UI.

        Examples
        --------
        >>> from ansys.aedt.core.extensions.hfss3dlayout.cutout import CutoutExtension
        >>> extension = CutoutExtension(withdraw=True)
        >>> extension.add_extension_content()

        """
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
        expansion.insert(tkinter.END, str(self.cutout_data.expansion_factor))
        expansion.grid(row=1, column=1, **DEFAULT_PADDING)
        self.__widgets["expansion_factor"] = expansion

        label_disj = ttk.Label(upper_frame, text="Fix disjoint nets:", style="PyAEDT.TLabel")
        label_disj.grid(row=2, column=0, **DEFAULT_PADDING)

        check_variable = tkinter.IntVar()
        check_variable.set(1 if self.cutout_data.fix_disjoints else 0)
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
    def objects_net(self) -> dict:
        """Get objects by net from the EDB modeler.

        Examples
        --------
        >>> from ansys.aedt.core.extensions.hfss3dlayout.cutout import CutoutExtension
        >>> extension = CutoutExtension(withdraw=True)
        >>> extension.objects_net

        """
        return self.__objects_net

    @property
    def widgets(self) -> dict:
        """Get mapping to the extension's widgets.

        Examples
        --------
        >>> from ansys.aedt.core.extensions.hfss3dlayout.cutout import CutoutExtension
        >>> extension = CutoutExtension(withdraw=True)
        >>> extension.widgets

        """
        return self.__widgets

    @property
    def execute_cutout(self) -> bool:
        """Get whether the cutout should be executed.

        Examples
        --------
        >>> from ansys.aedt.core.extensions.hfss3dlayout.cutout import CutoutExtension
        >>> extension = CutoutExtension(withdraw=True)
        >>> extension.execute_cutout

        """
        return self.__execute_cutout

    def __load_objects_net(self) -> dict[str, list[str]]:
        """Load objects by net from the EDB modeler."""
        res: defaultdict[str, list[str]] = defaultdict(list)
        if not self.hfss3dlayout_app.modeler.edb:
            self.release_desktop()
            raise AEDTRuntimeError("Extension cannot be used with an empty HFSS 3D Layout design.")
        for net, net_objs in self.hfss3dlayout_app.modeler.edb.layout.primitives_by_net.items():
            res[net].extend(obj.aedt_name for obj in net_objs)
        for net_obj in self.hfss3dlayout_app.modeler.edb.padstacks.instances.values():
            res[net_obj.net_name].append(net_obj.aedt_name)
        self.hfss3dlayout_app.modeler.edb.close()
        return dict(res)

    # Callbacks for the extension's buttons

    def __get_selection(self) -> list[str]:
        """Get the selected nets from the layout."""
        selections = self.hfss3dlayout_app.oeditor.GetSelections()
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

    def __select(self, selection_type: str) -> None:
        """Select nets from the layout."""
        selection = self.__get_selection()
        if not selection:
            raise AEDTRuntimeError("Empty selection. Select nets from layout and retry.")
        self.hfss3dlayout_app.logger.debug(f"Selected nets: {selection}")
        if selection_type == "signal":
            self.cutout_data.signals = selection
            variable = self.__widgets["signal_nets_variable"]
            variable.set(SELECTION_PERFORMED)
        elif selection_type == "reference":
            self.cutout_data.references = selection
            variable = self.__widgets["reference_nets_variable"]
            variable.set(SELECTION_PERFORMED)
        else:  # pragma: no cover
            raise AEDTRuntimeError(f"Unknown selection type: {selection_type}")

    def __reset_selection(self) -> None:
        """Reset the selected nets."""
        self.cutout_data.signals = []
        variable = self.__widgets["signal_nets_variable"]
        variable.set(WAITING_FOR_SELECTION)
        self.cutout_data.references = []
        variable = self.__widgets["reference_nets_variable"]
        variable.set(WAITING_FOR_SELECTION)

    def __output_data(self) -> None:
        """"""
        if not self.cutout_data.signals or not self.cutout_data.references:
            raise AEDTRuntimeError("Please select signal and reference nets before creating a cutout.")
        self.cutout_data.cutout_type = self.__widgets["cutout_type"].get()
        self.cutout_data.expansion_factor = float(self.__widgets["expansion_factor"].get("1.0", tkinter.END).strip())
        self.cutout_data.fix_disjoints = self.__widgets["fix_disjoints"].get() == 1
        self.__execute_cutout = True
        self.root.destroy()


def main(data: CutoutData) -> Path:
    """Main function to execute the cutout operation.

    Examples
    --------
    >>> from ansys.aedt.core.extensions.hfss3dlayout.cutout import CutoutData, main
    >>> data = CutoutData(signals=["SIG1"], references=["GND"], expansion_factor=3.0)
    >>> main(data)

    """
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

    edb = Edb(edbpath=str(aedb_path), cellname=active_design.GetName().split(";")[1], version=VERSION)
    edb.save_as(str(new_path))
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
        edb.layout_validation.disjoint_nets(
            net_list=None, keep_only_main_net=False, clean_disjoints_less_than=0.0, order_by_area=False
        )
    edb.close()

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
            main(extension.cutout_data)
    else:
        data = CutoutData()
        for key, value in args.items():
            setattr(data, key, value)
        main(data)
