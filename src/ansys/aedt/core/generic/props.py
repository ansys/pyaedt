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

"""Unified AEDT property dictionary used by boundaries, setups, mesh, CS, and history."""

from __future__ import annotations

import inspect
import json
import os

from ansys.aedt.core.generic.numbers_utils import _units_assignment
from ansys.aedt.core.generic.settings import settings

ASSIGNMENT_KEYS = ("Edges", "Faces", "Objects", "Vertices")

_OWNER_ALIASES = (
    "_pyaedt_owner",
    "_pyaedt_boundary",
    "_pyaedt_setup",
    "_pyaedt_mesh",
    "_pyaedt_cs",
    "_pyaedt_lists",
    "_pyaedt_user_defined_component",
    "_pyaedt_child",
)


def _owner_logger(owner):
    """Return the logger attached to an owning PyAEDT object."""
    app = getattr(owner, "_app", None)
    if app is not None:
        logger = getattr(app, "logger", None)
        if logger is not None:
            return logger
    for attr in ("_logger", "logger"):
        logger = getattr(owner, attr, None)
        if logger is not None:
            return logger
    return settings.logger


def _update_parameters(func):
    """Return explicit parameters of an owner ``update`` method, skipping ``self`` and *args/**kwargs."""
    try:
        signature = inspect.signature(func)
    except (TypeError, ValueError):
        return []
    parameters = []
    for parameter in signature.parameters.values():
        if parameter.name == "self":
            continue
        if parameter.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue
        parameters.append(parameter)
    return parameters


class BoundaryAssignmentList(list):
    """List of assignment entries that triggers ``update_assignment`` on mutation."""

    def __init__(self, props, iterable=()) -> None:
        super().__init__(iterable)
        self._boundary_props = props

    @staticmethod
    def _as_name(object):
        return object.name if not isinstance(object, str) else object

    def _notify(self) -> None:
        props = self._boundary_props
        owner = getattr(props, "_pyaedt_owner", None)
        if owner is None:
            return
        if not getattr(owner, "auto_update", False):
            return
        update_assignment = getattr(owner, "update_assignment", None)
        if not callable(update_assignment):
            return
        if not update_assignment(props._root()):
            _owner_logger(owner).warning("Update of assignment Failed. Check needed arguments")

    def append(self, object) -> None:
        super().append(self._as_name(object))
        self._notify()

    def extend(self, iterable) -> None:
        super().extend([self._as_name(object) for object in iterable])
        self._notify()

    def insert(self, index, object) -> None:
        super().insert(index, self._as_name(object))
        self._notify()

    def remove(self, object) -> None:
        super().remove(self._as_name(object))
        self._notify()

    def pop(self, index=-1):
        value = super().pop(index)
        self._notify()
        return value

    def clear(self) -> None:
        super().clear()
        self._notify()

    def __setitem__(self, key, value) -> None:
        super().__setitem__(key, value)
        self._notify()

    def __delitem__(self, key) -> None:
        super().__delitem__(key)
        self._notify()

    def __iadd__(self, other):
        super().__iadd__(other)
        self._notify()
        return self


class Props(dict):
    """AEDT component internal parameters.

    Nested dictionaries are wrapped so that ``props["a"]["b"]["c"] = value``
    still updates the full property tree. Assignment keys (``Objects``,
    ``Faces``, ``Edges``, ``Vertices``) are stored as ``BoundaryAssignmentList``
    so in-place list mutations trigger ``update_assignment``.

    Owner objects keep working through their existing update APIs:
    ``update(props)``, ``update(key, value)``, ``update()``,
    ``update_assignment``, ``update_native``, and ``update_property``.
    """

    def __init__(self, owner, props, parent=None) -> None:
        self._pyaedt_owner = None
        dict.__init__(self)
        self._pyaedt_parent = parent
        self._bind_owner(owner)
        if props:
            for key, value in props.items():
                dict.__setitem__(self, key, self._wrap(key, value))

    def _bind_owner(self, owner) -> None:
        for name in _OWNER_ALIASES:
            object.__setattr__(self, name, owner)

    def _root(self):
        """Return the top-level ``Props`` for this tree."""
        parent = getattr(self, "_pyaedt_parent", None)
        return parent if parent is not None else self

    def _wrap(self, key, value):
        if isinstance(value, dict):
            return type(self)(self._pyaedt_owner, value, parent=self._root())
        if key in ASSIGNMENT_KEYS and isinstance(value, list) and not isinstance(value, BoundaryAssignmentList):
            return BoundaryAssignmentList(self, value)
        if isinstance(value, list) and not isinstance(value, BoundaryAssignmentList):
            return [
                type(self)(self._pyaedt_owner, el, parent=self._root()) if isinstance(el, dict) else el for el in value
            ]
        return value

    def _setitem_without_update(self, key, value):
        dict.__setitem__(self, key, value)

    def __setitem__(self, key, value):
        if isinstance(value, dict):
            dict.__setitem__(self, key, type(self)(self._pyaedt_owner, value, parent=self._root()))
        else:
            value = _units_assignment(value)
            dict.__setitem__(self, key, self._wrap(key, value) if isinstance(value, list) else value)

        res = self._apply_owner_update(key, value)
        if res is False:
            _owner_logger(self._pyaedt_owner).warning("Update of %s Failed. Check needed arguments", key)

    def _apply_owner_update(self, key, value):
        owner = self._pyaedt_owner
        if owner is None:
            return True

        # BinaryTreeNode.properties must use update_property, even when the owner also has update()
        # (BoundaryObject, MeshOperation).
        history_props = getattr(owner, "_props", None)
        if history_props is self or history_props is self._root():
            update_property = getattr(owner, "update_property", None)
            if callable(update_property):
                return update_property(key, value)

        if key in ASSIGNMENT_KEYS:
            update_assignment = getattr(owner, "update_assignment", None)
            if callable(update_assignment):
                return update_assignment(self._root())

        update = getattr(owner, "update", None)
        if callable(update):
            parameters = _update_parameters(update)
            if not parameters:
                return update()
            first = parameters[0].name
            if first in ("key_name", "key") and len(parameters) >= 2:
                return update(key, value)
            if first in ("props", "properties", "update_dictionary"):
                return update(self._root())
            if len(parameters) == 1:
                return update(self._root())
            return update()

        update_property = getattr(owner, "update_property", None)
        if callable(update_property):
            return update_property(key, value)

        update_native = getattr(owner, "update_native", None)
        if callable(update_native):
            return update_native()
        return True

    def delete_all(self) -> None:
        for item in list(self.keys()):
            if not str(item).startswith("_pyaedt_"):
                dict.__delitem__(self, item)

    def pop(self, key, default=None):
        return dict.pop(self, key, default)

    def _export_properties_to_json(self, file_path, overwrite: bool = False) -> bool:
        """Export properties to a JSON file.

        Parameters
        ----------
        file_path : str
            File path for the JSON file.
        overwrite : bool, optional
            Whether to overwrite an existing file. The default is ``False``.
        """
        filter_keys = {"DataId", "SimSetupID", "ProdMajVerID", "ProjDesignSetup", "ProdMinVerID", "NumberOfProcessors"}
        if not file_path.endswith(".json"):
            file_path = file_path + ".json"
        export_dict = {k: v for k, v in self.items() if k not in filter_keys}
        if os.path.isfile(file_path) and not overwrite:
            if settings.logger:
                settings.logger.warning(f"Unable to overwrite file:{file_path}")
            return False
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(export_dict, indent=4, ensure_ascii=False))
        return True

    def _import_properties_from_json(self, file_path) -> bool:
        """Import properties from a JSON file.

        Parameters
        ----------
        file_path : str
            File path for the JSON file.
        """

        def set_props(target, source) -> None:
            for k, v in source.items():
                if k not in target:
                    _owner_logger(self._pyaedt_owner).warning(f"{k} is not a valid property name.")
                if not isinstance(v, dict):
                    dict.__setitem__(self, k, v)
                else:
                    if k not in target:
                        dict.__setitem__(self, k, {})
                    set_props(target[k], v)

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            set_props(self, data)
            if getattr(self._pyaedt_owner, "auto_update", False):
                res = self._apply_owner_update(None, None)
                if res is False:
                    _owner_logger(self._pyaedt_owner).warning("Update of properties failed. Check needed arguments")
        return True


AssignmentList = BoundaryAssignmentList
BoundaryProps = Props
SetupProps = Props
MeshProps = Props
CsProps = Props
ListsProps = Props
UserDefinedComponentProps = Props
HistoryProps = Props
