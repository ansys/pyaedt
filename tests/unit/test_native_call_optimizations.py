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
from ansys.aedt.core.modeler.cad.primitives import GeometryModeler


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
