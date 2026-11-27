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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ansys.aedt.core import Hfss3dLayout

from ansys.aedt.core.application import _get_obj_data
from ansys.aedt.core.application import _has_get_obj_data
from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.data_handlers import _dict2arg
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.props import Props as BoundaryProps
from ansys.aedt.core.modeler.cad.elements_3d import BinaryTreeNode
from ansys.aedt.core.modules.boundary.common import BoundaryCommon


class BoundaryObject3dLayout(BoundaryCommon, BinaryTreeNode, PyAedtBase):
    """Manages boundary data and execution for Hfss3dLayout.

    Parameters
    ----------
    app : object
        An AEDT application from ``ansys.aedt.core.application``.
    name : str
        Name of the boundary.
    props : dict, optional
        Properties of the boundary.
    boundarytype : str
        Type of the boundary.

    Examples
    --------
    >>> from ansys.aedt.core.modules.boundary.layout_boundary import BoundaryObject3dLayout
    >>> obj = BoundaryObject3dLayout()

    """

    def __init__(self, app: Hfss3dLayout, name: str, props=None, boundarytype: str = "Port") -> None:
        self._app = app
        self._name = name
        self._legacy_props = props or {}
        self.type = boundarytype
        if props:
            self._has_getobject = False
        else:
            self._has_getobject = _has_get_obj_data(self.child_object)

    def __getitem__(self, key):
        return self.props[key]

    def __setitem__(self, key, value):
        self.props[key] = value

    @pyaedt_function_handler()
    def _initialize_tree_node(self) -> bool:
        aedt_object = self._resolve_aedt_object()
        if aedt_object:
            BinaryTreeNode.__init__(self, self._name, aedt_object, False, app=self._app)
            return True
        return False

    def _resolve_aedt_object(self):
        excitations_oo = self._app.get_oo_object(self._app.odesign, "Excitations")
        child_object = None
        if self.name in self._app.get_oo_name(excitations_oo):
            child_object = self._app.get_oo_object(excitations_oo, self.name)

        if "Boundaries" in self._app.get_oo_name(self._app.odesign):
            boundaries_oo = self._app.get_oo_object(self._app.odesign, "Boundaries")
            if self.name in self._app.get_oo_name(boundaries_oo):
                child_object = self._app.get_oo_object(boundaries_oo, self.name)

        return child_object

    def _on_rename(self, old_name):
        if self._name != old_name:
            self._sync_cached_name()
            self._invalidate_tree_node()
            if self._app._boundaries.get(old_name) is self:
                self._app._boundaries.pop(old_name)
                self._app._boundaries[self._name] = self

    def _sync_cached_name(self):
        if "Port" in self._legacy_props:
            self._legacy_props["Port"] = self._name
        nested = self._legacy_props.get("Properties")
        if isinstance(nested, dict) and "Port" in nested:
            nested["Port"] = self._name

    def update_property(self, prop_name: str, prop_value: str) -> bool:
        old_name = self._name
        result = super().update_property(prop_name, prop_value)
        if prop_name == "Name":
            self._on_rename(old_name)
        return result

    @property
    def name(self) -> str:
        """Boundary Name.

        Examples
        --------
        >>> from ansys.aedt.core.modules.boundary.layout_boundary import BoundaryObject3dLayout
        >>> obj = BoundaryObject3dLayout()
        >>> obj.name

        """
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if value != self._name:
            self.update({"Port": value})

    @property
    def props(self) -> BoundaryProps:
        """Excitation data from AEDT or, when unavailable, the editor property cache.

        For AEDT objects supporting ``GetObjData``, properties are read from
        the object on each access. Older objects use a cached editor snapshot.
        Editing a property applies the change to AEDT immediately. Assign a
        complete dictionary obtained with ``props.to_dict()`` to apply several
        changes together.

        Returns
        -------
        :class:BoundaryProps

        Examples
        --------
        >>> from ansys.aedt.core.modules.boundary.layout_boundary import BoundaryObject3dLayout
        >>> obj = BoundaryObject3dLayout()
        >>> obj.props

        """
        if self._has_getobject:
            self._legacy_props = _get_obj_data(self.child_object)
        elif not self._legacy_props:
            self._legacy_props = self._get_editor_properties()
        boundary_type = self._legacy_props.get("Type") or self._legacy_props.get("BoundType")
        if boundary_type:
            self.type = boundary_type
        return BoundaryProps(self, self._legacy_props)

    @props.setter
    def props(self, value: dict) -> None:
        if not self.update(value):
            raise RuntimeError(f"Failed to update port {self.name}.")

    @pyaedt_function_handler()
    def _get_args(self, props=None):
        """Retrieve arguments.

        Parameters
        ----------
        props :
            The default is ``None``.

        Returns
        -------
        list
            List of boundary properties.

        """
        if props is None:
            props = self.props
        arg = ["NAME:" + self.name]
        _dict2arg(props, arg)
        return arg

    def _get_editor_properties(self):
        server = f"Excitations:{self.name}"
        names = self._app.oeditor.GetProperties("EM Design", server)
        props = {"Properties": {}}
        for name in names:
            if "Port" in name:
                props[name] = self._app.oeditor.GetPropertyValue("EM Design", server, name)
            else:
                props["Properties"][name] = self._app.oeditor.GetPropertyValue("EM Design", server, name)
        return props

    @pyaedt_function_handler()
    def update(self, properties: dict = None) -> bool:
        """Update the boundary.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.core.modules.boundary.layout_boundary import BoundaryObject3dLayout
        >>> obj = BoundaryObject3dLayout()
        >>> obj.update()

        """
        props = properties if properties is not None else self.props
        changes_only = isinstance(props, BoundaryProps)
        sections = [(props, self._legacy_props)]
        if isinstance(props.get("Properties"), dict):
            sections.append((props["Properties"], self._legacy_props.get("Properties", {})))
        editor_names = self._app.oeditor.GetProperties("EM Design", f"Excitations:{self.name}")
        for section, previous in sections:
            for el, value in section.items():
                if isinstance(value, dict) or (changes_only and el in previous and previous[el] == value):
                    continue
                if el == "Port" and self._name != value:
                    old_name = self._name
                    self._app.oeditor.SetPropertyValue("EM Design", "Excitations:" + old_name, el, value)
                    self._name = value
                    self._on_rename(old_name)
                elif el in editor_names and value != self._app.oeditor.GetPropertyValue(
                    "EM Design", "Excitations:" + self.name, el
                ):
                    self._app.oeditor.SetPropertyValue("EM Design", "Excitations:" + self.name, el, value)
                elif changes_only and el not in editor_names and el != "Port":
                    self._app.logger.warning("Property %s cannot be updated for port %s.", el, self.name)
                    return False

        if not self._has_getobject:
            self._legacy_props = self._get_editor_properties()
        elif isinstance(props, BoundaryProps):
            self._legacy_props = props.to_dict()
        self._sync_cached_name()
        return True

    def delete(self) -> bool:
        old_name = self.name
        if not super().delete():
            return False
        self._invalidate_tree_node()
        if self._app._boundaries.get(old_name) is self:
            self._app._boundaries.pop(old_name)
        return True
