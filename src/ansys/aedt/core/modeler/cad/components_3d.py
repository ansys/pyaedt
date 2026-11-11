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

import os
import re
import secrets
from typing import TYPE_CHECKING

from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.edb import Edb
from ansys.aedt.core.generic.constants import Axis
from ansys.aedt.core.generic.data_handlers import _dict2arg
from ansys.aedt.core.generic.file_utils import _uname
from ansys.aedt.core.generic.general_methods import _merge_props
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.props import Props as UserDefinedComponentProps
from ansys.aedt.core.generic.protocols import _AppWithOProject
from ansys.aedt.core.internal.desktop_sessions import _edb_sessions
from ansys.aedt.core.internal.errors import GrpcApiError
from ansys.aedt.core.modeler.cad.elements_3d import BinaryTreeNode

if TYPE_CHECKING:
    from ansys.aedt.core import Icepak
    from ansys.aedt.core.generic.constants import Axis
    from ansys.aedt.core.modeler.cad.object_3d import Object3d
    from ansys.aedt.core.modeler.cad.primitives_3d import Primitives3D


class UserDefinedComponentParameters(dict):
    """Provide user defined component parameters."""

    def __setitem__(self, key, value):
        try:
            self._component._app.oeditor.ChangeProperty(
                [
                    "NAME:AllTabs",
                    [
                        "NAME:Parameters",
                        ["NAME:PropServers", self._component.name],
                        ["NAME:ChangedProps", ["NAME:" + key, "Value:=", str(value)]],
                    ],
                ]
            )
            dict.__setitem__(self, key, value)
        except Exception:
            self._component._app.logger.warning("Property %s has not been edited.Check if readonly", key)

    def __init__(self, component, *args, **kw) -> None:
        dict.__init__(self, *args, **kw)
        self._component = component


class UserDefinedComponent(BinaryTreeNode, PyAedtBase):
    """Manages object attributes for 3DComponent and User Defined Model instances.

    Parameters
    ----------
    primitives : :class:`ansys.aedt.core.modeler.cad.primitives_3d.Primitives3D`
        Inherited parent object.
    name : str, optional
        Name of the component. The default value is ``None``.
    props : dict, optional
        Dictionary of properties. The default value is ``None``.
    component_type : str, optional
        Type of the component. The default value is ``None``.

    Examples
    --------
    Basic usage demonstrated with an HFSS design:

    >>> from ansys.aedt.core import Hfss
    >>> aedtapp = Hfss()
    >>> prim = aedtapp.modeler.user_defined_components

    Obtain user defined component names, to return a
    :class:`ansys.aedt.core.modeler.cad.components_3d.UserDefinedComponent`.

    >>> component_names = aedtapp.modeler.user_defined_components
    >>> component = aedtapp.modeler[component_names["3DC_Cell_Radome_In1"]]

    """

    def __init__(
        self,
        primitives: Primitives3D,
        name: str | None = None,
        props: dict | None = None,
        component_type: str | None = None,
        definition_name: str | None = None,
    ) -> None:
        self._primitives = primitives
        self._app = self._primitives._app

        if name:
            self._m_name = name
        else:
            self._m_name = _uname()

        # Props can not be retrieved from AEDT file, so only components created by PyAEDT will have it
        self._legacy_props = {}

        # Internal variables
        self._fix_udm_props = [
            "General[Name]",
            "Group",
            "Target Coordinate System",
            "Target Coordinate System/Choices",
            "Info[Name]",
            "Location",
            "Location/Choices",
            "Company",
            "Date",
            "Purpose",
            "Version",
        ]

        # Get definition name (parent component)
        self.definition_name = definition_name or None
        if definition_name is None:
            defined_components = self._app.oeditor.Get3DComponentDefinitionNames()
            defined_components = defined_components if defined_components else []
            for component in defined_components:
                if self._m_name in self._app.oeditor.Get3DComponentInstanceNames(component):
                    self.definition_name = component
                    break

        if component_type:
            self._legacy_props = {
                "TargetCS": "Global",
                "SubmodelDefinitionName": self.definition_name or self._m_name,
                "ComponentPriorityLists": {},
                "NextUniqueID": 0,
                "MoveBackwards": False,
                "DatasetType": "ComponentDatasetType",
                "DatasetDefinitions": {},
                "BasicComponentInfo": {
                    "ComponentName": self.definition_name or self._m_name,
                    "Company": "",
                    "Company URL": "",
                    "Model Number": "",
                    "Help URL": "",
                    "Version": "1.0",
                    "Notes": "",
                    "IconType": "",
                },
                "GeometryDefinitionParameters": {"VariableOrders": {}},
                "DesignDefinitionParameters": {"VariableOrders": {}},
                "MaterialDefinitionParameters": {"VariableOrders": {}},
                "DefReferenceCSID": 1,
                "MapInstanceParameters": "DesignVariable",
                "UniqueDefinitionIdentifier": "89d26167-fb77-480e-a7ab-"
                + "".join(secrets.choice("abcdef0123456789") for _ in range(int(12))),
                "OriginFilePath": "",
                "IsLocal": False,
                "ChecksumString": "",
                "ChecksumHistory": [],
                "VersionHistory": [],
                "NativeComponentDefinitionProvider": {"Type": component_type},
                "InstanceParameters": {"GeometryParameters": "", "MaterialParameters": "", "DesignParameters": ""},
            }

            if props:
                if "NativeComponentDefinitionProvider" in props or any(key in self._legacy_props for key in props):
                    _merge_props(self._legacy_props, props)
                else:
                    _merge_props(self._legacy_props["NativeComponentDefinitionProvider"], props)

            self.native_properties = self._legacy_props["NativeComponentDefinitionProvider"]

        self.__layout_component = None
        self.__is_3d_component = None
        self.__parameters = None

        self.__child_object = None
        # TODO: GetObjData is not available yet
        self._has_getobject = False

    def __str__(self) -> str:
        return f"""
         {type(self)}
         is_3d_component: {self.is_3d_component}   parts: {self.parts}
         --- read/write properties  ----
         name: {self.name}
         group_name: {self.group_name}
         mesh_assembly: {self.mesh_assembly}
         parameters: {self.parameters}
         target_coordinate_system: {self.target_coordinate_system}
         """

    @pyaedt_function_handler()
    def _initialize_tree_node(self) -> bool:
        if self._child_object:
            BinaryTreeNode.__init__(self, self._m_name, self._child_object, False, app=self._app)
            return True
        return False

    @property
    def _child_object(self):
        """Object-oriented properties.

        Returns
        -------
        AEDT object if any or None

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> component_names = app.modeler.user_defined_component_names
        >>> component = app.modeler.user_defined_components[component_names[0]]
        >>> component.child_object.GetChildNames()

        """
        if not self.__child_object:
            cc_names = self._primitives.user_defined_component_names
            if self._m_name in cc_names:
                self.__child_object = self._app.get_oo_object(self._app.oeditor, self._m_name)
        return self.__child_object

    @property
    def props(self) -> UserDefinedComponentProps:
        """Properties of the component.
        If the component is not created by PyAEDT, it will be empty.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> component_names = app.modeler.user_defined_component_names
        >>> component = app.modeler.user_defined_components[component_names[0]]
        >>> component.props

        """
        if self._legacy_props:
            return UserDefinedComponentProps(self, self._legacy_props)
        return UserDefinedComponentProps(self, self._legacy_props)

    @property
    def name(self) -> str:
        """Name of the component.

        Returns
        -------
        str
           Name of the object.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> component_names = app.modeler.user_defined_component_names
        >>> component = app.modeler.user_defined_components[component_names[0]]
        >>> component.name

        """
        return self._m_name

    @name.setter
    def name(self, component_name: str) -> None:
        not_valid_names = self._primitives.user_defined_component_names + self._primitives.object_names
        if component_name not in not_valid_names:
            if component_name != self._m_name:
                pcs = ["NAME:Name", "Value:=", component_name]
                self._change_property(pcs)
                self._primitives.user_defined_components.update({component_name: self})
                del self._primitives.user_defined_components[self._m_name]
                self._m_name = component_name
        else:  # pragma: no cover
            self._app.logger.warning("Name %s already assigned in the design", component_name)

    @property
    def layout_component(self) -> LayoutComponent | None:
        """Layout component object.

        Returns
        -------
        :class:`ansys.aedt.core.modeler.cad.components_3d.LayoutComponent`
            Layout Component.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> component_names = app.modeler.user_defined_component_names
        >>> component = app.modeler.user_defined_components[component_names[0]]
        >>> component.layout_component

        """
        if self.__layout_component is None and "Show Layout" in self.properties:
            self.__layout_component = LayoutComponent(self)
        return self.__layout_component

    @property
    def group_name(self) -> str:
        """Group the component belongs to.

        Returns
        -------
        str
            Name of the group.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> component_names = app.modeler.user_defined_component_names
        >>> component = app.modeler.user_defined_components[component_names[0]]
        >>> component.group_name

        """
        group = "Model"
        if "Group" in self.properties:
            group = self.properties["Group"]
        return group

    @group_name.setter
    def group_name(self, name: str) -> None:
        if "Group" in self.properties and name not in self._primitives.groups:
            self._primitives.create_group(group_name=name, components=self.name)
        else:
            pcs = ["NAME:Group", "Value:=", name]
            self._change_property(pcs)

    @property
    def is_3d_component(self) -> bool:
        """Whether the object is a 3D component.

        Returns
        -------
        bool
           ``True`` if a 3D Component, ``False`` if a user-defined model.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> component_names = app.modeler.user_defined_component_names
        >>> component = app.modeler.user_defined_components[component_names[0]]
        >>> component.is_3d_component

        """
        if self.__is_3d_component is None:
            definitions = list(self._app.oeditor.Get3DComponentDefinitionNames())
            for comp in definitions:
                if self.name in self._primitives.oeditor.Get3DComponentInstanceNames(comp):
                    self.__is_3d_component = True
                    break
            if not self.__is_3d_component:
                self.__is_3d_component = False
        return self.__is_3d_component

    @property
    def mesh_assembly(self) -> bool | None:
        """Mesh assembly flag.

        Returns
        -------
        bool
           ``True`` if mesh assembly is checked, ``None`` if a user-defined model.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> component_names = app.modeler.user_defined_component_names
        >>> component = app.modeler.user_defined_components[component_names[0]]
        >>> component.mesh_assembly

        """
        key = "Do Mesh Assembly"
        if self.is_3d_component and key in self.properties:
            ma = self.properties[key]
            return ma
        else:
            return None

    @mesh_assembly.setter
    def mesh_assembly(self, ma: bool) -> None:
        key = "Do Mesh Assembly"
        if self.is_3d_component and isinstance(ma, bool) and key in self.properties:
            self.properties[key] = ma

    @property
    def parameters(self) -> UserDefinedComponentParameters:
        """Component parameters.

        Returns
        -------
        dict
            :class:`ansys.aedt.core.modeler.cad.components_3d.UserDefinedComponentParameters`.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> component_names = app.modeler.user_defined_component_names
        >>> component = app.modeler.user_defined_components[component_names[0]]
        >>> component.parameters

        """
        if self.__parameters is None:
            if self.is_3d_component:
                parameters_tuple = list(self._primitives.oeditor.Get3DComponentParameters(self.name))
                parameters = {}
                for parameter in parameters_tuple:
                    if parameter[0] in self.properties:
                        value = self.properties[parameter[0]]
                        parameters[parameter[0]] = value
                self.__parameters = UserDefinedComponentParameters(self, parameters)
            else:
                props = list(self.properties)
                parameters_aedt = list(set(props) - set(self._fix_udm_props))
                parameter_name = [par for par in parameters_aedt if not re.findall(r"/", par)]
                parameters = {}
                for parameter in parameter_name:
                    if parameter in self.properties:
                        value = self.properties[parameter]
                        parameters[parameter] = value
                self.__parameters = UserDefinedComponentParameters(self, parameters)
        return self.__parameters

    @property
    def parts(self) -> dict[str, Object3d]:
        """Dictionary of objects that belong to the user-defined component.

        Returns
        -------
        dict[str, :class:`ansys.aedt.core.modeler.cad.object_3d.Object3d`]

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> component_names = app.modeler.user_defined_component_names
        >>> component = app.modeler.user_defined_components[component_names[0]]
        >>> component.parts

        """
        if self.is_3d_component:
            component_parts = list(self._app.oeditor.Get3DComponentPartNames(self.name))
        else:
            component_parts = list(self.properties)

        parts_id = [
            self._primitives.objects_by_name[part].id
            for part in self._primitives.objects_by_name.keys()
            if part in component_parts
        ]
        parts_dict = {part_id: self._primitives.objects[part_id] for part_id in parts_id}
        return parts_dict

    @property
    def target_coordinate_system(self) -> str | None:
        """Target coordinate system.

        Returns
        -------
        str
            Name of the target coordinate system.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> component_names = app.modeler.user_defined_component_names
        >>> component = app.modeler.user_defined_components[component_names[0]]
        >>> component.target_coordinate_system

        """
        coordinate_system = None
        if "Target Coordinate System" in self.properties:
            coordinate_system = self.properties["Target Coordinate System"]
        return coordinate_system

    @target_coordinate_system.setter
    def target_coordinate_system(self, value: str) -> None:
        if "Target Coordinate System" in self.properties and "Target_Coordinate_System_Choices" in dir(
            self.child_object
        ):
            options = self.child_object.Target_Coordinate_System_Choices
            if value in options:
                pcs = ["NAME:Target Coordinate System", "Value:=", value]
                self._change_property(pcs)

    @property
    def bounding_box(self) -> list:
        """Get bounding dimension of a user defined model.

        Returns
        -------
        list
            List of floats containing [x_min, y_min, z_min, x_max, y_max, z_max].

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> component_names = app.modeler.user_defined_component_names
        >>> component = app.modeler.user_defined_components[component_names[0]]
        >>> component.bounding_box

        """
        bb = [float("inf")] * 3 + [float("-inf")] * 3
        for _, obj in self.parts.items():
            bbox = obj.bounding_box
            bb = [min(bb[i], bbox[i]) for i in range(3)] + [max(bb[i + 3], bbox[i + 3]) for i in range(3)]
        return bb

    @property
    def center(self) -> list:
        """Get center coordinates of a user defined model.

        Returns
        -------
        list
            List of floats containing [x_center, y_center, z_center].

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> component_names = app.modeler.user_defined_component_names
        >>> component = app.modeler.user_defined_components[component_names[0]]
        >>> component.center

        """
        x_min, y_min, z_min, x_max, y_max, z_max = self.bounding_box
        x_center = (x_min + x_max) / 2
        y_center = (y_min + y_max) / 2
        z_center = (z_min + z_max) / 2
        return [x_center, y_center, z_center]

    @pyaedt_function_handler()
    def delete(self) -> None:
        """Delete the object.

        The project must be saved after the operation to update the list
        of names for user-defined components.

        References
        ----------
        >>> oEditor.Delete

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> component_names = app.modeler.user_defined_component_names
        >>> component = app.modeler.user_defined_components[component_names[0]]
        >>> component.delete()

        """
        arg = ["NAME:Selections", "Selections:=", self._m_name]
        self._app.oeditor.Delete(arg)
        del self._primitives.user_defined_components[self.name]
        self._primitives.cleanup_objects()
        self.__dict__ = {}

    @pyaedt_function_handler()
    def duplicate_and_mirror(self, origin: list | object, vector: list | object) -> list:
        """Duplicate and mirror a selection.

        Parameters
        ----------
        origin : float
            List of the ``[x, y, z]`` coordinates or
            Application.Position object for the selection.
        vector : float
            List of the ``[x1, y1, z1]`` coordinates or
            Application.Position object for the vector.

        Returns
        -------
        list
            List of objects created or an empty list.

        References
        ----------
        >>> oEditor.DuplicateMirror

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> component_names = app.modeler.user_defined_component_names
        >>> component = app.modeler.user_defined_components[component_names[0]]
        >>> component.duplicate_and_mirror(origin=[0, 0, 0], vector=[1, 0, 0])

        """
        return self._primitives.duplicate_and_mirror(self.name, origin=origin, vector=vector, is_3d_comp=True)

    @pyaedt_function_handler()
    def mirror(self, origin: list | object, vector: list | object) -> UserDefinedComponent | bool:
        """Mirror a selection.

        Parameters
        ----------
        origin : list, Position
            List of the ``[x, y, z]`` coordinates or
            the Application.Position object for the selection.
        vector : list, Position
            List of the ``[x1, y1, z1]`` coordinates or
            the Application.Position object for the vector.

        Returns
        -------
        ansys.aedt.core.modeler.cad.components_3d.UserDefinedComponent, bool
            3D object when successful, ``False`` when failed.

        References
        ----------
        >>> oEditor.Mirror

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> component_names = app.modeler.user_defined_component_names
        >>> component = app.modeler.user_defined_components[component_names[0]]
        >>> component.mirror(origin=[0, 0, 0], vector=[1, 0, 0])

        """
        if self.is_3d_component:
            if self._primitives.mirror(self.name, origin=origin, vector=vector):
                return self
        else:
            for part in self.parts:
                self._primitives.mirror(part, origin=origin, vector=vector)
            return self
        return False

    @pyaedt_function_handler()
    def rotate(self, axis: Axis | int, angle: float | int = 90.0, units: str = "deg") -> UserDefinedComponent | bool:
        """Rotate the selection.

        Parameters
        ----------
        axis : :class:`ansys.aedt.core.generic.constants.Axis`
            Coordinate system axis or the value of the enum :class:`ansys.aedt.core.generic.constants.Axis`.
        angle : float or int, optional
            Angle of rotation. The units, defined by ``unit``, can be either
            degrees or radians. The default is ``90.0``.
        units : text, optional
             Units for the angle. Options are ``"deg"`` or ``"rad"``.
             The default is ``"deg"``.

        Returns
        -------
        ansys.aedt.core.modeler.cad.components_3d.UserDefinedComponent, bool
            3D object when successful, ``False`` when failed.

        References
        ----------
        >>> oEditor.Rotate

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> from ansys.aedt.core.generic.constants import Axis
        >>> app = Hfss()
        >>> component_names = app.modeler.user_defined_component_names
        >>> component = app.modeler.user_defined_components[component_names[0]]
        >>> component.rotate(axis=Axis.Z)

        """
        if self.is_3d_component:
            if self._primitives.rotate(self.name, axis=axis, angle=angle, units=units):
                return self
        else:
            for part in self.parts:
                self._primitives.rotate(part, axis=axis, angle=angle, units=units)
            return self
        return False

    @pyaedt_function_handler()
    def move(self, vector: list | object) -> UserDefinedComponent | bool:
        """Move component from a list.

        Parameters
        ----------
        vector : list
            Vector of the direction move. It can be a list of the ``[x, y, z]``
            coordinates or a ``Position`` object.

        Returns
        -------
        ansys.aedt.core.modeler.cad.components_3d.UserDefinedComponent, bool
            3D object when successful, ``False`` when failed.

        References
        ----------
        >>> oEditor.Move

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> component_names = app.modeler.user_defined_component_names
        >>> component = app.modeler.user_defined_components[component_names[0]]
        >>> component.move(vector=[1, 0, 0])

        """
        if self.is_3d_component:
            if self._primitives.move(self.name, vector):
                return self
        else:
            for part in self.parts:
                self._primitives.move(part, vector)
            return self

        return False

    @pyaedt_function_handler()
    def duplicate_around_axis(
        self, axis: Axis, angle: int = 90, clones: int = 2, create_new_objects: bool = True
    ) -> list | bool:
        """Duplicate the component around the axis.

        Parameters
        ----------
        axis : :class:`ansys.aedt.core.generic.constants.Axis`
            Coordinate system axis of the object.
        angle : float, optional
            Angle of rotation in degrees. The default is ``90``.
        clones : int, optional
            Number of clones. The default is ``2``.
        create_new_objects : bool, optional
            Whether to create copies as new objects. The default is ``True``.

        Returns
        -------
        list
            List of names of the newly added objects.

        References
        ----------
        >>> oEditor.DuplicateAroundAxis

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> from ansys.aedt.core.generic.constants import Axis
        >>> app = Hfss()
        >>> component_names = app.modeler.user_defined_component_names
        >>> component = app.modeler.user_defined_components[component_names[0]]
        >>> component.duplicate_around_axis(axis=Axis.Z)

        """
        if self.is_3d_component:
            ret, added_objects = self._primitives.duplicate_around_axis(
                self.name, axis, angle, clones, create_new_objects=create_new_objects, is_3d_comp=True
            )
            return added_objects
        self._app.logger.warning("User-defined models do not support this operation.")
        return False

    @pyaedt_function_handler()
    def duplicate_along_line(self, vector: list | object, clones: int = 2, attach: bool = False) -> list | bool:
        """Duplicate the object along a line.

        Parameters
        ----------
        vector : list
            List of ``[x1 ,y1, z1]`` coordinates for the vector or the Application.Position object.
        clones : int, optional
            Number of clones. The default is ``2``.
        attach : bool, optional
            Whether to attach the object. The default is ``False``.

        Returns
        -------
        list
            List of names of the newly added objects.

        References
        ----------
        >>> oEditor.DuplicateAlongLine

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> from ansys.aedt.core.generic.constants import Axis
        >>> app = Hfss()
        >>> component_names = app.modeler.user_defined_component_names
        >>> component = app.modeler.user_defined_components[component_names[0]]
        >>> component.duplicate_along_line(vector=[1, 0, 0])

        """
        if self.is_3d_component:
            old_component_list = self._primitives.user_defined_component_names
            _, added_objects = self._primitives.duplicate_along_line(
                self.name, vector, clones, attach=attach, is_3d_comp=True
            )
            return list(set(added_objects) - set(old_component_list))
        self._app.logger.warning("User-defined models do not support this operation.")
        return False

    @pyaedt_function_handler()
    def update_native(self) -> bool:
        """Update the native component in AEDT.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> component_names = app.modeler.user_defined_component_names
        >>> component = app.modeler.user_defined_components[component_names[0]]
        >>> component.update_native()

        """
        self.update_props = {}
        self.update_props["DefinitionName"] = self._props["SubmodelDefinitionName"]
        self.update_props["GeometryDefinitionParameters"] = self._props["GeometryDefinitionParameters"]
        self.update_props["DesignDefinitionParameters"] = self._props["DesignDefinitionParameters"]
        self.update_props["MaterialDefinitionParameters"] = self._props["MaterialDefinitionParameters"]
        self.update_props["NextUniqueID"] = self._props["NextUniqueID"]
        self.update_props["MoveBackwards"] = self._props["MoveBackwards"]
        self.update_props["DatasetType"] = self._props["DatasetType"]
        self.update_props["DatasetDefinitions"] = self._props["DatasetDefinitions"]
        self.update_props["NativeComponentDefinitionProvider"] = self._props["NativeComponentDefinitionProvider"]
        self.update_props["ComponentName"] = self._props["BasicComponentInfo"]["ComponentName"]
        self.update_props["Company"] = self._props["BasicComponentInfo"]["Company"]
        self.update_props["Model Number"] = self._props["BasicComponentInfo"]["Model Number"]
        self.update_props["Help URL"] = self._props["BasicComponentInfo"]["Help URL"]
        self.update_props["Version"] = self._props["BasicComponentInfo"]["Version"]
        self.update_props["Notes"] = self._props["BasicComponentInfo"]["Notes"]
        self.update_props["IconType"] = self._props["BasicComponentInfo"]["IconType"]
        self._primitives.oeditor.EditNativeComponentDefinition(self._get_args(self.update_props))

        return True

    @pyaedt_function_handler()
    def _get_args(self, props=None):
        if props is None:
            props = self.props
        arg = ["NAME:EditNativeComponentDefinitionData"]
        _dict2arg(props, arg)
        return arg

    @pyaedt_function_handler()
    def _change_property(self, vPropChange):
        return self._primitives._change_component_property(vPropChange, self._m_name)

    @pyaedt_function_handler()
    def get_component_filepath(self) -> str:
        """Get 3d component file path.

        Returns
        -------
        str
            Path of the 3d component file.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> component_names = app.modeler.user_defined_component_names
        >>> component = app.modeler.user_defined_components[component_names[0]]
        >>> component.get_component_filepath()

        """
        return self._app.get_oo_property_value(self._app.oeditor, self.definition_name, "3D Component File Path")

    @pyaedt_function_handler()
    def update_definition(self, password: str | None = None, output_file: str = "", local_update: bool = False) -> bool:
        """Update 3d component definition.

        Parameters
        ----------
        password : str, optional
            Password for encrypted models. The default value is ``None``.
        output_file : str, optional
            New path containing the 3d component file. The default value is ``""``, which means
            that the 3d component file has not changed.
        local_update : bool, optional
            Whether to update the file only locally. Default is ``False``.

        Returns
        -------
        bool
            True if successful.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> component_names = app.modeler.user_defined_component_names
        >>> component = app.modeler.user_defined_components[component_names[0]]
        >>> component.update_definition()

        """
        if password is None:
            password = os.getenv("PYAEDT_ENCRYPTED_PASSWORD", "")
        self._app.oeditor.UpdateComponentDefinition(
            [
                "NAME:UpdateDefinitionData",
                "ForLocalEdit:=",
                local_update,
                "DefinitionNames:=",
                self.definition_name,
                "Passwords:=",
                [password],
                "NewFilePath:=",
                output_file,
            ]
        )
        self._app.modeler.refresh_all_ids()
        return True

    @pyaedt_function_handler()
    def edit_definition(self, password: str | None = None) -> _AppWithOProject | None:
        """Edit 3d Definition. Open AEDT Project and return PyAEDT object.

        Parameters
        ----------
        password : str, optional
            Password for encrypted models. The default value is ``""``.

        Returns
        -------
        _AppWithOProject | None
            PyAEDT object.

        Examples
        --------
        >>> from ansys.aedt.core import Hfss
        >>> app = Hfss()
        >>> component_names = app.modeler.user_defined_component_names
        >>> component = app.modeler.user_defined_components[component_names[0]]
        >>> new_app = component.edit_definition()

        """
        # TODO: Edit documentation to include all supported returned classes.
        # from ansys.aedt.core.generic.general_methods import is_linux
        if password is None:
            password = os.getenv("PYAEDT_ENCRYPTED_PASSWORD", "")

        project_list = [i for i in self._app.desktop_class.project_list]

        self._primitives.oeditor.Edit3DComponentDefinition(
            [
                "NAME:EditDefinitionData",
                ["NAME:DefinitionAndPassword", "Definition:=", self.definition_name, "Password:=", password],
            ]
        )

        new_project = [i for i in self._app.desktop_class.project_list if i not in project_list]

        if new_project:
            from ansys.aedt.core.generic.design_types import get_pyaedt_app

            project = self._app.desktop_class.active_project(new_project[0])
            # project = self._primitives._app.odesktop.GetActiveProject()
            project_name = project.GetName()
            project.GetDesigns()[0].GetName()
            design_name = project.GetDesigns()[0].GetName()
            # if is_linux:
            #     design_name = project.GetDesigns()[0].GetName()
            # else:
            #     design_name = project.GetActiveDesign().GetName()
            return get_pyaedt_app(project_name, design_name, desktop=self._app.desktop_class)
        return None


class LayoutComponent(PyAedtBase):
    """Manages object attributes for Layout components.

    Parameters
    ----------
    primitives : :class:`ansys.aedt.core.modeler.cad.primitives_3d.Primitives3D`
        Inherited parent object.
    name : str, optional
        Name of the component. The default value is ``None``.

    Examples
    --------
    >>> from ansys.aedt.core.modeler.cad.components_3d import LayoutComponent
    >>> obj = LayoutComponent()

    """

    def __init__(self, component) -> None:
        self._primitives = component._primitives
        self._name = component.name
        self._component = component
        self._edb_definition = None
        self._show_layout = None
        self._fast_transformation = None
        self._show_dielectric = None
        self._display_mode = None
        self.layers = {}
        self.nets = {}
        self.objects = {}
        self._edb_object = None
        self._edb_path = None
        if self.edb_definition and self.edb_path:
            self._get_edb_info()

    @property
    def edb_path(self) -> str:
        """EDB path.

        Returns
        -------
        str
           EDB file path.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import LayoutComponent
        >>> obj = LayoutComponent()
        >>> obj.edb_path

        """
        return self._edb_path

    @property
    def edb_object(self) -> Edb | bool:
        """EDB object.

        Returns
        -------
        :class:`ansys.aedt.core.edb.Edb`
           EDB object.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import LayoutComponent
        >>> obj = LayoutComponent()
        >>> obj.edb_object

        """
        if not self._edb_object:
            aedb_component_path = self._edb_path

            for edb_object in _edb_sessions:
                if edb_object.edbpath == aedb_component_path:
                    self._edb_object = edb_object
                    return self._edb_object

            if not aedb_component_path or not os.path.exists(aedb_component_path):  # pragma: no cover
                return False

            app = Edb(
                edbpath=aedb_component_path,
                isreadonly=True,
                version=self._primitives._app._aedt_version,
                student_version=self._primitives._app.student_version,
            )

            _edb_sessions.append(app)

            self._edb_object = app

        return self._edb_object

    @property
    def edb_definition(self) -> str | None:
        """Edb definition.

        Returns
        -------
        str
           EDB definition.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import LayoutComponent
        >>> obj = LayoutComponent()
        >>> obj.edb_definition

        """
        key = "EDB Definition"
        if key in self._primitives._app.get_oo_properties(self._primitives.oeditor, self._component.definition_name):
            edb_definition = self._primitives._app.get_oo_property_value(
                self._primitives.oeditor, self._component.definition_name, key
            )
            self._edb_definition = edb_definition
            aedb_folder = os.path.abspath(
                os.path.join(
                    self._primitives._app.project_path,
                    self._primitives._app.project_name + ".aedb",
                    "LayoutComponents",
                    edb_definition,
                )
            )
            if os.path.exists(aedb_folder):
                subdirs = next(os.walk(aedb_folder))[1]
                for subdir in subdirs:
                    if subdir.endswith(".aedb"):
                        self._edb_path = os.path.abspath(os.path.join(aedb_folder, subdir))
                        break
            return edb_definition
        else:
            return None

    @property
    def show_layout(self) -> bool | None:
        """Show layout flag.

        Returns
        -------
        bool
           `Show layout check box.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import LayoutComponent
        >>> obj = LayoutComponent()
        >>> obj.show_layout

        """
        key = "Show Layout"
        if key in self._primitives._app.get_oo_properties(self._primitives.oeditor, self._name):
            show_layout = self._primitives._app.get_oo_property_value(self._primitives.oeditor, self._name, key)
            self._show_layout = show_layout
            return show_layout
        else:  # pragma: no cover
            return None

    @show_layout.setter
    def show_layout(self, show_layout: bool) -> None:
        key = "Show Layout"
        if isinstance(show_layout, bool) and key in self._primitives._app.get_oo_properties(
            self._primitives.oeditor, self._name
        ):
            self._primitives._app.set_oo_property_value(self._primitives.oeditor, self._name, key, show_layout)
            self._show_layout = show_layout

    @property
    def fast_transformation(self) -> bool | None:
        """Show layout flag.

        Returns
        -------
        bool
           Fast transformation check box.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import LayoutComponent
        >>> obj = LayoutComponent()
        >>> obj.fast_transformation

        """
        key = "Fast Transformation"
        if key in self._primitives._app.get_oo_properties(self._primitives.oeditor, self._name):
            fast_transformation = self._primitives._app.get_oo_property_value(self._primitives.oeditor, self._name, key)
            self._fast_transformation = fast_transformation
            return fast_transformation
        else:  # pragma: no cover
            return None

    @fast_transformation.setter
    def fast_transformation(self, fast_transformation: bool) -> None:
        key = "Fast Transformation"
        if isinstance(fast_transformation, bool) and key in self._primitives._app.get_oo_properties(
            self._primitives.oeditor, self._name
        ):
            self._primitives._app.set_oo_property_value(self._primitives.oeditor, self._name, key, fast_transformation)
            self._fast_transformation = fast_transformation

    @property
    def show_dielectric(self) -> bool | None:
        """Show dielectric flag.

        Returns
        -------
        bool
           Show dielectric check box.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import LayoutComponent
        >>> obj = LayoutComponent()
        >>> obj.show_dielectric

        """
        key = "Object Attributes/ShowDielectric"

        if key in self._primitives._app.get_oo_properties(self._primitives.oeditor, self._name):
            show_dielectric = self._primitives._app.get_oo_property_value(self._primitives.oeditor, self._name, key)
            self._show_dielectric = show_dielectric
            return show_dielectric
        else:  # pragma: no cover
            return None

    @show_dielectric.setter
    def show_dielectric(self, show_dielectric: bool) -> None:
        key = "Object Attributes/ShowDielectric"
        if isinstance(show_dielectric, bool) and key in self._primitives._app.get_oo_properties(
            self._primitives.oeditor, self._name
        ):
            self._primitives._app.set_oo_property_value(self._primitives.oeditor, self._name, key, show_dielectric)
            self._show_dielectric = show_dielectric

    @property
    def display_mode(self) -> int | None:
        """Show layout flag.

        Returns
        -------
        int
           Layout display mode. Available modes are:
            * 0 : Layer.
            * 1 : Net.
            * 2 : Object.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import LayoutComponent
        >>> obj = LayoutComponent()
        >>> obj.display_mode

        """
        key = "Object Attributes/DisplayMode"

        if key in self._primitives._app.get_oo_properties(self._primitives.oeditor, self._name):
            display_mode = self._primitives._app.get_oo_property_value(self._primitives.oeditor, self._name, key)
            self._display_mode = display_mode
            return display_mode
        else:  # pragma: no cover
            return None

    @display_mode.setter
    def display_mode(self, display_mode: int) -> None:
        key = "Object Attributes/DisplayMode"
        if isinstance(display_mode, int) and key in self._primitives._app.get_oo_properties(
            self._primitives.oeditor, self._name
        ):
            self._primitives._app.set_oo_property_value(self._primitives.oeditor, self._name, key, display_mode)
            self._display_mode = display_mode

    @pyaedt_function_handler()
    def close_edb_object(self) -> bool:
        """Close EDB object.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import LayoutComponent
        >>> obj = LayoutComponent()
        >>> obj.close_edb_object()

        """
        if self.edb_object:
            try:
                self.edb_object.close()
                return True
            except Exception:  # pragma: no cover
                self._app.logger.error("EDB object cannot be closed.")
                return False
        else:  # pragma: no cover
            self._app.logger.warning("EDB object was not created.")
            return False

    @pyaedt_function_handler()
    def _get_edb_info(self) -> bool:
        """Get EDB information."""
        if self.edb_object:
            self.nets = {key: [True, False, 60] for key in self.edb_object.nets.netlist}
            self.layers = {key: [True, False, 60] for key in list(self.edb_object.stackup.layers.keys())}
            self.objects = {key: [True, False, 60] for key in list(self.edb_object.components.instances.keys())}
            return True
        else:  # pragma: no cover
            return False

    @pyaedt_function_handler()
    def update_visibility(self) -> bool:
        """Update layer visibility.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oEditor.ChangeProperty

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import LayoutComponent
        >>> obj = LayoutComponent()
        >>> obj.update_visibility()

        """
        vPropChange = [
            "NAME:Object Attributes",
            "ShowDielectric:=",
            self.show_dielectric,
            "DisplayMode:=",
            self.display_mode,
        ]

        if self.layers:
            layer_mode = ["NAME:ObjectAttributesInLayerMode"]
            for layer in self.layers:
                layer_mode.append(layer + ":=")
                layer_mode.append(self.layers[layer])
            vPropChange.append(layer_mode)
        if self.nets:
            net_mode = ["NAME:ObjectAttributesInNetMode"]
            for net in self.nets:
                net_mode.append(layer + ":=")
                net_mode.append(self.nets[net])
            vPropChange.append(net_mode)
        if self.objects:
            objects_mode = ["NAME:ObjectAttributesInObjectMode"]
            for objects in self.objects:
                objects_mode.append(objects + ":=")
                objects_mode.append(self.objects[objects])
            vPropChange.append(objects_mode)

        vChangedProps = ["NAME:ChangedProps", vPropChange]
        vPropServers = ["NAME:PropServers", self._name]
        vGeo3d = ["NAME:Visualization", vPropServers, vChangedProps]
        vOut = ["NAME:AllTabs", vGeo3d]
        self._primitives.oeditor.ChangeProperty(vOut)

        return True


class NativeComponentObject(UserDefinedComponent):
    """Manages Native Component data and execution.

    Parameters
    ----------
    app : object
        An AEDT application from ``ansys.aedt.core.application``.
    component_type : str
        Type of the component.
    component_name : str
        Name of the component.
    props : dict
        Properties of the boundary.

    Examples
    --------
    This example the par_beam returned object is a
    :class:`ansys.aedt.core.modules.boundary.layout_boundary.NativeComponentObject`.

    >>> from ansys.aedt.core import Hfss
    >>> hfss = Hfss(solution_type="SBR+")
    >>> ffd_file = "path/to/ffdfile.ffd"
    >>> par_beam = hfss.create_sbr_file_based_antenna(ffd_file)
    >>> par_beam.native_properties["Size"] = "0.1mm"
    >>> par_beam.update()
    >>> par_beam.delete()

    """

    def __init__(
        self, app: Icepak, component_type: str, name: str, props: dict, definition_name: str | None = None
    ) -> None:
        super().__init__(app.modeler, name, props, component_type, definition_name)
        self.__child_object = None
        self.__excitation_name = None

    @property
    def _child_object(self):
        """Object-oriented properties.

        Returns
        -------
        class:`ansys.aedt.core.modeler.cad.elements_3d.BinaryTreeNode`

        """
        if not self.__child_object:
            component_definition = self._app.oeditor.Get3DComponentDefinitionNames()
            for el in component_definition:
                design_childs = self._app.get_oo_name(self._app.get_oo_object(self._app.oeditor, el))
                if self._m_name in design_childs:
                    self.__child_object = self._app.get_oo_object(self._app.oeditor, f"{el}\\{self._m_name}")
                    break
        return self.__child_object

    @UserDefinedComponent.props.setter
    def props(self, value: dict) -> None:
        # Merge with existing props to support partial updates
        current_props = self.props.to_dict() if self._legacy_props else {}
        _merge_props(current_props, value)
        # Each Setup class must have an update method
        self.update(current_props)

    @property
    def name(self) -> str:
        """Boundary Name.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import NativeComponentObject
        >>> obj = NativeComponentObject()
        >>> obj.name

        """
        child_object = self._child_object
        if child_object:
            self._m_name = str(self.properties["Name"])
        return self._m_name

    @name.setter
    def name(self, value: str) -> None:
        if value in self._app.modeler.user_defined_component_names:
            raise ValueError(f"Name {value} already assigned in the design.")
        child_object = self._child_object
        if child_object:
            legacy_name = self._m_name
            self.properties["Name"] = value
            self._m_name = value
            self._app.modeler.user_defined_components[value] = self
            del self._app.modeler.user_defined_components[legacy_name]

    @property
    def definition_name(self) -> str | None:
        """Definition name of the native component.

        Returns
        -------
        str
           Name of the native component.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import NativeComponentObject
        >>> obj = NativeComponentObject()
        >>> obj.definition_name

        """
        definition_name = None
        if self.props and "SubmodelDefinitionName" in self.props:
            definition_name = self.props["SubmodelDefinitionName"]
        return definition_name or getattr(self, "_definition_name", None)

    @definition_name.setter
    def definition_name(self, value: str | None) -> None:
        self._definition_name = value

    @property
    def targetcs(self) -> str:
        """Native Component Coordinate System.

        Returns
        -------
        str
            Native Component Coordinate System.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import NativeComponentObject
        >>> obj = NativeComponentObject()
        >>> obj.targetcs

        """
        if "TargetCS" in list(self.props.keys()):
            return self.props["TargetCS"]
        else:
            return "Global"

    @targetcs.setter
    def targetcs(self, cs: str) -> None:
        self.props["TargetCS"] = cs

    @property
    def excitation_name(self) -> str:
        """Boundary Name.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import NativeComponentObject
        >>> obj = NativeComponentObject()
        >>> obj.name

        """
        return self.__excitation_name

    @pyaedt_function_handler()
    def _get_args(self, props=None):
        if props is None:
            props = self.props
        arg = ["NAME:InsertNativeComponentData"]
        _dict2arg(props, arg)
        return arg

    @pyaedt_function_handler()
    def create(self) -> bool:
        """Create a Native Component in AEDT.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import NativeComponentObject
        >>> obj = NativeComponentObject()
        >>> obj.create()

        """
        try:
            names = [i for i in self._app.excitation_names]
        except GrpcApiError:  # pragma: no cover
            names = []
        self._m_name = self._app.modeler.oeditor.InsertNativeComponent(self._get_args())
        try:
            a = [i for i in self._app.excitation_names if i not in names]
            self.__excitation_name = a[0].split(":")[0]
        except (GrpcApiError, IndexError):
            self.__excitation_name = self._m_name
        return True

    @pyaedt_function_handler()
    def update(self, properties: dict = None) -> bool:
        """Update the Native Component in AEDT.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import NativeComponentObject
        >>> obj = NativeComponentObject()
        >>> obj.update()

        """
        if not properties:
            properties = {}
            properties["DefinitionName"] = self.props["SubmodelDefinitionName"]
            properties["GeometryDefinitionParameters"] = self.props["GeometryDefinitionParameters"]
            properties["DesignDefinitionParameters"] = self.props["DesignDefinitionParameters"]
            properties["MaterialDefinitionParameters"] = self.props["MaterialDefinitionParameters"]
            properties["NextUniqueID"] = self.props["NextUniqueID"]
            properties["MoveBackwards"] = self.props["MoveBackwards"]
            properties["DatasetType"] = self.props["DatasetType"]
            properties["DatasetDefinitions"] = self.props["DatasetDefinitions"]
            properties["NativeComponentDefinitionProvider"] = self.props["NativeComponentDefinitionProvider"]
            properties["ComponentName"] = self.props["BasicComponentInfo"]["ComponentName"]
            properties["Company"] = self.props["BasicComponentInfo"]["Company"]
            properties["Model Number"] = self.props["BasicComponentInfo"]["Model Number"]
            properties["Help URL"] = self.props["BasicComponentInfo"]["Help URL"]
            properties["Version"] = self.props["BasicComponentInfo"]["Version"]
            properties["Notes"] = self.props["BasicComponentInfo"]["Notes"]
            properties["IconType"] = self.props["BasicComponentInfo"]["IconType"]
        self._app.modeler.oeditor.EditNativeComponentDefinition(self._get_args(properties))

        return True

    @pyaedt_function_handler()
    def delete(self) -> bool:
        """Delete the Native Component in AEDT.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import NativeComponentObject
        >>> obj = NativeComponentObject()
        >>> obj.delete()

        """
        self._app.modeler.oeditor.Delete(["NAME:Selections", "Selections:=", self.name])
        for el in self._app._native_components:
            if el.name == self.name:
                self._app._native_components.remove(el)
                del self._app.modeler.user_defined_components[self.name]
                self._app.modeler.cleanup_objects()
        return True


class NativeComponentPCB(NativeComponentObject):
    """Manages native component PCB data and execution.

    Parameters
    ----------
    app : object
        AEDT application from the ``ansys.aedt.core.application`` class.
    component_type : str
        Type of the component.
    component_name : str
        Name of the component.
    props : dict
        Properties of the boundary.

    Examples
    --------
    >>> from ansys.aedt.core.modeler.cad.components_3d import NativeComponentPCB
    >>> obj = NativeComponentPCB()

    """

    def __init__(self, app: Icepak, name: str, props: dict, definition_name: str | None = None) -> None:
        NativeComponentObject.__init__(self, app, "PCB", name, props, definition_name)

    @pyaedt_function_handler()
    def set_resolution(self, resolution: int) -> bool:
        """Set metal fraction mapping resolution.

        Parameters
        ----------
        resolution : int
            Resolution level. Accepted variables between 1 and 5.

        Returns
        -------
        bool
            True if successful, else False.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import NativeComponentPCB
        >>> obj = NativeComponentPCB()
        >>> obj.set_resolution(resolution=1)

        """
        if resolution < 1 or resolution > 5:
            self._app.logger.add_message(
                message_type=2,
                message_text="Valid resolution values are between 1 and 5.",
                level="Design",
                proj_name=self._app.project_name,
                des_name=self._app.design_name,
            )
            return False
        self.props["NativeComponentDefinitionProvider"]["Resolution"] = resolution
        self.props["NativeComponentDefinitionProvider"]["CustomResolution"] = False
        return True

    @pyaedt_function_handler()
    def set_custom_resolution(self, row: int, col: int) -> bool:
        """Set custom metal fraction mapping resolution.

        Parameters
        ----------
        row : int
            Resolution level in rows direction.
        col : int
            Resolution level in columns direction.

        Returns
        -------
        bool
            True if successful, else False.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import NativeComponentPCB
        >>> obj = NativeComponentPCB()
        >>> obj.set_custom_resolution(row=1, col=1)

        """
        self.props["NativeComponentDefinitionProvider"]["CustomResolutionRow"] = row
        self.props["NativeComponentDefinitionProvider"]["CustomResolutionCol"] = col
        self.props["NativeComponentDefinitionProvider"]["CustomResolution"] = True
        return True

    @property
    def power(self):
        """Power dissipation assigned to the PCB.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import NativeComponentPCB
        >>> obj = NativeComponentPCB()
        >>> obj.power

        """
        return self.props["NativeComponentDefinitionProvider"].get("Power", "0W")

    @pyaedt_function_handler()
    def set_high_side_radiation(
        self,
        enabled: bool,
        surface_material: str | None = "Steel-oxidised-surface",
        radiate_to_ref_temperature: bool = False,
        view_factor: int = 1,
        ref_temperature: str = "AmbientTemp",
    ) -> bool:
        """Set high side radiation properties.

        Parameters
        ----------
        enabled : bool
            Whether high side radiation is enabled.
        surface_material : str, optional
            Surface material to apply. Default is ``"Steel-oxidised-surface"``.
        radiate_to_ref_temperature : bool, optional
            Whether to radiate to a reference temperature instead of objects in the model.
            Default is ``False``.
        view_factor : float, optional
            View factor to use for radiation computation if ``radiate_to_ref_temperature``
            is set to ``True``. Default is 1.
        ref_temperature : str, optional
            Reference temperature to use for radiation computation if
            ``radiate_to_ref_temperature`` is set to True. Default is ``"AmbientTemp"``.

        Returns
        -------
        bool
            ``True`` if successful, else ``False``.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import NativeComponentPCB
        >>> obj = NativeComponentPCB()
        >>> obj.set_high_side_radiation(enabled=True)

        """
        high_rad = {
            "Radiate": enabled,
            "RadiateTo - High": "RefTemperature - High" if radiate_to_ref_temperature else "AllObjects - High",
            "Surface Material - High": surface_material,
        }
        if radiate_to_ref_temperature:
            high_rad["Ref. Temperature - High"] = (ref_temperature,)
            high_rad["View Factor - High"] = view_factor
        self.props["NativeComponentDefinitionProvider"]["HighSide"] = high_rad
        return True

    @power.setter
    def power(self, value: str) -> None:
        """Assign power dissipation to the PCB.

        Parameters
        ----------
        value : str
            Power to apply to the PCB.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import NativeComponentPCB
        >>> obj = NativeComponentPCB()
        >>> obj.power = "5W"

        """
        self.props["NativeComponentDefinitionProvider"]["Power"] = value

    @property
    def force_source_solve(self):
        """Force source solution option.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import NativeComponentPCB
        >>> obj = NativeComponentPCB()
        >>> obj.force_source_solve

        """
        return self.props["NativeComponentDefinitionProvider"].get("DefnLink", {}).get("ForceSourceToSolve", False)

    @force_source_solve.setter
    def force_source_solve(self, val: bool) -> None:
        """Set Whether to force source solution.

        Parameters
        ----------
        value : bool
            Whether to force source solution.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import NativeComponentPCB
        >>> obj = NativeComponentPCB()
        >>> obj.force_source_solve = True

        """
        if not isinstance(val, bool):
            self._app.logger.add_message(
                message_type=2,
                message_text="Only Boolean value can be accepted.",
                level="Design",
                proj_name=self._app.project_name,
                des_name=self._app.design_name,
            )
            return
        return self.props["NativeComponentDefinitionProvider"]["DefnLink"].update({"ForceSourceToSolve": val})

    @property
    def preserve_partner_solution(self) -> bool:
        """Preserve parner solution option.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import NativeComponentPCB
        >>> obj = NativeComponentPCB()
        >>> obj.preserve_partner_solution

        """
        return self.props["NativeComponentDefinitionProvider"].get("DefnLink", {}).get("PreservePartnerSoln", False)

    @preserve_partner_solution.setter
    def preserve_partner_solution(self, val: bool) -> None:
        """Set Whether to preserve partner solution.

        Parameters
        ----------
        val : bool
            Whether to preserve partner solution.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import NativeComponentPCB
        >>> obj = NativeComponentPCB()
        >>> obj.preserve_partner_solution = True

        """
        if not isinstance(val, bool):
            self._app.logger.add_message(
                message_type=2,
                message_text="Only boolean can be accepted.",
                level="Design",
                proj_name=self._app.project_name,
                des_name=self._app.design_name,
            )
            return
        return self.props["NativeComponentDefinitionProvider"]["DefnLink"].update({"PreservePartnerSoln": val})

    @property
    def included_parts(self) -> "None | PCBSettingsDeviceParts | PCBSettingsPackageParts":
        """Parts options.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import NativeComponentPCB
        >>> obj = NativeComponentPCB()
        >>> obj.included_parts

        """
        p = self.props["NativeComponentDefinitionProvider"].get("PartsChoice", 0)
        if p == 0:
            return None
        elif p == 1:
            return PCBSettingsDeviceParts(self, self._app)
        elif p == 2:
            return PCBSettingsPackageParts(self, self._app)

    @included_parts.setter
    def included_parts(self, value: str | int | None) -> None:
        """Set PCB parts incusion option.

        Parameters
        ----------
        value : str or int
            Valid options are ``"None"``, ``"Device"``, and ``"Package"`` (or 0, 1, and 2 respectivaly)

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import NativeComponentPCB
        >>> obj = NativeComponentPCB()
        >>> obj.included_parts = "Device"

        """
        if value is None:
            value = "None"
        part_map = {"None": 0, "Device": 1, "Package": 2}
        if not isinstance(value, int):
            value = part_map.get(value, None)
        if value is not None:
            self.props["NativeComponentDefinitionProvider"]["PartsChoice"] = value
        else:
            self._app.logger.add_message(
                message_type=2,
                message_text='Invalid part choice. Valid options are "None", "Device", and "Package" (or 0, 1, and 2 '
                "respectively).",
                level="Design",
                proj_name=self._app.project_name,
                des_name=self._app.design_name,
            )

    @pyaedt_function_handler()
    def set_low_side_radiation(
        self,
        enabled: bool,
        surface_material: str | None = "Steel-oxidised-surface",
        radiate_to_ref_temperature: bool = False,
        view_factor: int = 1,
        ref_temperature: str = "AmbientTemp",
    ) -> bool:
        """Set low side radiation properties.

        Parameters
        ----------
        enabled : bool
            Whether high side radiation is enabled.
        surface_material : str, optional
            Surface material to apply. Default is ``"Steel-oxidised-surface"``.
        radiate_to_ref_temperature : bool, optional
            Whether to radiate to a reference temperature instead of objects in the model.
            Default is ``False``.
        view_factor : float, optional
            View factor to use for radiation computation if ``radiate_to_ref_temperature``
            is set to True. Default is 1.
        ref_temperature : str, optional
            Reference temperature to use for radiation computation if
            ``radiate_to_ref_temperature`` is set to ``True``. Default is ``"AmbientTemp"``.

        Returns
        -------
        bool
            ``True`` if successful, else ``False``.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import NativeComponentPCB
        >>> obj = NativeComponentPCB()
        >>> obj.set_low_side_radiation(enabled=True)

        """
        low_side = {
            "Radiate": enabled,
            "RadiateTo": "RefTemperature - High" if radiate_to_ref_temperature else "AllObjects",
            "Surface Material": surface_material,
        }
        if radiate_to_ref_temperature:
            low_side["Ref. Temperature"] = (ref_temperature,)
            low_side["View Factor"] = view_factor
        self.props["NativeComponentDefinitionProvider"]["LowSide"] = low_side
        return True

    @power.setter
    def power(self, value: str) -> None:
        """Assign power dissipation to the PCB.

        Parameters
        ----------
        value : str
            Power to apply to the PCB.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import NativeComponentPCB
        >>> obj = NativeComponentPCB()
        >>> obj.power = "5W"

        """
        self.props["NativeComponentDefinitionProvider"]["Power"] = value

    @force_source_solve.setter
    def force_source_solve(self, val: bool) -> None:
        """Set Whether to force source solution.

        Parameters
        ----------
        value : bool
            Whether to force source solution.

        """
        if not isinstance(val, bool):
            self._app.logger.add_message(
                message_type=2,
                message_text="Only Boolean value can be accepted.",
                level="Design",
                proj_name=self._app.project_name,
                des_name=self._app.design_name,
            )
            return
        return self.props["NativeComponentDefinitionProvider"]["DefnLink"].update({"ForceSourceToSolve": val})

    @preserve_partner_solution.setter
    def preserve_partner_solution(self, val: bool) -> None:
        """Set Whether to preserve partner solution.

        Parameters
        ----------
        val : bool
            Whether to preserve partner solution.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import NativeComponentPCB
        >>> obj = NativeComponentPCB()
        >>> obj.preserve_partner_solution = True

        """
        if not isinstance(val, bool):
            self._app.logger.add_message(
                message_type=2,
                message_text="Only boolean can be accepted.",
                level="Design",
                proj_name=self._app.project_name,
                des_name=self._app.design_name,
            )
            return
        return self.props["NativeComponentDefinitionProvider"]["DefnLink"].update({"PreservePartnerSoln": val})

    @included_parts.setter
    def included_parts(self, value: str | int | None) -> None:
        """Set PCB parts incusion option.

        Parameters
        ----------
        value : str or int
            Valid options are ``"None"``, ``"Device"``, and ``"Package"`` (or 0, 1, and 2 respectivaly)

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import NativeComponentPCB
        >>> obj = NativeComponentPCB()
        >>> obj.included_parts = "Device"
        """
        if value is None:
            value = "None"
        part_map = {"None": 0, "Device": 1, "Package": 2}
        if not isinstance(value, int):
            value = part_map.get(value, None)
        if value is not None:
            self.props["NativeComponentDefinitionProvider"]["PartsChoice"] = value
        else:
            self._app.logger.add_message(
                message_type=2,
                message_text='Invalid part choice. Valid options are "None", "Device", and "Package" (or 0, 1, and 2'
                " respectively).",
                level="Design",
                proj_name=self._app.project_name,
                des_name=self._app.design_name,
            )

    @pyaedt_function_handler()
    def identify_extent_poly(self) -> str | bool:
        """Get polygon that defines board extent.

        Returns
        -------
        str
            Name of the polygon to include.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import NativeComponentPCB
        >>> obj = NativeComponentPCB()
        >>> obj.identify_extent_poly

        """
        from ansys.aedt.core import Hfss3dLayout

        prj = self.props["NativeComponentDefinitionProvider"]["DefnLink"]["Project"]
        if prj == "This Project*":
            prj = self._app.project_name
        layout = Hfss3dLayout(project=prj, design=self.props["NativeComponentDefinitionProvider"]["DefnLink"]["Design"])
        layer = [o for o in layout.modeler.stackup.drawing_layers if o.type == "outline"][0]
        outlines = [p for p in layout.modeler.polygons.values() if p.placement_layer == layer.name]
        if len(outlines) > 1:
            self._app.logger.add_message(
                message_type=0,
                message_text=f"{outlines[0].name} automatically selected as ``extent_polygon``, "
                f"pass ``extent_polygon`` argument explixitly to select a different one. "
                f"Available choices are: {', '.join([o.name for o in outlines])}",
                level="Design",
                proj_name=self._app.project_name,
                des_name=self._app.design_name,
            )
        elif len(outlines) == 0:
            self._app.logger.add_message(
                message_type=2,
                message_text="No polygon found in the Outline layer.",
                level="Design",
                proj_name=self._app.project_name,
                des_name=self._app.design_name,
            )
            return False
        return outlines[0].name

    @property
    def board_cutout_material(self) -> str:
        """Material applied to cutout regions.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import NativeComponentPCB
        >>> obj = NativeComponentPCB()
        >>> obj.board_cutout_material

        """
        return self.props["NativeComponentDefinitionProvider"].get("BoardCutoutMaterial", "air ")

    @property
    def via_holes_material(self) -> str:
        """Material applied to via hole regions.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import NativeComponentPCB
        >>> obj = NativeComponentPCB()
        >>> obj.via_holes_material

        """
        return self.props["NativeComponentDefinitionProvider"].get("ViaHoleMaterial", "copper")

    @board_cutout_material.setter
    def board_cutout_material(self, value: str) -> None:
        """Set material to apply to cutout regions.

        Parameters
        ----------
        value : str
            Material to apply to cutout regions.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import NativeComponentPCB
        >>> obj = NativeComponentPCB()
        >>> obj.board_cutout_material = "FR4"

        """
        self.props["NativeComponentDefinitionProvider"]["BoardCutoutMaterial"] = value

    @via_holes_material.setter
    def via_holes_material(self, value: str) -> None:
        """Set material to apply to via hole regions.

        Parameters
        ----------
        value : str
            Material to apply to via hole regions.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import NativeComponentPCB
        >>> obj = NativeComponentPCB()
        >>> obj.via_holes_material = "copper"

        """
        self.props["NativeComponentDefinitionProvider"]["ViaHoleMaterial"] = value

    @pyaedt_function_handler()
    def set_board_extents(self, extent_type: str = None, extent_polygon: str = None) -> bool:
        """Set board extent.

        Parameters
        ----------
        extent_type : str, optional
            Extent definition of the PCB. Default is ``None`` in which case the 3D Layout extent
            will be used. Other possible options are: ``"Bounding Box"`` or ``"Polygon"``.
        extent_polygon : str, optional
            Polygon name to use in the extent definition of the PCB. Default is ``None``. This
            argument is mandatory if ``extent_type`` is ``"Polygon"``.

        Returns
        -------
        bool
            ``True`` if successful. ``False`` otherwise.

        Examples
        --------
        >>> from ansys.aedt.core.modeler.cad.components_3d import NativeComponentPCB
        >>> obj = NativeComponentPCB()
        >>> obj.set_board_extents(extent_type=1, extent_polygon=1)

        """
        if extent_type is None:
            self.props["NativeComponentDefinitionProvider"]["Use3DLayoutExtents"] = True
        else:
            allowed_extent_types = ["Bounding Box", "Polygon"]
            if extent_type not in allowed_extent_types:
                self._app.logger.add_message(
                    message_type=2,
                    message_text=f"Accepted argument for ``extent_type`` are: {', '.join(allowed_extent_types)}. "
                    f"{extent_type} provided",
                    level="Design",
                    proj_name=self._app.project_name,
                    des_name=self._app.design_name,
                )
                return False
            self.props["NativeComponentDefinitionProvider"]["ExtentsType"] = extent_type
            if extent_type == "Polygon":
                if extent_polygon is None:
                    extent_polygon = self.identify_extent_poly()
                    if not extent_polygon:
                        return False
                self.props["NativeComponentDefinitionProvider"]["OutlinePolygon"] = extent_polygon
        return True


class PCBSettingsPackageParts(PyAedtBase):
    """Handle package part settings of the PCB component.

    Parameters
    ----------
    pcb_obj : :class:`ansys.aedt.core.modules.layout_boundary.NativeComponentPCB`
            Inherited pcb object.
    app : :class:`ansys.aedt.core.Icepak`
            Inherited application object.

    Examples
    --------
    >>> from ansys.aedt.core.modules.boundary.layout_boundary import PCBSettingsPackageParts
    >>> obj = PCBSettingsPackageParts()

    """

    def __init__(self, pcb_obj, app) -> None:
        self._app = app
        self.pcb = pcb_obj
        self._solderbumps_map = {"Lumped": "SbLumped", "Cylinders": "SbCylinder", "Boxes": "SbBlock"}

    def __eq__(self, other):
        if isinstance(other, str):
            return other == "Package"
        elif isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    @pyaedt_function_handler()
    def set_solderballs_modeling(self, modeling: str = None) -> bool:
        """Set how to model solderballs.

        Parameters
        ----------
        modeling : str, optional
            Method for modeling solderballs located below the stackup. The default is
            ``None``, in which case they are not modeled. Options for modeling are
            ``"Boxes"``, ``"Cylinders"``, and ``"Lumped"``.

        Returns
        -------
        bool
            ``True`` if successful, ``False`` otherwise.

        Examples
        --------
        >>> from ansys.aedt.core.modules.boundary.layout_boundary import PCBSettingsPackageParts
        >>> obj = PCBSettingsPackageParts()
        >>> obj.set_solderballs_modeling(modeling=1)

        """
        update_properties = {
            "CreateBottomSolderballs": modeling is not None,
            "BottomSolderballsModelType": self._solderbumps_map[modeling],
        }

        self.pcb.props["NativeComponentDefinitionProvider"].update(update_properties)
        return True

    @pyaedt_function_handler()
    def set_connectors_modeling(
        self,
        modeling: str = None,
        solderbumps_modeling: str = "Boxes",
        bondwire_material: str | None = "Au-Typical",
        bondwire_diameter: str = "0.05mm",
    ) -> bool:
        """Set how to model connectors.

        Parameters
        ----------
            modeling : str, optional
                Method for modeling connectors located above the stackup. The default is
                ``None``, in which case they are not modeled. Options for modeling are
                ``"Bondwire"`` and ``"Solderbump"``.
            solderbumps_modeling : str, optional
                Method for modeling solderbumps if ``modeling="Solderbump"``.
                The default is ```"Boxes"``. Options are ``"Boxes"``, ``"Cylinders"``,
                and ``"Lumped"``.
            bondwire_material : str, optional
                Bondwire material if ``modeling="Bondwire"``. The default is
                ``"Au-Typical"``.
            bondwire_diameter : str, optional
                Bondwires diameter if ``modeling="Bondwire".
                The default is ``"0.05mm"``.

        Returns
        -------
        bool
            ``True`` if successful, ``False`` otherwise.

        Examples
        --------
        >>> from ansys.aedt.core.modules.boundary.layout_boundary import PCBSettingsPackageParts
        >>> obj = PCBSettingsPackageParts()
        >>> obj.set_connectors_modeling(modeling=1, solderbumps_modeling=1)

        """
        valid_connectors = ["Solderbump", "Bondwire"]
        if modeling is not None and modeling not in valid_connectors:
            self._app.logger.add_message(
                message_type=2,
                message_text=f"{modeling} option is not supported. Use one of the following: "
                f"{', '.join(valid_connectors)}",
                level="Design",
                proj_name=self._app.project_name,
                des_name=self._app.design_name,
            )
            return False
        if bondwire_material not in self._app.materials.mat_names_aedt:
            self._app.logger.add_message(
                message_type=2,
                message_text=f"{bondwire_material} material is not present in the library.",
                level="Design",
                proj_name=self._app.project_name,
                des_name=self._app.design_name,
            )
            return False
        if self._solderbumps_map.get(solderbumps_modeling, None) is None:
            self._app.logger.add_message(
                message_type=2,
                message_text=f"Solderbumps modeling option {solderbumps_modeling} is not valid. "
                f"Available options are: {', '.join(list(self._solderbumps_map.keys()))}.",
                level="Design",
                proj_name=self._app.project_name,
                des_name=self._app.design_name,
            )
            return False

        update_properties = {
            "CreateTopSolderballs": modeling is not None,
            "TopConnectorType": modeling,
            "TopSolderballsModelType": self._solderbumps_map[solderbumps_modeling],
            "BondwireMaterial": bondwire_material,
            "BondwireDiameter": bondwire_diameter,
        }

        self.pcb.props["NativeComponentDefinitionProvider"].update(update_properties)
        return True

    def __repr__(self) -> str:
        return "Package"


class PCBSettingsDeviceParts(PyAedtBase):
    """Handle device part settings of the PCB component.

    Parameters
    ----------
    pcb_obj : :class:`ansys.aedt.core.modules.layout_boundary.NativeComponentPCB`
            Inherited pcb object.
    app : :class:`ansys.aedt.core.Icepak`
            Inherited application object.

    Examples
    --------
    >>> from ansys.aedt.core.modules.boundary.layout_boundary import PCBSettingsDeviceParts
    >>> obj = PCBSettingsDeviceParts()

    """

    def __init__(self, pcb_obj, app) -> None:
        self._app = app
        self.pcb = pcb_obj
        self._filter_map2name = {"Cap": "Capacitors", "Ind": "Inductors", "Res": "Resistors"}

    def __eq__(self, other):
        if isinstance(other, str):
            return other == "Device"
        elif isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return "Device"

    @property
    @pyaedt_function_handler()
    def simplify_parts(self) -> bool:
        """Get whether parts are simplified as cuboid.

        Examples
        --------
        >>> from ansys.aedt.core.modules.boundary.layout_boundary import PCBSettingsDeviceParts
        >>> obj = PCBSettingsDeviceParts()
        >>> obj.simplify_parts

        """
        return self.pcb.props["NativeComponentDefinitionProvider"]["ModelDeviceAsRect"]

    @simplify_parts.setter
    @pyaedt_function_handler()
    def simplify_parts(self, value: bool) -> None:
        """Set whether parts are simplified as cuboid.

        Parameters
        ----------
        value : bool
            Whether parts are simplified as cuboid.

        Examples
        --------
        >>> from ansys.aedt.core.modules.boundary.layout_boundary import PCBSettingsDeviceParts
        >>> obj = PCBSettingsDeviceParts()
        >>> obj.simplify_parts = True

        """
        self.pcb.props["NativeComponentDefinitionProvider"]["ModelDeviceAsRect"] = value

    @property
    @pyaedt_function_handler()
    def surface_material(self) -> str:
        """Surface material to apply to parts.

        Examples
        --------
        >>> from ansys.aedt.core.modules.boundary.layout_boundary import PCBSettingsDeviceParts
        >>> obj = PCBSettingsDeviceParts()
        >>> obj.surface_material

        """
        return self.pcb.props["NativeComponentDefinitionProvider"]["DeviceSurfaceMaterial"]

    @surface_material.setter
    @pyaedt_function_handler()
    def surface_material(self, value: str) -> None:
        """Set surface material to apply to parts.

        Parameters
        ----------
        value : str
            Surface material to apply to parts.

        Examples
        --------
        >>> from ansys.aedt.core.modules.boundary.layout_boundary import PCBSettingsDeviceParts
        >>> obj = PCBSettingsDeviceParts()
        >>> obj.surface_material = "Aluminum"

        """
        self.pcb.props["NativeComponentDefinitionProvider"]["DeviceSurfaceMaterial"] = value

    @property
    @pyaedt_function_handler()
    def footprint_filter(self) -> str | None:
        """Minimum component footprint for filtering.

        Examples
        --------
        >>> from ansys.aedt.core.modules.boundary.layout_boundary import PCBSettingsDeviceParts
        >>> obj = PCBSettingsDeviceParts()
        >>> obj.footprint_filter

        """
        if self.pcb.props["NativeComponentDefinitionProvider"]["PartsChoice"] != 1:
            self._app.logger.add_message(
                message_type=2,
                message_text="Device parts modeling is not active.  No filtering or override option is available.",
                level="Design",
                proj_name=self._app.project_name,
                des_name=self._app.design_name,
            )
            return None
        if self._app.settings.aedt_version < "2024.2":
            return None
        return self.filters.get("FootPrint", {}).get("Value", None)

    @footprint_filter.setter
    @pyaedt_function_handler()
    def footprint_filter(self, minimum_footprint: str | None) -> None:
        """Set minimum component footprint for filtering.

        Parameters
        ----------
        minimum_footprint : str
            Value with unit of the minimum component footprint for filtering.

        Examples
        --------
        >>> from ansys.aedt.core.modules.boundary.layout_boundary import PCBSettingsDeviceParts
        >>> obj = PCBSettingsDeviceParts()
        >>> obj.footprint_filter = "1mm2"

        """
        if self.pcb.props["NativeComponentDefinitionProvider"]["PartsChoice"] != 1:
            self._app.logger.add_message(
                message_type=2,
                message_text="Device parts modeling is not active.  No filtering or override option is available.",
                level="Design",
                proj_name=self._app.project_name,
                des_name=self._app.design_name,
            )
            return
        if self._app.settings.aedt_version < "2024.2":
            return
        new_filters = self.pcb.props["NativeComponentDefinitionProvider"].get("Filters", [])
        if "FootPrint" in new_filters:
            new_filters.remove("FootPrint")
        if minimum_footprint is not None:
            new_filters.append("FootPrint")
            self.pcb.props["NativeComponentDefinitionProvider"]["FootPrint"] = minimum_footprint
        self.pcb.props["NativeComponentDefinitionProvider"]["Filters"] = new_filters

    @property
    def power_filter(self) -> str | None:
        """Minimum component power for filtering.

        Examples
        --------
        >>> from ansys.aedt.core.modules.boundary.layout_boundary import PCBSettingsDeviceParts
        >>> obj = PCBSettingsDeviceParts()
        >>> obj.power_filter

        """
        if self.pcb.props["NativeComponentDefinitionProvider"]["PartsChoice"] != 1:
            self._app.logger.add_message(
                message_type=2,
                message_text="Device parts modeling is not active.  No filtering or override option is available.",
                level="Design",
                proj_name=self._app.project_name,
                des_name=self._app.design_name,
            )
            return None
        return self.filters.get("Power", {}).get("Value")

    @power_filter.setter
    def power_filter(self, minimum_power: str | None) -> None:
        """Set minimum component power for filtering.

        Parameters
        ----------
        minimum_power : str | None
            Value with unit of the minimum component power for filtering.

        Examples
        --------
        >>> from ansys.aedt.core.modules.boundary.layout_boundary import PCBSettingsDeviceParts
        >>> obj = PCBSettingsDeviceParts()
        >>> obj.power_filter = "1W"

        """
        if self.pcb.props["NativeComponentDefinitionProvider"]["PartsChoice"] != 1:
            self._app.logger.add_message(
                message_type=2,
                message_text="Device parts modeling is not active.  No filtering or override option is available.",
                level="Design",
                proj_name=self._app.project_name,
                des_name=self._app.design_name,
            )
            return
        new_filters = self.pcb.props["NativeComponentDefinitionProvider"].get("Filters", [])
        if "Power" in new_filters:
            new_filters.remove("Power")
        if minimum_power is not None:
            new_filters.append("Power")
            self.pcb.props["NativeComponentDefinitionProvider"]["PowerVal"] = minimum_power
        self.pcb.props["NativeComponentDefinitionProvider"]["Filters"] = new_filters

    @property
    @pyaedt_function_handler()
    def type_filters(self) -> list | None:
        """Types of component that are filtered.

        Examples
        --------
        >>> from ansys.aedt.core.modules.boundary.layout_boundary import PCBSettingsDeviceParts
        >>> obj = PCBSettingsDeviceParts()
        >>> obj.type_filters

        """
        if self.pcb.props["NativeComponentDefinitionProvider"]["PartsChoice"] != 1:
            self._app.logger.add_message(
                message_type=2,
                message_text="Device parts modeling is not active.  No filtering or override option is available.",
                level="Design",
                proj_name=self._app.project_name,
                des_name=self._app.design_name,
            )
            return None
        return self.filters.get("Types")

    @type_filters.setter
    def type_filters(self, object_type: str | list) -> None:
        """Set types of component to filter.

        Parameters
        ----------
        object_type : str or list
            Types of object to filter. Options are ``"Capacitors"``, ``"Inductors"``, and ``"Resistors"``.

        Examples
        --------
        >>> from ansys.aedt.core.modules.boundary.layout_boundary import PCBSettingsDeviceParts
        >>> obj = PCBSettingsDeviceParts()
        >>> obj.type_filters = ["Capacitors", "Inductors"]

        """
        if self.pcb.props["NativeComponentDefinitionProvider"]["PartsChoice"] != 1:
            self._app.logger.add_message(
                message_type=2,
                message_text="Device parts modeling is not active.  No filtering or override option is available.",
            )
            return
        if not isinstance(object_type, list):
            object_type = [object_type]
        if not all(o in self._filter_map2name.values() for o in object_type):
            self._app.logger.add_message(
                message_type=2,
                message_text=f"Accepted elements of the list are: {', '.join(list(self._filter_map2name.values()))}",
                level="Design",
                proj_name=self._app.project_name,
                des_name=self._app.design_name,
            )
        else:
            new_filters = self.pcb.props["NativeComponentDefinitionProvider"].get("Filters", [])
            map2arg = {v: k for k, v in self._filter_map2name.items()}
            for f, _ in self._filter_map2name.items():
                if f in new_filters:
                    new_filters.remove(f)
            new_filters += [map2arg[o] for o in object_type]
            self.pcb.props["NativeComponentDefinitionProvider"]["Filters"] = new_filters

    @property
    @pyaedt_function_handler()
    def height_filter(self) -> str | None:
        """Minimum component height for filtering.

        Examples
        --------
        >>> from ansys.aedt.core.modules.boundary.layout_boundary import PCBSettingsDeviceParts
        >>> obj = PCBSettingsDeviceParts()
        >>> obj.height_filter

        """
        if self.pcb.props["NativeComponentDefinitionProvider"]["PartsChoice"] != 1:
            self._app.logger.add_message(
                message_type=2,
                message_text="Device parts modeling is not active.  No filtering or override option is available.",
                level="Design",
                proj_name=self._app.project_name,
                des_name=self._app.design_name,
            )
            return None
        return self.filters.get("Height", {}).get("Value", None)

    @height_filter.setter
    def height_filter(self, minimum_height: str | None) -> None:
        """Set minimum component height for filtering and whether to filter 2D objects.

        Parameters
        ----------
        minimum_height : str | None
            Value with unit of the minimum component power for filtering.

        Examples
        --------
        >>> from ansys.aedt.core.modules.boundary.layout_boundary import PCBSettingsDeviceParts
        >>> obj = PCBSettingsDeviceParts()
        >>> obj.height_filter = "1mm"

        """
        if self.pcb.props["NativeComponentDefinitionProvider"]["PartsChoice"] != 1:
            self._app.logger.add_message(
                message_type=2,
                message_text="Device parts modeling is not active.  No filtering or override option is available.",
                level="Design",
                proj_name=self._app.project_name,
                des_name=self._app.design_name,
            )
            return
        new_filters = self.pcb.props["NativeComponentDefinitionProvider"].get("Filters", [])
        if "Height" in new_filters:
            new_filters.remove("Height")
        if minimum_height is not None:
            new_filters.append("Height")
            self.pcb.props["NativeComponentDefinitionProvider"]["HeightVal"] = minimum_height
        self.pcb.props["NativeComponentDefinitionProvider"]["Filters"] = new_filters

    @property
    @pyaedt_function_handler()
    def objects_2d_filter(self) -> bool | None:
        """Whether 2d objects are filtered.

        Examples
        --------
        >>> from ansys.aedt.core.modules.boundary.layout_boundary import PCBSettingsDeviceParts
        >>> obj = PCBSettingsDeviceParts()
        >>> obj.objects_2d_filter

        """
        if self.pcb.props["NativeComponentDefinitionProvider"]["PartsChoice"] != 1:
            self._app.logger.add_message(
                message_type=2,
                message_text="Device parts modeling is not active.  No filtering or override option is available.",
                level="Design",
                proj_name=self._app.project_name,
                des_name=self._app.design_name,
            )
            return None
        return self.filters.get("Exclude2DObjects", False)

    @objects_2d_filter.setter
    def objects_2d_filter(self, enable: bool) -> None:
        """Set whether 2d objects are filtered.

        Parameters
        ----------
        enable : bool
            Whether 2d objects are filtered.

        Examples
        --------
        >>> from ansys.aedt.core.modules.boundary.layout_boundary import PCBSettingsDeviceParts
        >>> obj = PCBSettingsDeviceParts()
        >>> obj.objects_2d_filter = True

        """
        if self.pcb.props["NativeComponentDefinitionProvider"]["PartsChoice"] != 1:
            self._app.logger.add_message(
                message_type=2,
                message_text="Device parts modeling is not active.  No filtering or override option is available.",
                level="Design",
                proj_name=self._app.project_name,
                des_name=self._app.design_name,
            )
            return
        new_filters = self.pcb.props["NativeComponentDefinitionProvider"].get("Filters", [])
        if "HeightExclude2D" in new_filters:
            new_filters.remove("HeightExclude2D")
        if enable:
            new_filters.append("HeightExclude2D")
        self.pcb.props["NativeComponentDefinitionProvider"]["Filters"] = new_filters

    @property
    @pyaedt_function_handler()
    def filters(self) -> dict | None:
        """All active filters.

        Examples
        --------
        >>> from ansys.aedt.core.modules.boundary.layout_boundary import PCBSettingsDeviceParts
        >>> obj = PCBSettingsDeviceParts()
        >>> obj.filters

        """
        if self.pcb.props["NativeComponentDefinitionProvider"].get("PartsChoice", None) != 1:
            self._app.logger.add_message(
                message_type=2,
                message_text="Device parts modeling is not active.  No filtering or override option is available.",
                level="Design",
                proj_name=self._app.project_name,
                des_name=self._app.design_name,
            )
            return None
        out_filters = {"Type": {"Capacitors": False, "Inductors": False, "Resistors": False}}
        filters = self.pcb.props["NativeComponentDefinitionProvider"].get("Filters", [])
        filter_map2type = {
            "Cap": "Type",
            "FootPrint": "FootPrint",
            "Height": "Height",
            "HeightExclude2D": None,
            "Ind": "Type",
            "Power": "Power",
            "Res": "Type",
        }
        filter_map2val = {"FootPrint": "FootPrint", "Height": "HeightVal", "Power": "PowerVal"}
        for f in filters:
            if filter_map2type[f] == "Type":
                out_filters["Type"][self._filter_map2name[f]] = True
            elif filter_map2type[f] is not None:
                out_filters[f] = {"Value": filter_map2val[f]}
        if "HeightExclude2D" in filters:
            out_filters["Exclude2DObjects"] = True
        return out_filters

    @property
    @pyaedt_function_handler()
    def overridden_components(self) -> dict:
        """All overridden components.

        Examples
        --------
        >>> from ansys.aedt.core.modules.boundary.layout_boundary import PCBSettingsDeviceParts
        >>> obj = PCBSettingsDeviceParts()
        >>> obj.overridden_components

        """
        override_component = (
            self.pcb.props["NativeComponentDefinitionProvider"]
            .get("instanceOverridesMap", {})
            .get("oneOverrideBlk", [])
        )
        return {o["overrideName"]: o["overrideProps"] for o in override_component}

    @pyaedt_function_handler()
    def _override_common(
        self,
        map_name,
        package=None,
        part=None,
        reference_designator=None,
        filter_component: bool = False,
        power=None,
        r_jb=None,
        r_jc=None,
        height=None,
    ) -> bool:
        override_component = (
            self.pcb.props["NativeComponentDefinitionProvider"]
            .get(map_name, {})  # "instanceOverridesMap"
            .get("oneOverrideBlk", [])
        )
        if map_name == "instanceOverridesMap":
            for o in override_component:
                if o["overrideName"] == reference_designator:
                    override_component.remove(o)
        elif map_name == "definitionOverridesMap":  # pragma: no cover
            for o in override_component:
                if o["overridePartNumberName"] == part:
                    override_component.remove(o)
        new_filter = {}
        if filter_component or any(override_val is not None for override_val in [power, r_jb, r_jc, height]):
            if map_name == "instanceOverridesMap":
                new_filter.update({"overrideName": reference_designator})
            elif map_name == "definitionOverridesMap":  # pragma: no cover
                new_filter.update({"overridePartNumberName": part, "overrideGeometryName": package})
            new_filter.update(
                {
                    "overrideProps": {
                        "isFiltered": filter_component,
                        "isOverridePower": power is not None,
                        "isOverrideThetaJb": r_jb is not None,
                        "isOverrideThetaJc": r_jc is not None,
                        "isOverrideHeight": height is not None,
                        "powerOverride": power if power is not None else "nan",
                        "thetaJbOverride": r_jb if r_jb is not None else "nan",
                        "thetaJcOverride": r_jc if r_jc is not None else "nan",
                        "heightOverride": height if height is not None else "nan",
                    },
                }
            )
            override_component.append(new_filter)
        self.pcb.props["NativeComponentDefinitionProvider"][map_name] = {"oneOverrideBlk": override_component}
        return True

    @pyaedt_function_handler()
    def override_definition(
        self,
        package: str,
        part: str,
        filter_component: bool = False,
        power: str = None,
        r_jb: str = None,
        r_jc: str = None,
        height: str = None,
    ) -> bool:
        """Set component override.

        Parameters
        ----------
        package : str
            Package name of the definition to override.
        part : str
            Part name of the definition to override.
        filter_component : bool, optional
            Whether to filter out the component. The default is ``False``.
        power : str, optional
            Override component power. Default is ``None``, in which case the power is not overridden.
        r_jb : str, optional
            Override component r_jb value. Default is ``None``, in which case the resistance is not overridden.
        r_jc : str, optional
            Override component r_jc value. Default is ``None``, in which case the resistance is not overridden.
        height : str, optional
            Override component height value. Default is ``None``, in which case the height is not overridden.

        Returns
        -------
        bool
            ``True`` if successful, ``False`` otherwise.

        Examples
        --------
        >>> from ansys.aedt.core.modules.boundary.layout_boundary import PCBSettingsDeviceParts
        >>> obj = PCBSettingsDeviceParts()
        >>> obj.override_definition(package=1, part="Box1")

        """
        if self._app.settings.aedt_version < "2024.2":
            self._app.logger.add_message(
                message_type=2,
                message_text="This method is available only with AEDT 2024 R2 or later. "
                "Use 'override_instance()' method instead.",
                level="Design",
                proj_name=self._app.project_name,
                des_name=self._app.design_name,
            )
            return False
        return self._override_common(  # pragma : no cover
            "definitionOverridesMap",
            package=package,
            part=part,
            filter_component=filter_component,
            power=power,
            r_jb=r_jb,
            r_jc=r_jc,
            height=height,
        )

    @pyaedt_function_handler()
    def override_instance(
        self,
        reference_designator: str,
        filter_component: bool = False,
        power: str = None,
        r_jb: str = None,
        r_jc: str = None,
        height: str = None,
    ) -> bool:
        """Set instance override.

        Parameters
        ----------
        reference_designator : str
            Reference designator of the instance to override.
        filter_component : bool, optional
            Whether to filter out the component. The default is ``False``.
        power : str, optional
            Override component power. The default is ``None``, in which case the power is not overridden.
        r_jb : str, optional
            Override component r_jb value. The default is ``None``, in which case the resistance is not overridden.
        r_jc : str, optional
            Override component r_jc value. The default is ``None``, in which case the resistance is not overridden.
        height : str, optional
            Override component height value. The default is ``None``, in which case the height is not overridden.

        Returns
        -------
        bool
            ``True`` if successful, ``False`` otherwise.

        Examples
        --------
        >>> from ansys.aedt.core.modules.boundary.layout_boundary import PCBSettingsDeviceParts
        >>> obj = PCBSettingsDeviceParts()
        >>> obj.override_instance(reference_designator=1)

        """
        return self._override_common(
            "instanceOverridesMap",
            reference_designator=reference_designator,
            filter_component=filter_component,
            power=power,
            r_jb=r_jb,
            r_jc=r_jc,
            height=height,
        )
