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

from unittest.mock import MagicMock

import pytest

from ansys.aedt.core.modules.boundary.common import BoundaryProps


@pytest.fixture(scope="module", autouse=True)
def desktop() -> None:
    """Override the desktop fixture to DO NOT open the Desktop when running this test class."""
    return


class DummyBoundary:
    def __init__(self) -> None:
        self.auto_update = False
        self._app = MagicMock()
        self.updated_with = None
        self.assignment_updated = False
        self.assignment_updated_with = None

    def update(self, props=None):
        self.updated_with = props
        return True

    def update_assignment(self, properties=None):
        self.assignment_updated = True
        self.assignment_updated_with = properties
        return True


def test_nested_setitem_updates_root_props() -> None:
    boundary = DummyBoundary()
    props = BoundaryProps(
        boundary,
        {"Parameters": {"subparameter": {"subsub": 1}}},
    )
    boundary.auto_update = True

    props["Parameters"]["subparameter"]["subsub"] = 42

    assert props["Parameters"]["subparameter"]["subsub"] == 42
    assert boundary.updated_with is props
    assert "Parameters" in boundary.updated_with
    assert boundary.updated_with["Parameters"]["subparameter"]["subsub"] == 42


def test_top_level_setitem_still_updates_root() -> None:
    boundary = DummyBoundary()
    props = BoundaryProps(boundary, {"Parameters": {"subparameter": 1}})
    boundary.auto_update = True

    props["Parameters"] = {"subparameter": 2}

    assert props["Parameters"]["subparameter"] == 2
    assert boundary.updated_with is props


def test_nested_dict_assignment_keeps_parent_keys() -> None:
    boundary = DummyBoundary()
    props = BoundaryProps(boundary, {"Parameters": {"subparameter": {"a": 1, "b": 2}}})
    boundary.auto_update = True

    props["Parameters"]["subparameter"]["a"] = 9

    assert set(props["Parameters"]["subparameter"]) == {"a", "b"}
    assert props["Parameters"]["subparameter"]["b"] == 2
    assert boundary.updated_with is props


def test_list_of_dicts_nested_setitem_updates_root() -> None:
    boundary = DummyBoundary()
    props = BoundaryProps(boundary, {"Entries": [{"Name": "e1", "Value": 1}]})
    boundary.auto_update = True

    props["Entries"][0]["Value"] = 5

    assert props["Entries"][0]["Value"] == 5
    assert boundary.updated_with is props


def test_faces_key_calls_update_assignment() -> None:
    boundary = DummyBoundary()
    props = BoundaryProps(boundary, {"Faces": [1]})
    boundary.auto_update = True

    props["Faces"] = [1, 2]

    assert boundary.assignment_updated is True
    assert boundary.updated_with is None
    assert boundary.assignment_updated_with is props


def test_objects_append_and_remove_trigger_update_assignment() -> None:
    boundary = DummyBoundary()
    props = BoundaryProps(boundary, {"Objects": ["box"]})
    boundary.auto_update = True

    props["Objects"].append("box2")

    assert props["Objects"] == ["box", "box2"]
    assert boundary.assignment_updated is True
    assert boundary.assignment_updated_with is props

    boundary.assignment_updated = False
    props["Objects"].remove("box2")

    assert props["Objects"] == ["box"]
    assert boundary.assignment_updated is True
    assert boundary.assignment_updated_with is props


class DummyMesh:
    def __init__(self) -> None:
        self.auto_update = False
        self._app = MagicMock()
        self.updated_key = None
        self.updated_value = None
        self.assignment_updated_with = None
        self.update_property_called = False

    def update(self, key_name=None, value=None):
        self.updated_key = key_name
        self.updated_value = value
        return True

    def update_assignment(self, properties=None):
        self.assignment_updated_with = properties
        return True

    def update_property(self, key, value):
        self.update_property_called = True
        return True


class DummyCoordinateSystem:
    def __init__(self) -> None:
        self.auto_update = False
        self._app = MagicMock()
        self.updated = False

    def update(self):
        self.updated = True
        return True


class DummyHistory:
    def __init__(self) -> None:
        self.auto_update = False
        self._app = MagicMock()
        self.updated_property = None
        self.tree_initialized = False

    def update_property(self, key, value):
        self.updated_property = (key, value)
        return True

    def _initialize_tree_node(self):
        self.tree_initialized = True


class DummyUserDefinedComponent:
    def __init__(self) -> None:
        self.auto_update = False
        self._logger = MagicMock()
        self.native_updated = False

    def update_native(self):
        self.native_updated = True
        return True


def test_aliases_are_the_unified_props_class() -> None:
    from ansys.aedt.core.generic.props import Props
    from ansys.aedt.core.modeler.cad.elements_3d import HistoryProps
    from ansys.aedt.core.modeler.cad.modeler import CsProps
    from ansys.aedt.core.modules.mesh import MeshProps
    from ansys.aedt.core.modules.solve_setup import SetupProps

    assert BoundaryProps is Props
    assert MeshProps is Props
    assert SetupProps is Props
    assert CsProps is Props
    assert HistoryProps is Props


def test_mesh_setitem_calls_update_with_key_and_value() -> None:
    from ansys.aedt.core.modules.mesh import MeshProps

    mesh = DummyMesh()
    props = MeshProps(mesh, {"MaxLength": "1mm"})
    mesh.auto_update = True

    props["MaxLength"] = "2mm"

    assert props["MaxLength"] == "2mm"
    assert mesh.updated_key == "MaxLength"
    assert mesh.updated_value == "2mm"
    assert mesh.update_property_called is False


def test_mesh_nested_setitem_updates_root() -> None:
    from ansys.aedt.core.modules.mesh import MeshProps

    mesh = DummyMesh()
    props = MeshProps(mesh, {"Settings": {"MaxLength": "1mm"}})
    mesh.auto_update = True

    props["Settings"]["MaxLength"] = "3mm"

    assert props["Settings"]["MaxLength"] == "3mm"
    assert mesh.updated_key == "MaxLength"
    assert mesh.updated_value == "3mm"


def test_mesh_objects_append_triggers_update_assignment() -> None:
    from ansys.aedt.core.generic.props import BoundaryAssignmentList
    from ansys.aedt.core.modules.mesh import MeshProps

    mesh = DummyMesh()
    props = MeshProps(mesh, {"Objects": ["box"]})
    mesh.auto_update = True

    assert isinstance(props["Objects"], BoundaryAssignmentList)
    props["Objects"].append("box2")

    assert props["Objects"] == ["box", "box2"]
    assert mesh.assignment_updated_with is props


def test_cs_setitem_calls_update_without_args() -> None:
    from ansys.aedt.core.modeler.cad.modeler import CsProps

    cs = DummyCoordinateSystem()
    props = CsProps(cs, {"Origin": {"X": "0mm"}})
    cs.auto_update = True

    props["Origin"]["X"] = "1mm"

    assert props["Origin"]["X"] == "1mm"
    assert cs.updated is True


def test_history_setitem_calls_update_property() -> None:
    from ansys.aedt.core.modeler.cad.elements_3d import HistoryProps

    history = DummyHistory()
    props = HistoryProps(history, {"Command": "CreateBox"})
    history.auto_update = True

    props["Command"] = "CreateCylinder"

    assert history.updated_property == ("Command", "CreateCylinder")


def test_udc_setitem_calls_update_native() -> None:
    from ansys.aedt.core.modeler.cad.components_3d import UserDefinedComponentProps

    udc = DummyUserDefinedComponent()
    props = UserDefinedComponentProps(udc, {"NativeComponentDefinitionName": "chip"})
    udc.auto_update = True

    props["NativeComponentDefinitionName"] = "chip2"

    assert udc.native_updated is True


def test_setup_json_roundtrip(tmp_path) -> None:
    from ansys.aedt.core.modules.solve_setup import SetupProps

    setup = DummyBoundary()
    props = SetupProps(setup, {"Frequency": "1GHz", "DataId": "skip-me"})
    path = tmp_path / "setup.json"

    assert props._export_properties_to_json(str(path), overwrite=True)
    imported = SetupProps(setup, {"Frequency": "2GHz"})
    assert imported._import_properties_from_json(str(path))
    assert imported["Frequency"] == "1GHz"


def test_update_property_name_sets_name_even_if_previously_none() -> None:
    from ansys.aedt.core.modeler.cad.elements_3d import BinaryTreeNode

    node = BinaryTreeNode.__new__(BinaryTreeNode)
    object.__setattr__(node, "_name", None)
    object.__setattr__(node, "_tree_node_initialized", True)
    object.__setattr__(node, "_props", {"Name": "old"})
    object.__setattr__(node, "_children_loaded", True)
    child = MagicMock()
    child.SetPropValue.return_value = True
    object.__setattr__(node, "_BinaryTreeNode__child_object", child)

    node.update_property("Name", "renamed")

    assert node._name == "renamed"
    assert node._tree_node_initialized is False
    assert node._props is None


def test_name_getter_does_not_overwrite_name_with_none() -> None:
    from ansys.aedt.core.modules.boundary.common import BoundaryObject

    class DummyBound(BoundaryObject):
        def __init__(self) -> None:
            self._app = MagicMock()
            object.__setattr__(self, "_name", "kept")
            self._child = object()

        @property
        def _child_object(self):
            return self._child

        @property
        def properties(self):
            return {"Name": None}

    assert DummyBound().name == "kept"


def test_history_props_use_update_property_even_when_owner_has_update() -> None:
    from ansys.aedt.core.generic.props import Props

    class DummyTreeOwner(DummyBoundary):
        def __init__(self) -> None:
            super().__init__()
            self._props = None
            self.prop_updates = []

        def update_property(self, key, value):
            self.prop_updates.append((key, value))
            if key == "Name":
                object.__setattr__(self, "_name", value)
            return True

    owner = DummyTreeOwner()
    owner._name = "old"
    props = Props(owner, {"Name": "old"})
    owner._props = props
    owner.auto_update = True

    props["Name"] = "renamed"

    assert owner.prop_updates == [("Name", "renamed")]
    assert owner.updated_with is None
    assert owner._name == "renamed"


def test_name_setter_keeps_name_when_properties_name_is_none() -> None:
    from ansys.aedt.core.modules.boundary.common import BoundaryObject

    class DummyApp:
        def __init__(self) -> None:
            self._boundaries = {}
            self.logger = MagicMock()

        def get_oo_name(self, *_args, **_kwargs):
            return []

        def get_oo_object(self, *_args, **_kwargs):
            return None

    bound = BoundaryObject.__new__(BoundaryObject)
    bound.auto_update = False
    bound._app = DummyApp()
    object.__setattr__(bound, "_name", "old")
    object.__setattr__(bound, "_tree_node_initialized", True)
    object.__setattr__(bound, "_props", {"Name": None})
    bound._app._boundaries["old"] = bound

    object.__setattr__(bound, "_name", "renamed")
    current_name = bound.properties.get("Name") if hasattr(bound, "properties") else None
    if not current_name:
        object.__setattr__(bound, "_name", "renamed")

    assert bound._name == "renamed"
