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

"""Unit tests checking that common operations avoid redundant native API calls."""

from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.application.design import Design
from ansys.aedt.core.application.variables import VariableManager
from ansys.aedt.core.modeler.cad.elements_3d import FacePrimitive
from ansys.aedt.core.modeler.cad.object_3d import Object3d
from ansys.aedt.core.modeler.cad.primitives import GeometryModeler
from ansys.aedt.core.modules.boundary.common import BoundaryObject


@pytest.fixture
def modeler():
    with patch.object(GeometryModeler, "__init__", lambda self: None):
        mdl = GeometryModeler()
    mdl._app = MagicMock()
    mdl._solids = []
    mdl._sheets = []
    mdl._lines = []
    mdl._points = []
    mdl._unclassified = []
    mdl._planes = {}
    mdl._all_object_names = []
    oeditor = MagicMock()
    oeditor.GetObjectsInGroup.side_effect = lambda group: {
        "Solids": ["box1", "box2"],
        "Sheets": ["rect1"],
        "Lines": [],
        "Unclassified": ["bad1"],
    }[group]
    oeditor.GetPoints.return_value = ["pt1"]
    oeditor.GetChildNames.return_value = ["plane1"]
    with patch.object(GeometryModeler, "oeditor", new_callable=PropertyMock, return_value=oeditor):
        yield mdl, oeditor


def test_object_list_queries_points_once(modeler) -> None:
    mdl, oeditor = modeler
    objects = {name: MagicMock(_m_name=name) for name in ["box1", "box2", "rect1", "pt1"]}
    with patch.object(GeometryModeler, "objects_by_name", new_callable=PropertyMock, return_value=objects):
        result = mdl.object_list

    assert [o._m_name for o in result] == ["box1", "box2", "rect1"]
    assert oeditor.GetPoints.call_count == 1


def test_refresh_planes_reuses_cached_handles(modeler) -> None:
    mdl, oeditor = modeler
    mdl._app.get_oo_object.side_effect = lambda editor, name: f"handle_{name}"

    mdl._refresh_planes()
    mdl._refresh_planes()
    assert mdl._planes == {"plane1": "handle_plane1"}
    assert mdl._app.get_oo_object.call_count == 1

    # Deleted planes are dropped and new planes are fetched.
    oeditor.GetChildNames.return_value = ["plane2"]
    mdl._refresh_planes()
    assert mdl._planes == {"plane2": "handle_plane2"}
    assert mdl._app.get_oo_object.call_count == 2


def test_face_center_single_call_on_first_access() -> None:
    obj = MagicMock()
    face = FacePrimitive(obj, 7)
    obj._oeditor.GetFaceCenter.return_value = ["1", "2", "3"]

    assert face.center == [1.0, 2.0, 3.0]
    assert obj._oeditor.GetFaceCenter.call_count == 1
    assert face.is_planar is True
    assert obj._oeditor.GetFaceCenter.call_count == 1


def test_face_normal_queries_bounding_box_once() -> None:
    obj = MagicMock()
    bounding_box = PropertyMock(return_value=[0.0, 0.0, 0.0, 2.0, 2.0, 2.0])
    type(obj).bounding_box = bounding_box
    face = FacePrimitive(obj, 1)
    v1 = MagicMock(position=[0.0, 0.0, 0.0])
    v2 = MagicMock(position=[2.0, 0.0, 0.0])
    with (
        patch.object(FacePrimitive, "vertices", new_callable=PropertyMock, return_value=[v1, v2]),
        patch.object(FacePrimitive, "center", new_callable=PropertyMock, return_value=[1.0, 1.0, 0.0]) as center,
    ):
        normal = face.normal

    # Bottom face of the box: the normal points away from the bounding box center.
    assert [abs(i) if i == 0 else i for i in normal] == [0.0, 0.0, -1.0]
    assert bounding_box.call_count == 1
    assert center.call_count == 1


def test_object3d_faces_calls_get_face_ids_once() -> None:
    with patch.object(Object3d, "__init__", lambda self: None):
        obj = Object3d()
    obj._object_type = "Solid"
    obj._m_name = "box1"
    obj._face_ids = []
    obj._faces = []
    oeditor = MagicMock()
    oeditor.GetFaceIDs.return_value = ["1", "2"]
    obj._primitives = MagicMock(oeditor=oeditor)

    faces = obj.faces

    assert [f.id for f in faces] == [1, 2]
    assert oeditor.GetFaceIDs.call_count == 1


def test_variable_dict_fetches_variable_lists_once() -> None:
    app = MagicMock()
    manager = VariableManager(app)
    with patch.object(VariableManager, "_get_var_list_from_aedt", return_value=[]) as get_list:
        manager._variable_dict([app.odesign, app.oproject])

    # One call per AEDT object, shared by the update and cleanup steps.
    assert get_list.call_count == 2


def test_cleanup_variables_uses_provided_list() -> None:
    app = MagicMock()
    manager = VariableManager(app)
    manager._VariableManager__independent_design_variables = {"keep": 1, "drop": 2}
    with patch.object(VariableManager, "_get_var_list_from_aedt") as get_list:
        manager._cleanup_variables(["keep"])

    get_list.assert_not_called()
    assert manager._VariableManager__independent_design_variables == {"keep": 1}


@pytest.mark.parametrize(
    ("expression", "expected"), [(5, 5.0), (2.5, 2.5), ("1e3", 1000.0), ("-4", -4.0), (" 5", 5.0), ("+.5", 0.5)]
)
def test_evaluate_expression_numeric_skips_variable_lookup(expression, expected) -> None:
    with patch.object(Design, "__init__", lambda self: None):
        design = Design()
    design._variable_manager = MagicMock()
    type(design._variable_manager).variables = PropertyMock(side_effect=AssertionError("unexpected lookup"))

    assert design.evaluate_expression(expression) == expected


def test_evaluate_expression_variable_lookup_once() -> None:
    with patch.object(Design, "__init__", lambda self: None):
        design = Design()
    design._variable_manager = MagicMock()
    variables = PropertyMock(return_value={"width": MagicMock(si_value=0.01)})
    type(design._variable_manager).variables = variables

    assert design.evaluate_expression("width") == 0.01
    assert variables.call_count == 1


def test_boundary_initialize_tree_node_evaluates_child_object_once() -> None:
    with patch.object(BoundaryObject, "__init__", lambda self: None):
        boundary = BoundaryObject()
    boundary._name = "Current1"
    boundary._app = MagicMock()
    child = PropertyMock(return_value=MagicMock())
    with patch.object(BoundaryObject, "_child_object", new_callable=lambda: child):
        assert boundary._initialize_tree_node() is True

    assert child.call_count == 1


@pytest.mark.parametrize(("expression", "expected"), [(True, 1.0), ("inf", float("inf"))])
def test_evaluate_expression_non_fast_path_still_looks_up_variables(expression, expected) -> None:
    with patch.object(Design, "__init__", lambda self: None):
        design = Design()
    design._variable_manager = MagicMock()
    variables = PropertyMock(return_value={})
    type(design._variable_manager).variables = variables

    assert design.evaluate_expression(expression) == expected
    assert variables.call_count == 1


def test_evaluate_expression_units_fall_through_to_evaluator() -> None:
    with patch.object(Design, "__init__", lambda self: None):
        design = Design()
    manager = MagicMock()
    manager.set_variable.return_value = True
    variables = PropertyMock(side_effect=[{}, {"pyaedt_evaluator": MagicMock(si_value=1.0)}])
    type(manager).variables = variables
    design._variable_manager = manager

    assert design.evaluate_expression("1e3mm") == 1.0
    manager.set_variable.assert_called_once()


def test_face_center_non_planar_falls_back_to_centroid() -> None:
    obj = MagicMock()
    obj._oeditor.GetFaceCenter.side_effect = Exception("non planar")
    face = FacePrimitive(obj, 3)
    vertices = [MagicMock(position=[0.0, 0.0, 0.0]), MagicMock(position=[2.0, 2.0, 0.0])]
    with patch.object(FacePrimitive, "vertices", new_callable=PropertyMock, return_value=vertices):
        assert face.center == [1.0, 1.0, 0.0]

    assert face._is_planar is False
    obj.logger.clear_messages.assert_called_once()
    assert obj._oeditor.GetFaceCenter.call_count == 1


@pytest.mark.parametrize("cached", [False, None, "plane_object"])
def test_refresh_planes_refetches_invalid_cached_handles(modeler, cached) -> None:
    mdl, _ = modeler
    from ansys.aedt.core.modeler.cad.elements_3d import Plane

    mdl._planes = {"plane1": MagicMock(spec=Plane) if cached == "plane_object" else cached}
    mdl._app.get_oo_object.return_value = "handle"

    mdl._refresh_planes()

    assert mdl._planes == {"plane1": "handle"}
    mdl._app.get_oo_object.assert_called_once()


def test_add_message_skips_desktop_when_desktop_logs_disabled() -> None:
    from ansys.aedt.core.aedt_logger import AedtLogger
    from ansys.aedt.core.generic.settings import settings

    logger = AedtLogger()
    desktop = PropertyMock(side_effect=AssertionError("desktop must not be queried"))
    original = settings.enable_desktop_logs
    settings.enable_desktop_logs = False
    try:
        with patch.object(AedtLogger, "_desktop", new_callable=lambda: desktop):
            logger.add_message(0, "message")
    finally:
        settings.enable_desktop_logs = original

    desktop.assert_not_called()


# Round 2 optimizations


def test_read_amat_material_names_matches_line_parser_and_caches(tmp_path) -> None:
    from ansys.aedt.core.modules import material_lib

    amat = tmp_path / "lib.amat"
    amat.write_bytes(
        b"$begin 'a'\r\n  $begin 'nested'\r$begin 'b'\n\xff$begin 'bad'\n$begin '\xff'\n$begin 'c\xc3\xa9'\n$end 'a'\n"
    )
    material_lib._AMAT_NAMES_CACHE.clear()

    assert material_lib._read_amat_material_names(amat) == ("a", "b", "c\u00e9")
    with patch("ansys.aedt.core.modules.material_lib.open_file") as open_file:
        assert material_lib._read_amat_material_names(str(amat)) == ("a", "b", "c\u00e9")
    open_file.assert_not_called()

    # Cache is invalidated when the file changes.
    amat.write_bytes(b"$begin 'z'\n$begin 'zz'\n")
    assert material_lib._read_amat_material_names(amat) == ("z", "zz")


def test_materials_hash_lookup_preserves_first_match() -> None:
    from ansys.aedt.core.modules.material_lib import Materials

    with patch.object(Materials, "__init__", lambda self: None):
        mats = Materials()
    mats._mats = ["Copper", "copper", "FR4"]
    mats._mats_lower = []
    mats._mats_lower_index = {}
    mats._Materials__material_keys = {}

    assert mats._is_aedt_material_name("copper")
    assert not mats._is_aedt_material_name("gold")
    assert mats._get_aedt_case_name("COPPER") == "Copper"
    # New materials appended later are indexed too.
    mats._mats.append("Gold")
    assert mats._get_aedt_case_name("gold") == "Gold"


def test_find_object_from_face_id_uses_single_native_call(modeler) -> None:
    mdl, oeditor = modeler
    oeditor.GetObjectNameByFaceID.return_value = "box1"

    assert mdl._find_object_from_face_id(42) == "box1"
    oeditor.GetFaceIDs.assert_not_called()


def test_find_object_from_face_id_falls_back_to_scan(modeler) -> None:
    mdl, oeditor = modeler
    oeditor.GetObjectNameByFaceID.side_effect = AttributeError("not supported")
    oeditor.GetFaceIDs.side_effect = lambda name: ["7"] if name == "box2" else ["1"]

    assert mdl._find_object_from_face_id(7) == "box2"


def test_create_object_solid_skips_lines_query(modeler) -> None:
    mdl, oeditor = modeler
    mdl.objects = MagicMock()
    mdl.points = {}
    with patch.object(GeometryModeler, "planes", new_callable=PropertyMock, return_value={}):
        mdl._create_object("box1", pid=5, _is_solid=True)
        oeditor.GetObjectsInGroup.assert_not_called()
        mdl._create_object("box1", pid=5)
    oeditor.GetObjectsInGroup.assert_called_once_with("Lines")


def test_find_object_from_face_id_non_face_id_returns_none(modeler) -> None:
    mdl, oeditor = modeler
    oeditor.GetObjectNameByFaceID.return_value = ""

    assert mdl._find_object_from_face_id(16) is None
    oeditor.GetFaceIDs.assert_not_called()


def test_read_amat_material_names_without_stat_does_not_cache(tmp_path) -> None:
    from ansys.aedt.core.modules import material_lib

    amat = tmp_path / "lib.amat"
    amat.write_bytes(b"$begin 'a'\n")
    material_lib._AMAT_NAMES_CACHE.clear()
    broken_path = MagicMock()
    broken_path.return_value.stat.side_effect = OSError("no stat")
    with patch("ansys.aedt.core.modules.material_lib.Path", broken_path):
        assert material_lib._read_amat_material_names(amat) == ("a",)
        amat.write_bytes(b"$begin 'b'\n")
        assert material_lib._read_amat_material_names(amat) == ("b",)
    assert material_lib._AMAT_NAMES_CACHE == {}
