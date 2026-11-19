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

from types import SimpleNamespace
from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.application.aedt_objects import AedtObjects
from ansys.aedt.core.generic.general_methods import SetupDict
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modeler.cad.elements_3d import BinaryTreeNode
from ansys.aedt.core.modules.design_xploration import OptimetricsSetup
from ansys.aedt.core.modules.design_xploration import Optimizations
from ansys.aedt.core.modules.design_xploration import OptimizationSetup
from ansys.aedt.core.modules.design_xploration import Parametrics
from ansys.aedt.core.modules.design_xploration import ParametricSetup


@pytest.fixture
def mock_app():
    app = MagicMock()
    app.nominal_sweep = "Setup1 : LastAdaptive"
    app.variable_manager.variables = {"w1": MagicMock()}
    return app


def _manager(cls, app, existing=None):
    """Build a Parametrics or Optimizations manager without AEDT."""
    obj = cls.__new__(cls)
    obj._app = app
    obj.logger = MagicMock()
    obj.optimetrics = MagicMock()
    obj.optimetrics._get_setup_types.return_value = existing or {}
    prefix = f"_{cls.__name__}"
    setattr(obj, f"{prefix}__setups", SetupDict())
    setattr(obj, f"{prefix}__setup_names", [])
    setattr(obj, f"{prefix}__setups_by_type", SetupDict())
    return obj


def test_optimizations_getitem_returns_optimization_setup() -> None:
    optimizations = Optimizations.__new__(Optimizations)
    optimizations._Optimizations__setups = SetupDict()

    with (
        patch.object(Optimizations, "setup_names", new_callable=PropertyMock, return_value=["Opt1"]),
        patch("ansys.aedt.core.modules.design_xploration.OptimizationSetup") as mock_opt,
        patch("ansys.aedt.core.modules.design_xploration.ParametricSetup") as mock_par,
    ):
        setup = optimizations["Opt1"]

    mock_opt.assert_called_once_with(app=optimizations, name="Opt1", props={})
    mock_par.assert_not_called()
    assert setup is mock_opt.return_value


@pytest.mark.parametrize(
    "manager_type, setup_class, setup_type",
    [(Parametrics, ParametricSetup, "OptiParametric"), (Optimizations, OptimizationSetup, "OptiOptimization")],
)
def test_create_without_get_obj_data_registers_setup_in_parent(mock_app, manager_type, setup_class, setup_type) -> None:
    parent = _manager(manager_type, mock_app)
    setup = setup_class.__new__(setup_class)
    setup._parent = parent
    setup._app = parent._app
    setup._name = "Parametric1"
    setup._legacy_props = {"Sim. Setups": ["Setup1"]}
    setup._has_getobject = False
    setup._OptimetricsSetup__setup_type = setup_type

    with (
        patch.object(setup_class, "_child_object", new_callable=PropertyMock, return_value=None),
        patch("ansys.aedt.core.modules.design_xploration._has_get_obj_data", return_value=False),
        patch.object(manager_type, "setup_names", new_callable=PropertyMock, return_value=["Parametric1"]),
    ):
        assert setup.create() is setup
        assert parent.setups["Parametric1"] is setup

    parent._app.ooptimetrics.InsertSetup.assert_called_once()


@pytest.mark.parametrize("manager_type", [Parametrics, Optimizations])
def test_setup_registry_lifecycle_does_not_refresh_aedt(mock_app, manager_type):
    parent = _manager(manager_type, mock_app)
    setup = MagicMock()
    setup.name = "Original"
    cache = vars(parent)[f"_{manager_type.__name__}__setups"]

    with patch.object(manager_type, "setup_names", new_callable=PropertyMock) as setup_names:
        parent._register_setup(setup)
        assert cache["Original"] is setup
        parent._rename_setup("Original", "Renamed", setup)
        assert "Original" not in cache
        assert cache["Renamed"] is setup
        parent._unregister_setup("Renamed")
        parent._unregister_setup("Missing")
        assert not cache
        setup_names.assert_not_called()
    parent.optimetrics._get_setup_types.assert_not_called()


@pytest.mark.parametrize(
    "manager_type, setup_class", [(Parametrics, ParametricSetup), (Optimizations, OptimizationSetup)]
)
def test_setup_rename_and_delete_update_parent_cache(mock_app, manager_type, setup_class):
    parent = _manager(manager_type, mock_app)
    mock_app.optimetrics.setup_names = []
    setup = setup_class.__new__(setup_class)
    setup._parent = parent
    setup._app = mock_app
    setup._name = "Original"
    cache = vars(parent)[f"_{manager_type.__name__}__setups"]
    handle = MagicMock()

    with (
        patch.object(setup_class, "_child_object", new_callable=PropertyMock, return_value=None),
        patch.object(setup_class, "child_object", new_callable=PropertyMock, return_value=handle),
    ):
        parent._register_setup(setup)
        setup.name = "Renamed"
        handle.Rename.assert_called_once_with("Renamed")
        assert "Original" not in cache
        assert cache["Renamed"] is setup
        assert setup.delete()
        assert not cache
        mock_app.ooptimetrics.DeleteSetups.assert_called_once_with(["Renamed"])


def test_optimizations_add_unsupported_type(mock_app) -> None:
    optimizations = _manager(Optimizations, mock_app)
    with pytest.raises(ValueError, match="Unsupported optimization type"):
        optimizations.add(optimization_type="Invented")


@pytest.mark.parametrize(
    "field_names, expected_report_type",
    [(None, "Standard"), (["Sphere1"], "Far Fields"), (["Sphere2"], "Standard")],
)
def test_optimizations_add_field_setup_context(mock_app, field_names, expected_report_type):
    optimizations = _manager(Optimizations, mock_app)
    mock_app.design_solutions.report_type = "Standard"
    mock_app.modeler.sheet_names = []
    mock_app.solution_type = "DrivenModal"
    if field_names is None:
        del mock_app.field_setups
    else:
        mock_app.field_setups = [SimpleNamespace(name=name) for name in field_names]

    with patch("ansys.aedt.core.modules.design_xploration.OptimizationSetup") as setup_class:
        setup = setup_class.return_value
        setup._legacy_props = {"Goals": {}}
        optimizations.add(name="Opt1", calculation="Gain", context="Sphere1")

    assert setup._get_context.call_args.args[7] == expected_report_type
    mock_app.logger.debug.assert_not_called()


@pytest.mark.parametrize(
    "modeler, solution_type, expected_report_type",
    [
        (None, "DrivenModal", "Standard"),
        (SimpleNamespace(), "DrivenModal", "Standard"),
        (SimpleNamespace(sheet_names=["Sheet1"]), "DrivenModal", "Fields"),
        (SimpleNamespace(), "Q3D Extractor", "Matrix"),
    ],
)
def test_optimizations_add_sheet_context(mock_app, modeler, solution_type, expected_report_type):
    optimizations = _manager(Optimizations, mock_app)
    mock_app.design_solutions.report_type = "Standard"
    mock_app.modeler = modeler
    mock_app.solution_type = solution_type
    del mock_app.field_setups

    with patch("ansys.aedt.core.modules.design_xploration.OptimizationSetup") as setup_class:
        setup = setup_class.return_value
        setup._legacy_props = {"Goals": {}}
        optimizations.add(name="Opt1", calculation="Gain", context="Sheet1")

    assert setup._get_context.call_args.args[7] == expected_report_type


@pytest.mark.parametrize(
    "modeler, expected_report_type",
    [(None, "Standard"), (SimpleNamespace(), "Standard"), (SimpleNamespace(sheet_names=["Sheet1"]), "Fields")],
)
def test_add_calculation_sheet_context(mock_app, modeler, expected_report_type):
    mock_app.design_solutions.report_type = "Standard"
    mock_app.modeler = modeler
    mock_app.solution_type = "DrivenModal"
    setup = OptimetricsSetup.__new__(OptimetricsSetup)
    setup._app = mock_app
    props = MagicMock()
    props.to_dict.return_value = {"Goals": {}}

    with (
        patch.object(OptimetricsSetup, "props", new_callable=PropertyMock, return_value=props),
        patch.object(OptimetricsSetup, "setup_type", new_callable=PropertyMock, return_value="OptiOptimization"),
        patch.object(OptimetricsSetup, "_get_domain"),
        patch.object(OptimetricsSetup, "_get_context") as get_context,
        patch.object(OptimetricsSetup, "update", return_value=True),
    ):
        assert setup.add_calculation(calculation="Gain", context="Sheet1")

    assert get_context.call_args.args[7] == expected_report_type


@pytest.mark.parametrize(
    "modeler, expected_context",
    [
        (None, {"Context": "Line1"}),
        (SimpleNamespace(), {"Context": "Line1"}),
        (SimpleNamespace(line_names=["Line1"]), {"Context": "Line1", "PointCount": 17}),
    ],
)
def test_get_context_handles_optional_line_names(mock_app, modeler, expected_context):
    mock_app.modeler = modeler
    mock_app.solution_type = "DrivenModal"
    mock_app.existing_analysis_sweeps = [mock_app.nominal_sweep]
    setup = OptimetricsSetup.__new__(OptimetricsSetup)
    setup._app = mock_app

    result = setup._get_context("Gain", "<=", 1, 1, context="Line1", polyline_points=17)

    assert result["SimValueContext"] == expected_context


def test_parametric_variation_requires_end_point(mock_app):
    setup = ParametricSetup.__new__(ParametricSetup)
    setup._app = mock_app
    with pytest.raises(ValueError, match="end point is required"):
        setup.add_variation("w1", 1)


def test_parametric_single_value_does_not_require_end_point(mock_app):
    mock_app.variable_manager.__getitem__.return_value.units = "mm"
    mock_app.value_with_units.return_value = "1mm"
    setup = ParametricSetup.__new__(ParametricSetup)
    setup._app = mock_app
    props = MagicMock()
    props.to_dict.return_value = {"Sweeps": {}}
    with (
        patch.object(ParametricSetup, "props", new_callable=PropertyMock, return_value=props),
        patch.object(ParametricSetup, "_activate_variable"),
        patch.object(ParametricSetup, "update", return_value=True) as update,
    ):
        assert setup.add_variation("w1", 1, variation_type="SingleValue")

    assert update.call_args.args[0]["Sweeps"]["SweepDefinition"]["Data"] == "1mm"


@pytest.mark.parametrize("setup_type", ["OptiOptimization", "OptiDXDOE", "OptiSensitivity", "OptiStatistical"])
def test_optimization_variation_preserves_formatted_values(mock_app, setup_type):
    variable = mock_app.variable_manager.variables["w1"]
    variable.units = "mm"
    variable.numeric_value = 5
    mock_app.variable_manager.__getitem__.return_value = variable
    mock_app.desktop_class.aedt_version_id = "2024.1"
    mock_app.value_with_units.side_effect = lambda value, units: value if isinstance(value, str) else f"{value}{units}"
    setup = OptimizationSetup.__new__(OptimizationSetup)
    setup._app = mock_app
    props = MagicMock()
    props.to_dict.return_value = {"Variables": {}, "StartingPoint": {}}
    with (
        patch.object(OptimizationSetup, "props", new_callable=PropertyMock, return_value=props),
        patch.object(OptimizationSetup, "setup_type", new_callable=PropertyMock, return_value=setup_type),
        patch.object(OptimizationSetup, "_activate_variable"),
        patch.object(OptimizationSetup, "update", return_value=True) as update,
    ):
        assert setup.add_variation("w1", 0, 10)

    result = update.call_args.args[0]
    assert result["StartingPoint"]["w1"] == "5mm"
    values = result["Variables"]["w1"]
    if setup_type == "OptiOptimization":
        assert values[values.index("MinStep:=") + 1] == "0.1mm"
        assert values[values.index("MaxStep:=") + 1] == "1.0mm"
    if setup_type == "OptiSensitivity":
        assert values[values.index("IDisp:=") + 1] == "5mm"


def test_optimization_variation_requires_aedt_version(mock_app):
    variable = mock_app.variable_manager.variables["w1"]
    variable.units = "mm"
    mock_app.variable_manager.__getitem__.return_value = variable
    mock_app.desktop_class.aedt_version_id = None
    setup = OptimizationSetup.__new__(OptimizationSetup)
    setup._app = mock_app
    props = MagicMock()
    props.to_dict.return_value = {"Variables": {}, "StartingPoint": {}}
    with (
        patch.object(OptimizationSetup, "props", new_callable=PropertyMock, return_value=props),
        patch.object(OptimizationSetup, "setup_type", new_callable=PropertyMock, return_value="OptiOptimization"),
        patch.object(OptimizationSetup, "_activate_variable"),
        pytest.raises(AEDTRuntimeError, match="AEDT version is unavailable"),
    ):
        setup.add_variation("w1", 0, 10)


def test_missing_optimetrics_module_is_reported(mock_app):
    mock_app.ooptimetrics = None
    setup = OptimetricsSetup.__new__(OptimetricsSetup)
    setup._app = mock_app
    with pytest.raises(AEDTRuntimeError, match="Optimetrics module is not available"):
        setup._optimetrics_module


@pytest.mark.parametrize("design_type, available", [("HFSS", True), ("Maxwell Circuit", False)])
def test_aedt_objects_optimetrics_module(design_type, available):
    app = AedtObjects.__new__(AedtObjects)
    app._ooptimetrics = None
    module = MagicMock()
    with (
        patch.object(AedtObjects, "design_type", new_callable=PropertyMock, return_value=design_type),
        patch.object(AedtObjects, "get_module", return_value=module) as get_module,
    ):
        assert app.ooptimetrics is (module if available else None)
        assert app.ooptimetrics is (module if available else None)

    if available:
        get_module.assert_called_once_with("Optimetrics")
    else:
        get_module.assert_not_called()


def test_optimetrics_child_lookup_does_not_reuse_deleted_handle(mock_app):
    setup = OptimetricsSetup.__new__(OptimetricsSetup)
    setup._app = mock_app
    setup._name = "Opt1"
    folder = MagicMock()
    handle = MagicMock()
    mock_app.get_oo_object.side_effect = lambda parent, name: folder if name == "Optimetrics" else handle
    mock_app.get_oo_name.side_effect = [["Optimetrics"], ["Opt1"], ["Optimetrics"], []]

    assert setup._child_object is handle
    assert setup._child_object is None
    assert repr(setup) == "Opt1"
    assert str(setup) == "Opt1"
    handle.GetPropValue.assert_not_called()


def test_delete_clears_optimetrics_tree_and_parent_cache(mock_app):
    parent = MagicMock()
    setup = OptimetricsSetup.__new__(OptimetricsSetup)
    setup._parent = parent
    setup._name = "Opt1"
    BinaryTreeNode.__init__(setup, "Opt1", MagicMock(), app=mock_app)
    setup._children = {"Goal": MagicMock()}
    setup._props = MagicMock()
    setup._legacy_props = {"IsEnabled": True}
    parent.setups = {"Opt1": setup}
    mock_app.get_oo_name.return_value = []

    assert setup.delete()

    mock_app.ooptimetrics.DeleteSetups.assert_called_once_with(["Opt1"])
    assert setup._BinaryTreeNode__child_object is None
    assert setup._props is None
    assert setup._legacy_props == {}
    assert parent.setups == {}
    assert setup.child_object is None
    assert setup.children == {}
    assert setup.name == "Opt1"


def test_optimizations_add_duplicate_name(mock_app) -> None:
    optimizations = _manager(Optimizations, mock_app, {"Opt1": "OptiOptimization"})
    with pytest.raises(AEDTRuntimeError, match="Name Opt1 already exists"):
        optimizations.add(name="Opt1")


def test_optimizations_add_without_setup(mock_app) -> None:
    mock_app.nominal_sweep = None
    optimizations = _manager(Optimizations, mock_app)
    with pytest.raises(AEDTRuntimeError, match="At least one setup is needed"):
        optimizations.add()


def test_parametrics_add_without_setup(mock_app) -> None:
    mock_app.nominal_sweep = None
    parametrics = _manager(Parametrics, mock_app)
    with pytest.raises(AEDTRuntimeError, match="At least one setup is needed"):
        parametrics.add("w1", 0, 1)


def test_parametrics_add_invalid_variation_type_creates_nothing(mock_app) -> None:
    parametrics = _manager(Parametrics, mock_app)
    with patch("ansys.aedt.core.modules.design_xploration.ParametricSetup") as mock_setup:
        with pytest.raises(AEDTRuntimeError, match="Unsupported variation type Invented"):
            parametrics.add("w1", 0, 1, variation_type="Invented")
    mock_setup.assert_not_called()
