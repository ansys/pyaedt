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
from pathlib import Path
import shutil
import tempfile
from typing import TYPE_CHECKING
from typing import Any
from typing import Literal
from typing import cast

import numpy as np
from pydantic import AliasChoices, model_validator
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import PrivateAttr
from pyedb import Edb

import ansys.aedt.core
from ansys.aedt.core.generic.constants import Axis
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.file_utils import read_toml

if TYPE_CHECKING:
    from ansys.aedt.core.hfss import Hfss

# Below is the backend for the MCAD assembly extension.


CONFIG_DICT = ConfigDict(extra="forbid", validate_assignment=True, populate_by_name=True)

OPERATIONS = Literal["move", "rotate"]


def get_all_ecads(cad: MCADAssembly| MCADComponent | ECADComponent) -> list[ECADComponent]:
    temp = []

    def elevate_lib(sub_comp: ECADComponent | MCADComponent):
        if isinstance(sub_comp, ECADComponent):
            temp.append(sub_comp)
        temp.extend(get_all_ecads(sub_comp))

    for i in cad.mcad_sub_components.values():
        elevate_lib(i)
    for i in cad.ecad_sub_components.values():
        elevate_lib(i)

    return temp


class Arrange(BaseModel):
    """Define a transformation applied while assembling a component."""

    model_config = CONFIG_DICT

    operation: OPERATIONS = Field(..., description="Transformation type to apply to the component.")
    # Rotate parameters
    axis: str | None = Field(default="X", description="Axis used for rotation operations.")
    angle: str | None = Field(default="0deg", description="Rotation angle expression used for rotate operations.")

    # Move parameters
    vector: list[str | int | float] | None = Field(
        default_factory=lambda: ["0mm", "0mm", "0mm"],
        description="Translation vector used for move operations.",
    )


COMPONENT_TYPE = Literal["ecad", "mcad"]


class PlacementPinMapping(BaseModel):
    """Store placement pin mapping information for a component."""

    model_config = CONFIG_DICT

    reference_designator: str | None = Field(
        default=None, description="Reference designator of the component footprint in the layout."
    )
    pin_1_loc: tuple[str | int | float, str | int | float, str | int | float] | None = Field(
        default=None, description="Location of pin 1 in the 3D component."
    )
    pin_2_loc: tuple[str | int | float, str | int | float, str | int | float] | None = Field(
        default=None, description="Location of pin 2 in the 3D component."
    )

class EcadCompInfo(BaseModel):
    """Store resolved layout pin mapping data for a placed component. Internal use only."""

    model_config = CONFIG_DICT

    refdes: str | None = Field(
        default=None, description="Reference designator of the resolved layout component."
    )
    part_name: str | None = Field(default=None, description="Name of the part of the component.")
    cs_name: str | None = Field(default=None, description="Coordinate system created for the mapped component.")
    pin1_location: tuple[str | int | float, str | int | float] | None = Field(
        default=None, description="XY location of the first pin in the layout component."
    )
    flip: bool | None = Field(
        default=False, description="Whether the component must be flipped during placement."
    )
    thickness_offset: float | None = Field(
        default=None, description="Stackup thickness offset used when placing a flipped component."
    )
    lower_elevation: float | None = Field(default=None, description="Layer lower elevation.")
    upper_elevation: float | None = Field(default=None, description="Layer upper elevation.")
    rotation_rad: int | float | None = Field(
        default=0, description="Resolved in-plane rotation angle for the mapped component, in radians."
    )


class MCADComponent(BaseModel):
    """Describe an MCAD or ECAD component included in an MCAD assembly."""

    @property
    def sub_components(self):
        temp = {}
        temp.update(self.ecad_sub_components)
        temp.update(self.mcad_sub_components)
        return temp

    model_config = CONFIG_DICT

    component_type: COMPONENT_TYPE | None = Field(
        default="mcad", description="Type of component to insert into the assembly."
    )
    name: str = Field(default="", description="Instance name of the component in the assembly.")
    model: str = Field(..., description="Model definition name used to resolve the component file.")

    use_pin_mapping: bool = Field(
        default=False, description="Whether layout pin mapping should drive component placement."
    )
    placement_pin_mapping: PlacementPinMapping | None = Field(
        default_factory=PlacementPinMapping,
        description="Pin mapping inputs used to place the component from layout reference data.",
    )

    target_coordinate_system: str | None = Field(
        default="Global", description="Coordinate system where the component instance is inserted."
    )

    arranges: list[Arrange] = Field(
        default_factory=list,
        description="Ordered transformation operations applied after component insertion.",
    )
    password: str | None = Field(default=None, description="Password used to open protected 3D component files.")

    mcad_sub_components: dict[str, MCADComponent] = Field(
        default_factory=dict,
        description="Top-level components that make up the MCAD assembly.",
    )
    ecad_sub_components: dict[str, ECADComponent] = Field(
        default_factory=dict,
        description="Top-level components that make up the MCAD assembly.",
    )

    # Mcad parameters
    geometry_parameters: dict[str, str | float | int] | None = Field(
        default=None, description="Geometry parameter overrides passed when inserting an MCAD component."
    )

    # Ecad parameters
    reference_coordinate_system: str | None = Field(
        default="Global",
        description="Reference coordinate system used when importing an ECAD component definition.",
    )

    # internal properties
    _rotate_index: int = PrivateAttr(default=0)

    @model_validator(mode="before")
    @classmethod
    def preprocess(cls, data):
        legacy_1 = data.pop("assembly", {})
        legacy_2 = data.pop("sub_components", {})
        legacy_1.update(legacy_2)

        data["mcad_sub_components"] = data.get("mcad_sub_components", {})
        data["ecad_sub_components"] = data.get("ecad_sub_components", {})

        for i, j in legacy_1.items():
            if j.component_type == "mcad":
                data["mcad_sub_components"][i] = j
            else:
                data["ecad_sub_components"][i] = j
        return data

    def _assemble_sub_components(self, hfss, cs_prefix: str | None = "", version: str | None = None):
        for _name, comp in self.sub_components.items():
            if comp.use_pin_mapping:
                pin_mapping_info = self._ecad_comp_info[comp.placement_pin_mapping.reference_designator]
            else:
                pin_mapping_info = None
            comp._assemble(hfss, cs_prefix, version, pin_mapping_info=pin_mapping_info)

    def _apply_arrange(self, hfss: "Hfss"):
        for i in self.arranges:
            if i.operation == "rotate":
                self._rotate_index += 1
                axis = i.axis or "Z"
                angle = i.angle or "0deg"
                hfss.modeler.rotate(self.name, getattr(Axis, axis), angle)
                hfss.modeler.oeditor.ChangeProperty(
                    [
                        "NAME:AllTabs",
                        [
                            "NAME:Geometry3DCmdTab",
                            ["NAME:PropServers", f"{self.name}:Rotate:{self._rotate_index}"],
                            ["NAME:ChangedProps", ["NAME:Coordinate System", "Value:=", self.target_coordinate_system]],
                        ],
                    ]
                )
            elif i.operation == "move":
                hfss.modeler.move(self.name, i.vector or ["0mm", "0mm", "0mm"])

    def add_sub_mcad_component(self, name: str, model: str) -> MCADComponent:
        """Add sub 3D component."""
        comp = MCADComponent(name=name, model=model)
        self.mcad_sub_components[name] = comp
        return comp

    def add_sub_ecad_component(self, name: str, model: str) -> ECADComponent:
        """Add sub 3D layout component."""
        comp = ECADComponent(name=name, model=model)
        self.ecad_sub_components[name] = comp
        return comp

    def add_arrange_rotate(self, axis: str = "X", angle: str = "0deg") -> Arrange:
        """Add a rotation arrange operation.

        Parameters
        ----------
        axis : str, optional
            Rotation axis. The default is ``"X"``.
        angle : str, optional
            Rotation angle expression. The default is ``"0deg"``.

        Returns
        -------
        Arrange
            Added arrange operation.

        """
        arrange = Arrange(operation="rotate", axis=axis, angle=angle)
        self.arranges.append(arrange)
        return arrange

    def add_arrange_move(self, vector: list[str | int | float] = ("0mm", "0mm", "0mm")) -> Arrange:
        """Add a translation arrange operation.

        Parameters
        ----------
        vector : list[str | int | float], optional
            Translation vector. The default is ``("0mm", "0mm", "0mm")``.

        Returns
        -------
        Arrange
            Added arrange operation.

        """
        arrange = Arrange(operation="move", vector=list(vector))
        self.arranges.append(arrange)
        return arrange

    def _assemble(
        self,
        hfss: "Hfss",
        cs_prefix: str | None = None,
        version: str | None = None,
        pin_mapping_info: EcadCompInfo | None = None,
    ):
        """Assemble the component into an HFSS design.

        Parameters
        ----------
        hfss : ansys.aedt.core.hfss.Hfss
            HFSS application instance used for geometry insertion.
        cs_prefix : str, optional
            Prefix applied to the target coordinate system name when inserting
            nested components.
        version : str, optional
            AEDT version used when opening EDB-backed layout components.
        pin_mapping_info : PinMapping, optional
            Resolved placement information used for pin-mapped components.

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
            self.arranges.append(Arrange(operation="rotate", axis="Z", angle=f"{-np.degrees(angle_rad):.0f}deg"))

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

        model_path = self._top_assembly._runtime_mcad_models[self.model]
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
                            pin_mapping.pin1_location = (p1_loc[0], p1_loc[1])
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
                            self._ecad_comp_info[refdes] = pin_mapping

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


class ECADComponent(MCADComponent):
    """Describe an MCAD or ECAD component included in an MCAD assembly."""
    component_type: COMPONENT_TYPE | None = Field(
        default="ecad", description="Type of component to insert into the assembly."
    )

    layout_coordinate_systems: list[str] | None = Field(
        default_factory=list,
        description="Coordinate systems imported from an ECAD layout component definition.",
    )
    assembly_all_from_library: bool = Field(default=False)

    model_libraries: list[str] = Field(default_factory=list)

    # internal properties
    _ecad_comp_info: dict[str, EcadCompInfo] = PrivateAttr(default_factory=dict)

    _mcad_component_from_library: list[str] = PrivateAttr(default_factory=list)

    def add_sub_mcad_component_from_library(
            self,
            library_path:str|Path|None=None,
            reference_designators:list[str] | None=None,
    ) -> None:
        """Add 3D subcomponents from a model library.

        Parameters
        ----------
        library_path : str
            Path to the library folder containing ``model_library.toml``.

        """
        if library_path:
            self.model_libraries.append(str(library_path))

        if reference_designators:
            temp = reference_designators if isinstance(reference_designators, list) else [reference_designators]
            self._mcad_component_from_library.extend(temp)


        # models = read_toml(Path(library_path) / "model_library.toml")
        #
        # for comp_def, item in models.items():
        #     if comp_def not in self._top_assembly._library_component_models:
        #         path = str(Path(library_path) / item["model_path"])
        #         self._top_assembly._library_component_models[comp_def] = path
        #
        # edb = Edb(self._top_assembly.layout_component_models[self.model])
        # for name_def, comp_def in edb.definitions.components.items():
        #     if name_def not in models:
        #         continue
        #     for comp in comp_def.components:
        #         a3d_comp = self.add_sub_mcad_component(name=comp, model=name_def)
        #         a3d_comp.password = models[name_def].get("password")
        #         a3d_comp.use_pin_mapping = True
        #         a3d_comp.placement_pin_mapping.reference_designator = comp
        #         a3d_comp.placement_pin_mapping.pin_1_loc = models[name_def].get("pin_1_loc")
        #         a3d_comp.placement_pin_mapping.pin_2_loc = models[name_def].get("pin_2_loc")
        # edb.close()

class CoordinateSystem(BaseModel):
    """Define a coordinate system entry for an MCAD assembly."""

    model_config = CONFIG_DICT

    origin: list[str] | None = Field(
        default_factory=lambda: ["0mm", "0mm", "0mm"],
        description="Origin of the coordinate system expressed as XYZ values.",
    )
    reference_coordinate_system: str | None = Field(
        default="Global",
        validation_alias=AliasChoices("reference_coordinate_system", "reference_cs"),
        description="Parent coordinate system used to define this coordinate system.",
    )
    name: str | None = Field(default=None, description="Name assigned to the coordinate system in HFSS.")


class MCADAssembly(BaseModel):
    """Represent the full MCAD assembly configuration consumed by the backend."""
    @property
    def sub_components(self):
        temp = {}
        temp.update(self.ecad_sub_components)
        temp.update(self.mcad_sub_components)
        return temp

    model_config = CONFIG_DICT

    coordinate_system: dict[str, CoordinateSystem] = Field(
        default_factory=dict,
        description="Coordinate system definitions available to the assembly.",
    )
    ecad_component_models: dict[str, str] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("ecad_component_models", "layout_component_models"),
        description="Mapping of ECAD model names to their source file paths.",
    )
    mcad_component_models: dict[str, str] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("mcad_component_models", "component_models"),
        description="Mapping of MCAD model names to their source file paths.",
    )
    model_libraries: list[str] = Field(
        default_factory=list,
        description="Mapping of MCAD model library paths.",
    )

    mcad_sub_components: dict[str, MCADComponent] = Field(
        default_factory=dict,
        description="Top-level components that make up the MCAD assembly.",
    )
    ecad_sub_components: dict[str, ECADComponent] = Field(
        default_factory=dict,
        description="Top-level components that make up the MCAD assembly.",
    )

    @model_validator(mode="before")
    @classmethod
    def preprocess(cls, data):
        legacy_1 = data.pop("assembly", {})
        legacy_2 = data.pop("sub_components", {})
        legacy_1.update(legacy_2)

        data["mcad_sub_components"] = data.get("mcad_sub_components", {})
        data["ecad_sub_components"] = data.get("ecad_sub_components", {})

        for i, j in legacy_1.items():
            if j.component_type == "mcad":
                data["mcad_sub_components"][i] = j
            else:
                data["ecad_sub_components"][i] = j
        return data


    # @classmethod
    # def _load(cls, data: dict) -> "MCADAssembly":
    #     obj = cls(
    #         coordinate_system=data.get("coordinate_system", {}),
    #         component_models=data.get("component_models", {}),
    #         layout_component_models=data.get("layout_component_models", {}),
    #         sub_components={name: Component._load(name, comp) for name, comp in data.get("sub_components", {}).items()},
    #     )
    #     return obj


    def add_mcad_component_model(self, name: str, path: str):
        """Add component model."""
        self.mcad_component_models[name] = path

    def add_ecad_component_model(self, name: str, path: str):
        """Add component model."""
        self.ecad_component_models[name] = path

    def add_coordinate_system(self, name: str):
        """Add coordinate system."""
        cs = CoordinateSystem(name=name, reference_coordinate_system="Global")
        self.coordinate_system[name] = cs
        return cs

    def add_sub_mcad_component(self, name: str, model: str) -> MCADComponent:
        """Add sub component."""
        comp = MCADComponent(name=name, model=model)
        self.mcad_sub_components[name] = comp
        return comp

    def add_sub_ecad_component(self, name: str, model: str) -> ECADComponent:
        """Add sub component."""
        comp = ECADComponent(name=name, model=model)
        self.ecad_sub_components[name] = comp
        return comp

    def add_model_library(self, library_path: str | Path):
        """Add a model library path."""
        self.model_libraries.append(str(library_path))


class MCADAssemblyService:
    """Manage the execution of an MCAD assembly inside HFSS."""

    def __init__(
        self,
        config: MCADAssembly,
        project_dir: Path,
        model_dir: Path | None,
        hfss: Hfss | None,
    ):
        self.config = config.model_copy(deep=True)
        self.project_dir = project_dir
        self.model_dir = model_dir
        self.hfss = hfss
        self._temp_model_dir = self.project_dir / "models"
        self._temp_model_dir.mkdir(parents=True, exist_ok=True)

        self._runtime_mcad_models = {}
        self._runtime_ecad_models = {}
        self.runtime_comp_lib_models = {}

        self.version = self.hfss.desktop_class.aedt_version_id if self.hfss else None


    @staticmethod
    def _resolve_model_path(path: str | Path, model_dir: Path | None) -> Path:
        source_path = Path(path)
        return source_path if source_path.is_absolute() else model_dir / source_path

    def execute(self):
        self.pre_process_config()
        self.stage_models()
        self.assemble()

    def pre_process_config(self):

        all_ecad = get_all_ecads(self.config)
        # Elevates library path to MCADAssembly level so that it can be used to resolve component models.
        for i in all_ecad:
            self.config.model_libraries.extend(i.model_libraries)

        for i in self.config.model_libraries:
            for i2, j2 in read_toml(Path(i) / "model_library.toml").items():
                j2["model_path"] = Path(i) / j2["model_path"]
                self.runtime_comp_lib_models[i2] = j2

        # Get all component information from ecad
        for ecad in all_ecad:
            aedb = self.config.ecad_component_models[ecad.model]

            edb = Edb(aedb, version=self.version)
            if ecad.assembly_all_from_library:
                edb_components = edb.components.instances
            else:
                edb_components = {ref: j for ref, j in edb.components.instances.items() if ref in ecad._mcad_component_from_library}
            for ref, obj in edb_components.items():
                ecad_comp_info = EcadCompInfo(refdes=ref,cs_name=None)
                pins = obj.pins
                pin_names = list(pins.keys())
                p1_name = sorted(pin_names)[0]
                p1_loc = pins[p1_name].position
                ecad_comp_info.pin1_location = (p1_loc[0], p1_loc[1])

                signal_layers = list(edb.stackup.signal_layers)
                ecad_comp_info.flip = (
                    True if signal_layers.index(obj.placement_layer) > len(signal_layers) / 2 else False
                )
                ecad_comp_info.thickness_offset = edb.stackup.signal_layers[obj.placement_layer].thickness

                if len(pin_names) > 1:
                    p2_name = sorted(pin_names)[1]
                    p2_loc = pins[p2_name].position

                    dx, dy = np.array(p2_loc) - np.array(p1_loc)
                    angle_rad = np.arctan2(dy, dx)
                    ecad_comp_info.rotation_rad = angle_rad

                ecad_comp_info.part_name = obj.component_def.part_name
                layer_obj = edb.stackup.layers[obj.placement_layer]
                ecad_comp_info.lower_elevation = layer_obj.lower_elevation
                ecad_comp_info.upper_elevation = layer_obj.upper_elevation
                ecad._ecad_comp_info[ref] = ecad_comp_info

            edb.close()

        self._runtime_ecad_models.update(self.config.ecad_component_models)
        self._runtime_mcad_models.update(self.config.mcad_component_models)
        for ecad in all_ecad:
            for ref, info in ecad._ecad_comp_info.items():
                if not ecad.assembly_all_from_library and ref not in ecad._mcad_component_from_library:
                    continue

                if info.part_name in self.runtime_comp_lib_models.keys():
                    model_info = self.runtime_comp_lib_models[info.part_name]
                    self._runtime_mcad_models[info.part_name] = model_info["model_path"]
                    c = ecad.add_sub_mcad_component(name=ref, model=info.part_name)
                    c.use_pin_mapping = True
                    c.placement_pin_mapping.reference_designator = ref
                    c.placement_pin_mapping.pin_1_loc = model_info.get("pin_1_loc")
                    c.placement_pin_mapping.pin_2_loc = model_info.get("pin_2_loc")


    def stage_models(self) -> None:
        """Stage model files into the run-specific working directory."""

        for name, path in self._runtime_ecad_models.items():
            source_path = self._resolve_model_path(path, self.model_dir)
            if source_path.suffix == ".aedb":
                temp_path = shutil.copytree(source_path, self._temp_model_dir / source_path.name)
            else:
                temp_path = shutil.copy(source_path, self._temp_model_dir)
            self._runtime_ecad_models[name] = str(temp_path)

        for name, path in self._runtime_mcad_models.items():
            source_path = self._resolve_model_path(path, self.model_dir)
            shutil.copy(source_path, self._temp_model_dir)
            self._runtime_mcad_models[name] = str(self._temp_model_dir / source_path.name)

    def assemble(self) -> None:
        """Execute the full MCAD assembly workflow."""
        for name, value in self.config.coordinate_system.items():
            value.name = name
            value_ = value.model_dump()
            value_["reference_cs"] = value_.pop("reference_coordinate_system", None)
            self.hfss.modeler.create_coordinate_system(**value_)

        temp = self.config.sub_components

        def assemble_sub_components(
                cad: ECADComponent|MCADComponent,
                cs_prefix: str | None = None,
                ecad_com_info: list[EcadCompInfo] | None = None,
        ):


            if cad.component_type == "mcad":
                if cad.use_pin_mapping:
                    cad.target_coordinate_system = cad.placement_pin_mapping.reference_designator + "_"
                    _temp = cad.placement_pin_mapping
                    cad.arranges.append(Arrange(operation="move", vector=list(_temp.pin_1_loc)))

                    if _temp.pin_2_loc is not None:
                        dx, dy = np.array(_temp.pin_2_loc[:2]) - np.array(_temp.pin_1_loc[:2])
                        angle_rad = np.arctan2(dy, dx)
                    else:
                        angle_rad = 0
                    cad.arranges.append(
                        Arrange(operation="rotate", axis="Z", angle=f"{-np.degrees(angle_rad):.0f}deg"))

                    comp_info = ecad_com_info[cad.placement_pin_mapping.reference_designator]

                    if comp_info and comp_info.flip:
                        cad.arranges.append(Arrange(operation="rotate", axis="X", angle="180deg"))
                        cad.arranges.append(
                            Arrange(operation="move", vector=[0, 0, f"{-comp_info.thickness_offset}meter"]))
                        rotation = -comp_info.rotation_rad
                    else:
                        rotation = comp_info.rotation_rad
                    cad.arranges.append(Arrange(operation="rotate", axis="Z", angle=f"{np.degrees(rotation):.0f}deg"))

                if cs_prefix:
                    cad.target_coordinate_system = f"{cs_prefix}_{cad.target_coordinate_system}"
                model_path = self._runtime_mcad_models[cad.model]
                if not Path(model_path).exists():
                    raise FileNotFoundError(f"{model_path} does not exist")
                _comp = self.hfss.modeler.insert_3d_component(
                    name=cad.name,
                    input_file=model_path,
                    coordinate_system=cad.target_coordinate_system,
                    password=cad.password,
                    geometry_parameters=cad.geometry_parameters,
                )
                model_name = None
            else:

                model_path = self._runtime_ecad_models[cad.model]
                cad.model = generate_unique_name(cad.model)

                comps = [
                    j.placement_pin_mapping.reference_designator
                    for i, j in cad.mcad_sub_components.items()
                    if j.use_pin_mapping
                ]
                if comps:
                    edb = Edb(model_path, version=self.version)
                    for refdes, obj in edb.components.instances.items():
                        if refdes in comps:
                            obj.enabled = False
                            cs_name = refdes + "_"
                            pins = obj.pins
                            pin_names = list(pins.keys())
                            p1_name = sorted(pin_names)[0]
                            p1_loc = pins[p1_name].position

                            edb.modeler.insert_coordinate_system(
                                name=cs_name, x=p1_loc[0], y=p1_loc[1], layer=obj.placement_layer
                            )
                            cad.layout_coordinate_systems.append(cs_name)

                    edb.save()
                    edb.close()

                self.hfss.modeler.add_layout_component_definition(file_path=model_path, name=cad.model)
                _comp = self.hfss.modeler._insert_layout_component_instance(
                    name=cad.name,
                    definition_name=cad.model,
                    target_coordinate_system=cad.target_coordinate_system,
                    parameter_mapping=None,
                    import_coordinate_systems=cad.layout_coordinate_systems,
                    reference_coordinate_system=cad.reference_coordinate_system,
                )
                for new_name in list(self.hfss.modeler.oeditor.Get3DComponentPartNames(_comp)):
                    self.hfss.modeler._create_object(new_name)

                udm_obj = self.hfss.modeler._create_user_defined_component(_comp)
                udm_obj.name = _comp
                cad.name = _comp

                model_name = cad.model

            if _comp is False:
                raise ValueError(cad.name, cad.model, cad.target_coordinate_system)

            for i in cad.arranges:
                if i.operation == "rotate":
                    cad._rotate_index += 1
                    axis = i.axis or "Z"
                    angle = i.angle or "0deg"
                    self.hfss.modeler.rotate(cad.name, getattr(Axis, axis), angle)
                    self.hfss.modeler.oeditor.ChangeProperty(
                        [
                            "NAME:AllTabs",
                            [
                                "NAME:Geometry3DCmdTab",
                                ["NAME:PropServers", f"{cad.name}:Rotate:{cad._rotate_index}"],
                                ["NAME:ChangedProps",
                                 ["NAME:Coordinate System", "Value:=", cad.target_coordinate_system]],
                            ],
                        ]
                    )
                elif i.operation == "move":
                    self.hfss.modeler.move(cad.name, i.vector or ["0mm", "0mm", "0mm"])

            for i in cad.sub_components.values():
                comp_info = cad._ecad_comp_info if cad.component_type == "ecad" else None
                assemble_sub_components(i, cs_prefix=model_name, ecad_com_info=comp_info)

        for _name, comp in temp.items():
            assemble_sub_components(comp)


def run(
    config_data: MCADAssembly | dict | str | Path,
    project_dir: str = None,
    model_dir: str = None,
    version: str = None,
    port: int = None,
    aedt_process_id: int = None,
    student_version: bool = False,
    hfss: Hfss=None,
):
    """Build an MCAD assembly in HFSS from a configuration.

    Parameters
    ----------
    config_data : dict | str | pathlib.Path
        Assembly configuration dictionary or path to a JSON configuration file.
    project_dir : str, optional
        Output directory for the generated AEDT project. When omitted, a
        temporary directory is created.
    model_dir : str, optional
        Base directory used to resolve relative model paths from the
        configuration.
    version : str, optional
        AEDT version to use. When omitted, the active configured version is
        used.
    port : int, optional
        gRPC port of an existing AEDT session.
    aedt_process_id : int, optional
        Process identifier of an existing AEDT session.
    student_version : bool, optional
        Whether to connect to a student version of AEDT.
    hfss : ansys.aedt.core.hfss.Hfss, optional
        Existing HFSS instance to reuse instead of creating a new session.

    Returns
    -------
    None

    """
    if isinstance(config_data, MCADAssembly):
        config = config_data
    else:
        if isinstance(config_data, str | Path):
            with open(config_data, "r") as f:
                config_data = json.load(f)
        config = MCADAssembly.model_validate(config_data)

    project_dir = Path(tempfile.mkdtemp(prefix="mcad_assembly_")) if not project_dir else Path(project_dir)
    model_dir = Path(model_dir) if model_dir else None

    if hfss is None:
        ng = True
        hfss = ansys.aedt.core.Hfss(
            project=str(project_dir / "assembly.aedt"),
            version=version,
            port=port,
            aedt_process_id=aedt_process_id,
            student_version=student_version,
            non_graphical=ng,
        )
    else:
        ng = False

    service = MCADAssemblyService(
        config=config,
        project_dir=project_dir,
        model_dir=model_dir,
        hfss=hfss,
    )
    service.execute()
    if ng:
        hfss.save_project()
        hfss.release_desktop()
        hfss.logger.info(f"Project saved to {project_dir}")
