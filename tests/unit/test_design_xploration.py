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
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.generic.general_methods import SetupDict
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modules.design_xploration import Optimizations
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


def test_create_without_get_obj_data_registers_setup_in_parent() -> None:
    parent = MagicMock()
    parent.setups = {}
    setup = ParametricSetup.__new__(ParametricSetup)
    setup._parent = parent
    setup._app = parent._app
    setup._name = "Parametric1"
    setup._legacy_props = {"Sim. Setups": ["Setup1"]}
    setup._has_getobject = False
    setup._OptimetricsSetup__setup_type = "OptiParametric"

    with (
        patch.object(ParametricSetup, "_child_object", new_callable=PropertyMock, return_value=None),
        patch("ansys.aedt.core.modules.design_xploration._has_get_obj_data", return_value=False),
    ):
        assert setup.create() is setup

    parent._app.ooptimetrics.InsertSetup.assert_called_once()
    assert parent.setups["Parametric1"] is setup


def test_optimizations_add_unsupported_type(mock_app) -> None:
    optimizations = _manager(Optimizations, mock_app)
    with pytest.raises(ValueError, match="Unsupported optimization type"):
        optimizations.add(optimization_type="Invented")


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
