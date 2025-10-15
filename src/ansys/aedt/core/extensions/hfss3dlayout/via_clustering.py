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

from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import tkinter
from tkinter import messagebox
from tkinter import ttk

from pyedb import Edb

from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core import generate_unique_name
from ansys.aedt.core.extensions.misc import ExtensionCommon
from ansys.aedt.core.extensions.misc import ExtensionCommonData
from ansys.aedt.core.extensions.misc import ExtensionHFSS3DLayoutCommon
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.internal.errors import AEDTRuntimeError

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()

# Extension batch arguments
EXTENSION_DEFAULT_ARGUMENTS = {
    "aedb_path": "",
    "design_name": "",
    "new_aedb_path": "",
    "nets_filter": [],
    "start_layer": "",
    "stop_layer": "",
    "contour_list": [],
}
EXTENSION_TITLE = "Via Clustering Extension"


@dataclass
class ViaClusteringExtensionData(ExtensionCommonData):
    """Data class containing user input and computed data."""

    aedb_path: str = EXTENSION_DEFAULT_ARGUMENTS["aedb_path"]
    design_name: str = EXTENSION_DEFAULT_ARGUMENTS["design_name"]
    new_aedb_path: str = EXTENSION_DEFAULT_ARGUMENTS["new_aedb_path"]
    nets_filter: list = None
    start_layer: str = EXTENSION_DEFAULT_ARGUMENTS["start_layer"]
    stop_layer: str = EXTENSION_DEFAULT_ARGUMENTS["stop_layer"]
    contour_list: list = None

    def __post_init__(self):
        if self.nets_filter is None:
            self.nets_filter = EXTENSION_DEFAULT_ARGUMENTS["nets_filter"].copy()
        if self.contour_list is None:
            self.contour_list = EXTENSION_DEFAULT_ARGUMENTS["contour_list"].copy()


class ViaClusteringExtension(ExtensionHFSS3DLayoutCommon):
    """Extension for via clustering in AEDT."""

    def __init__(self, withdraw: bool = False):
        # Initialize the common extension class with the title and theme color
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=False,
            toggle_row=5,
            toggle_column=3,
        )
        # Add private attributes and initialize them through __load_aedt_info
        self.__layers = None
        self.__active_project_path = None
        self.__active_project_name = None
        self.__aedb_path = None
        self.__load_aedt_info()

        # Tkinter widgets
        self._widgets["project_name_entry"] = None
        self._widgets["start_layer_combo"] = None
        self._widgets["stop_layer_combo"] = None
        self._widgets["start_layer_var"] = None
        self._widgets["stop_layer_var"] = None

        # Trigger manually since add_extension_content requires loading info first
        self.add_extension_content()

    def __load_aedt_info(self):
        """Load HFSS 3D Layout info."""
        active_project = self.desktop.active_project()
        self.__active_project_path = active_project.GetPath()
        self.__active_project_name = active_project.GetName()
        active_design_name = self.desktop.active_design().GetName().split(";")[1]
        aedb_path = Path(self.__active_project_path) / (self.__active_project_name + ".aedb")
        self.__aedb_path = os.path.join(
            self.__active_project_path,
            self.__active_project_name + ".aedb",
        )

        edb = Edb(aedb_path, active_design_name, edbversion=VERSION)
        self.__layers = list(edb.stackup.signal_layers.keys())
        edb.close()

        if not self.__layers:
            self.release_desktop()
            raise AEDTRuntimeError("No signal layers are defined in this design.")

    def add_extension_content(self):
        """Add custom content to the extension UI."""
        # Project name label and entry
        project_label = ttk.Label(
            self.root,
            text="Project name:",
            width=30,
            style="PyAEDT.TLabel",
        )
        project_label.grid(row=0, column=0, padx=15, pady=10)
        self._widgets["project_label"] = project_label

        self.project_name_entry = tkinter.Text(self.root, width=30, height=1)
        self.project_name_entry.insert(
            tkinter.END,
            generate_unique_name(self.__active_project_name, n=2),
        )
        self.project_name_entry.grid(row=1, column=0, pady=10, padx=15)
        self._widgets["project_name_entry"] = self.project_name_entry

        # Start layer selection
        label_start_layer = ttk.Label(
            self.root,
            text="Start layer:",
            width=30,
            style="PyAEDT.TLabel",
        )
        label_start_layer.grid(row=0, column=1, padx=15, pady=10)
        self._widgets["label_start_layer"] = label_start_layer

        self.start_layer_var = tkinter.StringVar()
        self.start_layer_var.set(self.__layers[0])
        self.start_layer_combo = ttk.Combobox(
            self.root,
            width=30,
            style="PyAEDT.TCombobox",
            name="start_layer_combo",
            state="readonly",
            textvariable=self.start_layer_var,
        )
        self.start_layer_combo["values"] = self.__layers
        self.start_layer_combo.current(0)
        self.start_layer_combo.grid(row=1, column=1, padx=15, pady=10)
        self.start_layer_combo.focus_set()
        self._widgets["start_layer_combo"] = self.start_layer_combo

        # Stop layer selection
        label_stop_layer = ttk.Label(
            self.root,
            text="Stop layer:",
            width=30,
            style="PyAEDT.TLabel",
        )
        label_stop_layer.grid(row=0, column=2, padx=15, pady=10)
        self._widgets["label_stop_layer"] = label_stop_layer

        self.stop_layer_var = tkinter.StringVar()
        self.stop_layer_var.set(self.__layers[-1])
        self.stop_layer_combo = ttk.Combobox(
            self.root,
            width=30,
            style="PyAEDT.TCombobox",
            name="stop_layer_combo",
            state="readonly",
            textvariable=self.stop_layer_var,
        )
        self.stop_layer_combo["values"] = self.__layers
        self.stop_layer_combo.current(len(self.__layers) - 1)
        self.stop_layer_combo.grid(row=1, column=2, padx=15, pady=10)
        self._widgets["stop_layer_combo"] = self.stop_layer_combo

        # Buttons
        def add_drawing_layer():
            """Add a drawing layer for via merging."""
            hfss = Hfss3dLayout(
                new_desktop=False,
                version=VERSION,
                port=PORT,
                aedt_process_id=AEDT_PROCESS_ID,
                student_version=IS_STUDENT,
            )
            layer = hfss.modeler.stackup.add_layer("via_merging")
            layer.usp = True
            hfss.desktop_class.release_desktop(False, False)

        def callback_merge_vias(extension: ViaClusteringExtension):
            """Callback for merging via instances."""
            hfss = Hfss3dLayout(
                new_desktop=False,
                version=VERSION,
                port=PORT,
                aedt_process_id=AEDT_PROCESS_ID,
                student_version=IS_STUDENT,
            )
            hfss.save_project()
            primitives = hfss.modeler.objects_by_layer(layer="via_merging")
            if not primitives:
                messagebox.showwarning(message="No primitives found on layer defined for merging padstack instances.")
                hfss.desktop_class.release_desktop(False, False)
                extension.release_desktop()
                raise AEDTRuntimeError("No primitives found on layer defined for merging padstack instances.")

            contour_list = []
            for primitive in primitives:
                prim = hfss.modeler.geometries[primitive]
                if prim.prim_type == "poly" or prim.prim_type == "rect":
                    pts = [pt for pt in [_pt.position for _pt in prim.points]]
                    contour_list.append(pts)
                else:
                    hfss.logger.warning(
                        f"Unsupported primitive {prim.name}, only polygon and rectangles are supported."
                    )

            project_name = extension._widgets["project_name_entry"].get("1.0", tkinter.END).strip()
            start_layer = extension._widgets["start_layer_combo"].get()
            stop_layer = extension._widgets["stop_layer_combo"].get()
            new_aedb_path = os.path.join(
                extension._ViaClusteringExtension__active_project_path,
                project_name + ".aedb",
            )

            via_clustering_data = ViaClusteringExtensionData(
                aedb_path=extension._ViaClusteringExtension__aedb_path,
                design_name=extension._ViaClusteringExtension__active_project_name,
                new_aedb_path=new_aedb_path,
                start_layer=start_layer,
                stop_layer=stop_layer,
                contour_list=contour_list,
            )
            extension.data = via_clustering_data
            hfss.desktop_class.release_desktop(False, False)
            extension.root.destroy()

        button_add_layer = ttk.Button(
            self.root,
            text="Add layer",
            width=20,
            command=add_drawing_layer,
            style="PyAEDT.TButton",
            name="add_layer",
        )
        button_add_layer.grid(row=3, column=0, padx=15, pady=10)
        self._widgets["button_add_layer"] = button_add_layer

        button_merge_vias = ttk.Button(
            self.root,
            text="Merge padstack instances",
            width=20,
            command=lambda: callback_merge_vias(self),
            style="PyAEDT.TButton",
            name="merge_vias",
        )
        button_merge_vias.grid(row=4, column=0, padx=15, pady=10)
        self._widgets["button_merge_vias"] = button_merge_vias


def main(data: ViaClusteringExtensionData):
    """Main function to run the via clustering extension."""
    if not data.aedb_path:
        raise AEDTRuntimeError("No AEDB path provided to the extension.")

    if not data.design_name:
        raise AEDTRuntimeError("No design name provided to the extension.")

    if not data.new_aedb_path:
        raise AEDTRuntimeError("No new AEDB path provided to the extension.")

    start_layer = data.start_layer
    stop_layer = data.stop_layer
    design_name = data.design_name
    contour_list = data.contour_list
    aedb_path = data.aedb_path
    new_aedb_path = data.new_aedb_path

    # Copy the original AEDB to new location
    shutil.copytree(aedb_path, new_aedb_path)

    # Perform via clustering
    edb = Edb(new_aedb_path, design_name, edbversion=VERSION)
    edb.padstacks.merge_via(
        contour_boxes=contour_list,
        net_filter=None,
        start_layer=start_layer,
        stop_layer=stop_layer,
    )

    # Clean up via_merging layer primitives
    for prim in edb.modeler.primitives_by_layer["via_merging"]:
        prim.delete()

    edb.save()
    edb.close_edb()

    if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
        h3d = Hfss3dLayout(new_aedb_path)
        h3d.logger.info("Project generated correctly.")
        h3d.desktop_class.release_desktop(False, False)

    return True


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)

    import pyedb

    if pyedb.__version__ < "0.35.0":
        raise Exception("PyEDB 0.35.0 or recent needs to run this extension.")

    # Open UI
    if not args["is_batch"]:
        extension: ExtensionCommon = ViaClusteringExtension(withdraw=False)

        tkinter.mainloop()

        if extension.data is not None:
            main(extension.data)

    else:
        data = ViaClusteringExtensionData()
        for key, value in args.items():
            setattr(data, key, value)
        main(data)
