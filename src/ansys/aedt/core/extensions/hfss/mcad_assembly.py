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

from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import tkinter
from tkinter import filedialog
from tkinter import ttk
from typing import TYPE_CHECKING

from pydantic import BaseModel
from pydantic import Field

import ansys.aedt.core
from ansys.aedt.core.extensions.misc import ExtensionCommon
from ansys.aedt.core.extensions.misc import ExtensionHFSSCommon
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.generic.constants import Axis
from ansys.aedt.core.generic.file_utils import generate_unique_name

if TYPE_CHECKING:
    from ansys.aedt.core.hfss import Hfss

DATA = {
    "component_models": {
        "case": "Chassi.a3dcomp",
        "cable": "Cable_1.a3dcomp",
        "clamp_monitor": "BCI_MONITORING_CLAMP.a3dcomp",
    },
    "layout_component_models": {
        "pcb": "DCDC-Converter-App_main.aedbcomp",
    },
    "coordinate_system": {
        "GLOBAL_2": {"origin": ["100mm", "0mm", "0mm"], "reference_cs": "Global"},
        "CS_CLAMP": {"origin": ["-130mm", "80mm", "12mm"], "reference_cs": "GLOBAL_2"},
    },
    "assembly": {
        "case": {
            "component_type": "mcad",
            "model": "case",
            "reference_coordinate_system": "Global",
            "target_coordinate_system": "GLOBAL_2",
            "arranges": [
                {"operation": "rotate", "axis": "X", "angle": "0deg"},
                {"operation": "move", "vector": ["0mm", "0mm", "0mm"]},
            ],
            "sub_components": {
                "pcb": {
                    "component_type": "ecad",
                    "model": "pcb",
                    "target_coordinate_system": "Guiding_Pin",
                    "layout_coordinate_systems": ["CABLE1_via_65", "CABLE2_via_65", "H0_via_65"],
                    "reference_coordinate_system": "H0_via_65",
                    "arranges": [
                        {"operation": "rotate", "axis": "X", "angle": "0deg"},
                        {"operation": "move", "vector": ["0mm", "0mm", "0mm"]},
                    ],
                    "sub_components": {
                        "cable_1": {
                            "component_type": "mcad",
                            "model": "cable",
                            "target_coordinate_system": "CABLE1_via_65",
                        },
                        "cable_2": {
                            "component_type": "mcad",
                            "model": "cable",
                            "target_coordinate_system": "CABLE2_via_65",
                        },
                    },
                }
            },
        },
        "clamp_monitor": {
            "component_type": "mcad",
            "model": "clamp_monitor",
            "reference_coordinate_system": "Global",
            "target_coordinate_system": "CS_CLAMP",
        },
    },
}
"""Stored data."""


# Frontend
class AedtInfo(BaseModel):
    """Provide AEDT info."""

    version: str = ""
    """Value for version."""
    port: int
    """Value for port."""
    aedt_process_id: int | None
    """Value for AEDT process id."""
    student_version: bool | None = False
    """Value for student version."""


class MCADAssemblyFrontend(ExtensionHFSSCommon):
    """Provide MCAD assembly frontend."""

    EXTENSION_TITLE = "MCAD Assembly"
    """Title displayed for the extension."""
    GRID_PARAMS = {"padx": 15, "pady": 10, "sticky": "nsew"}
    """Grid params."""
    PACK_PARAMS = {"padx": 15, "pady": 10}
    """Pack params."""

    tab_frame_main = None
    """Value for tab frame main."""

    local_path = ""
    """Path to local."""
    config_data: dict = dict()
    """Value for config data."""

    def __init__(self, withdraw: bool = False) -> None:
        self.aedt_info = AedtInfo(
            port=get_port(), version=get_aedt_version(), aedt_process_id=get_process_id(), student_version=is_student()
        )

        super().__init__(
            self.EXTENSION_TITLE,
            withdraw=withdraw,
            add_custom_content=True,
            toggle_row=2,
            toggle_column=0,
        )

    def add_toggle_theme_button(
        self, parent: tkinter.Widget, toggle_row: int | None = None, toggle_column: int | None = None
    ) -> None:
        """Create a button to toggle between light and dark themes.

        Examples
        --------
        >>> import tkinter
        >>> from ansys.aedt.core.extensions.hfss.mcad_assembly import MCADAssemblyFrontend
        >>> frontend = MCADAssemblyFrontend(withdraw=True)
        >>> frame = tkinter.Frame(frontend.root)
        >>> frontend.add_toggle_theme_button(frame)

        """
        button_frame = ttk.Frame(
            parent, style="PyAEDT.TFrame", relief=tkinter.SUNKEN, borderwidth=2, name="theme_button_frame"
        )
        button_frame.pack(fill="both", expand=False, **{"padx": 5, "pady": 5})

        ttk.Button(
            button_frame,
            width=10,
            text="Run",
            command=lambda: self._run(self.config_data),
            style="PyAEDT.TButton",
            name="run",
        ).pack(anchor="w", side="left", **{"padx": 15, "pady": 10})

        self._widgets["button_frame"] = button_frame

        change_theme_button = ttk.Button(
            button_frame,
            width=10,
            text="\u263d",
            command=self.toggle_theme,
            style="PyAEDT.TButton",
            name="theme_toggle_button",
        )
        # change_theme_button.grid(row=0, column=0, **{"padx": 15, "pady": 10})
        change_theme_button.pack(anchor="e", side="right", **{"padx": 15, "pady": 10})
        self._widgets["change_theme_button"] = change_theme_button

    def add_extension_content(self) -> None:
        """Add custom content to the extension UI.

        Examples
        --------
        >>> from ansys.aedt.core.extensions.hfss.mcad_assembly import MCADAssemblyFrontend
        >>> extension = MCADAssemblyFrontend(withdraw=True)
        >>> extension.add_extension_content()

        """
        self.root.geometry("700x600")

        menubar = tkinter.Menu(self.root)
        self.root.config(menu=menubar)

        nb = ttk.Notebook(self.root, name="notebook", style="PyAEDT.TNotebook")
        self.tab_frame_main = ttk.Frame(nb, name="main", style="PyAEDT.TFrame")

        nb.add(self.tab_frame_main, text="Main")

        nb.pack(fill="both", expand=True)

        create_tab_main(self.tab_frame_main, self)

    def _run(self, config_data: dict):
        hfss = ansys.aedt.core.Hfss(**self.aedt_info.model_dump())
        app = MCADAssemblyBackend._load(data=config_data, cur_dir=self.local_path)
        app._run(hfss)
        del app

        if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
            hfss.desktop_class.release_desktop(False, False)
        else:
            hfss.close_project(save=False)
        return


# create main tab
def create_tab_main(tab_frame: tkinter.Widget, master: MCADAssemblyFrontend) -> None:
    """Create tab main."""
    tree = ttk.Treeview(tab_frame, name="tree")
    tree.pack(expand=True, fill="both", **master.PACK_PARAMS)

    ttk.Button(
        tab_frame,
        # width=10,
        text="Load Configure File",
        command=lambda: load_dict(tree, master),
        style="PyAEDT.TButton",
        name="load",
    ).pack(anchor="w", **master.PACK_PARAMS)


def load_dict(tree: ttk.Treeview, master: MCADAssemblyFrontend) -> None:
    """Load dict."""
    file_path = filedialog.askopenfilename(
        title="Select Design",
        filetypes=(("JSON", "*.json"), ("All files", "*.*")),
    )
    if not file_path:  # pragma: no cover
        return
    else:
        with open(file_path, "r") as f:
            data = json.load(f)
            local_path = Path(file_path)
            master.local_path = local_path.parent
            master.config_data = data
    tree.delete(*tree.get_children())  # clear everything

    for key in ["coordinate_system", "component_models", "layout_component_models"]:
        temp = tree.insert("", "end", text=key, open=False)
        for key, value in master.config_data.get(key, {}).items():
            text = f"{key}: {value}"
            tree.insert(temp, "end", text=text, open=False)

    node3 = tree.insert("", "end", text=str("assembly"), open=False)
    insert_items(tree, node3, master.config_data.get("assembly", {}))


def insert_items(tree: ttk.Treeview, parent: str, dictionary: dict | list | str | int | float | None) -> None:
    """Insert items."""
    if isinstance(dictionary, dict):
        for key, value in dictionary.items():
            node = tree.insert(parent, "end", text=str(key), open=False)
            insert_items(tree, node, value)
    elif isinstance(dictionary, list):
        for idx, item in enumerate(dictionary):
            node = tree.insert(parent, "end", text=f"[{idx}]", open=False)
            insert_items(tree, node, item)
    else:
        tree.insert(parent, "end", text=str(dictionary))


# end of create_tab_main function

# End of frontend


# Below is the backend for the MCAD assembly extension.
class Arrange(BaseModel):
    """Provide arrange."""

    operation: str
    """Value for operation."""
    # Rotate parameters
    axis: str | None = "X"
    """Value for axis."""
    angle: str | None = "0deg"
    """Value for angle."""

    # Move parameters
    vector: list[str | int | float] | None = ["0mm", "0mm", "0mm"]
    """Value for vector."""

    class Config:
        extra = "forbid"


class Component(BaseModel):
    """Provide component."""

    component_type: str
    """Value for component type."""
    name: str
    """Value for name."""
    model: str
    """Value for model."""

    target_coordinate_system: str
    """Value for target coordinate system."""
    layout_coordinate_systems: list[str] | None = Field(default_factory=list)
    """Value for layout coordinate systems."""
    arranges: list[Arrange] = Field(default_factory=list)
    """Value for arranges."""
    sub_components: dict | None = Field(default_factory=dict)
    """Value for sub components."""
    password: str | None = None
    """Value for password."""

    # Mcad parameters
    geometry_parameters: dict[str, str | float | int] | None = None
    """Value for geometry parameters."""

    # Ecad parameters
    reference_coordinate_system: str = "Global"
    """Value for reference coordinate system."""

    # internal properties
    __rotate_index: int | None = 0

    class Config:
        extra = "forbid"

    @classmethod
    def _load(cls, name: str, data: dict) -> Component:
        sub_components = {name: cls._load(name, comp) for name, comp in data.get("sub_components", {}).items()}
        data_ = data.copy()
        data_["sub_components"] = sub_components
        data_["name"] = name
        return cls(**data_)

    def _assemble_sub_components(self, hfss, cs_prefix: str = ""):
        for name, comp in self.sub_components.items():
            comp.assemble(hfss, cs_prefix)

    def _apply_arrange(self, hfss: "Hfss"):
        for i in self.arranges:
            if i.operation == "rotate":
                self.__rotate_index = self.__rotate_index + 1
                hfss.modeler.rotate(self.name, getattr(Axis, i.axis), i.angle)
                hfss.modeler.oeditor.ChangeProperty(
                    [
                        "NAME:AllTabs",
                        [
                            "NAME:Geometry3DCmdTab",
                            ["NAME:PropServers", f"{self.name}:Rotate:{self.__rotate_index}"],
                            ["NAME:ChangedProps", ["NAME:Coordinate System", "Value:=", self.target_coordinate_system]],
                        ],
                    ]
                )
            elif i.operation == "move":
                hfss.modeler.move(self.name, i.vector)

    def assemble(self, hfss: "Hfss", cs_prefix: str | None = None):
        """Parameters
        ----------
         cs_prefix : str
            This is the name of the component definition.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> from ansys.aedt.core.extensions.hfss.mcad_assembly import COMPONENT_MODELS, Component
        >>> hfss = Hfss()
        >>> model_name = next(iter(COMPONENT_MODELS))
        >>> component = Component(
        ...     component_type="mcad", name="Bracket1", model=model_name, target_coordinate_system="Global"
        ... )
        >>> component.assemble(hfss)

        """
        if cs_prefix:
            self.target_coordinate_system = f"{cs_prefix}_{self.target_coordinate_system}"

        if self.component_type == "mcad":
            comp = hfss.modeler.insert_3d_component(
                name=self.name,
                input_file=COMPONENT_MODELS[self.model],
                coordinate_system=self.target_coordinate_system,
                password=self.password,
                geometry_parameters=self.geometry_parameters,
            )
            model_name = None
        else:
            model_path = COMPONENT_MODELS[self.model]
            self.model = generate_unique_name(self.model)
            hfss.modeler.add_layout_component_definition(file_path=model_path, name=self.model)
            comp = hfss.modeler._insert_layout_component_instance(
                name=self.name,
                definition_name=self.model,
                target_coordinate_system=self.target_coordinate_system,
                parameter_mapping=None,
                import_coordinate_systems=self.layout_coordinate_systems,
                reference_coordinate_system=self.reference_coordinate_system,
            )
            for new_name in list(hfss.modeler.oeditor.Get3DComponentPartNames(comp)):
                hfss.modeler._create_object(new_name)

            udm_obj = hfss.modeler._create_user_defined_component(comp)
            udm_obj.name = comp
            self.name = comp

            model_name = self.model

        if comp is False:
            raise ValueError(self.name, self.model, self.target_coordinate_system)

        self._apply_arrange(hfss)
        if self.sub_components:
            self._assemble_sub_components(hfss, cs_prefix=model_name)


Component.model_rebuild()

COMPONENT_MODELS = {}
"""Component models."""


class MCADAssemblyBackend(BaseModel):
    """Provide MCAD assembly backend."""

    coordinate_system: dict[str, dict[str, str | list[str]]] = Field(default_factory=dict)
    """Value for coordinate system."""
    layout_component_models: dict[str, str] = Field(default_factory=dict)
    """Value for layout component models."""
    component_models: dict[str, str] = Field(default_factory=dict)
    """Value for component models."""
    sub_components: dict[str, Component] = Field(default_factory=dict)
    """Value for sub components."""

    class Config:
        extra = "forbid"

    @classmethod
    def _load(cls, data: dict, cur_dir: str) -> "MCADAssemblyBackend":
        cur_dir = Path(cur_dir)

        for name, file_path in data.get("component_models", {}).items():
            if not Path(file_path).drive:
                data["component_models"][name] = str(cur_dir / file_path)
        for name, file_path in data.get("layout_component_models", {}).items():
            if not Path(file_path).drive:
                data["layout_component_models"][name] = str(cur_dir / file_path)

        return cls(
            coordinate_system=data.get("coordinate_system", {}),
            component_models=data.get("component_models", {}),
            layout_component_models=data.get("layout_component_models", {}),
            sub_components={name: Component._load(name, comp) for name, comp in data.get("assembly", {}).items()},
        )

    def _run(self, hfss: "Hfss"):
        for name, value in self.coordinate_system.items():
            hfss.modeler.create_coordinate_system(name=name, **value)

        COMPONENT_MODELS.update(self.layout_component_models)
        COMPONENT_MODELS.update(self.component_models)

        for name, comp in self.sub_components.items():
            comp.assemble(hfss)


# End of MCADAssemblyBackend

if __name__ == "__main__":  # pragma: no cover
    args = get_arguments()

    if not args["is_batch"]:
        temp = Path(tempfile.TemporaryDirectory(suffix=".ansys").name)
        temp.mkdir()
        extension: ExtensionCommon = MCADAssemblyFrontend(withdraw=False)
        extension.working_directory = temp
        tkinter.mainloop()
