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

"""Unit tests for the modeler round-trip reduction (object type caching and fast paths)."""

import json
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from ansys.aedt.core import Hfss
from ansys.aedt.core.application.design import Design
from ansys.aedt.core.modeler.cad.elements_3d import FacePrimitive
from ansys.aedt.core.modeler.cad.object_3d import Object3d
from ansys.aedt.core.modeler.cad.primitives import GeometryModeler


def _make_editor(groups: dict) -> MagicMock:
    editor = MagicMock()
    editor.GetObjectsInGroup.side_effect = lambda group: list(groups.get(group, []))
    editor.GetPoints.return_value = []
    editor.GetChildNames.return_value = ["Global:XY", "Global:YZ"]
    editor.GetObjectIDByName.side_effect = lambda name: 10 + sorted(groups.get("Solids", [])).index(name)
    editor.GetAllObjectInfo.side_effect = lambda names: json.dumps(
        [{"Name": n, "id": 10 + sorted(groups.get("Solids", [])).index(n)} for n in names]
    )
    return editor


@pytest.fixture
def modeler():
    """Create a ``GeometryModeler`` bound to a mocked editor with two solids."""
    groups = {"Solids": ["Box1", "Box2"], "Sheets": [], "Lines": [], "Unclassified": []}
    editor = _make_editor(groups)
    with patch("ansys.aedt.core.hfss.Hfss.__init__", lambda x: None):
        app = Hfss()
        app._logger = MagicMock()
        app._oeditor = editor
        app._odesign = MagicMock()
        app.get_oo_object = MagicMock(side_effect=lambda editor, name: MagicMock(name=name))
        gm = GeometryModeler(app)
    gm._groups = groups
    return gm


def test_cached_object_types_single_refresh(modeler) -> None:
    editor = modeler.oeditor
    editor.GetObjectsInGroup.reset_mock()
    with modeler._cached_object_types():
        for _ in range(5):
            assert modeler.object_names == ["Box1", "Box2"]
    # One refresh queries the four groups once.
    assert editor.GetObjectsInGroup.call_count == 4
    # Leaving the scope re-enables the refresh.
    editor.GetObjectsInGroup.reset_mock()
    _ = modeler.object_names
    assert editor.GetObjectsInGroup.call_count == 4


def test_cached_object_types_nested_scope(modeler) -> None:
    with modeler._cached_object_types():
        with modeler._cached_object_types():
            _ = modeler.object_names
        assert modeler._object_types_cached
    assert not modeler._object_types_cached
    assert modeler._object_types_cache_depth == 0


def test_refresh_planes_reuses_handles(modeler) -> None:
    modeler._refresh_planes()
    first = dict(modeler._planes)
    modeler._app.get_oo_object.reset_mock()
    modeler._refresh_planes()
    modeler._app.get_oo_object.assert_not_called()
    assert modeler._planes == first
    modeler.oeditor.GetChildNames.return_value = ["Global:XY", "Global:YZ", "Global:XZ"]
    modeler._refresh_planes()
    modeler._app.get_oo_object.assert_called_once()
    assert set(modeler._planes) == {"Global:XY", "Global:YZ", "Global:XZ"}


def test_get_obj_id_fast_path(modeler) -> None:
    modeler.refresh_all_ids()
    assert modeler.get_obj_id("Box2") == 11
    modeler.oeditor.GetObjectsInGroup.reset_mock()
    assert modeler.get_obj_id("Box1") == 10
    assert modeler.does_object_exists("Box1")
    modeler.oeditor.GetObjectsInGroup.assert_not_called()


def test_get_obj_id_missing_object(modeler) -> None:
    modeler.refresh_all_ids()
    assert modeler.get_obj_id("Missing") is None
    assert not modeler.does_object_exists("Missing")


def test_delete_filters_invalid_names_without_skipping(modeler) -> None:
    """Consecutive invalid names were skipped when removing items while iterating."""
    modeler.refresh_all_ids()
    modeler.oeditor.Delete.reset_mock()
    assert modeler.delete(["Box1", "Bad1", "Bad2", "Box2"])
    selections = modeler.oeditor.Delete.call_args[0][0][2]
    assert selections == "Box1,Box2"


def test_delete_returns_false_when_nothing_valid(modeler) -> None:
    modeler.refresh_all_ids()
    assert not modeler.delete(["Bad1", "Bad2"])
    modeler.oeditor.Delete.assert_not_called()


def test_object_list_queries_points_once(modeler) -> None:
    modeler.refresh_all_ids()
    modeler.oeditor.GetPoints.reset_mock()
    objs = modeler.object_list
    assert sorted(o.name for o in objs) == ["Box1", "Box2"]
    assert modeler.oeditor.GetPoints.call_count == 1


def test_faces_single_get_face_ids_call() -> None:
    primitives = MagicMock()
    primitives.oeditor.GetFaceIDs.return_value = ["7", "8"]
    with patch("ansys.aedt.core.modeler.cad.object_3d.Object3d.__init__", lambda x: None):
        obj = Object3d()
    obj._primitives = primitives
    obj._m_name = "Box1"
    obj._object_type = "Solid"
    obj._face_ids = []
    obj._faces = []
    faces = obj.faces
    assert [f.id for f in faces] == [7, 8]
    assert primitives.oeditor.GetFaceIDs.call_count == 1


def test_face_center_single_get_face_center_call() -> None:
    obj = MagicMock()
    obj._oeditor.GetFaceCenter.return_value = ["1", "2", "3"]
    face = FacePrimitive(obj, 7)
    assert face.center == [1.0, 2.0, 3.0]
    assert face.is_planar
    assert obj._oeditor.GetFaceCenter.call_count == 1


def test_face_center_non_planar_fallback() -> None:
    obj = MagicMock()
    obj._oeditor.GetFaceCenter.side_effect = Exception("not planar")
    face = FacePrimitive(obj, 7)
    with patch.object(FacePrimitive, "vertices", new=[]), patch.object(FacePrimitive, "edges", new=[]):
        assert face.center is None
    assert face.is_planar is False


@pytest.mark.parametrize(
    ("expression", "expected"),
    [(3, 3.0), (2.5, 2.5), ("42", 42.0), ("-1e-3", -1e-3), (".5", 0.5), ("1e3", 1000.0), (" 7 ", 7.0)],
)
def test_evaluate_expression_numeric_fast_path(expression, expected) -> None:
    design = MagicMock()
    result = Design.evaluate_expression(design, expression)
    assert result == expected
    assert not design._variable_manager.variables.__contains__.called


def test_evaluate_expression_variable_lookup_still_used() -> None:
    design = MagicMock()
    variable = MagicMock(si_value=0.01)
    design._variable_manager.variables = {"width": variable}
    assert Design.evaluate_expression(design, "width") == 0.01


def test_find_object_from_face_id_single_lookup(modeler) -> None:
    modeler.oeditor.GetObjectNameByFaceID.return_value = "Box2"
    assert modeler._find_object_from_face_id(42) == "Box2"
    modeler.oeditor.GetObjectNameByFaceID.assert_called_once_with(42)
    modeler.oeditor.GetFaceIDs.assert_not_called()


def test_find_object_from_face_id_not_found(modeler) -> None:
    modeler.oeditor.GetObjectNameByFaceID.return_value = ""
    assert modeler._find_object_from_face_id(42) is None
    modeler.oeditor.GetObjectNameByFaceID.return_value = "NonExisting"
    assert modeler._find_object_from_face_id(42) is None


def test_find_object_from_edge_id_single_lookup(modeler) -> None:
    modeler.oeditor.GetObjectNameByEdgeID.return_value = "Box1"
    assert modeler._find_object_from_edge_id("7") == "Box1"
    modeler.oeditor.GetObjectNameByEdgeID.assert_called_once_with(7)
    modeler.oeditor.GetEdgeIDsFromObject.assert_not_called()
    modeler.oeditor.GetObjectNameByEdgeID.return_value = ""
    assert modeler._find_object_from_edge_id(8) is None


def test_move_face_one_lookup_per_face(modeler) -> None:
    modeler.oeditor.GetObjectNameByFaceID.side_effect = lambda f: "Box1" if int(f) < 200 else "Box2"
    with patch.object(GeometryModeler, "model_units", new="mm"):
        assert modeler.move_face([101, 102, 201], offset=1.0)
    assert modeler.oeditor.GetObjectNameByFaceID.call_count == 3
    params = modeler.oeditor.MoveFaces.call_args[0][1]
    assert [int(f) for f in params[1][-1]] == [101, 102]
    assert [int(f) for f in params[2][-1]] == [201]


@pytest.mark.parametrize("is_polyline", [False, True])
def test_create_object_explicit_type_skips_lines_query(modeler, is_polyline) -> None:
    modeler.oeditor.GetObjectsInGroup.reset_mock()
    with patch.object(Object3d, "id", new=99):
        obj = modeler._create_object("Box1", is_polyline=is_polyline)
    assert obj.is_polyline is is_polyline
    assert all(c.args != ("Lines",) for c in modeler.oeditor.GetObjectsInGroup.call_args_list)


def test_create_object_default_queries_lines(modeler) -> None:
    modeler._groups["Lines"] = ["Poly1"]
    modeler.oeditor.GetObjectsInGroup.reset_mock()
    with patch.object(Object3d, "id", new=99):
        obj = modeler._create_object("Poly1")
    assert obj.is_polyline is True
    assert any(c.args == ("Lines",) for c in modeler.oeditor.GetObjectsInGroup.call_args_list)


def test_function_handler_skips_logging_when_debug_disabled() -> None:
    from ansys.aedt.core.generic import general_methods
    from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
    from ansys.aedt.core.generic.settings import settings

    @pyaedt_function_handler()
    def add_one(value):
        return value + 1

    old = (settings.enable_debug_logger, settings.enable_debug_edb_logger)
    try:
        settings.enable_debug_logger = False
        settings.enable_debug_edb_logger = False
        with patch.object(general_methods, "_log_method") as log_method:
            assert add_one(1) == 2
            log_method.assert_not_called()
        settings.enable_debug_logger = True
        with patch.object(general_methods, "_log_method") as log_method:
            assert add_one(1) == 2
            log_method.assert_called_once()
    finally:
        settings.enable_debug_logger, settings.enable_debug_edb_logger = old


def test_grpc_wrapper_method_lookup_is_case_insensitive() -> None:
    from ansys.aedt.core.internal.grpc_plugin_dll_class import AedtObjWrapper

    wrapper = AedtObjWrapper.__new__(AedtObjWrapper)
    wrapper.__dict__["objectID"] = 1
    wrapper.__dict__["__methodNames__"] = ["GetFaceIDs", "CreateBox"]
    wrapper.__dict__["dllapi"] = MagicMock()
    wrapper.__dict__["is_linux"] = False
    with patch.object(AedtObjWrapper, "__Invoke__", return_value=["1"]) as invoke:
        assert wrapper.getfaceids("Box1") == ["1"]
        invoke.assert_called_once_with("GetFaceIDs", ("Box1",))
    assert wrapper.__dict__["__methodMap__"]["createbox"] == "CreateBox"
    with pytest.raises(AttributeError):
        _ = wrapper.NotAMethod


def test_find_object_from_face_id_native_error_returns_none(modeler) -> None:
    modeler.oeditor.GetObjectNameByFaceID.side_effect = Exception("COM error")
    assert modeler._find_object_from_face_id(42) is None
    modeler.oeditor.GetObjectNameByEdgeID.side_effect = Exception("COM error")
    assert modeler._find_object_from_edge_id(42) is None


def test_get_obj_id_stale_cached_id_refreshes(modeler) -> None:
    modeler.refresh_all_ids()
    assert modeler.get_obj_id("Box1") == 10
    # Simulate Box1 recreated outside PyAEDT with a different ID.
    modeler.oeditor.GetObjectIDByName.side_effect = lambda name: 55 if name == "Box1" else 11
    modeler.oeditor.GetAllObjectInfo.side_effect = lambda names: json.dumps(
        [{"Name": n, "id": 55 if n == "Box1" else 11} for n in names]
    )
    modeler.oeditor.GetObjectsInGroup.reset_mock()
    modeler.get_obj_id("Box1")
    # The stale id triggers a refresh instead of being returned from the cache blindly.
    assert modeler.oeditor.GetObjectsInGroup.called


@pytest.mark.parametrize("expression", [".5mm", "-x", "1mm+2mm"])
def test_evaluate_expression_non_numeric_strings_skip_fast_path(expression) -> None:
    design = MagicMock()
    variables = MagicMock()
    variables.__contains__.return_value = False
    design._variable_manager.variables = variables
    try:
        Design.evaluate_expression(design, expression)
    except Exception:  # The mocked AEDT evaluator path is not fully emulated.
        pass
    # The variable lookup is reached, so the numeric fast path did not swallow the expression.
    variables.__contains__.assert_called_with(expression)
