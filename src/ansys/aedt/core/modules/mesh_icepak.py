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

from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import cast

from ansys.aedt.core.application import _get_obj_data
from ansys.aedt.core.application import _has_get_obj_data
from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.data_handlers import _dict2arg
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.general_methods import SetupDict
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.props import Props as MeshProps
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modeler.cad.elements_3d import BinaryTreeNode
from ansys.aedt.core.modules.mesh import MeshOperation

if TYPE_CHECKING:
    from ansys.aedt.core.application.analysis_icepak import FieldAnalysisIcepak
    from ansys.aedt.core.generic.protocols import _OMeshDesign
    from ansys.aedt.core.generic.protocols import _OMeshModule
    from ansys.aedt.core.generic.protocols import _OMeshTypedObject


UserSpecifiedSettings = dict(
    {
        "Enable": True,
        "MeshMethod": "MesherHD",
        "UserSpecifiedSettings": True,
        "MaxElementSizeX": "0.04mm",
        "MaxElementSizeY": "0.03mm",
        "MaxElementSizeZ": "0.015mm",
        "MinElementsInGap": "3",
        "MinElementsOnEdge": "2",
        "MaxSizeRatio": "2",
        "NoOGrids": False,
        "EnableMLM": True,
        "EnforeMLMType": "3D",
        "MaxLevels": "0",
        "BufferLayers": "0",
        "UniformMeshParametersType": "Average",
        "StairStepMeshing": False,
        "2DMLMType": "2DMLM_None",
        "MinGapX": "0.08mm",
        "MinGapY": "0.06mm",
        "MinGapZ": "0.03mm",
        "Objects": ["Settings_SubRegion"],
        "ProximitySizeFunction": True,
        "CurvatureSizeFunction": True,
        "EnableTransition": False,
        "OptimizePCBMesh": True,
        "Enable2DCutCell": False,
        "EnforceCutCellMeshing": False,
        "Enforce2dot5DCutCell": False,
        "NonHDMesherEnabled": False,
    }
)
"""Value for UserSpecifiedSettings."""

GeneralSettings = dict(
    {
        "Enable": True,
        "MeshMethod": "MesherHD",
        "UserSpecifiedSettings": False,
        "MeshRegionResolution": 3,
        "GeometryBasedMeshing": False,
        "MinGapX": "0.08mm",
        "MinGapY": "0.06mm",
        "MinGapZ": "0.03mm",
        "Objects": ["Settings_SubRegion"],
        "ProximitySizeFunction": True,
        "CurvatureSizeFunction": True,
        "EnableTransition": False,
        "OptimizePCBMesh": True,
        "Enable2DCutCell": False,
        "EnforceCutCellMeshing": False,
        "Enforce2dot5DCutCell": False,
        "NonHDMesherEnabled": False,
    }
)
"""Value for GeneralSettings."""


class MeshRegionBase:
    """Base class for Icepak mesh region properties and methods.

    This class provides common functionality shared between ``MeshRegion``
    and ``GlobalMeshRegion`` classes.

    Examples
    --------
    >>> from ansys.aedt.core import Icepak
    >>> icepak = Icepak()
    >>> icepak.mesh.global_region.manual_settings

    """

    _has_getobject: bool
    _legacy_props: dict
    _name: str

    def __getitem__(self, key: str) -> Any:
        """Return a setup property by key.

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> icepak = Icepak()
        >>> region = icepak.mesh.regions[0]
        >>> prop_value = region["MeshRegionResolution"]

        """
        return self.props[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set a setup property by key.

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> icepak = Icepak()
        >>> region = icepak.mesh.regions[0]
        >>> region["MeshRegionResolution"] = 1

        """
        self.props[key] = value

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name

    @property
    def props(self) -> MeshProps:
        """Properties of the mesh operation.

        Returns
        -------
        :class:`ansys.aedt.core.generic.props.Props`

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> icepak = Icepak()
        >>> icepak.mesh.global_region.props

        """
        if self._legacy_props and not self._has_getobject:
            return MeshProps(self, self._legacy_props)

        if self._has_getobject:
            self._legacy_props = self._get_props_from_aedt() or {}

        if not self._legacy_props:
            self._legacy_props = self._get_props_fallback() or {}

        return MeshProps(self, self._legacy_props)

    @props.setter
    def props(self, value: dict) -> None:
        self.update(props=value)

    def _get_props_from_aedt(self) -> dict:
        """Retrieve properties from AEDT object data.

        Returns
        -------
        dict
            Properties dictionary from AEDT.

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> icepak = Icepak()
        >>> icepak.mesh.global_region._get_props_from_aedt()

        """
        return {}

    def _get_props_fallback(self) -> dict:
        """Retrieve properties using fallback method.

        Returns
        -------
        dict
            Properties dictionary from fallback source.

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> icepak = Icepak()
        >>> icepak.mesh.global_region._get_props_fallback()

        """
        return {}

    @property
    def manual_settings(self) -> bool | None:
        """Whether manual mesh settings are enabled.

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> icepak = Icepak()
        >>> icepak.mesh.global_region.manual_settings

        """
        props = self.props
        if "UserSpecifiedSettings" in props:
            return props["UserSpecifiedSettings"]
        return None

    @manual_settings.setter
    def manual_settings(self, value: bool) -> None:
        props = self.props.to_dict()
        if value != props.get("UserSpecifiedSettings"):
            if not value:
                new_props = dict(GeneralSettings)
            else:
                new_props = dict(UserSpecifiedSettings)

            # Keep the assignment and enabled state of the mesh region
            if "Objects" in props:
                new_props["Objects"] = props["Objects"]
            if "Enable" in props:
                new_props["Enable"] = props["Enable"]
            self.update(props=new_props)

    @property
    def name(self) -> str:
        """Name of the mesh region.

        Returns
        -------
        str

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> icepak = Icepak()
        >>> icepak.mesh.global_region.name

        """
        return self._name

    @pyaedt_function_handler()
    def update(self, props: dict | None = None) -> bool:
        """Update the mesh.

        Parameters
        ----------
        props : dict, optional
            New properties to update. The default is ``None``, in which case
            it uses the current properties.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.Edit

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> icepak = Icepak()
        >>> props = icepak.mesh.global_region.props.to_dict()
        >>> icepak.mesh.global_region.update(props)
        >>> region = icepak.mesh.regions[1]
        >>> props = region.props.to_dict()
        >>> region.update(props)

        """
        if props is None:
            props = self.props.to_dict()

        aedt_props = self._get_args(props)

        self._update_aedt(aedt_props)

        if not self._has_getobject:
            self._legacy_props = props
        return True

    def _update_aedt(self, aedt_props: list) -> None:  # pragma: no cover
        """Execute the AEDT update command.

        Parameters
        ----------
        aedt_props : list
            Properties formatted for AEDT API.

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> icepak = Icepak()
        >>> props = icepak.mesh.global_region.props.to_dict()
        >>> icepak.mesh.global_region.update(props)

        """
        raise NotImplementedError("Subclasses MeshRegion or GlobalMeshRegion must implement _update_aedt.")

    @pyaedt_function_handler()
    def _get_args(self, props: dict | None = None) -> list:
        """Retrieve arguments.

        Returns
        -------
        list
            List of arguments for the mesh operation.

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> icepak = Icepak()
        >>> icepak.mesh.global_region._get_args()

        """
        props = self._legacy_props if not props else props
        arg = ["NAME:" + self._name]
        _dict2arg(props, arg)
        return arg


class MeshRegion(MeshRegionBase, BinaryTreeNode, PyAedtBase):
    """Provides Icepak subregions mesh properties and methods.

    Parameters
    ----------
    mesh : :class:`ansys.aedt.core.modules.mesh_icepak.IcepakMesh`
        PyAEDT mesh region instance.
    name : str, optional
        Mesh region name.
    props : dict, optional
        Mesh region properties.

    Examples
    --------
    >>> from ansys.aedt.core import Icepak
    >>> icepak = Icepak()
    >>> icepak.mesh.regions

    """

    def __init__(self, mesh: IcepakMesh, name: str, props: dict) -> None:
        self._mesh: IcepakMesh = mesh
        self._app: FieldAnalysisIcepak = self._mesh._app
        self._legacy_props = {}
        self._name = name

        self._manual_settings = None
        self.__settings = None

        self.__child_object = None
        if props:
            self._legacy_props = props

        self._has_getobject = _has_get_obj_data(self._child_object)

    @pyaedt_function_handler()
    def _initialize_tree_node(self) -> bool:
        child_object = self._child_object
        if child_object:
            BinaryTreeNode.__init__(self, self._name, child_object, False, app=self._app)
            return True
        return False

    @property
    def _child_object(self):
        """Object-oriented properties.

        Returns
        -------
        AEDT object if any or `None`.

        """
        if not self.__child_object:
            design_childs = self._app.get_oo_name(self._app.odesign)

            if "Mesh" in design_childs:
                cc = self._app.get_oo_object(self._app.odesign, "Mesh")
                cc_names = self._app.get_oo_name(cc)
                if self._name in cc_names:
                    self.__child_object = self._app.get_oo_object(cc, self._name)
        return self.__child_object

    def _get_props_from_aedt(self) -> dict:
        """Retrieve properties from AEDT object data.

        Returns
        -------
        dict
            Properties dictionary from AEDT.

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> icepak = Icepak()
        >>> region = icepak.mesh.regions[0]
        >>> region._get_props_from_aedt()

        """
        return _get_obj_data(self._child_object) or {}

    def _get_props_fallback(self) -> dict:
        """Retrieve properties using fallback method from design_properties.

        Returns
        -------
        dict
            Properties dictionary from design_properties.

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> icepak = Icepak()
        >>> region = icepak.mesh.regions[0]
        >>> region._get_props_fallback()

        """
        dp = self._app.design_properties
        if not isinstance(dp, dict):  # pragma: no cover
            return {}

        mesh_regions = dp.get("MeshRegion", {})
        mesh_setup = mesh_regions.get("MeshSetup", {})

        mesh_region = mesh_setup.get("MeshRegions", {})

        if self._name in mesh_region:
            return mesh_region.get(self._name, {})
        elif self._name in mesh_setup:
            return mesh_setup.get(self._name, {})
        return {}

    @property
    def name(self) -> str:
        """Name of the mesh region.

        Returns
        -------
        str

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> icepak = Icepak()
        >>> region = icepak.mesh.regions[0]
        >>> region.name

        """
        child_object = self._child_object
        if child_object is not None:
            self._name = child_object.Name
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        region_names = self._mesh.region_names

        if value in region_names:
            raise ValueError(f"Name {value} already assigned in the design.")

        self.child_object.Name = str(value)

        self.__child_object = None
        object.__setattr__(self, "_name", value)
        object.__setattr__(self, "_tree_node_initialized", False)
        object.__setattr__(self, "_props", None)
        object.__setattr__(self, "_children_loaded", False)

    @property
    def assignment(self) -> list:
        """Retrieve assignments.

        Returns
        -------
        list
            List of assigned objects.

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> icepak = Icepak()
        >>> region = icepak.mesh.regions[0]
        >>> region.assignments

        """
        props = self.props
        if "Objects" in props:
            return props["Objects"]
        else:  # pragma: no cover
            assignments = []
            child_object = self._child_object
            if child_object is not None:
                if "Assignment" in child_object.GetPropNames():
                    assignment = getattr(child_object, "Assignment", [])
                    if isinstance(assignment, str):
                        assignments = [item.strip() for item in assignment.split(",") if item.strip()]
                    elif isinstance(assignment, list):
                        assignments = assignment
            return assignments

    @pyaedt_function_handler()
    def enable(self) -> bool:
        """Enable a setup.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.EditSetup

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> icepak = Icepak()
        >>> region = icepak.mesh.regions[0]
        >>> region.enable()

        """
        if "Enable" in self.props:
            self.props["Enable"] = True
        else:  # pragma: no cover
            self._app.logger.warning("No enabled setup found.")
            return False
        return True

    @pyaedt_function_handler()
    def disable(self) -> bool:
        """Disable a setup.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.EditSetup

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> icepak = Icepak()
        >>> region = icepak.mesh.regions[0]
        >>> region.disable()

        """
        if "Enable" in self.props:
            self.props["Enable"] = False
        else:  # pragma: no cover
            self._app.logger.warning("No enabled setup found.")
            return False
        return True

    def _update_aedt(self, aedt_props: list) -> None:
        """Execute the AEDT update command.

        Parameters
        ----------
        aedt_props : list
            Properties formatted for AEDT API.

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> icepak = Icepak()
        >>> region = icepak.mesh.regions[0]
        >>> props = region.props.to_dict()
        >>> region.update(props)

        """
        try:
            cast("_OMeshModule", self._app.omeshmodule).EditMeshRegion(self.name, aedt_props)
        except Exception:  # pragma: no cover
            raise AEDTRuntimeError("Update mesh region failed.")

    @pyaedt_function_handler()
    def delete(self) -> bool:
        """Delete the mesh region.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.DeleteMeshRegions()

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> icepak = Icepak()
        >>> region = icepak.mesh.regions[0]
        >>> region.delete()

        """
        cast("_OMeshModule", self._app.omeshmodule).DeleteMeshRegions([self.name])
        return True

    @pyaedt_function_handler()
    def create(self) -> MeshRegion:
        """Create a mesh region.

        Returns
        -------
        :class:`ansys.aedt.core.modules.mesh_icepak.MeshRegion`
            The created mesh operation.

        References
        ----------
        >>> oModule.AssignMeshRegion

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> icepak = Icepak()
        >>> mesh_region = icepak.mesh.assign_mesh_region()

        """
        aedt_props = self._get_args()

        non_model_solids = []

        if settings.aedt_version is None or settings.aedt_version <= "2023.2":
            non_model_solids = list(self._app.modeler.non_model_objects)

        cast("_OMeshModule", self._app.omeshmodule).AssignMeshRegion(aedt_props)

        # GetObjData is available for some objects in 2026R1
        self._has_getobject = _has_get_obj_data(self._child_object)

        # API renames the subregion, and if GetObjData not available, we need to refresh the prop
        new_name = f"{self.name}_SubRegion"
        if (
            settings.aedt_version is not None
            and settings.aedt_version > "2023.2"
            and not self._has_getobject
            and new_name in self._app.modeler.object_names
        ):  # pragma: no cover
            self._legacy_props["Objects"] = [new_name]
        elif settings.aedt_version is None or settings.aedt_version <= "2023.2":
            new_non_model_solids = list(self._app.modeler.non_model_objects)
            added_non_model_solids = [obj for obj in new_non_model_solids if obj not in non_model_solids]
            self._legacy_props["Objects"] = added_non_model_solids

        if not self._has_getobject:  # pragma: no cover
            # If a new mesh region is created, and GetObjData is not available,
            # it is needed to populated setups dictionary because if not props will be empty.
            self._mesh._register_region(self)

        return self


class GlobalMeshRegion(MeshRegionBase):
    """Icepak global mesh properties and methods.

    Parameters
    ----------
    app : :class:`ansys.aedt.core.application.analysis_icepak.FieldAnalysisIcepak`

    Examples
    --------
    >>> from ansys.aedt.core import Icepak
    >>> icepak = Icepak()
    >>> icepak.mesh.global_region

    """

    def __init__(self, app: FieldAnalysisIcepak) -> None:
        self._app = app
        self._name = "Global"

        self._manual_settings = False
        self._legacy_props = {}

        # Assign the global mesh region to a Region object if it exists in the modeler solid bodies
        self.assignment = None
        if "Region" in app.modeler.solid_bodies:
            self.assignment = "Region"

        # TODO: AEDT API does not have GetObjData for the global mesh region yet
        self._has_getobject = False

    def _get_props_fallback(self) -> dict:
        """Retrieve properties using fallback method from design_properties.

        Returns
        -------
        dict
            Properties dictionary from design_properties.

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> icepak = Icepak()
        >>> icepak.mesh._get_props_fallback()

        """
        dp = self._app.design_properties
        if not isinstance(dp, dict):
            return {}

        mesh_region = dp.get("MeshRegion", {})
        mesh_setup = mesh_region.get("MeshSetup", {})
        if settings.aedt_version is not None and settings.aedt_version > "2023.2":
            global_settings = mesh_setup.get("Global", {})
            if isinstance(global_settings, dict) and global_settings.get("DType") == "RegionT":
                return global_settings
        else:  # pragma: no cover
            mesh_regions = mesh_setup.get("MeshRegions", {})
            global_settings = mesh_regions.get("Global", {})
            if isinstance(global_settings, dict):
                return global_settings
        return {}

    def _update_aedt(self, aedt_props: list) -> None:
        """Execute the AEDT update command.

        Parameters
        ----------
        aedt_props : list
            Properties formatted for AEDT API.

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> icepak = Icepak()
        >>> props = icepak.mesh.global_region.props.to_dict()
        >>> icepak.mesh._update_aedt(props)

        """
        try:
            cast("_OMeshModule", self._app.omeshmodule).EditGlobalMeshRegion(aedt_props)
        except Exception:  # pragma: no cover
            raise AEDTRuntimeError("Update global mesh region properties failed.")


class IcepakMesh(PyAedtBase):
    """Manages Icepak mesh functions.

    Parameters
    ----------
    app : :class:`ansys.aedt.core.application.analysis_icepak.FieldAnalysisIcepak`

    Examples
    --------
    >>> from ansys.aedt.core import Icepak
    >>> icepak = Icepak()
    >>> cylinder = icepak.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
    >>> model_resolution = icepak.mesh.assign_model_resolution(cylinder, 1e-4, "ModelRes1")

    """

    def __init__(self, app: FieldAnalysisIcepak) -> None:
        self._app = app

        design_type = self._app._odesign.GetDesignType()
        if not hasattr(self._app._design_type, "mesher"):  # pragma: no cover
            raise RuntimeError(f"Invalid design type {design_type}.")

        self._odesign: _OMeshDesign = cast("_OMeshDesign", self._app.odesign)

        self.__operations = SetupDict()
        self.__regions = SetupDict()
        self.__global_mesh_region = None

        self.__child_object = None

    def _register_operation(self, operation: MeshOperation) -> None:
        """Store a newly created mesh operation in the local cache."""
        self.__operations[operation.name] = operation

    def _register_region(self, region: MeshRegion) -> None:
        """Store a newly created mesh region in the local cache."""
        self.__regions[region.name] = region

    @property
    def global_region(self) -> GlobalMeshRegion | None:
        """Global mesh region.

        Returns
        -------
        :class:`ansys.aedt.core.modules.mesh.GlobalMeshRegion`
            Global mesh region object.

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> icepak = Icepak()
        >>> icepak.mesh.global_region

        """
        if not self.__global_mesh_region:
            self.__global_mesh_region = GlobalMeshRegion(self._app)
        return self.__global_mesh_region

    @property
    def region_names(self) -> list[str]:
        """Mesh region names.

        Returns
        -------
        list
            Mesh region names.

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> icepak = Icepak()
        >>> icepak.mesh.region_names

        """
        return self._get_mesh_names()[0]

    @property
    def regions(self) -> SetupDict:
        """Mesh regions.

        Returns
        -------
        :class:`ansys.aedt.core.generic.general_methods.SetupDict`
            Mapping of mesh regions.

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> app = Icepak()
        >>> mesh_regions = app.mesh.regions

        """
        region_names = self.region_names
        for region in region_names:
            if region not in self.__regions:
                if region != "Global":
                    self.__regions[region] = MeshRegion(mesh=self, name=region, props={})
                else:
                    self.__regions[region] = self.global_region

        active_names = set(region_names)
        for region_name in list(self.__regions.keys()):
            if region_name not in active_names:
                del self.__regions[region_name]

        return self.__regions

    @property
    def operation_names(self) -> list[str]:
        """Mesh operation names.

        Returns
        -------
        list
            Mesh region names.

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> icepak = Icepak()
        >>> icepak.mesh.operation_names

        """
        return self._get_mesh_names()[1]

    @property
    def operations(self) -> SetupDict:
        """Mesh operations.

        Returns
        -------
        :class:`ansys.aedt.core.generic.general_methods.SetupDict`
            Mapping of mesh regions.

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> app = Icepak()
        >>> mesh_regions = app.mesh.operations

        """
        operation_names = self.operation_names
        for operation in operation_names:
            if operation not in self.__operations:
                self.__operations[operation] = MeshOperation(mesh=self, name=operation, props={})

        active_names = set(operation_names)
        for region_name in list(self.__operations.keys()):
            if region_name not in active_names:
                del self.__operations[region_name]

        return self.__operations

    @property
    def child_names(self) -> list[str]:
        """All mesh region and operation names.

        Returns
        -------
        list
            Mesh region names followed by mesh operation names.

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> app = Icepak()
        >>> mesh_child_names = app.mesh.child_names

        """
        region_names, operation_names = self._get_mesh_names()
        return region_names + operation_names

    @property
    def bounding_dimension(self) -> list:
        """Bounding dimension.

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> app = Icepak()
        >>> mesh_child_names = app.mesh.bounding_dimension

        """
        return self._app.modeler.get_bounding_dimension()

    @pyaedt_function_handler()
    def assign_mesh_region(
        self,
        assignment: str | list | None = None,
        level: int = 5,
        name: str | None = None,
    ) -> MeshRegion | bool:
        """Assign a predefined surface mesh level to an object.

        Parameters
        ----------
        assignment : str, list, optional
            List of objects to apply the mesh region to. The default
            is ``None``, in which case all objects are selected.
        level : int, optional
            Level of the surface mesh. Options are ``1`` through ``5``. The default
            is ``5``.
        name : str, optional
            Name of the mesh region. The default is ``"MeshRegion1"``.

        Returns
        -------
        :class:`ansys.aedt.core.modules.mesh_icepak.IcepakMesh.MeshRegion`

        References
        ----------
        >>> oModule.AssignMeshRegion

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> app = Icepak()
        >>> box = app.modeler.create_box([5, 5, 5], [20, 50, 80])
        >>> app.mesh.assign_mesh_region(assignment=box.name)

        """
        if not name:
            name = generate_unique_name("MeshRegion")
        elif name in self.region_names:
            name = generate_unique_name(name)

        is_subregion = False

        if assignment is None:
            assignment = list(self._app.modeler.object_names)
            if "Region" in assignment:
                assignment.remove("Region")
        elif not isinstance(assignment, list):
            if isinstance(assignment, str) and assignment in self._app.modeler.object_names:
                model = self._app.modeler[assignment]
                if "CreateSubRegion:1" in model.children:
                    is_subregion = True
            assignment = [assignment]

        props = dict(GeneralSettings)

        props["MeshRegionResolution"] = level

        if settings.aedt_version is not None and settings.aedt_version > "2023.2" and not is_subregion:
            region = self._app.modeler.create_subregion(
                padding_values=[0, 0, 0, 0, 0, 0], padding_types="Percentage Offset", assignment=assignment
            )
            props["Objects"] = [region.name]
        else:
            props["Objects"] = assignment

        mesh_region = MeshRegion(mesh=self, name=name, props=props)

        return mesh_region.create()

    @pyaedt_function_handler()
    def assign_mesh_level(self, mesh_order: dict, name: str | None = None) -> list[MeshOperation | bool] | bool:
        """Assign a mesh level to objects.

        Parameters
        ----------
        mesh_order : dict
            Dictionary where the key is the object name and the value is the mesh level.
        name : str, optional
            Name of the mesh operation. The default is ``None``.

        Returns
        -------
        list[:class:`ansys.aedt.core.modules.mesh.MeshOperation`] or bool
            The created mesh operations, or ``False`` if an operation fails.

        References
        ----------
        >>> oModule.AssignMeshOperation

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> app = Icepak()
        >>> box = app.modeler.create_box([5, 5, 5], [20, 50, 80])
        >>> app.mesh.assign_mesh_level(mesh_order={box.name: 2})

        """
        level_order = {}
        for obj in mesh_order:
            if mesh_order[obj] not in level_order:
                level_order[mesh_order[obj]] = []
            level_order[mesh_order[obj]].append(obj)
        list_meshops = []

        for level in level_order:
            if name:
                name = generate_unique_name(name, "L_" + str(level))
            else:
                name = generate_unique_name("Icepak", "L_" + str(level))

            props = {
                "Enable": True,
                "Local Mesh Parameters Enabled": False,
                "Objects": level_order[level],
                "MaxLevel": str(level),
                "MinLevel": str(level),
                "IncrLevel": "0",
                "Mesh Reuse Enabled": False,
                "Mesh Reuse File": "",
                "Mesh Object(s) Separately Enabled": False,
            }

            mop = MeshOperation(self, name, props)

            list_meshops.append(mop.create())

        return list_meshops

    @pyaedt_function_handler()
    def assign_mesh_level_to_group(
        self,
        mesh_level: int,
        group_name: str,
        enable_local_mesh_parameters: bool = False,
        local_mesh_parameters: str = "No local mesh parameters",
        name: str | None = None,
    ) -> MeshOperation | bool:
        """Assign a mesh level to a group.

        Parameters
        ----------
        mesh_level : int
            Level of mesh to assign. Options are ``1`` through ``5``.
        group_name : str
            Name of the group.
        enable_local_mesh_parameters : bool, optional
            The default is ``False``.
        local_mesh_parameters : str, optional
            The default is ``"No Local Mesh Parameters"``.
        name : str, optional
            Name of the mesh operation. The default is ``None``.

        Returns
        -------
        :class:`ansys.aedt.core.modules.mesh.MeshOperation`

        References
        ----------
        >>> oModule.AssignMeshOperation

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> app = Icepak()
        >>> box1 = app.modeler.create_box([5, 5, 5], [20, 50, 80])
        >>> box2 = app.modeler.create_box([10, 10, 10], [50, 50, 2])
        >>> group = app.modeler.create_group([box1.name, box2.name], group_name="mygroup")
        >>> app.mesh.assign_mesh_level_to_group(mesh_level=1, group_name=group)

        """
        if not name:
            name = generate_unique_name("MeshLevel")
        elif name in self.operation_names:
            name = generate_unique_name(name)

        props = {
            "Enable": True,
            "Local Mesh Parameters Enabled": enable_local_mesh_parameters,
            "MaxLevel": mesh_level,
            "MinLevel": mesh_level,
            "IncrLevel": "0",
            "Groups": [str(group_name)],
            "Local Mesh Parameters Type": local_mesh_parameters,
        }

        mop = MeshOperation(self, name, props)

        return mop.create()

    @pyaedt_function_handler()
    def assign_mesh_reuse(
        self, assignment: list, mesh_file: str | Path, name: str | None = None
    ) -> MeshOperation | bool:
        """Assign a mesh file to objects.

        Parameters
        ----------
        assignment : str or list
            Names of objects to which the mesh file is assignment.
        mesh_file : str or :class:`pathlib.Path`
            Path to the mesh file.
        name : str, optional
            Name of the mesh operation. The default is ``None``, in which case it will be
            generated automatically.

        Returns
        -------
        :class:`ansys.aedt.core.modules.mesh.MeshOperation`

        References
        ----------
        >>> oModule.AssignMeshOperation

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> app = Icepak()
        >>> box1 = app.modeler.create_box([5, 5, 5], [20, 50, 80])
        >>> app.mesh.assign_mesh_reuse(assignment=box1.name, mesh_file="example.msh")

        """
        mesh_file = Path(mesh_file)
        if not mesh_file.is_file():
            raise FileNotFoundError(f"Mesh file does not exist: {mesh_file}.")

        objs = self._app.modeler.convert_to_selections(assignment, True)

        if not name:
            name = generate_unique_name("MeshFile")
        elif name in self.operation_names:
            name = generate_unique_name(name)

        props = {
            "Enable": True,
            "Local Mesh Parameters Enabled": False,
            "Objects": objs,
            "MaxLevel": "0",
            "MinLevel": "0",
            "IncrLevel": "0",
            "Mesh Reuse Enabled": True,
            "Mesh Reuse File": str(mesh_file),
            "Mesh Object(s) Separately Enabled": False,
        }
        mop = MeshOperation(self, name, props)
        return mop.create()

    @pyaedt_function_handler()
    def get_mesh_region(self, name: str) -> MeshRegion | None:
        """Get mesh region.

        Parameters
        ----------
        name : str
            Name of the mesh region.

        Returns
        -------
        :class:`ansys.aedt.core.modules.mesh_icepak.MeshRegion`

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> app = Icepak()
        >>> region_names = app.mesh.region_names
        >>> op2 = app.mesh.get_mesh_region(region_names[1])

        """
        if name in self.region_names:
            if name not in self.__regions:
                if name != "Global":
                    self.__regions[name] = MeshRegion(mesh=self, name=name, props={})
                else:
                    self.__regions[name] = self.global_region
            return self.__regions[name]
        return None

    @pyaedt_function_handler()
    def get_mesh_operation(self, name: str) -> MeshOperation | None:
        """Get mesh operation.

        Parameters
        ----------
        name : str
            Name of the mesh operation.

        Returns
        -------
        :class:`ansys.aedt.core.modules.mesh.MeshOperation`

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> app = Icepak()
        >>> operation_names = app.mesh.operation_names
        >>> op2 = app.mesh.get_mesh_operation(operation_names[1])

        """
        if name in self.operation_names:
            if name not in self.__operations:
                self.__operations[name] = MeshOperation(mesh=self, name=name, props={})
            return self.__operations[name]
        return None

    @pyaedt_function_handler()
    def generate_mesh(self, name: str | None = None) -> bool:
        """Generate the mesh for a given setup name.

        Parameters
        ----------
        name : str, optional
            Name of the design to mesh. Default is ``None`` in which case the first available setup will be selected.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oDesign.GenerateMesh

        Examples
        --------
        >>> from ansys.aedt.core import Icepak
        >>> app = Icepak()
        >>> box = app.modeler.create_box([5, 5, 5], [20, 50, 80])
        >>> setup = app.create_setup()
        >>> app.mesh.generate_mesh(name=setup.name)

        """
        setup_names = self._app.setup_names
        if name is None and setup_names:
            name = setup_names[0]
        elif not setup_names:
            raise AEDTRuntimeError("At least one setup has to be defined.")
        return self._odesign.GenerateMesh(name) == 0

    @pyaedt_function_handler()
    def _get_mesh_names(self) -> tuple[list[str], list[str]]:
        """Return mesh region and operation names."""
        region_names = ["Global"]
        operation_names = []

        if not self._app._is_object_oriented_enabled():  # pragma: no cover
            return region_names, operation_names

        mesh_object = self._app.get_oo_object(self._app.odesign, "Mesh")
        if not mesh_object:  # pragma: no cover
            return region_names, operation_names

        child_names = self._app.get_oo_name(mesh_object)
        for name in child_names:
            child_object = self._app.get_oo_object(mesh_object, name)
            if child_object:
                child_object_attributes = dir(child_object)
                if "GetObjType" in child_object_attributes:
                    object_type = cast("_OMeshTypedObject", child_object).GetObjType()
                    if object_type.lower() in ["mesh region", "meshregion"]:
                        region_names.append(name)
                    elif object_type.lower() in ["mesh operation", "meshoperation"]:
                        operation_names.append(name)
                else:
                    if "Mesh_Resolution" in child_object_attributes or "Minimum_Gap_X" in child_object_attributes:
                        region_names.append(name)
                    else:
                        operation_names.append(name)

        # AEDT API can not get the available mesh regions in 3D Components,
        # so we need to use the design properties to get them.
        component_names = self._app.modeler.user_defined_component_names
        if component_names:
            child_names.append("Global")
            component_regions, component_operations = self._get_mesh_3d_components(child_names)
            region_names.extend(component_regions)
            operation_names.extend(component_operations)

        return region_names, operation_names

    @pyaedt_function_handler()
    def _get_mesh_3d_components(self, mesh_names) -> tuple[list, list]:
        component_regions = []
        component_operations = []

        dp = self._app.design_properties
        if not isinstance(dp, dict):
            return component_regions, component_operations

        mesh_region = dp.get("MeshRegion", {})

        mesh_setup = mesh_region.get("MeshSetup", {})

        for region_name, region_settings in mesh_setup.get("MeshRegions", {}).items():
            if isinstance(region_settings, dict) and region_name not in mesh_names:
                component_regions.append(region_name)

        for operation_name, operation_settings in mesh_setup.get("MeshOperations", {}).items():
            if isinstance(operation_settings, dict) and operation_name not in mesh_names:
                component_operations.append(operation_name)

        for region_name, region_settings in mesh_setup.items():
            if region_name in {"MeshRegions", "MeshOperations"}:
                continue
            if isinstance(region_settings, dict) and region_name not in mesh_names:
                if region_settings.get("DType") == "RegionT":
                    component_regions.append(region_name)
                elif region_settings.get("DType") == "OpT":
                    component_operations.append(region_name)
        return component_regions, component_operations
