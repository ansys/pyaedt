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

    def __init__(self, app, name: str, props=None, boundarytype: str = "Port") -> None:
        self.auto_update = False
        self._app = app
        self._name = name
        self.__props = None
        if props:
            self.__props = BoundaryProps(self, props)
        self.type = boundarytype
        self.auto_update = True

    @pyaedt_function_handler()
    def _initialize_tree_node(self) -> bool:
        aedt_object = self._resolve_aedt_object()
        if aedt_object:
            BinaryTreeNode.__init__(self, self._name, aedt_object, False, app=self._app, auto_update=self.auto_update)
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
            self._invalidate_tree_node()
            if self._app._boundaries.get(old_name) is self:
                self._app._boundaries.pop(old_name)
                self._app._boundaries[self._name] = self

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
        old_name = self._name
        auto_update = self.auto_update
        props = None
        old_port = None
        try:
            self.auto_update = False
            props = self.props
            if "Port" in props:
                old_port = props["Port"]
                dict.__setitem__(props, "Port", value)
            if not self.update():
                return
            self._name = value
            self._on_rename(old_name)
        finally:
            if props is not None and old_port is not None and self._name == old_name and old_name != value:
                dict.__setitem__(props, "Port", old_port)
            self.auto_update = auto_update

    @property
    def props(self) -> BoundaryProps:
        """Excitation data.

        Returns
        -------
        :class:BoundaryProps

        Examples
        --------
        >>> from ansys.aedt.core.modules.boundary.layout_boundary import BoundaryObject3dLayout
        >>> obj = BoundaryObject3dLayout()
        >>> obj.props

        """
        child_object = self.child_object
        has_obj_data = _has_get_obj_data(child_object)
        if self.__props and not (has_obj_data and self.auto_update):
            return self.__props
        if has_obj_data:
            props = _get_obj_data(child_object)
        else:
            boundary_data = self._get_boundary_data(self.name)
            props = boundary_data[0] if boundary_data else {}

        if props:
            self.__props = BoundaryProps(self, props)
            if has_obj_data:
                boundary_type = props.get("Type") or props.get("BoundType")
            else:
                boundary_type = boundary_data[1]
            if boundary_type:
                self._type = boundary_type
        return self.__props

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

    @pyaedt_function_handler()
    def _refresh_properties(self) -> None:
        if len(self._app.oeditor.GetProperties("EM Design", f"Excitations:{self.name}")) != len(self.props):
            propnames = self._app.oeditor.GetProperties("EM Design", f"Excitations:{self.name}")
            props = {}
            for prop in propnames:
                props[prop] = self._app.oeditor.GetPropertyValue("EM Design", f"Excitations:{self.name}", prop)
            self.__props = BoundaryProps(self, props)

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
        updated = False
        props = properties if properties is not None else self.props
        for el in list(props.keys()):
            if el == "Port" and self._name != props[el]:
                old_name = self._name
                new_name = props[el]
                self._app.oeditor.SetPropertyValue("EM Design", "Excitations:" + self.name, el, new_name)
                self._name = new_name
                self._on_rename(old_name)
            elif el in self._app.oeditor.GetProperties("EM Design", f"Excitations:{self.name}") and props[
                el
            ] != self._app.oeditor.GetPropertyValue("EM Design", "Excitations:" + self.name, el):
                self._app.oeditor.SetPropertyValue("EM Design", "Excitations:" + self.name, el, props[el])
                updated = True

        if updated:
            self._refresh_properties()

        return True

    def delete(self) -> bool:
        old_name = self.name
        if not super().delete():
            return False
        self._invalidate_tree_node()
        if self._app._boundaries.get(old_name) is self:
            self._app._boundaries.pop(old_name)
        return True
