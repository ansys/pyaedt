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

import json
import os
from pathlib import Path
import tempfile
import tkinter
from tkinter import filedialog
from tkinter import ttk
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

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


# Frontend
class AedtInfo(BaseModel):
    version: str = ""
    port: int
    aedt_process_id: Union[int, None]
    student_version: bool = False


class MCADAssemblyFrontend(ExtensionHFSSCommon):
    EXTENSION_TITLE = "MCAD Assembly"
    GRID_PARAMS = {"padx": 15, "pady": 10, "sticky": "nsew"}
    PACK_PARAMS = {"padx": 15, "pady": 10}

    tab_frame_main = None

    config_data: dict = dict()

    def __init__(self, withdraw: bool = False):
        self.aedt_info = AedtInfo(
            port=get_port(), version=get_aedt_version(), aedt_process_id=get_process_id(), student_version=is_student()
        )

        super().__init__(
            self.EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=True,
            toggle_row=2,
            toggle_column=0,
        )

    def add_toggle_theme_button(self, parent, toggle_row, toggle_column):
        return

    def add_toggle_theme_button_(self, parent):
        """Create a button to toggle between light and dark themes."""
        button_frame = ttk.Frame(
            parent, style="PyAEDT.TFrame", relief=tkinter.SUNKEN, borderwidth=2, name="theme_button_frame"
        )
        button_frame.pack(fill="both", expand=False, **{"padx": 5, "pady": 5})

        ttk.Button(
            button_frame,
            width=10,
            text="Run",
            command=lambda: self.run(self.config_data),
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

    def add_extension_content(self):
        self.root.geometry("700x600")

        menubar = tkinter.Menu(self.root)
        self.root.config(menu=menubar)

        nb = ttk.Notebook(self.root, name="notebook", style="PyAEDT.TNotebook")
        self.tab_frame_main = ttk.Frame(nb, name="main", style="PyAEDT.TFrame")

        nb.add(self.tab_frame_main, text="Main")

        nb.pack(fill="both", expand=True)

        create_tab_main(self.tab_frame_main, self)
        self.add_toggle_theme_button_(self.root)

    def run(self, config_data):
        hfss = ansys.aedt.core.Hfss(**self.aedt_info.model_dump())
        app = MCADAssemblyBackend.load(data=config_data)
        app.run(hfss)
        del app

        if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
            hfss.desktop_class.release_desktop(False, False)
        else:
            hfss.close_project(save=False)
        return


# create main tab
def create_tab_main(tab_frame, master):
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


def load_dict(tree, master):
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
            for name, file_path in data.get("component_models", {}).items():
                if not Path(file_path).drive:
                    data["component_models"][name] = str(local_path.parent / file_path)
            for name, file_path in data.get("layout_component_models", {}).items():
                if not Path(file_path).drive:
                    data["layout_component_models"][name] = str(local_path.parent / file_path)
            master.config_data = data
    tree.delete(*tree.get_children())  # clear everything

    for key in ["coordinate_system", "component_models", "layout_component_models"]:
        temp = tree.insert("", "end", text=key, open=False)
        for key, value in master.config_data.get(key, {}).items():
            text = f"{key}: {value}"
            tree.insert(temp, "end", text=text, open=False)

    node3 = tree.insert("", "end", text=str("assembly"), open=False)
    insert_items(tree, node3, master.config_data.get("assembly", {}))


def insert_items(tree, parent, dictionary):
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
    operation: str
    # Rotate parameters
    axis: Optional[str] = "X"
    angle: Optional[str] = "0deg"

    # Move parameters
    vector: Optional[list[Union[str, int, float]]] = ["0mm", "0mm", "0mm"]

    class Config:
        extra = "forbid"


class Component(BaseModel):
    component_type: str
    name: str
    model: str

    target_coordinate_system: str
    layout_coordinate_systems: Optional[List[str]] = Field(default_factory=list)
    arranges: List[Arrange] = Field(default_factory=list)
    sub_components: Optional[Dict] = Field(default_factory=dict)
    password: str = None

    # Mcad parameters
    geometry_parameters: Optional[Dict[str, Union[str, float, int]]] = None

    # Ecad parameters
    reference_coordinate_system: str = "Global"

    # internal properties
    __rotate_index: Optional[int] = 0

    class Config:
        extra = "forbid"

    @classmethod
    def load(cls, name, data):
        sub_components = {name: cls.load(name, comp) for name, comp in data.get("sub_components", {}).items()}
        data_ = data.copy()
        data_["sub_components"] = sub_components
        data_["name"] = name
        return cls(**data_)

    def assemble_sub_components(self, hfss, cs_prefix=""):
        for name, comp in self.sub_components.items():
            comp.assemble(hfss, cs_prefix)

    def apply_arrange(self, hfss):
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

    def assemble(self, hfss, cs_prefix=None):
        """
        Parameters
        ----------
         cs_prefix : str
            This is the name of the component definition.
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

        self.apply_arrange(hfss)
        if self.sub_components:
            self.assemble_sub_components(hfss, cs_prefix=model_name)


Component.model_rebuild()

COMPONENT_MODELS = {}


class MCADAssemblyBackend(BaseModel):
    coordinate_system: Dict[str, Dict[str, Union[str, List[str]]]] = Field(default_factory=dict)
    layout_component_models: Dict[str, str] = Field(default_factory=dict)
    component_models: Dict[str, str] = Field(default_factory=dict)
    sub_components: Dict[str, Component] = Field(default_factory=dict)

    class Config:
        extra = "forbid"

    @classmethod
    def load(cls, data):
        return cls(
            coordinate_system=data.get("coordinate_system", {}),
            component_models=data.get("component_models", {}),
            layout_component_models=data.get("layout_component_models", {}),
            sub_components={name: Component.load(name, comp) for name, comp in data.get("assembly", {}).items()},
        )

    def run(self, hfss):
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
