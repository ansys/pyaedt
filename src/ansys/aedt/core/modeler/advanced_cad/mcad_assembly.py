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
from typing import Sequence
from typing import cast

import numpy as np
from pydantic import AliasChoices
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import PrivateAttr
from pydantic import model_validator
from pyedb import Edb

import ansys.aedt.core
from ansys.aedt.core.generic.constants import Axis
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.file_utils import read_toml
from ansys.aedt.core.generic.numbers_utils import decompose_variable_value

if TYPE_CHECKING:
    from ansys.aedt.core.hfss import Hfss

# Below is the backend for the MCAD assembly extension.


CONFIG_DICT = ConfigDict(extra="forbid", validate_assignment=True, populate_by_name=True)

OPERATIONS = Literal["move", "rotate"]


def get_all_ecads(cad: MCADAssembly | MCADComponent | ECADComponent) -> list[ECADComponent]:
    """Recursively collect all ECAD components from an assembly or component tree.

    Parameters
    ----------
    cad : MCADAssembly | MCADComponent | ECADComponent
        The assembly or component to traverse for ECAD components.

    Returns
    -------
    list[ECADComponent]
        Flat list of all ECAD components found in the hierarchy.

    """
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
    vector: Sequence[str | int | float] | None = Field(
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


class _EcadCompInfo(BaseModel):
    """Store resolved layout pin mapping data for a placed component.

    .. warning::
        This is an internal class used for internal assembly processing.
        It is not part of the public API and may change without notice.

    """

    model_config = CONFIG_DICT

    refdes: str | None = Field(default=None, description="Reference designator of the resolved layout component.")
    part_name: str | None = Field(default=None, description="Name of the part of the component.")
    cs_name: str | None = Field(default=None, description="Coordinate system created for the mapped component.")
    pin1_location: tuple[str | int | float, str | int | float] | None = Field(
        default=None, description="XY location of the first pin in the layout component."
    )
    flip: bool | None = Field(default=False, description="Whether the component must be flipped during placement.")
    thickness_offset: float | None = Field(
        default=None, description="Stackup thickness offset used when placing a flipped component."
    )
    lower_elevation: float | None = Field(default=None, description="Layer lower elevation.")
    upper_elevation: float | None = Field(default=None, description="Layer upper elevation.")
    rotation_rad: int | float | None = Field(
        default=0, description="Resolved in-plane rotation angle for the mapped component, in radians."
    )


class MCADComponent(BaseModel):
    """Describe a single MCAD or ECAD component instance in an assembly.

    This model represents a single component instance with its configuration,
    transformations, and nested subcomponents organized by type (MCAD or ECAD).
    Components can be placed in the assembly using coordinate systems and
    transformations, and can have child components to form hierarchies.

    Examples
    --------
    Create an MCAD component and configure placement:

    >>> comp = MCADComponent(name="connector", model="USB_Type_A")
    >>> comp.target_coordinate_system = "CS_1"
    >>> comp.add_arrange_rotate(axis="Z", angle="90deg")

    """

    @property
    def sub_components(self):
        """Return a combined dictionary of all child subcomponents.

        Provides a unified view of both ECAD and MCAD child components.
        When keys overlap, ECAD components take precedence.

        Returns
        -------
        dict[str, MCADComponent | ECADComponent]
            Dictionary combining ECAD and MCAD subcomponents. Keys are component
            instance names and values are the component objects. ECAD components
            override any MCAD components with the same key.

        """
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

    target_coordinate_system: str = Field(
        default="Global", description="Coordinate system where the component instance is inserted."
    )

    arranges: list[Arrange] = Field(
        default_factory=list,
        description="Ordered transformation operations applied after component insertion.",
    )
    password: str | None = Field(default=None, description="Password used to open protected 3D component files.")

    mcad_sub_components: dict[str, MCADComponent] = Field(
        default_factory=dict,
        description="List of 3D components aligned to this component in the hierarchy assembly.",
    )
    ecad_sub_components: dict[str, ECADComponent] = Field(
        default_factory=dict,
        description="List of layout components aligned to this component in the hierarchy assembly.",
    )

    # Mcad parameters
    geometry_parameters: dict[str, str | float | int] | None = Field(
        default=None, description="Geometry parameter overrides passed when inserting an MCAD component."
    )

    reference_coordinate_system: str = Field(
        default="Global",
        description="Reference coordinate system used as the handle",
    )

    # internal properties
    _rotate_index: int = PrivateAttr(default=0)

    @model_validator(mode="before")
    @classmethod
    def preprocess(cls, data):
        """Normalize and validate component configuration formats.

        This validator handles backward compatibility by automatically converting
        legacy component configuration formats. It merges the legacy 'assembly'
        and 'sub_components' keys into separate 'mcad_sub_components' and
        'ecad_sub_components' dictionaries based on the child component's
        ``component_type`` field.

        Parameters
        ----------
        data : dict
            Raw input data before model validation.

        Returns
        -------
        dict
            Normalized data with separated and categorized component types.

        Notes
        -----
        This method ensures that old configuration files using the 'assembly' or
        'sub_components' keys continue to work with the new component structure.
        Layout-specific fields are removed from MCAD components during normalization.

        """
        legacy_1 = data.pop("assembly", {})
        legacy_2 = data.pop("sub_components", {})
        legacy_1.update(legacy_2)

        data["mcad_sub_components"] = data.get("mcad_sub_components", {})
        data["ecad_sub_components"] = data.get("ecad_sub_components", {})

        for i, j in legacy_1.items():
            if j["component_type"] == "mcad":
                j.pop("layout_coordinate_systems", None)
                data["mcad_sub_components"][i] = j
            else:
                data["ecad_sub_components"][i] = j

        return data

    def add_sub_mcad_component(self, name: str, model: str) -> MCADComponent:
        """Add a child MCAD (3D) subcomponent.

        Create and register an MCAD (3D model) subcomponent as a child of this
        component. This creates a hierarchical relationship where the new component
        is subordinate to the current component in the assembly tree.

        Parameters
        ----------
        name : str
            Instance name for this child component.
        model : str
            Reference name of a registered MCAD model.

        Returns
        -------
        MCADComponent
            The created MCAD component instance, ready for configuration.

        Examples
        --------
        Add a connector subcomponent to a PCB component:

        >>> pcb = MCADComponent(name="main_pcb", model="PCB_Model")
        >>> connector = pcb.add_sub_mcad_component(
        ...     name="usb_connector", model="USB_TypeA"
        ... )
        >>> connector.target_coordinate_system = "USB_Mount_Point"

        """
        comp = MCADComponent(name=name, model=model)
        self.mcad_sub_components[name] = comp
        return comp

    def add_sub_ecad_component(self, name: str, model: str) -> ECADComponent:
        """Add a child ECAD (layout) subcomponent.

        Create and register an ECAD (layout/PCB) subcomponent as a child of this
        component. This creates a hierarchical relationship where the new component
        is subordinate to the current component in the assembly tree.

        Parameters
        ----------
        name : str
            Instance name for this child component.
        model : str
            Reference name of a registered ECAD model.

        Returns
        -------
        ECADComponent
            The created ECAD component instance, ready for configuration.

        Examples
        --------
        Add a secondary PCB layout as a child of a connector component:

        >>> connector = MCADComponent(name="connector", model="USB_Connector")
        >>> daughter_board = connector.add_sub_ecad_component(
        ...     name="daughter_pcb", model="DaughterBoard"
        ... )
        >>> daughter_board.target_coordinate_system = "Connector_CS"
        >>> daughter_board.layout_coordinate_systems = ["PCB_Origin"]

        """
        comp = ECADComponent(name=name, model=model)
        self.ecad_sub_components[name] = comp
        return comp

    def add_arrange_rotate(self, axis: str = "X", angle: str = "0deg") -> Arrange:
        """Add a rotation transformation to the component.

        Register a rotation operation to be applied to this component during
        assembly. Rotations are applied in the order they are added and use
        the component's target coordinate system as the reference.

        Parameters
        ----------
        axis : str, optional
            Axis of rotation. Valid values are ``"X"``, ``"Y"``, or ``"Z"``.
            The default is ``"X"``.
        angle : str, optional
            Rotation angle as an expression string (e.g., ``"90deg"``, ``"45deg"``).
            The default is ``"0deg"``.

        Returns
        -------
        Arrange
            The created rotation transformation object.

        Examples
        --------
        Rotate a component 90 degrees around the Z-axis:

        >>> comp.add_arrange_rotate(axis="Z", angle="90deg")

        """
        arrange = Arrange(operation="rotate", axis=axis, angle=angle)
        self.arranges.append(arrange)
        return arrange

    def add_arrange_move(self, vector: Sequence[str | int | float] = ("0mm", "0mm", "0mm")) -> Arrange:
        """Add a translation transformation to the component.

        Register a translation operation to be applied to this component during
        assembly. Translations are applied in the order they are added and are
        relative to the component's target coordinate system.

        Parameters
        ----------
        vector : Sequence[str | int | float], optional
            Translation vector as a sequence of three values [x, y, z] with units.
            Each value can be a string expression (e.g., ``"1mm"``, ``"0.5in"``)
            or a numeric value (interpreted as the system default unit).
            The default is ``("0mm", "0mm", "0mm")``.

        Returns
        -------
        Arrange
            The created translation transformation object.

        Examples
        --------
        Move a component 5mm in the X direction:

        >>> comp.add_arrange_move(vector=("5mm", "0mm", "0mm"))

        """
        arrange = Arrange(operation="move", vector=list(vector))
        self.arranges.append(arrange)
        return arrange


class ECADComponent(MCADComponent):
    """Describe an ECAD (PCB layout) component in an MCAD assembly.

    Extends ``MCADComponent`` with ECAD-specific properties for managing PCB layouts
    and their integration with 3D models. This class handles layout coordinate systems,
    library-based component population, and pin mapping for automatic placement of
    3D models based on PCB component references.

    Examples
    --------
    Create an ECAD component with layout coordinate systems:

    >>> pcb = ECADComponent(name="main_board", model="MainPCB")
    >>> pcb.layout_coordinate_systems = ["USB_Port", "Antenna_Mount"]
    >>> pcb.reference_coordinate_system = "PCB_Origin"

    Add 3D components from a library based on PCB reference designators:

    >>> pcb.add_sub_mcad_component_from_library(  # doctest: +SKIP
    ...     library_path="path/to/library",
    ...     reference_designators=["U1", "U2", "J1"]
    ... )

    """

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
    _ecad_comp_info: dict[str, _EcadCompInfo] = PrivateAttr(default_factory=dict)

    _mcad_component_from_library: list[str] = PrivateAttr(default_factory=list)

    def add_sub_mcad_component_from_library(
            self,
            library_path: str | Path | None = None,
            reference_designators: list[str] | None = None,
    ) -> None:
        """Register 3D component library entries for automatic assembly.

        Configure the ECAD component to populate 3D models from a library based on
        PCB reference designators. This enables automatic placement of 3D component
        models (such as 0805 resistors or BGA packages) at positions defined by
        their footprints in the PCB layout.

        Parameters
        ----------
        library_path : str | Path, optional
            Path to the library folder containing ``model_library.toml``. This file
            maps component part numbers/names to 3D model files and pin locations.
            If not provided, must have been set at the assembly level.
        reference_designators : list[str], optional
            List of reference designators from the PCB to include in automatic assembly.
            For example, ``["U1", "U2", "J1"]`` marks these components from the layout
            to be automatically populated with 3D models. If not provided, no components
            are marked for assembly (or all if ``assembly_all_from_library`` is enabled).

        Examples
        --------
        Add specific components from a library:

        >>> pcb = ECADComponent(name="main_board", model="MainPCB")
        >>> pcb.add_sub_mcad_component_from_library(  # doctest: +SKIP
        ...     library_path="/models/component_library",
        ...     reference_designators=["U1", "U2", "C1", "C2"]
        ... )

        Register library without specific designators (requires global library config):

        >>> pcb.add_sub_mcad_component_from_library(  # doctest: +SKIP
        ...     reference_designators=["IC1", "J1"]
        ... )

        """
        if library_path:
            self.model_libraries.append(str(library_path))

        if reference_designators:
            temp = reference_designators if isinstance(reference_designators, list) else [reference_designators]
            self._mcad_component_from_library.extend(temp)


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
    """Represent the full MCAD assembly configuration consumed by the backend.

    This model holds the complete configuration for an MCAD assembly including
    coordinate systems, component models, and the hierarchy of MCAD/ECAD components.
    It serves as the configuration object passed to the ``run()`` function to
    orchestrate the assembly process in HFSS.

    Examples
    --------
    Create a basic assembly with registered models:

    >>> from pathlib import Path
    >>> from ansys.aedt.core.modeler.advanced_cad.mcad_assembly import MCADAssembly
    >>> assembly = MCADAssembly()
    >>> assembly.add_mcad_component_model(  # doctest: +SKIP
    ...     name="connector", path="path/to/connector.a3dcomp"
    ... )
    >>> assembly.add_ecad_component_model(  # doctest: +SKIP
    ...     name="pcb", path="path/to/board.aedb"
    ... )
    >>> pcb = assembly.add_sub_ecad_component(name="pcb_1", model="pcb")

    """

    @property
    def sub_components(self):
        """Return a combined dictionary of all top-level subcomponents.

        Provides a unified view of both ECAD and MCAD subcomponents in the
        assembly. When keys overlap, ECAD components take precedence.

        Returns
        -------
        dict[str, MCADComponent | ECADComponent]
            Dictionary combining ECAD and MCAD subcomponents. Keys are component
            instance names and values are the component objects. ECAD components
            override any MCAD components with the same key.

        """
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
        description="Mapping of MCAD model library paths. Supports relative path to configure file.",
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
        """Normalize and validate component configuration formats.

        This validator handles backward compatibility by automatically converting
        legacy assembly configuration formats. It merges the legacy 'assembly' and
        'sub_components' keys into separate 'mcad_sub_components' and 'ecad_sub_components'
        dictionaries based on the component's ``component_type`` field.

        Parameters
        ----------
        data : dict
            Raw input data before model validation.

        Returns
        -------
        dict
            Normalized data with separated and categorized component types.

        Notes
        -----
        This method ensures that old configuration files using the 'assembly' or
        'sub_components' keys continue to work with the new component structure.

        """
        legacy_1 = data.pop("assembly", {})
        legacy_2 = data.pop("sub_components", {})
        legacy_1.update(legacy_2)

        data["mcad_sub_components"] = data.get("mcad_sub_components", {})
        data["ecad_sub_components"] = data.get("ecad_sub_components", {})

        for i, j in legacy_1.items():
            if j["component_type"] == "mcad":
                j.pop("layout_coordinate_systems", None)
                data["mcad_sub_components"][i] = j
            else:
                data["ecad_sub_components"][i] = j
        return data

    def add_mcad_component_model(self, name: str, path: str):
        """Register an MCAD component model.

        Add a named MCAD (3D) component model that can be referenced when
        instantiating components in the assembly. This is the first step in
        using a 3D component model - register it before creating instances.

        Parameters
        ----------
        name : str
            Model name used as a reference when adding components.
            Should be unique within the assembly configuration.
        path : str
            File path to the MCAD component file (e.g., ``.a3dcomp``, ``.step``).
            Can be absolute or relative to the configuration directory.

        Examples
        --------
        Register multiple MCAD models:

        >>> assembly = MCADAssembly()
        >>> assembly.add_mcad_component_model(
        ...     name="USB_Connector", path="models/connectors/usb_type_a.a3dcomp"
        ... )
        >>> assembly.add_mcad_component_model(
        ...     name="RF_Shield", path="models/shields/rf_cage.step"
        ... )

        Create instances from registered models:

        >>> connector = assembly.add_sub_mcad_component(
        ...     name="J1", model="USB_Connector"
        ... )

        """
        self.mcad_component_models[name] = path

    def add_ecad_component_model(self, name: str, path: str):
        """Register an ECAD component model.

        Add a named ECAD (layout/PCB) component model that can be referenced when
        instantiating components in the assembly. This is the first step in using
        a PCB layout - register it before creating instances.

        Parameters
        ----------
        name : str
            Model name used as a reference when adding components.
            Should be unique within the assembly configuration.
        path : str
            File path to the ECAD component file (e.g., ``.aedb``).
            Can be absolute or relative to the configuration directory.

        Examples
        --------
        Register PCB layout models:

        >>> assembly = MCADAssembly()
        >>> assembly.add_ecad_component_model(
        ...     name="MainBoard", path="pcb/main_assembly.aedb"
        ... )
        >>> assembly.add_ecad_component_model(
        ...     name="DaughterBoard", path="pcb/daughter_card.aedb"
        ... )

        Create instances from registered models:

        >>> main_pcb = assembly.add_sub_ecad_component(
        ...     name="PCB_1", model="MainBoard"
        ... )

        """
        self.ecad_component_models[name] = path

    def add_coordinate_system(self, name: str)->CoordinateSystem:
        """Create and register a new coordinate system.

        Define a coordinate system in the global reference frame that can be
        used as a placement target for components in the assembly. Coordinate
        systems serve as anchors for component placement and orientation.

        Parameters
        ----------
        name : str
            Unique name for the coordinate system. This name is used when
            assigning a component's ``target_coordinate_system``.

        Returns
        -------
        CoordinateSystem
            The created coordinate system object, positioned at the global origin
            and using the global coordinate system as its reference.

        Examples
        --------
        Create multiple coordinate systems for component placement:

        >>> assembly = MCADAssembly()
        >>> cs_main = assembly.add_coordinate_system(name="MainCS")
        >>> cs_connector = assembly.add_coordinate_system(name="Connector_Mount")
        >>> cs_antenna = assembly.add_coordinate_system(name="Antenna_Position")

        Use coordinate systems to place components:

        >>> pcb = assembly.add_sub_ecad_component(name="PCB_1", model="MainBoard")
        >>> pcb.target_coordinate_system = "MainCS"
        >>> connector = pcb.add_sub_mcad_component(
        ...     name="USB_Port", model="USB_Connector"
        ... )
        >>> connector.target_coordinate_system = "Connector_Mount"

        """
        cs = CoordinateSystem(name=name, reference_coordinate_system="Global")
        self.coordinate_system[name] = cs
        return cs

    def add_sub_mcad_component(self, name: str, model: str) -> MCADComponent:
        """Add a top-level MCAD (3D) subcomponent to the assembly.

        Create and register an MCAD (3D model) subcomponent instance at the
        top level of the assembly hierarchy. The component is ready for
        configuration including placement, transformations, and child components.

        Parameters
        ----------
        name : str
            Instance name for this component in the assembly.
            Must be unique within the assembly.
        model : str
            Reference name of a registered MCAD model (see ``add_mcad_component_model``).

        Returns
        -------
        MCADComponent
            The created MCAD component instance, ready for configuration.

        Examples
        --------
        Add top-level MCAD components to an assembly:

        >>> assembly = MCADAssembly()
        >>> assembly.add_mcad_component_model(
        ...     name="Enclosure", path="models/chassis.a3dcomp"
        ... )
        >>> assembly.add_mcad_component_model(
        ...     name="Antenna", path="models/antenna.step"
        ... )
        >>> enclosure = assembly.add_sub_mcad_component(
        ...     name="Case", model="Enclosure"
        ... )
        >>> antenna = assembly.add_sub_mcad_component(
        ...     name="ANT1", model="Antenna"
        ... )

        Configure the component after creation:

        >>> enclosure.target_coordinate_system = "MainCS"
        >>> enclosure.add_arrange_rotate(axis="Z", angle="45deg")

        """
        comp = MCADComponent(name=name, model=model)
        self.mcad_sub_components[name] = comp
        return comp

    def add_sub_ecad_component(self, name: str, model: str) -> ECADComponent:
        """Add a top-level ECAD (layout) subcomponent to the assembly.

        Create and register an ECAD (layout/PCB) subcomponent instance at the
        top level of the assembly hierarchy. The component is ready for
        configuration including coordinate systems, transformations, and child
        components.

        Parameters
        ----------
        name : str
            Instance name for this component in the assembly.
            Must be unique within the assembly.
        model : str
            Reference name of a registered ECAD model (see ``add_ecad_component_model``).

        Returns
        -------
        ECADComponent
            The created ECAD component instance, ready for configuration.

        Examples
        --------
        Add top-level PCB layout components to an assembly:

        >>> assembly = MCADAssembly()
        >>> assembly.add_ecad_component_model(
        ...     name="MainBoard", path="pcb/main.aedb"
        ... )
        >>> assembly.add_ecad_component_model(
        ...     name="DaughterBoard", path="pcb/daughter.aedb"
        ... )
        >>> main_pcb = assembly.add_sub_ecad_component(
        ...     name="PCB_1", model="MainBoard"
        ... )
        >>> daughter_pcb = assembly.add_sub_ecad_component(
        ...     name="PCB_2", model="DaughterBoard"
        ... )

        Configure the component with layout-specific settings:

        >>> main_pcb.target_coordinate_system = "MainCS"
        >>> main_pcb.layout_coordinate_systems = ["USB_Mount", "Antenna_Base"]
        >>> main_pcb.reference_coordinate_system = "PCB_Origin"

        """
        comp = ECADComponent(name=name, model=model)
        self.ecad_sub_components[name] = comp
        return comp

    def add_model_library(self, library_path: str | Path):
        """Register a model library for component resolution.

        Add a library path that contains a ``model_library.toml`` file. This file
        defines mappings from component reference designators to 3D component models,
        enabling automatic population of MCAD components from ECAD layouts.
        Libraries provide a centralized way to manage component-to-model relationships.

        Parameters
        ----------
        library_path : str | Path
            Path to the library folder containing ``model_library.toml``. Can be
            an absolute path or relative to the configuration file location.
            The ``model_library.toml`` file should map component part numbers/
            designators to 3D model files and pin location information.

        Examples
        --------
        Register model libraries at the assembly level:

        >>> assembly = MCADAssembly()
        >>> assembly.add_model_library(
        ...     library_path="/project/component_libraries/standard"
        ... )
        >>> assembly.add_model_library(
        ...     library_path="/project/component_libraries/custom"
        ... )

        Use with ECAD components for automatic population:

        >>> pcb = assembly.add_sub_ecad_component(
        ...     name="PCB_1", model="MainBoard"
        ... )
        >>> pcb.add_sub_mcad_component_from_library(  # doctest: +SKIP
        ...     reference_designators=["U1", "U2", "J1", "J2"]
        ... )

        Notes
        -----
        Libraries registered at the assembly level are available to all components.
        Individual components can also register their own libraries if needed.
        The component reference designators must match those in the ``model_library.toml``
        mapping.

        """
        self.model_libraries.append(str(library_path))


class MCADAssemblyService:
    """Manage the execution of an MCAD assembly inside HFSS.

    This service handles the preprocessing, staging, and assembly of an MCAD
    assembly configuration into an active HFSS design.

    """

    def __init__(
            self,
            config: MCADAssembly,
            project_dir: Path,
            model_dir: Path | None,
            app: Hfss | None,
    ):
        """Initialize the MCAD assembly service.

        Parameters
        ----------
        config : MCADAssembly
            The assembly configuration to execute.
        project_dir : Path
            Output directory for the assembly project.
        model_dir : Path, optional
            Base directory for resolving relative model paths.
        app : Hfss, optional
            Active HFSS instance. If ``None``, a new instance is created.

        """
        self.config = config.model_copy(deep=True)
        self.project_dir = project_dir
        self.model_dir = model_dir
        self.hfss = app
        self._temp_model_dir = self.project_dir / "models"
        self._temp_model_dir.mkdir(parents=True, exist_ok=True)

        self._runtime_mcad_models = {}
        self._runtime_ecad_models = {}
        self.runtime_comp_lib_models = {}

        self.version = self.hfss.desktop_class.aedt_version_id if self.hfss else None

    @staticmethod
    def _resolve_model_path(path: str | Path, model_dir: Path | None) -> Path:
        """Resolve a model path, handling both absolute and relative paths.

        Parameters
        ----------
        path : str | Path
            The model path to resolve.
        model_dir : Path, optional
            Base directory for relative path resolution.

        Returns
        -------
        Path
            Resolved absolute path to the model.

        """
        source_path = Path(path)
        if source_path.is_absolute():
            return source_path
        if model_dir is None:
            raise ValueError("model_dir must be provided when using relative model paths.")
        return model_dir / source_path

    def execute(self):
        """Execute the complete MCAD assembly workflow.

        Orchestrates preprocessing, model staging, and assembly into HFSS.

        """
        self.pre_process_config()
        self.stage_models()
        self.assemble()

    def pre_process_config(self):
        """Preprocess the assembly configuration.

        Elevates library paths, resolves ECAD component information from EDB files,
        and auto-populates MCAD components from library definitions when enabled.

        """
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
            if not aedb.endswith(".aedb"):
                continue

            edb = Edb(aedb, version=self.version)
            if ecad.assembly_all_from_library:
                edb_components = edb.components.instances
            else:
                edb_components = {
                    ref: j for ref, j in edb.components.instances.items() if ref in ecad._mcad_component_from_library
                }
            for ref, obj in edb_components.items():
                ecad_comp_info = _EcadCompInfo(refdes=ref, cs_name=None)
                pins = obj.pins
                if not pins:
                    continue
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

                ecad_comp_info.part_name = obj.component_definition.part_name
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
                if info.part_name is None:
                    continue

                if info.part_name in self.runtime_comp_lib_models.keys():
                    model_info = self.runtime_comp_lib_models[info.part_name]
                    self._runtime_mcad_models[info.part_name] = model_info["model_path"]
                    c = ecad.add_sub_mcad_component(name=ref, model=info.part_name)
                    c.use_pin_mapping = True
                    pin_mapping = c.placement_pin_mapping
                    if pin_mapping is None:
                        raise ValueError(f"No placement pin mapping initialized for {ref}.")
                    pin_mapping.reference_designator = ref
                    pin_1_loc = model_info.get("pin_1_loc")
                    if pin_1_loc is not None:
                        pin_mapping.pin_1_loc = cast(
                            tuple[str | int | float, str | int | float, str | int | float], tuple(pin_1_loc)
                        )
                    pin_2_loc = model_info.get("pin_2_loc")
                    if pin_2_loc is not None:
                        pin_mapping.pin_2_loc = cast(
                            tuple[str | int | float, str | int | float, str | int | float], tuple(pin_2_loc)
                        )

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
        hfss = self.hfss
        if hfss is None:
            raise ValueError("HFSS application instance is required to assemble the MCAD model.")

        modeler: Any = hfss.modeler
        for name, value in self.config.coordinate_system.items():
            value.name = name
            value_ = value.model_dump()
            value_["reference_cs"] = value_.pop("reference_coordinate_system", None)
            modeler.create_coordinate_system(**value_)

        temp = self.config.sub_components

        def assemble_sub_components(
                cad: ECADComponent | MCADComponent,
                ecad_com_info: dict[str, _EcadCompInfo],
                cs_prefix: str | None = None,
        ):
            if cad.component_type == "mcad":
                if cad.use_pin_mapping:
                    pin_mapping = cad.placement_pin_mapping
                    if pin_mapping is None:
                        raise ValueError(f"Pin mapping required for MCAD component '{cad.name}'.")
                    refdes = pin_mapping.reference_designator
                    if refdes is None:
                        raise ValueError(f"Pin mapping reference designator is missing for component '{cad.name}'.")
                    cad.target_coordinate_system = f"{refdes}_"
                    pin_1_loc = pin_mapping.pin_1_loc
                    if pin_1_loc is None:
                        raise ValueError(f"Pin 1 location is missing for component '{cad.name}'.")
                    cad.arranges.append(Arrange(operation="move", vector=list(pin_1_loc)))

                    if pin_mapping.pin_2_loc is not None:
                        dx, dy = np.array(pin_mapping.pin_2_loc[:2]) - np.array(pin_1_loc[:2])
                        angle_rad = np.arctan2(dy, dx)
                    else:
                        angle_rad = 0
                    cad.arranges.append(Arrange(operation="rotate", axis="Z", angle=f"{-np.degrees(angle_rad):.0f}deg"))

                    if refdes in ecad_com_info:
                        comp_info = ecad_com_info[refdes]

                        if comp_info.flip:
                            cad.arranges.append(Arrange(operation="rotate", axis="X", angle="180deg"))
                            thickness_offset = comp_info.thickness_offset
                            if thickness_offset is not None:
                                cad.arranges.append(
                                    Arrange(operation="move", vector=[0, 0, f"{-thickness_offset}meter"])
                                )
                            rotation = -comp_info.rotation_rad if comp_info.rotation_rad is not None else 0
                        else:
                            rotation = comp_info.rotation_rad if comp_info.rotation_rad is not None else 0
                        cad.arranges.append(
                            Arrange(operation="rotate", axis="Z", angle=f"{np.degrees(rotation):.0f}deg")
                        )

                if cs_prefix:
                    cad.target_coordinate_system = f"{cs_prefix}_{cad.target_coordinate_system}"
                model_path = self._runtime_mcad_models[cad.model]
                if not Path(model_path).exists():
                    raise FileNotFoundError(f"{model_path} does not exist")

                _comp = modeler.insert_3d_component(
                    name=cad.name,
                    input_file=model_path,
                    coordinate_system=cad.target_coordinate_system,
                    password=cad.password,
                    geometry_parameters=cad.geometry_parameters or {},
                )
                model_name = None
            else:
                if not isinstance(cad, ECADComponent):  # pragma: no cover
                    raise TypeError("Unsupported component type.")
                model_path = self._runtime_ecad_models[cad.model]
                cad.model = generate_unique_name(cad.model)

                comps = []
                for j in cad.mcad_sub_components.values():
                    if j.use_pin_mapping:
                        pin_mapping = j.placement_pin_mapping
                        if pin_mapping is not None:
                            comps.append(pin_mapping.reference_designator)
                comps = [ref for ref in comps if ref is not None]
                if comps:
                    cad.layout_coordinate_systems = cad.layout_coordinate_systems or []
                    edb = Edb(model_path, version=self.version)
                    for refdes, obj in edb.components.instances.items():
                        if refdes in comps:
                            obj.enabled = False

                            pins = obj.pins
                            pin_names = list(pins.keys())
                            p1_name = sorted(pin_names)[0]
                            p1_loc = pins[p1_name].position
                            cs_name = f"{refdes}_"
                            edb.modeler.insert_coordinate_system(
                                name=cs_name, x=p1_loc[0], y=p1_loc[1], layer=obj.placement_layer
                            )
                            cad.layout_coordinate_systems.append(cs_name)

                    edb.save()
                    edb.close()

                _comp = modeler.insert_layout_component(
                    input_file=model_path,
                    coordinate_system=cad.target_coordinate_system,
                    name=cad.name,
                    parameter_mapping=False,
                    layout_coordinate_systems=cad.layout_coordinate_systems or [],
                    reference_coordinate_system=cad.reference_coordinate_system,
                )
                model_name = _comp.definition_name
                cad.name = _comp.name

                hfss.save_project()

            if _comp is False:
                raise ValueError(cad.name, cad.model, cad.target_coordinate_system)

            # self.hfss.logger.reset_timer()

            for i in cad.arranges:
                if i.operation == "rotate":
                    cad._rotate_index += 1
                    axis = i.axis or "Z"
                    angle = i.angle or "0deg"
                    angle, units = decompose_variable_value(angle)
                    hfss.modeler.rotate(cad.name, getattr(Axis, axis), angle, units)

                    # It is more efficient changing the property with ChangeProperty than with the SetPropValue
                    hfss.modeler.oeditor.ChangeProperty(
                        [
                            "NAME:AllTabs",
                            [
                                "NAME:Geometry3DCmdTab",
                                ["NAME:PropServers", f"{cad.name}:Rotate:{cad._rotate_index}"],
                                [
                                    "NAME:ChangedProps",
                                    ["NAME:Coordinate System", "Value:=", cad.target_coordinate_system],
                                ],
                            ],
                        ]
                    )

                elif i.operation == "move":
                    hfss.modeler.move(cad.name, list(i.vector or ["0mm", "0mm", "0mm"]))

            # self.hfss.logger.info_timer(f"Perform arranges for component {_comp.name}.")

            for i in cad.sub_components.values():
                if isinstance(cad, ECADComponent):
                    comp_info = cad._ecad_comp_info
                else:
                    comp_info = {}
                assemble_sub_components(i, cs_prefix=model_name, ecad_com_info=comp_info)

        for _name, comp in temp.items():
            assemble_sub_components(comp, ecad_com_info=dict(), cs_prefix=None)


def run(
        config_data: MCADAssembly | dict | str | Path,
        project_dir: str | None = None,
        model_dir: str | None = None,
        version: str | None = None,
        port: int | None = None,
        aedt_process_id: int | None = None,
        student_version: bool = False,
        app: Hfss | None = None,
) -> str:
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
    app : ansys.aedt.core.hfss.Hfss, optional
        Existing HFSS instance to reuse instead of creating a new session.

    Returns
    -------
    str
        Path to the directory containing the generated AEDT project.

    Examples
    --------

    >>> hfss = Hfss(version="2026.1")
    >>> run(config_data="config_2.json", app=hfss)
    >>> hfss.release_desktop(
    ...     close_desktop=False, close_projects=False
    ... )

    """
    if isinstance(config_data, MCADAssembly):
        config = config_data
    else:
        if isinstance(config_data, str | Path):
            with open(config_data, "r") as f:
                config_data = json.load(f)
        config = MCADAssembly.model_validate(config_data)

    project_dir_path = Path(tempfile.mkdtemp(prefix="mcad_assembly_")) if project_dir is None else Path(project_dir)
    model_dir_path = Path(model_dir) if model_dir else Path.cwd()

    if app is None:
        ng = True
        app = ansys.aedt.core.Hfss(
            project=str(project_dir_path / "assembly.aedt"),
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
        project_dir=project_dir_path,
        model_dir=model_dir_path,
        app=app,
    )
    service.execute()
    if ng:
        app.save_project()
        app.logger.info(f"Project saved to {project_dir_path}")
        app.release_desktop()
    return str(project_dir_path)
