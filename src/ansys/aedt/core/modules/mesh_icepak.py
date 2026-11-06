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

import copy
import os.path
from typing import TYPE_CHECKING
from typing import Any

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
from ansys.aedt.core.modeler.cad.components_3d import UserDefinedComponent
from ansys.aedt.core.modeler.cad.elements_3d import BinaryTreeNode
from ansys.aedt.core.modeler.cad.object_3d import Object3d
from ansys.aedt.core.modules.mesh import MeshOperation

if TYPE_CHECKING:
    from ansys.aedt.core.application.analysis_icepak import FieldAnalysisIcepak


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


class MeshRegion(BinaryTreeNode, PyAedtBase):
    """Provides Icepak subregions mesh properties and methods."""

    def __getitem__(self, key: str) -> Any:
        """Return a setup property by key."""
        return self.props[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set a setup property by key."""
        self.props[key] = value

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name

    def __init__(self, mesh: IcepakMesh, name: str, props: dict) -> None:
        self._mesh: IcepakMesh = mesh
        self._app: Any = self._mesh._app
        self._legacy_props = {}
        self._name = name

        self._manual_settings = None
        self.__settings = None

        self.__child_object = None
        if props:
            self._legacy_props = MeshProps(self, props)

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
        class:`ansys.aedt.core.modeler.cad.elements_3d.BinaryTreeNode`

        """
        if not self.__child_object:
            design_childs = self._app.get_oo_name(self._app.odesign)

            if "Mesh" in design_childs:
                cc = self._app.get_oo_object(self._app.odesign, "Mesh")
                cc_names = self._app.get_oo_name(cc)
                if self._name in cc_names:
                    self.__child_object = self._app.get_oo_object(cc, self._name)
        return self.__child_object

    @property
    def props(self) -> MeshProps:
        """Properties of the mesh operation.

        Returns
        -------
        :class:`ansys.aedt.core.generic.props.Props`

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> o = hfss.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> surface = hfss.mesh.assign_surface_mesh(o.name, 3, "Surface")
        >>> surface.props

        """
        if self._legacy_props and not self._has_getobject:
            return MeshProps(self, self._legacy_props)

        if self._has_getobject:
            self._legacy_props = _get_obj_data(self._child_object) or {}

        if not self._legacy_props:
            # Fallback if previous method fails. The information is retrieved from design_properties (AEDT file)
            dp = self._app.design_properties
            if not isinstance(dp, dict):  # pragma: no cover
                return MeshProps(self, self._legacy_props)

            mesh_regions = dp.get("MeshRegion", {})
            mesh_setup = mesh_regions.get("MeshSetup", {})

            mesh_region = mesh_setup.get("MeshRegions", {})

            if self._name in mesh_region:
                self._legacy_props = mesh_region.get(self._name, {})
            elif self._name in mesh_setup:
                self._legacy_props = mesh_setup.get(self._name, {})

        return MeshProps(self, self._legacy_props)

    @props.setter
    def props(self, value: dict) -> None:
        self.update(props=value)

    @property
    def manual_settings(self) -> bool | None:
        """Whether manual mesh settings are enabled."""
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
        >>> from ansys.aedt.core.modules.mesh_icepak import MeshRegion
        >>> obj = MeshRegion()
        >>> obj.name

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

        if "Rename" in dir(self._app.omeshmodule):
            self._app.omeshmodule.Rename(self.name, str(value))
        elif "RenameOp" in dir(self._app.omeshmodule):
            self._app.omeshmodule.RenameOp(self.name, str(value))
        else:  # pragma: no cover
            raise AEDTRuntimeError("AEDT API does not support mesh operation rename.")

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

        """
        if "Enable" in self.props:
            self.props["Enable"] = True
        elif "Enabled" in self.props:
            self.props["Enabled"] = True
        elif "IsEnabled" in self.props:
            self.props["IsEnabled"] = True
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
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> setup = app.create_setup()
        >>> setup.disable()

        """
        if "Enable" in self.props:
            self.props["Enable"] = False
        elif "Enabled" in self.props:
            self.props["Enabled"] = False
        elif "IsEnabled" in self.props:
            self.props["IsEnabled"] = False
        else:  # pragma: no cover
            self._app.logger.warning("No enabled setup found.")
            return False
        return True

    @pyaedt_function_handler()
    def update(self, props: dict | None = None) -> bool:
        """Update the mesh.

        Parameters
        ----------
        props : dict, optional
            New properties to update. The  default is ``None``, in which case it uses the current properties.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.Edit

        """
        if props is None:
            props = self.props.to_dict()

        aedt_props = self._get_args(props)

        self._app.omeshmodule.Edit(self.name, aedt_props)

        if not self._has_getobject:
            self._legacy_props = props
        return True

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
        >>> from ansys.aedt.core.modules.mesh_icepak import MeshRegion
        >>> obj = MeshRegion()
        >>> obj.delete()

        """
        self._app.omeshmodule.DeleteMeshRegions([self.name])
        self._app.mesh.meshregions.remove(self)
        return True

    @pyaedt_function_handler()
    def create(self) -> bool:
        """Create a mesh region.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.AssignMeshRegion

        Examples
        --------
        >>> from ansys.aedt.core.modules.mesh_icepak import MeshRegion
        >>> obj = MeshRegion()
        >>> obj.create()

        """
        if self.name == "Settings":
            self._app.logger.error("Cannot create a new mesh region with this Name")
            return False
        args = ["NAME:" + self.name, "Enable:=", self.enable]
        args += self.settings.parse_settings_as_args()
        args += self._parse_assignment_value()
        self._app.omeshmodule.AssignMeshRegion(args)
        self._app.mesh.meshregions.append(self)
        self._app.modeler.refresh_all_ids()
        result = self._initialize_tree_node()
        if result:
            self._assignment = self.assignment
        return result

    @pyaedt_function_handler()
    def _get_args(self, props: dict | None = None) -> list:
        """Retrieve arguments.

        Returns
        -------
        list
            List of arguments for the mesh operation.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> o = hfss.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> surface = hfss.mesh.assign_surface_mesh(o.name, 3, "Surface")
        >>> surface._get_args()

        """
        props = self.props if not props else props
        arg = ["NAME:" + self._name]
        _dict2arg(props, arg)
        return arg


class GlobalMeshRegion:
    """Icepak global mesh properties and methods.

    Examples
    --------
    >>> from ansys.aedt.core.modules.mesh_icepak import GlobalMeshRegion
    >>> obj = GlobalMeshRegion()

    """

    def __getitem__(self, key: str) -> Any:
        """Return a setup property by key."""
        return self.props[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set a setup property by key."""
        self.props[key] = value

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name

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

    @property
    def props(self) -> MeshProps:
        """Properties of the mesh operation.

        Returns
        -------
        :class:`ansys.aedt.core.generic.props.Props`

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> o = hfss.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> surface = hfss.mesh.assign_surface_mesh(o.name, 3, "Surface")
        >>> surface.props

        """
        if self._legacy_props and not self._has_getobject:
            return MeshProps(self, self._legacy_props)

        if not self._legacy_props:
            # Fallback if previous method fails. The information is retrieved from design_properties (AEDT file)
            self._legacy_props = self._get_global_region_settings() or {}

        return MeshProps(self, self._legacy_props)

    @props.setter
    def props(self, value: dict) -> None:
        self.update(props=value)

    @property
    def manual_settings(self) -> bool | None:
        """Whether manual mesh settings are enabled."""
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
        >>> from ansys.aedt.core.modules.mesh_icepak import MeshRegion
        >>> obj = MeshRegion()
        >>> obj.name

        """
        return self._name

    @pyaedt_function_handler()
    def update(self, props: dict | None = None) -> bool:
        """Update the mesh.

        Parameters
        ----------
        props : dict, optional
            New properties to update. The  default is ``None``, in which case it uses the current properties.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.Edit

        """
        if props is None:
            props = self.props.to_dict()

        aedt_props = self._get_args(props)

        self._app.omeshmodule.EditGlobalMeshRegion(aedt_props)

        if not self._has_getobject:
            self._legacy_props = props
        return True

    @pyaedt_function_handler()
    def _get_global_region_settings(self):
        dp = self._app.design_properties
        if not isinstance(dp, dict):
            return {}

        mesh_region = dp.get("MeshRegion", {})
        mesh_setup = mesh_region.get("MeshSetup", {})
        if settings.aedt_version > "2023.2":
            global_settings = mesh_setup.get("Global", {})
            if isinstance(global_settings, dict) and global_settings.get("DType") == "RegionT":
                return global_settings
        else:  # pragma: no cover
            mesh_regions = mesh_setup.get("MeshRegions", {})
            global_settings = mesh_regions.get("Global", {})
            if isinstance(global_settings, dict):
                return global_settings
        return {}

    @pyaedt_function_handler()
    def _get_args(self, props: dict | None = None) -> list:
        """Retrieve arguments.

        Returns
        -------
        list
            List of arguments for the mesh operation.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> hfss = Hfss()
        >>> o = hfss.modeler.create_cylinder(0, [0, 0, 0], 3, 20, 0)
        >>> surface = hfss.mesh.assign_surface_mesh(o.name, 3, "Surface")
        >>> surface._get_args()

        """
        props = self.props if not props else props
        arg = ["NAME:" + self._name]
        _dict2arg(props, arg)
        return arg


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

        self._odesign = self._app.odesign

        self.__operations = SetupDict()
        self.__regions = SetupDict()
        self.__global_mesh_region = None

        self.__child_object = None

    @property
    def global_region(self) -> GlobalMeshRegion:
        """Return the global mesh region.

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
        """Return the names of all mesh regions."""
        return self._get_mesh_names()[0]

    @property
    def regions(self) -> SetupDict:
        """Return the available mesh regions.

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
        """Return the names of all mesh operations."""
        return self._get_mesh_names()[1]

    @property
    def operations(self) -> SetupDict:
        """Return the available mesh operations.

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
        """Return the names of all mesh regions and operations.

        Returns
        -------
        List
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
        >>> from ansys.aedt.core.modules.mesh_icepak import IcepakMesh
        >>> obj = IcepakMesh()
        >>> obj.bounding_dimension

        """
        return self._app.modeler.get_bounding_dimension()

    @pyaedt_function_handler()
    def assign_mesh_level(self, mesh_order: dict, name: str = None) -> list[MeshOperation] | bool:
        """Assign a mesh level to objects.

        Parameters
        ----------
        mesh_order : dict
            Dictionary where the key is the object name and the value is
            the mesh level.
        name :  str, optional
            Name of the mesh operation. The default is ``None``.

        Returns
        -------
        list[:class:`ansys.aedt.core.modules.mesh.MeshOperation`]
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.AssignMeshOperation

        Examples
        --------
        >>> from ansys.aedt.core.modules.mesh_icepak import IcepakMesh
        >>> obj = IcepakMesh()
        >>> obj.assign_mesh_level(mesh_order={"Name": "Value"})

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
            props = dict({"Enable": True, "Level": str(level), "Objects": level_order[level]})
            mop = MeshOperation(self, name, props, "Icepak")
            mop.create()
            self.meshoperations.append(mop)
            list_meshops.append(name)
        return list_meshops

    @pyaedt_function_handler()
    def assign_mesh_from_file(self, assignment: list, file_name: str, name: str = None) -> MeshOperation | bool:
        """Assign a mesh from a file to objects.

        Parameters
        ----------
        assignment : list
            List of objects to apply the mesh file to.
        file_name :  str
            Full path to the mesh (MSH) file.
        name :  str, optional
            Name of the mesh operations. Default is ``None``.

        Returns
        -------
         :class:`ansys.aedt.core.modules.mesh.MeshOperation`
            Mesh Operation object. ``False`` when failed.

        References
        ----------
        >>> oModule.AssignMeshOperation

        Examples
        --------
        >>> from ansys.aedt.core.modules.mesh_icepak import IcepakMesh
        >>> obj = IcepakMesh()
        >>> obj.assign_mesh_from_file(assignment="Box1", file_name="example.txt")

        """
        objs = self._app.modeler.convert_to_selections(assignment, True)
        if name:
            name = generate_unique_name("MeshFile")
        else:
            name = generate_unique_name("MeshFile")
        props = dict({"Enable": True, "MaxLevel": str(0), "MinLevel": str(0), "Objects": objs})
        props["Local Mesh Parameters Enabled"] = False
        props["Mesh Reuse Enabled"] = True
        props["Mesh Reuse File"] = file_name
        props["Local Mesh Parameters Type"] = "3DPolygon Local Mesh Parameters"
        props["Height count"] = "0"
        props["Top height"] = "0mm"
        props["Top ratio"] = "0"
        props["Bottom height"] = "0mm"
        props["Bottom ratio"] = "0"
        mop = MeshOperation(self, name, props, "Icepak")
        if mop.create():
            self.meshoperations.append(mop)
            return mop
        return False

    @pyaedt_function_handler()
    def assign_priorities(self, assignment: list[list[Object3d | UserDefinedComponent | str]]) -> bool:
        """Set objects priorities.

        Parameters
        ----------
        assignment : List[List[Union[Object3d, UserDefinedComponent, str]
            List of lists of objects. Each list corresponds to one priority level from low to high.
            This means that the first list has the lowest priority while the last list
            has the highest priority. Objects not explicitly passed in the lists are assigned
            to a priority level lower than the objects in the first list.

        Returns
        -------
        bool
            ``True`` when successful, "False" when failed.

        References
        ----------
        >>> oEditor.UpdatePriorityList

        Examples
        --------
        >>> ipk.mesh.assign_priorities([["Box1", "Rectangle1"], ["Box2", "Fan1_1"], ["Heatsink1_1"]])

        """
        if not assignment or not isinstance(assignment, list) or not isinstance(assignment[0], list):
            raise AttributeError("``assignment`` input must be a list of lists.")
        props = {"PriorityListParameters": []}
        self._app.logger.info("Parsing input objects information for priority assignment. This operation can take time")
        udc = self._modeler.user_defined_components
        udc._parse_objs()
        for level, objects in enumerate(assignment):
            level += 1
            if isinstance(objects[0], str):
                objects = [self._modeler.objects_by_name.get(o, udc.get(o, None)) for o in objects]
            obj_3d = [
                o
                for o in objects
                if (isinstance(o, Object3d) and o.is_3d)
                or (isinstance(o, UserDefinedComponent) and any(p.is_3d for p in o.parts.values()))
            ]
            obj_2d = [
                o
                for o in objects
                if (isinstance(o, Object3d) and not o.is_3d)
                or (isinstance(o, UserDefinedComponent) and any(not p.is_3d for p in o.parts.values()))
            ]
            if obj_3d:
                level_3d = {
                    "EntityList": ", ".join([o.name for o in obj_3d]),
                    "PriorityNumber": level,
                    "PriorityListType": "3D",
                }
                if all(isinstance(o, Object3d) for o in obj_3d):
                    level_3d["EntityType"] = "Object"
                elif all(isinstance(o, UserDefinedComponent) for o in obj_3d):
                    level_3d["EntityType"] = "Component"
                else:
                    raise AttributeError("Cannot assign components and parts on the same level.")
                props["PriorityListParameters"].append(level_3d)
            if obj_2d:
                level_2d = {
                    "EntityList": ", ".join([o.name for o in obj_2d]),
                    "PriorityNumber": level,
                    "PriorityListType": "2D",
                }
                if all(isinstance(o, Object3d) for o in obj_2d):
                    level_2d["EntityType"] = "Object"
                elif all(isinstance(o, UserDefinedComponent) for o in obj_2d):
                    level_2d["EntityType"] = "Component"
                else:
                    raise AttributeError("Cannot assign components and parts on the same level.")
                props["PriorityListParameters"].append(level_2d)
        props = {"UpdatePriorityListData": props}
        self._app.logger.info("Input objects information for priority assignment completed.")
        args = []
        _dict2arg(props, args)
        self._modeler.oeditor.UpdatePriorityList(args[0])
        return True

    @pyaedt_function_handler()
    def assign_mesh_region(
        self, assignment: list = None, level: int = 5, name: str = None, **kwargs
    ) -> MeshRegion | bool:
        """Assign a predefined surface mesh level to an object.

        Parameters
        ----------
        assignment : list, optional
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
        >>> from ansys.aedt.core.modules.mesh_icepak import IcepakMesh
        >>> obj = IcepakMesh()
        >>> obj.assign_mesh_region(assignment="Box1", name="MyObject")

        """
        if not name:
            name = generate_unique_name("MeshRegion")
        if assignment is None:
            assignment = [i for i in self._modeler.object_names]
        meshregion = MeshRegion(self._app, assignment, name)
        meshregion.manual_settings = False
        meshregion.settings["MeshRegionResolution"] = level
        all_objs = [i for i in self._modeler.object_names]
        created = bool(meshregion)
        if created:
            if settings.aedt_version < "2024.1":
                objectlist2 = self._modeler.object_names
                added_obj = [i for i in objectlist2 if i not in all_objs]
                if not added_obj:
                    added_obj = [i for i in objectlist2 if i not in all_objs or i in assignment]
                meshregion.Objects = added_obj
                meshregion.SubModels = None
            meshregion.update()
            return meshregion
        else:
            return False

    @pyaedt_function_handler()
    def generate_mesh(self, name: str = None) -> bool:
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
        >>> from ansys.aedt.core.modules.mesh_icepak import IcepakMesh
        >>> obj = IcepakMesh()
        >>> obj.generate_mesh(name="MyObject")

        """
        if name is None:
            name = []
        return self._odesign.GenerateMesh(name) == 0

    @pyaedt_function_handler()
    def assign_mesh_level_to_group(
        self,
        mesh_level: int,
        group_name: str,
        enable_local_mesh_parameters: bool = False,
        local_mesh_parameters: str = "No local mesh parameters",
        name: str = None,
    ) -> MeshOperation:
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
        >>> from ansys.aedt.core.modules.mesh_icepak import IcepakMesh
        >>> obj = IcepakMesh()
        >>> obj.assign_mesh_level_to_group(mesh_level=1, group_name=1)

        """
        if name:
            for el in self.meshoperations:
                if el.name == name:
                    name = generate_unique_name(name)
                    break
        else:
            name = generate_unique_name("MeshLevel")
        props = dict(
            {
                "Enable": True,
                "Level": mesh_level,
                "Local Mesh Parameters Enabled": enable_local_mesh_parameters,
                "Groups": [str(group_name)],
                "Local Mesh Parameters Type": local_mesh_parameters,
            }
        )
        mop = MeshOperation(self, name, props, "Icepak")
        mop.create()
        self.meshoperations.append(mop)
        return mop

    def assign_mesh_reuse(self, assignment: list, mesh_file: str, name: str = None) -> MeshOperation | bool:
        """Assign a mesh file to objects.

        Parameters
        ----------
        assignment : str or list
            Names of objects to which the mesh file is assignment.
        mesh_file : str
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
        >>> from ansys.aedt.core.modules.mesh_icepak import IcepakMesh
        >>> obj = IcepakMesh()
        >>> obj.assign_mesh_reuse(assignment="Box1", mesh_file="example.txt")

        """
        if not os.path.exists(mesh_file):
            self._app.logger.error("Mesh file does not exist.")
            return False
        if name:
            for el in self.meshoperations:
                if el.name == name:
                    name = generate_unique_name(name)
                    break
        else:
            name = generate_unique_name("MeshReuse")
        if not isinstance(assignment, list):
            assignment = [assignment]
        props = dict({"Enable": True, "Mesh Reuse Enabled": True, "Mesh Reuse File": mesh_file, "Objects": assignment})
        mop = MeshOperation(self, name, props, "Icepak")
        mop.create()
        self.meshoperations.append(mop)
        return mop

    @pyaedt_function_handler()
    def get_mesh_region(self, name: str) -> MeshRegion | None:
        """Get mesh region.

        Parameters
        ----------
        name : str
            Name of the setup.

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
                if "GetObjType" in dir(child_object):
                    object_type = child_object.GetObjType()
                    if object_type.lower() in ["mesh region", "meshregion"]:
                        region_names.append(name)
                    elif object_type.lower() in ["mesh operation", "meshoperation"]:
                        operation_names.append(name)
                else:
                    if "Mesh_Resolution" in dir(child_object) or "Minimum_Gap_X" in dir(child_object):
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

        mesh_setup = copy.deepcopy(mesh_region.get("MeshSetup", {}))

        if "MeshRegions" in mesh_setup:
            for region_name, region_settings in mesh_setup["MeshRegions"].items():
                if isinstance(region_settings, dict) and region_name not in mesh_names:
                    component_regions.append(region_name)
            del mesh_setup["MeshRegions"]

        if "MeshOperations" in mesh_setup:
            for operation_name, operation_settings in mesh_setup["MeshOperations"].items():
                if isinstance(operation_settings, dict) and operation_name not in mesh_names:
                    component_operations.append(operation_name)
            del mesh_setup["MeshOperations"]

        for region_name, region_settings in mesh_setup.items():
            if isinstance(region_settings, dict) and region_name not in mesh_names:
                if region_settings.get("DType") == "RegionT":
                    component_regions.append(region_name)
                elif region_settings.get("DType") == "OpT":
                    component_operations.append(region_name)
        return component_regions, component_operations
