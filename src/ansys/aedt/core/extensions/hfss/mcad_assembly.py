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
import shutil
import tempfile
import tkinter
from tkinter import filedialog
from tkinter import ttk
from typing import TYPE_CHECKING
from typing import Any
from typing import Literal
from typing import cast

import numpy as np
from pydantic import AliasChoices
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pyedb import Edb

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
from ansys.aedt.core.generic.file_utils import read_toml

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

CONFIG_DICT = ConfigDict(extra="forbid", validate_assignment=True, populate_by_name=True)


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

    local_path: Path | str = ""
    """Path to local."""
    config_data: dict = dict()
    """Value for config data."""

    def __init__(self, withdraw: bool = False) -> None:

        super().__init__(
            self.EXTENSION_TITLE,
            withdraw=withdraw,
            add_custom_content=True,
            toggle_row=2,
            toggle_column=0,
        )

    def add_toggle_theme_button(self, parent: tkinter.Misc, toggle_row: int, toggle_column: int) -> None:
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
        button_frame.pack(fill="both", expand=False, padx=5, pady=5)

        ttk.Button(
            button_frame,
            width=10,
            text="Run",
            command=lambda: run(self.config_data, model_dir=self.local_path),
            style="PyAEDT.TButton",
            name="run",
        ).pack(anchor="w", side="left", padx=15, pady=10)

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
        change_theme_button.pack(anchor="e", side="right", padx=15, pady=10)
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


# create main tab
def create_tab_main(tab_frame: tkinter.Widget, master: MCADAssemblyFrontend) -> None:
    """Create tab main."""
    tree = ttk.Treeview(tab_frame, name="tree")
    tree.pack(
        expand=True,
        fill="both",
        padx=master.PACK_PARAMS["padx"],
        pady=master.PACK_PARAMS["pady"],
    )

    ttk.Button(
        tab_frame,
        # width=10,
        text="Load Configure File",
        command=lambda: load_dict(tree, master),
        style="PyAEDT.TButton",
        name="load",
    ).pack(anchor="w", padx=master.PACK_PARAMS["padx"], pady=master.PACK_PARAMS["pady"])


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

    temp = master.config_data.get("assembly", {})
    if not temp:
        temp = master.config_data.get("sub_components", {})
    insert_items(tree, node3, temp)


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
OPERATIONS = Literal["move", "rotate"]


class Arrange(BaseModel):
    """Provide arrange."""

    model_config = CONFIG_DICT

    operation: OPERATIONS
    """Value for operation."""
    # Rotate parameters
    axis: str | None = "X"
    """Value for axis."""
    angle: str | None = "0deg"
    """Value for angle."""

    # Move parameters
    vector: list[str | int | float] | None = ["0mm", "0mm", "0mm"]
    """Value for vector."""


COMPONENT_TYPE = Literal["ecad", "mcad"]


class PlacementPinMapping(BaseModel):
    model_config = CONFIG_DICT

    reference_designator: str | None = None
    pin_1_loc: tuple[str | int | float, str | int | float, str | int | float] | None = None
    pin_2_loc: tuple[str | int | float, str | int | float, str | int | float] | None = None


class Component(BaseModel):
    """Provide component."""

    model_config = CONFIG_DICT

    class PinMapping(BaseModel):
        model_config = CONFIG_DICT

        refdes: str | None = None
        cs_name: str | None = None
        """Value for refdes."""
        pin1_location: tuple[str | int | float, str | int | float] | None = None
        flip: bool | None = False
        thickness_offset: float | None = None
        rotation_rad: int | float | None = 0

    component_type: COMPONENT_TYPE | None = Field("mcad")
    """Value for component type."""
    name: str = ""
    """Value for name."""
    model: str
    """Value for model."""

    use_pin_mapping: bool = False
    placement_pin_mapping: PlacementPinMapping | None = Field(default_factory=PlacementPinMapping)
    __pin_mapping_info: dict[str, PinMapping] | None = {}

    target_coordinate_system: str | None = "Global"
    """Value for target coordinate system."""
    layout_coordinate_systems: list[str] | None = Field(default_factory=list)
    """Value for layout coordinate systems."""
    arranges: list[Arrange] = Field(default_factory=list)
    """Value for arranges."""
    sub_components: dict[str, "Component"] = Field(default_factory=dict)
    """Value for sub components."""
    password: str | None = None
    """Value for password."""

    # Mcad parameters
    geometry_parameters: dict[str, str | float | int] | None = None
    """Value for geometry parameters."""

    # Ecad parameters
    reference_coordinate_system: str | None = "Global"
    """Value for reference coordinate system."""

    # internal properties
    __rotate_index: int | None = 0

    _top_assembly: MCADAssemblyBackend | None = None

    @classmethod
    def _load(cls, name: str, data: dict) -> Component:
        sub_components = {name: cls._load(name, comp) for name, comp in data.get("sub_components", {}).items()}
        data_ = data.copy()
        data_["sub_components"] = sub_components
        data_["name"] = name
        return cls(**data_)

    def _assemble_sub_components(self, hfss, cs_prefix: str | None = "", version: str | None = None):
        for _name, comp in self.sub_components.items():
            if comp.use_pin_mapping:
                pin_mapping_info = self.__pin_mapping_info[comp.placement_pin_mapping.reference_designator]
            else:
                pin_mapping_info = None
            comp.assemble(hfss, cs_prefix, version, pin_mapping_info=pin_mapping_info)

    def _apply_arrange(self, hfss: "Hfss"):
        for i in self.arranges:
            if i.operation == "rotate":
                self.__rotate_index += 1
                axis = i.axis or "X"
                angle = i.angle or "0deg"
                hfss.modeler.rotate(self.name, getattr(Axis, axis), angle)
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
                hfss.modeler.move(self.name, i.vector or ["0mm", "0mm", "0mm"])

    def add_sub_mcad_component(self, name: str, model: str) -> Component:
        """Add sub component."""
        comp = Component(name=name, model=model, component_type="mcad")
        comp._top_assembly = self._top_assembly
        self.sub_components[name] = comp
        return comp

    def add_sub_ecad_component(self, name: str, model: str) -> Component:
        """Add sub component."""
        comp = Component(name=name, model=model, component_type="ecad")
        comp._top_assembly = self._top_assembly
        self.sub_components[name] = comp
        return comp

    def add_sub_mcad_component_from_library(self, library_path):
        """Add sub component."""

        models = read_toml(Path(library_path) / "model_library.toml")

        for comp_def, item in models.items():
            if comp_def not in COMPONENT_MODELS_:
                path = str(Path(library_path) / item["model_path"])
                COMPONENT_MODELS_[comp_def] = path

        edb = Edb(self._top_assembly.layout_component_models[self.model])
        for name_def, comp_def in edb.definitions.components.items():
            if name_def not in models:
                continue
            for comp in comp_def.components:
                a3d_comp = self.add_sub_mcad_component(name=comp, model=name_def)
                a3d_comp.use_pin_mapping = True
                a3d_comp.placement_pin_mapping.reference_designator = comp
                a3d_comp.placement_pin_mapping.pin_1_loc = models[name_def].get("pin_1_loc")
                a3d_comp.placement_pin_mapping.pin_2_loc = models[name_def].get("pin_2_loc")
        edb.close()

    def assemble(
        self,
        hfss: "Hfss",
        cs_prefix: str | None = None,
        version: str | None = None,
        pin_mapping_info: PinMapping | None = None,
    ):
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
        modeler = cast(Any, hfss.modeler)

        if self.use_pin_mapping:
            self.target_coordinate_system = self.placement_pin_mapping.reference_designator + "_"
            temp = self.placement_pin_mapping
            self.arranges.append(Arrange(operation="move", vector=list(temp.pin_1_loc)))

            if temp.pin_2_loc is not None:
                dx, dy = np.array(temp.pin_2_loc[:2]) - np.array(temp.pin_1_loc[:2])
                angle_rad = np.arctan2(dy, dx)
            else:
                angle_rad = 0
            self.arranges.append(Arrange(operation="rotate", axis="X", angle=f"{-np.degrees(angle_rad):.0f}deg"))

            comp_cs = pin_mapping_info

            if comp_cs and comp_cs.flip:
                self.arranges.append(Arrange(operation="rotate", axis="X", angle="180deg"))
                self.arranges.append(Arrange(operation="move", vector=[0, 0, f"{-comp_cs.thickness_offset}meter"]))
                rotation = -comp_cs.rotation_rad
            else:
                rotation = comp_cs.rotation_rad
            self.arranges.append(Arrange(operation="rotate", axis="Z", angle=f"{np.degrees(rotation):.0f}deg"))

        if cs_prefix:
            self.target_coordinate_system = f"{cs_prefix}_{self.target_coordinate_system}"

        model_path = COMPONENT_MODELS[self.model]
        if not Path(model_path).exists():
            raise FileNotFoundError(f"{model_path} does not exist")
        if self.component_type == "mcad":
            # a3dcomp
            comp = modeler.insert_3d_component(
                name=self.name,
                input_file=model_path,
                coordinate_system=self.target_coordinate_system,
                password=self.password,
                geometry_parameters=self.geometry_parameters,
            )
            model_name = None

        else:
            if Path(model_path).suffix == ".aedb":
                comps = [
                    j.placement_pin_mapping.reference_designator
                    for i, j in self.sub_components.items()
                    if j.use_pin_mapping
                ]
                if comps:
                    edb = Edb(model_path, version=version)
                    for refdes, obj in edb.components.instances.items():
                        if refdes in comps:
                            obj.enabled = False
                            cs_name = refdes + "_"
                            pin_mapping = Component.PinMapping(refdes=refdes, cs_name=cs_name)
                            pins = obj.pins
                            pin_names = list(pins.keys())
                            p1_name = sorted(pin_names)[0]
                            p1_loc = pins[p1_name].position

                            edb.modeler.insert_coordinate_system(
                                name=cs_name, x=p1_loc[0], y=p1_loc[1], layer=obj.placement_layer
                            )
                            self.layout_coordinate_systems.append(cs_name)
                            pin_mapping.pin1_location = tuple(p1_loc)
                            signal_layers = list(edb.stackup.signal_layers)
                            pin_mapping.flip = (
                                True if signal_layers.index(obj.placement_layer) > len(signal_layers) / 2 else False
                            )
                            pin_mapping.thickness_offset = edb.stackup.signal_layers[obj.placement_layer].thickness

                            if len(pin_names) > 1:
                                p2_name = sorted(pin_names)[1]
                                p2_loc = pins[p2_name].position

                                dx, dy = np.array(p2_loc) - np.array(p1_loc)
                                angle_rad = np.arctan2(dy, dx)
                                pin_mapping.rotation_rad = angle_rad
                            self.__pin_mapping_info[refdes] = pin_mapping

                    edb.save()
                    edb.close(terminate_rpc_session=False)

            self.model = generate_unique_name(self.model)
            modeler.add_layout_component_definition(file_path=model_path, name=self.model)
            comp = modeler._insert_layout_component_instance(
                name=self.name,
                definition_name=self.model,
                target_coordinate_system=self.target_coordinate_system,
                parameter_mapping=None,
                import_coordinate_systems=self.layout_coordinate_systems,
                reference_coordinate_system=self.reference_coordinate_system,
            )
            for new_name in list(modeler.oeditor.Get3DComponentPartNames(comp)):
                modeler._create_object(new_name)

            udm_obj = modeler._create_user_defined_component(comp)
            udm_obj.name = comp
            self.name = comp

            model_name = self.model

        if comp is False:
            raise ValueError(self.name, self.model, self.target_coordinate_system)

        self._apply_arrange(hfss)
        if self.sub_components:
            self._assemble_sub_components(hfss, cs_prefix=model_name, version=version)


Component.model_rebuild()

COMPONENT_MODELS = {}
COMPONENT_MODELS_ = {}  #
"""Component models."""
PCB_COORDINATES = {}


class CoordinateSystem(BaseModel):
    model_config = CONFIG_DICT

    origin: list[str] | None = ["0mm", "0mm", "0mm"]
    reference_coordinate_system: str | None = Field(
        "Global", validation_alias=AliasChoices("reference_coordinate_system", "reference_cs")
    )
    name: str | None = None


class MCADAssemblyBackend(BaseModel):
    """Provide MCAD assembly backend."""

    model_config = CONFIG_DICT

    coordinate_system: dict[str, CoordinateSystem] = Field(default_factory=dict)
    """Value for coordinate system."""
    layout_component_models: dict[str, str] = Field(default_factory=dict)
    """Value for layout component models."""
    component_models: dict[str, str] = Field(default_factory=dict)
    """Value for component models."""
    sub_components: dict[str, Component] = Field(
        default_factory=dict, validation_alias=AliasChoices("sub_components", "assembly")
    )
    """Value for sub components."""

    @classmethod
    def _load(cls, data: dict) -> "MCADAssemblyBackend":
        return cls(
            coordinate_system=data.get("coordinate_system", {}),
            component_models=data.get("component_models", {}),
            layout_component_models=data.get("layout_component_models", {}),
            sub_components={name: Component._load(name, comp) for name, comp in data.get("sub_components", {}).items()},
        )

    def add_mcad_component_model(self, name: str, path: str):
        """Add component model."""
        self.component_models[name] = path

    def add_ecad_component_model(self, name: str, path: str):
        """Add component model."""
        self.layout_component_models[name] = path

    def add_coordinate_system(self, name: str):
        """Add coordinate system."""
        cs = CoordinateSystem(name=name)
        self.coordinate_system[name] = cs
        return cs

    def add_sub_mcad_component(self, name: str, model: str) -> Component:
        """Add sub component."""
        comp = Component(name=name, model=model, component_type="mcad")
        comp._top_assembly= self
        self.sub_components[name] = comp
        return comp

    def add_sub_ecad_component(self, name: str, model: str) -> Component:
        """Add sub component."""
        comp = Component(name=name, model=model, component_type="ecad")
        comp._top_assembly = self
        self.sub_components[name] = comp
        return comp


def run(
    config_data: dict | str | Path,
    project_dir: str = None,
    model_dir: str = None,
    version: str = None,
    port: int = None,
    aedt_process_id: int = None,
    student_version: bool = False,
    hfss=None,
):
    if isinstance(config_data, str | Path):
        with open(config_data, "r") as f:
            config_data = json.load(f)

    if not project_dir:
        project_dir = Path(tempfile.mkdtemp(prefix="mcad_assembly_"))
    else:
        project_dir = Path(project_dir)
    temp_model_dir = project_dir / "models"
    temp_model_dir.mkdir(parents=True, exist_ok=True)

    app = MCADAssemblyBackend._load(data=config_data)

    version = version if version else get_aedt_version()
    if hfss is None:
        hfss = ansys.aedt.core.Hfss(
            project=str(project_dir / "assembly.aedt"),
            version=version,
            port=port if port else get_port(),
            aedt_process_id=aedt_process_id if aedt_process_id else get_process_id(),
            student_version=student_version if student_version else is_student(),
        )

    model_dir = Path(model_dir) if model_dir else None

    # models added in add_mcad_component_from_library
    for i, j in COMPONENT_MODELS_.items():
        if i in COMPONENT_MODELS:
            continue
        path = Path(j)
        shutil.copy(path, temp_model_dir)
        COMPONENT_MODELS[i] = str(temp_model_dir / path.name)

    for name, path in app.layout_component_models.items():
        path = Path(path) if Path(path).drive else model_dir / Path(path)
        if path.suffix == ".aedb":
            temp_path = shutil.copytree(path, temp_model_dir / path.name)
        else:
            temp_path = shutil.copy(path, temp_model_dir)
        COMPONENT_MODELS[name] = str(temp_path)

    for name, path in app.component_models.items():
        path = Path(path) if Path(path).drive else model_dir / Path(path)
        shutil.copy(path, temp_model_dir)
        COMPONENT_MODELS[name] = str(temp_model_dir / path.name)

    for name, value in app.coordinate_system.items():
        value.name = name
        value_ = value.model_dump()
        value_["reference_cs"] = value_.pop("reference_coordinate_system", None)
        hfss.modeler.create_coordinate_system(**value_)

    for name, comp in app.sub_components.items():
        comp.assemble(hfss, version=version)

    if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
        hfss.desktop_class.release_desktop(False, False)


# End of MCADAssemblyBackend

if __name__ == "__main__":  # pragma: no cover
    args = get_arguments()

    if not args["is_batch"]:
        temp = Path(tempfile.TemporaryDirectory(suffix=".ansys").name)
        temp.mkdir()
        extension: ExtensionCommon = MCADAssemblyFrontend(withdraw=False)
        cast(Any, extension).working_directory = temp
        tkinter.mainloop()
