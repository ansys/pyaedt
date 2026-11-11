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
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.props import Props as UserDefinedComponentProps
from ansys.aedt.core.generic.protocols import _AppWithOProject
from ansys.aedt.core.internal.desktop_sessions import _edb_sessions
from ansys.aedt.core.modeler.cad.elements_3d import BinaryTreeNode

if TYPE_CHECKING:
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
        self.definition_name = None
        defined_components = self._app.oeditor.Get3DComponentDefinitionNames()
        defined_components = defined_components if defined_components else []
        for component in defined_components:
            if self._m_name in self._app.oeditor.Get3DComponentInstanceNames(component):
                self.definition_name = component
                break

        if component_type:
            self._legacy_props = {
                "TargetCS": "Global",
                "SubmodelDefinitionName": self.definition_name,
                "ComponentPriorityLists": {},
                "NextUniqueID": 0,
                "MoveBackwards": False,
                "DatasetType": "ComponentDatasetType",
                "DatasetDefinitions": {},
                "BasicComponentInfo": {
                    "ComponentName": self.definition_name,
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
                self._legacy_props
                self._update_props(
                    self._props["NativeComponentDefinitionProvider"],
                    props.get("NativeComponentDefinitionProvider", props),
                )
            self.native_properties = self._props["NativeComponentDefinitionProvider"]

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
