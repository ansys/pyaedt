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

import os.path
from typing import TYPE_CHECKING

from ansys.aedt.core.application import _get_obj_data
from ansys.aedt.core.application import _has_get_obj_data
from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.data_handlers import _dict2arg
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.general_methods import SetupDict
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.numbers_utils import _units_assignment
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.internal.errors import GrpcApiError
from ansys.aedt.core.modeler.cad.components_3d import UserDefinedComponent
from ansys.aedt.core.modeler.cad.elements_3d import BinaryTreeNode
from ansys.aedt.core.modeler.cad.object_3d import Object3d
from ansys.aedt.core.modules.mesh import MeshOperation

if TYPE_CHECKING:
    from ansys.aedt.core.application.analysis_icepak import FieldAnalysisIcepak


# Solid Region and Subregion classes
class CommonRegion(PyAedtBase):
    """Provide common region."""

    def __init__(self, app, name: str) -> None:
        self._app = app
        self._name = name
        self._padding_type = None  # ["Percentage Offset"] * 6
        self._padding_value = None  # [50] * 6
        self._coordinate_system = None  # "Global"
        self._dir_order = ["+X", "-X", "+Y", "-Y", "+Z", "-Z"]

    @property
    def padding_types(self) -> list[str]:
        """Get a list of strings containing the padding types used.

        One for each direction in the following order:
        +X, -X, +Y, -Y, +Z, -Z.

        Returns
        -------
        List[str]

        Examples
        --------
        >>> from ansys.aedt.core.modules.mesh_icepak import CommonRegion
        >>> obj = CommonRegion()
        >>> obj.padding_types

        """
        self._update_region_data()
        return self._padding_type

    @property
    def padding_values(self) -> list[float]:
        """Get a list of padding values (string or float) used.

        Get one for each direction, in the following order:
        +X, -X, +Y, -Y, +Z, -Z.

        Returns
        -------
        List[Union[str, float]]

        Examples
        --------
        >>> from ansys.aedt.core.modules.mesh_icepak import CommonRegion
        >>> obj = CommonRegion()
        >>> obj.padding_values

        """
        self._update_region_data()
        return self._padding_value

    @property
    def positive_x_padding_type(self) -> str:
        """Get a string with the padding type used in the +X direction.

        Returns
        -------
        str

        Examples
        --------
        >>> from ansys.aedt.core.modules.mesh_icepak import CommonRegion
        >>> obj = CommonRegion()
        >>> obj.positive_x_padding_type

        """
        return self._get_region_data("+X")

    @property
    def negative_x_padding_type(self) -> str:
        """Get a string with the padding type used in the -X direction.

        Returns
        -------
        str

        Examples
        --------
        >>> from ansys.aedt.core.modules.mesh_icepak import CommonRegion
        >>> obj = CommonRegion()
        >>> obj.negative_x_padding_type

        """
        return self._get_region_data("-X")

    @property
    def positive_y_padding_type(self) -> str:
        """Get a string with the padding type used in the +Y direction.

        Returns
        -------
        str

        Examples
        --------
        >>> from ansys.aedt.core.modules.mesh_icepak import CommonRegion
        >>> obj = CommonRegion()
        >>> obj.positive_y_padding_type

        """
        return self._get_region_data("+Y")

    @property
    def negative_y_padding_type(self) -> str:
        """Get a string with the padding type used in the -Y direction.

        Returns
        -------
        str

        Examples
        --------
        >>> from ansys.aedt.core.modules.mesh_icepak import CommonRegion
        >>> obj = CommonRegion()
        >>> obj.negative_y_padding_type

        """
        return self._get_region_data("-Y")

    @property
    def positive_z_padding_type(self) -> str:
        """Get a string with the padding type used in the +Z direction.

        Returns
        -------
        str

        Examples
        --------
        >>> from ansys.aedt.core.modules.mesh_icepak import CommonRegion
        >>> obj = CommonRegion()
        >>> obj.positive_z_padding_type

        """
        return self._get_region_data("+Z")

    @property
    def negative_z_padding_type(self) -> str:
        """Get a string with the padding type used in the -Z direction.

        Returns
        -------
        str

        Examples
        --------
        >>> from ansys.aedt.core.modules.mesh_icepak import CommonRegion
        >>> obj = CommonRegion()
        >>> obj.negative_z_padding_type

        """
        return self._get_region_data("-Z")

    @property
    def positive_x_padding(self) -> float:
        """Get a string with the padding value used in the +X direction.

        Returns
        -------
        float

        Examples
        --------
        >>> from ansys.aedt.core.modules.mesh_icepak import CommonRegion
        >>> obj = CommonRegion()
        >>> obj.positive_x_padding

        """
        return self._get_region_data("+X", False)

    @property
    def negative_x_padding(self) -> float:
        """Get a string with the padding value used in the -X direction.

        Returns
        -------
        float

        Examples
        --------
        >>> from ansys.aedt.core.modules.mesh_icepak import CommonRegion
        >>> obj = CommonRegion()
        >>> obj.negative_x_padding

        """
        return self._get_region_data("-X", False)

    @property
    def positive_y_padding(self) -> float:
        """Get a string with the padding value used in the +Y direction.

        Returns
        -------
        float

        Examples
        --------
        >>> from ansys.aedt.core.modules.mesh_icepak import CommonRegion
        >>> obj = CommonRegion()
        >>> obj.positive_y_padding

        """
        return self._get_region_data("+Y", False)

    @property
    def negative_y_padding(self) -> float:
        """Get a string with the padding value used in the -Y direction.

        Returns
        -------
        float

        Examples
        --------
        >>> from ansys.aedt.core.modules.mesh_icepak import CommonRegion
        >>> obj = CommonRegion()
        >>> obj.negative_y_padding

        """
        return self._get_region_data("-Y", False)

    @property
    def positive_z_padding(self) -> float:
        """Get a string with the padding value used in the +Z direction.

        Returns
        -------
        float

        Examples
        --------
        >>> from ansys.aedt.core.modules.mesh_icepak import CommonRegion
        >>> obj = CommonRegion()
        >>> obj.positive_z_padding

        """
        return self._get_region_data("+Z", False)

    @property
    def negative_z_padding(self) -> float:
        """Get a string with the padding value used in the -Z direction.

        Returns
        -------
        float

        Examples
        --------
        >>> from ansys.aedt.core.modules.mesh_icepak import CommonRegion
        >>> obj = CommonRegion()
        >>> obj.negative_z_padding

        """
        return self._get_region_data("-Z", False)

    @padding_types.setter
    def padding_types(self, values: list[str]) -> None:
        if not isinstance(values, list):
            values = [values] * 6
        for i, direction in enumerate(self._dir_order):
            self._set_region_data(values[i], direction, True)

    @padding_values.setter
    def padding_values(self, values: list[float]) -> None:
        if not isinstance(values, list):
            values = [values] * 6
        for i, direction in enumerate(self._dir_order):
            self._set_region_data(values[i], direction, False)

    @positive_x_padding_type.setter
    def positive_x_padding_type(self, value: float) -> None:
        self._set_region_data(value, "+X", True)

    @negative_x_padding_type.setter
    def negative_x_padding_type(self, value: float) -> None:
        self._set_region_data(value, "-X", True)

    @positive_y_padding_type.setter
    def positive_y_padding_type(self, value: float) -> None:
        self._set_region_data(value, "+Y", True)

    @negative_y_padding_type.setter
    def negative_y_padding_type(self, value: float) -> None:
        self._set_region_data(value, "-Y", True)

    @positive_z_padding_type.setter
    def positive_z_padding_type(self, value: float) -> None:
        self._set_region_data(value, "+Z", True)

    @negative_z_padding_type.setter
    def negative_z_padding_type(self, value: float) -> None:
        self._set_region_data(value, "-Z", True)

    @positive_x_padding.setter
    def positive_x_padding(self, value: float) -> None:
        self._set_region_data(value, "+X", False)

    @negative_x_padding.setter
    def negative_x_padding(self, value: float) -> None:
        self._set_region_data(value, "-X", False)

    @positive_y_padding.setter
    def positive_y_padding(self, value: float) -> None:
        self._set_region_data(value, "+Y", False)

    @negative_y_padding.setter
    def negative_y_padding(self, value: float) -> None:
        self._set_region_data(value, "-Y", False)

    @positive_z_padding.setter
    def positive_z_padding(self, value: float) -> None:
        self._set_region_data(value, "+Z", False)

    @negative_z_padding.setter
    def negative_z_padding(self, value: float) -> None:
        self._set_region_data(value, "-Z", False)

    @property
    def object(self):
        """Get the subregion modeler object.

        Returns
        -------
        ::class::modeler.cad.object_3d.Object3d

        Examples
        --------
        >>> from ansys.aedt.core.modules.mesh_icepak import CommonRegion
        >>> obj = CommonRegion()
        >>> obj.object

        """
        if isinstance(self, Region):
            # use native apis instead of history() for performance reasons
            for o, oo in self._app.modeler.objects_by_name.items():
                child_names = self._app.get_oo_name(self._app.oeditor, o)
                if child_names and child_names[0].startswith("CreateRegion"):
                    return oo
            return None
        else:
            return self._app.modeler.objects_by_name.get(self._name, None)

    @property
    def name(self) -> str:
        """Get the subregion name.

        Returns
        -------
        str

        Examples
        --------
        >>> from ansys.aedt.core.modules.mesh_icepak import CommonRegion
        >>> obj = CommonRegion()
        >>> obj.name

        """
        return self.object.name

    @name.setter
    def name(self, value: str) -> None:
        try:
            if self._app.modeler.objects_by_name[self._name].name != value:
                self._app.modeler.objects_by_name[self._name].name = value
        except KeyError:
            if self._app.modeler.objects_by_name[value].history().command == "CreateSubRegion":
                self._name = value

    def _set_region_data(self, value, direction=None, padding_type: bool = True):
        self._update_region_data()
        region = self.object
        create_region = region.history()
        set_type = ["Data", "Type"][int(padding_type)]
        create_region.properties[f"{direction} Padding {set_type}"] = value

    def _update_region_data(self) -> None:
        region = self.object
        if (
            hasattr(self._app, "logger") and self._app.logger and hasattr(self._app.logger, "suspend_logic")
        ):  # pragma: no cover
            with self._app.logger.suspend_logging():
                create_region = region.history()
        else:
            create_region = region.history()
        self._padding_type = []
        self._padding_value = []
        for padding_direction in ["+X", "-X", "+Y", "-Y", "+Z", "-Z"]:
            self._padding_type.append(create_region.properties[f"{padding_direction} Padding Type"])
            self._padding_value.append(create_region.properties[f"{padding_direction} Padding Data"])
            self._coordinate_system = create_region.properties["Coordinate System"]

    def _get_region_data(self, direction=None, padding_type: bool = True):
        self._update_region_data()
        idx = self._dir_order.index(direction)
        if padding_type:
            return self._padding_type[idx]
        else:
            return self._padding_value[idx]


class SubRegion(CommonRegion):
    """Provides Icepak mesh subregions properties and methods.

    Examples
    --------
    >>> from ansys.aedt.core.modules.mesh_icepak import SubRegion
    >>> obj = SubRegion()

    """

    def __init__(self, app, parts, name: str | None = None) -> None:
        if name is None:
            name = generate_unique_name("SubRegion")
        super(SubRegion, self).__init__(app, name)
        self.create(0, "Percentage Offset", name, parts)

    def create(
        self, padding_values: list[str | float], padding_types: list[str], region_name: str, parts: list[str]
    ) -> bool:
        """Create subregion object.

        Parameters
        ----------
        padding_values : list of str or float
            List of padding values to apply in each direction, in the following order:
            +X, -X, +Y, -Y, +Z, -Z.
        padding_types : list of str
            List of padding types to apply in each direction, in the following order:
            +X, -X, +Y, -Y, +Z, -Z.
        region_name : str
            Name to assign to the subregion.
        parts : list of str
            Parts to be included in the subregion.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.core.modules.mesh_icepak import SubRegion
        >>> obj = SubRegion()
        >>> obj.create(padding_values=[1, 2, 3], padding_types=["Box1"], region_name=1, parts=["Box1"])

        """
        try:
            if (
                self.object is not None and self._app.modeler.objects_by_name.get(self.object.name, False)
            ) or self._app.modeler.objects_by_name.get(region_name, False):
                self._app.logger.error(f"{self.object.name} already exists in the design.")
                return False
            if not isinstance(parts, list):
                objects = [parts]
                if not isinstance(objects[0], str):
                    objects = [o.name for o in objects]
            self._app.modeler.create_subregion(padding_values, padding_types, parts, region_name)
            return True
        except Exception:
            return False

    def delete(self) -> bool:
        """Delete the subregion object.

        Returns
        -------
        bool
           ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.core.modules.mesh_icepak import SubRegion
        >>> obj = SubRegion()
        >>> obj.delete()

        """
        try:
            self.object.delete()
            self._app.mesh.meshregions.remove(
                [mo for mo in self._app.mesh.meshregions.values() if mo.subregion == self][0]
            )
            return True
        except Exception:
            return False

    @property
    def parts(self) -> dict:
        """Parts included in the subregion.

        Returns
        -------
        dict
            Dictionary with the part names as keys and ::class::modeler.cad.object_3d.Object3d as values.

        Examples
        --------
        >>> from ansys.aedt.core.modules.mesh_icepak import SubRegion
        >>> obj = SubRegion()
        >>> obj.parts

        """
        if self.object:
            history = self.object.history().properties
            return {obj_name: self._app.modeler[obj_name] for obj_name in history["Part Names"].split(",")}
        else:
            return {}

    @parts.setter
    def parts(self, parts: list[str]) -> None:
        """Parts included in the subregion.

        Parameters
        ----------
        parts : List[str]
            List of strings containing all the parts that must be included in the subregion.
        """
        self._app.modeler.reassign_subregion(self, parts)


class Region(CommonRegion):
    """Provides Icepak global mesh region properties and methods.

    Examples
    --------
    >>> from ansys.aedt.core.modules.mesh_icepak import Region
    >>> obj = Region()

    """

    def __init__(self, app) -> None:
        super(Region, self).__init__(app=app, name=None)
        try:
            self._update_region_data()
        except AttributeError:
            pass


class MeshSettings(PyAedtBase):
    """Manages mesh settings.

    It can be used like a dictionary. Available keys change according
    to the type of settings chosen (manual or automatic).

    Examples
    --------
    >>> from ansys.aedt.core.modules.mesh_icepak import MeshSettings
    >>> obj = MeshSettings()

    """

    _automatic_mesh_settings = {
        "MeshRegionResolution": 3,
        "GeometryBasedMeshing": True,
    }  # min: 1, max: 5
    _common_mesh_settings = {
        "FacetLevel": 3,
        "ProximitySizeFunction": True,
        "CurvatureSizeFunction": True,
        "EnableTransition": False,
        "OptimizePCBMesh": True,
        "Enable2DCutCell": False,
        "EnforceCutCellMeshing": False,
        "Enforce2dot5DCutCell": False,
        "StairStepMeshing": False,
        "StairStepSliderMeshing": False,
        "NonHDMesherEnabled": False,
        "MeshMethod": "MesherHD",
        "ComputeGap": True,
    }
    _manual_mesh_settings = {
        "MaxElementSizeX": "0.02mm",
        "MaxElementSizeY": "0.02mm",
        "MaxElementSizeZ": "0.03mm",
        "MinElementsInGap": "3",
        "MinElementsOnEdge": "2",
        "MaxSizeRatio": "2",
        "NoOGrids": False,
        "EnableMLM": True,
        "EnforeMLMType": "3D",
        "MaxLevels": "0",
        "BufferLayers": "0",
        "UniformMeshParametersType": "Average",
        "2DMLMType": "2DMLM_None",
        "MinGapX": "1mm",
        "MinGapY": "1mm",
        "MinGapZ": "1mm",
    }

    def __init__(self, mesh_class, app) -> None:
        self._app = app
        self._mesh_class = mesh_class
        self._instance_settings = self._common_mesh_settings.copy()
        self._instance_settings.update(self._manual_mesh_settings.copy())
        self._instance_settings.update(self._automatic_mesh_settings.copy())

    def parse_settings_as_args(self) -> list:
        """Parse mesh region settings.

        Returns
        -------
        List
            Arguments to pass to native APIs.

        Examples
        --------
        >>> from ansys.aedt.core.modules.mesh_icepak import MeshSettings
        >>> obj = MeshSettings()
        >>> obj.parse_settings_as_args()

        """
        out = []
        for k, v in self._instance_settings.items():
            out.append(k + ":=")
            if k in ["MaxElementSizeX", "MaxElementSizeY", "MaxElementSizeZ", "MinGapX", "MinGapY", "MinGapZ"]:
                v = self._app.value_with_units(v, self._app.modeler.model_units)
            out.append(v)
        out += ["UserSpecifiedSettings:=", self._mesh_class.manual_settings]
        return out

    def parse_settings_as_dictionary(self) -> dict:
        """Parse mesh region settings.

        Returns
        -------
        dict
            Settings of the subregion.

        Examples
        --------
        >>> from ansys.aedt.core.modules.mesh_icepak import MeshSettings
        >>> obj = MeshSettings()
        >>> obj.parse_settings_as_dictionary()

        """
        out = {}
        for k in self.keys():
            v = self._instance_settings[k]
            if k in ["MaxElementSizeX", "MaxElementSizeY", "MaxElementSizeZ", "MinGapX", "MinGapY", "MinGapZ"]:
                v = self._app.value_with_units(v, getattr(self._app.modeler, "model_units"))
            out[k] = v
        return out

    def keys(self) -> set:
        """Get mesh region settings keys.

        Returns
        -------
        dict_keys
            Available settings keys.

        Examples
        --------
        >>> from ansys.aedt.core.modules.mesh_icepak import MeshSettings
        >>> obj = MeshSettings()
        >>> obj.keys()

        """
        if self._mesh_class.manual_settings:
            return set(self._manual_mesh_settings.keys()) | set(self._common_mesh_settings.keys())
        else:
            return set(self._automatic_mesh_settings.keys()) | set(self._common_mesh_settings.keys())

    def values(self):
        """Get mesh region settings values.

        Returns
        -------
        dict_values
            Settings values.

        Examples
        --------
        >>> from ansys.aedt.core.modules.mesh_icepak import MeshSettings
        >>> obj = MeshSettings()
        >>> obj.values()

        """
        return self.parse_settings_as_dictionary().values()

    def items(self):
        """Get mesh region settings items.

        Returns
        -------
        dict_items
            Settings items.

        Examples
        --------
        >>> from ansys.aedt.core.modules.mesh_icepak import MeshSettings
        >>> obj = MeshSettings()
        >>> obj.items()

        """
        return self.parse_settings_as_dictionary().items()

    def __repr__(self) -> str:
        return repr(self.parse_settings_as_dictionary())

    def __getitem__(self, key):
        if key == "Level":  # backward compatibility
            key = "MeshRegionResolution"
        if key in self.keys():
            return self._instance_settings[key]
        else:
            raise KeyError("Setting not available.")

    def __setitem__(self, key, value):
        value = _units_assignment(value)
        if key == "Level":  # backward compatibility
            key = "MeshRegionResolution"
        if key in self.keys():
            if key == "MeshRegionResolution":
                try:
                    value = int(value)
                    if value < 1:
                        self._app.logger.warning(
                            'Minimum resolution value is 1. `"MeshRegionResolution"` has been set to 1.'
                        )
                        value = 1
                    if value > 5:
                        self._app.logger.warning(
                            'Maximum resolution value is 5. `"MeshRegionResolution"` has been set to 5.'
                        )
                        value = 5
                except TypeError:
                    pass
            self._instance_settings[key] = value
        else:
            self._app.logger.error("Setting not available.")

    def __delitem__(self, key):
        self._app.logger.error("Setting cannot be removed.")

    def __iter__(self):
        return iter(self.keys())

    def __len__(self) -> int:
        return len(self.keys())

    def __contains__(self, x) -> bool:
        return x in self.keys()


class MeshRegionCommon(BinaryTreeNode, PyAedtBase):
    """Manages Icepak mesh region settings.

    Examples
    --------
    >>> from ansys.aedt.core.modules.mesh_icepak import MeshRegionCommon
    >>> obj = MeshRegionCommon()

    """

    def __init__(self, app: FieldAnalysisIcepak, units: str, name: str) -> None:

        self._app = app
        self._name = name
        self._manual_settings = False
        self._model_units = units
        self._settings = None
        self.__child_object = None

        if self._name == "Settings":
            self._has_getobject = False
        else:
            self._has_getobject = _has_get_obj_data(self._child_object)

    @property
    def settings(self):
        """Get the mesh region settings."""
        if self._settings and not self._has_getobject:
            return self._settings

        if self._settings is None:
            self._settings = MeshSettings(self, self._app)
            if self._has_getobject:
                region_settings = _get_obj_data(self._child_object) or {}
            else:
                region_settings = self._get_global_region_settings() or {}

            self._manual_settings = region_settings.get("UserSpecifiedSettings", False)
            for key, value in region_settings.items():
                if key in self._settings:
                    self._settings[key] = value
        return self._settings

    #
    # @pyaedt_function_handler()
    # def _initialize_tree_node(self) -> bool:
    #     child_object = self._child_object
    #     if child_object:
    #         BinaryTreeNode.__init__(self, self._name, child_object, False, app=self._app)
    #         return True
    #     return False
    #
    # @property
    # def _child_object(self):
    #     """Object-oriented properties.
    #
    #     Returns
    #     -------
    #     class:`ansys.aedt.core.modeler.cad.elements_3d.BinaryTreeNode`
    #
    #     """
    #     if not self.__child_object:
    #         design_childs = self._app.get_oo_name(self._app.odesign)
    #
    #         if "Mesh" in design_childs:
    #             cc = self._app.get_oo_object(self._app.odesign, "Mesh")
    #             cc_names = self._app.get_oo_name(cc)
    #             if self._name in cc_names:
    #                 self.__child_object = self._app.get_oo_object(cc, self._name)
    #     return self.__child_object

    # if self._name == "Settings":
    #     return True
    #
    # if self._child_object:
    #     child_object = self._app.get_oo_object(self._app.odesign, f"Mesh/{self._name}")
    #     if child_object:
    #         BinaryTreeNode.__init__(self, self._name, child_object, False, app=self._app)
    #         return True
    # return False

    # @property
    # def manual_settings(self) -> bool:
    #     """Whether manual mesh settings are enabled."""
    #     return self._manual_settings
    #
    # @manual_settings.setter
    # def manual_settings(self, value: bool) -> None:
    #     self._manual_settings = value
    #     self.update()

    # def __getattr__(self, name: str):
    #     if name == "UserSpecifiedSettings":
    #         return self.manual_settings
    #     if not name.startswith("_"):
    #         mesh_settings = self.__dict__.get("_settings")
    #         if mesh_settings is not None and name in mesh_settings:
    #             return mesh_settings[name]
    #     raise AttributeError(f"{type(self).__name__!s} object has no attribute {name!r}")
    #
    # def __setattr__(self, name: str, value):
    #     skip_properties = [
    #         "manual_settings",
    #         "settings",
    #         "_name",
    #         "_model_units",
    #         "_app",
    #         "_assignment",
    #         "assignment",
    #         "enable",
    #         "name",
    #     ]
    #     skip_properties_binary = [
    #         "_props",
    #         "_saved_root_name",
    #         "_get_child_obj_arg",
    #         "_node",
    #         "child_object",
    #         "auto_update",
    #         "_children",
    #         "_children_loading",
    #         "_children_loaded",
    #         "_segments",
    #         "_tree_node_initialized",
    #         "_tree_node_initializing",
    #         "_BinaryTreeNode__first_level",
    #         "_BinaryTreeNode__child_object",
    #     ]
    #     if name == "UserSpecifiedSettings":
    #         self.manual_settings = value
    #     elif name in skip_properties_binary:
    #         super(BinaryTreeNode, self).__setattr__(name, value)
    #     elif name not in skip_properties and not name.startswith("_"):
    #         mesh_settings = self.settings
    #         if name in mesh_settings:
    #             mesh_settings[name] = value
    #         else:
    #             self._app.logger.error(
    #                 f"Setting name {name} is not available. Available parameters are: "
    #                 f"{', '.join(mesh_settings.keys())}."
    #             )
    #     else:
    #         super(MeshRegionCommon, self).__setattr__(name, value)


class MeshRegion(BinaryTreeNode, PyAedtBase):
    """Provides Icepak subregions mesh properties and methods."""

    def __init__(self, app: FieldAnalysisIcepak, assignment: str, name: str) -> None:

        self._assignment = assignment
        self.enable = True
        if settings.aedt_version > "2023.2" and assignment is not None:
            if not isinstance(assignment, list):
                objects = [assignment]
            if (
                objects[0] not in self._app.modeler.user_defined_components
                and self._app.modeler[objects[0]]
                and self._app.modeler[objects[0]].history().command == "CreateSubRegion"
            ):
                self._assignment = objects[0]
            else:
                self._assignment = SubRegion(app, objects)
        else:
            self._assignment = assignment
        if self._assignment is not None:
            self.create()

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

    def _parse_assignment_value(self, assignment=None):
        if assignment is None:
            assignment = self.assignment
        a = []
        if isinstance(assignment, SubRegion):
            a += ["Objects:=", [assignment.name]]
        else:
            if any(o in self._app.modeler.object_names for o in assignment):
                obj_assignment = [o for o in assignment if o in self._app.modeler.object_names]
                a += ["Objects:=", obj_assignment]
            if any(o in self._app.modeler.user_defined_components for o in assignment):
                obj_assignment = [o for o in assignment if o in self._app.modeler.user_defined_components]
                a += ["Submodels:=", obj_assignment]
        return a

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
        if self._child_object:
            self._name = str(self.properties["Name"])
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._app.odesign.ChangeProperty(
            [
                "NAME:AllTabs",
                [
                    "NAME:Icepak",
                    ["NAME:PropServers", f"MeshRegion:{self.name}"],
                    ["NAME:ChangedProps", ["NAME:Name", "Value:=", value]],
                ],
            ]
        )
        self._app.modeler.refresh()
        self._name = value
        result = self._initialize_tree_node()
        if isinstance(self.assignment, SubRegion) and result:
            self._assignment = self.assignment

    @pyaedt_function_handler()
    def update(self) -> bool:
        """Update mesh region settings with the settings in the object variable.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.EditMeshRegion

        Examples
        --------
        >>> from ansys.aedt.core.modules.mesh_icepak import MeshRegion
        >>> obj = MeshRegion()
        >>> obj.update()

        """
        args = ["NAME:" + self.name, "Enable:=", self.enable]
        args += self.settings.parse_settings_as_args()
        args += self._parse_assignment_value()
        args += ["UserSpecifiedSettings:=", self.manual_settings]
        try:
            self._app.omeshmodule.EditMeshRegion(self.name, args)
            # return self._initialize_tree_node()
            return True
        except GrpcApiError:  # pragma : no cover
            return False

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

    @property
    def manual_settings(self) -> bool:
        """Whether manual mesh settings are enabled."""
        return self._manual_settings

    @manual_settings.setter
    def manual_settings(self, value: bool) -> None:
        self._manual_settings = value
        self.update()

    @property
    def settings(self):
        """Get the mesh region settings."""
        if self._settings and not self._has_getobject:
            return self._settings

        if self._settings is None:
            self._settings = MeshSettings(self, self._app)
            if self._has_getobject:
                region_settings = _get_obj_data(self._child_object) or {}
            else:
                region_settings = self._get_global_region_settings() or {}

            self._manual_settings = region_settings.get("UserSpecifiedSettings", False)
            for key, value in region_settings.items():
                if key in self._settings:
                    self._settings[key] = value
        return self._settings

    @property
    def assignment(self) -> list:
        """List of objects included in mesh region.

        Returns
        -------
        list

        Examples
        --------
        >>> from ansys.aedt.core.modules.mesh_icepak import MeshRegion
        >>> obj = MeshRegion()
        >>> obj.assignment

        """
        if isinstance(self._assignment, SubRegion):
            mesh_oo = self._app.get_oo_object(self._app.odesign, "Mesh")
            if self.name in self._app.get_oo_name(self._app.odesign, "Mesh"):
                # try to update name, APIs lacking an easy method before 242
                if self._app.settings.aedt_version < "2024.2":  # pragma: no cover
                    parts = []
                    subparts = []
                    region_props = self._app.get_oo_properties(mesh_oo, self.name)
                    if "Parts" in region_props:
                        parts = self._app.get_oo_property_value(mesh_oo, self.name, "Parts")
                    if "Submodels" in region_props:
                        subparts = self._app.get_oo_property_value(mesh_oo, self.name, "Submodels")
                    if not isinstance(parts, list):
                        parts = [parts]
                    if not isinstance(subparts, list):
                        subparts = [subparts]
                    parts += subparts
                    sub_regions = self._app.modeler.non_model_objects
                    for sr in sub_regions:
                        p1 = []
                        p2 = []
                        if "Part Names" in self._app.modeler[sr].history().properties:
                            p1 = self._app.modeler[sr].history().properties.get("Part Names", None)
                            if not isinstance(p1, list):
                                p1 = [p1]
                        elif "Submodel Names" in self._app.modeler[sr].history().properties:
                            p2 = self._app.modeler[sr].history().properties.get("Submodel Names", None)
                            if not isinstance(p2, list):
                                p2 = [p2]
                        p1 += p2
                        if "CreateSubRegion" == self._app.modeler[sr].history().command and all(p in p1 for p in parts):
                            self._assignment.name = sr
                else:
                    self._assignment.name = self._app.get_oo_property_value(mesh_oo, self.name, "Assignment")
            return self._assignment
        elif isinstance(self._assignment, list):
            return self._assignment
        else:
            return [self._assignment]

    @assignment.setter
    def assignment(self, value: list) -> None:
        arg = ["NAME:Assignment"] + self._parse_assignment_value(value)
        try:
            self._app.omeshmodule.ReassignMeshRegion(self.name, arg)
            self._assignment = value
        except GrpcApiError:  # pragma : no cover
            self._app.logger.error("Mesh region reassignment failed.")

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


class GlobalMeshRegion:
    """Icepak global mesh properties and methods.

    Examples
    --------
    >>> from ansys.aedt.core.modules.mesh_icepak import GlobalMeshRegion
    >>> obj = GlobalMeshRegion()

    """

    def __init__(self, app: FieldAnalysisIcepak) -> None:
        self._app = app
        self._name = "Global"

        self._manual_settings = False

        self.__settings = None

        # Assign the global mesh region to a Region object if it exists in the modeler solid bodies
        self.assignment = None
        if "Region" in app.modeler.solid_bodies:
            self.assignment = Region(app)

        # TODO: AEDT API does not have GetObjData for the global mesh region yeet
        self._has_getobject = False

    @property
    def settings(self):
        """Get the mesh region settings."""
        if self.__settings and not self._has_getobject:
            return self.__settings

        if self.__settings is None:
            self.__settings = MeshSettings(self, self._app)
            region_settings = self._get_global_region_settings() or {}

            self._manual_settings = region_settings.get("UserSpecifiedSettings", False)
            for key, value in region_settings.items():
                if key in self.__settings:
                    self.__settings[key] = value
        return self.__settings

    @property
    def manual_settings(self) -> bool:
        """Whether manual mesh settings are enabled."""
        return self._manual_settings

    @manual_settings.setter
    def manual_settings(self, value: bool) -> None:
        self._manual_settings = value
        self.update()

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
    def update(self) -> bool:
        """Update mesh region settings with the settings in the object variable.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.EditGlobalMeshRegion

        Examples
        --------
        >>> from ansys.aedt.core.modules.mesh_icepak import GlobalMeshRegion
        >>> obj = GlobalMeshRegion()
        >>> obj.update()

        """
        args = ["NAME:Settings"]
        args += self.settings.parse_settings_as_args()
        args += ["UserSpecifiedSettings:=", self.manual_settings]
        if self.assignment is not None:
            args += ["Objects:=", [self.assignment.name]]
        try:
            self._app.omeshmodule.EditGlobalMeshRegion(args)
            return True
        except GrpcApiError:  # pragma : no cover
            return False


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
        for region in self.region_names:
            if region not in self.__regions:
                self.__regions[region] = MeshRegion(mesh=self, name=region, props={})

        active_names = set(self.region_names)
        for region_name in list(self.__regions):
            if region_name not in active_names:
                del self.__regions[region_name]

        return self.__regions

    @property
    def operation_names(self) -> list[str]:
        """Return the names of all mesh operations."""
        return self._get_mesh_names()[1]

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
    def meshregions_dict(self) -> dict:
        """Get mesh regions in the design.

        Returns
        -------
        dict
            Dictionary with mesh region names as keys and mesh region objects as values.

        Examples
        --------
        >>> from ansys.aedt.core.modules.mesh_icepak import IcepakMesh
        >>> obj = IcepakMesh()
        >>> obj.meshregions_dict

        """
        return {mr.name: mr for mr in self.meshregions}

    @property
    def boundingdimension(self) -> list:
        """Bounding dimension.

        Examples
        --------
        >>> from ansys.aedt.core.modules.mesh_icepak import IcepakMesh
        >>> obj = IcepakMesh()
        >>> obj.boundingdimension

        """
        return self._app.modeler.get_bounding_dimension()

    @pyaedt_function_handler()
    def _get_mesh_names(self) -> tuple[list[str], list[str]]:
        """Return mesh region and operation names."""
        region_names = []
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
                object_type = child_object.GetObjType()
                if object_type.lower() in ["mesh region", "meshregion"]:
                    region_names.append(name)
                elif object_type.lower() in ["mesh operation", "meshoperation"]:
                    operation_names.append(name)

        return region_names, operation_names

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
