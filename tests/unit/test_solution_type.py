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

from ansys.aedt.core.application.design_solutions import DesignSolution
from ansys.aedt.core.application.design_solutions import HFSSDesignSolution
from ansys.aedt.core.application.design_solutions import IcepakDesignSolution
from ansys.aedt.core.application.design_solutions import Maxwell2DDesignSolution
from ansys.aedt.core.application.design_solutions import RmXprtDesignSolution
from ansys.aedt.core.generic.aedt_constants import HfssConstants
from ansys.aedt.core.generic.aedt_constants import IcepakConstants
from ansys.aedt.core.generic.aedt_constants import Maxwell2dConstants
from ansys.aedt.core.generic.aedt_constants import Q3dConstants
from ansys.aedt.core.generic.aedt_constants import RmxprtConstants
from ansys.aedt.core.internal.aedt_versions import CURRENT_STABLE_AEDT_VERSION

AEDT_VERSION = str(CURRENT_STABLE_AEDT_VERSION)


def test_base_setter_error():
    """DesignSolution.solution_type setter should not raise on a dropped connection."""
    ds = DesignSolution.__new__(DesignSolution)
    ds._odesign = MagicMock()
    ds._odesign.GetSolutionType.side_effect = RuntimeError("connection lost")
    ds._design_type = HfssConstants
    ds._solution_type = None
    ds._solution_options = {
        "Modal": {"name": "HFSS Modal Network", "options": None},
        "Terminal": {"name": "HFSS Terminal Network", "options": None},
    }

    ds.solution_type = None

    assert ds._solution_type == HfssConstants.solution_default


@pytest.mark.parametrize(
    ("solution_class", "design_type"),
    [(DesignSolution, Q3dConstants), (HFSSDesignSolution, HfssConstants)],
)
def test_getter_error(solution_class, design_type):
    """Solution type getters should use the default after a dropped connection."""
    solution = solution_class.__new__(solution_class)
    solution._odesign = MagicMock()
    solution._odesign.GetSolutionType.side_effect = RuntimeError("connection lost")
    solution._design_type = design_type
    solution._solution_type = None

    assert solution.solution_type == design_type.solution_default


@pytest.mark.parametrize(
    ("solution_class", "design_type", "solution_options"),
    [
        (DesignSolution, Q3dConstants, {}),
        (HFSSDesignSolution, HfssConstants, HfssConstants.solution_types),
    ],
)
def test_setter_without_design(solution_class, design_type, solution_options):
    """Solution type setters should use the default without an attached design."""
    solution = solution_class.__new__(solution_class)
    solution._odesign = None
    solution._design_type = design_type
    solution._solution_type = None
    solution._solution_options = solution_options
    if solution_class is HFSSDesignSolution:
        solution._aedt_version = AEDT_VERSION

    solution.solution_type = None

    assert solution._solution_type == design_type.solution_default


def test_base_getter():
    """DesignSolution.solution_type getter should return the AEDT solution type."""
    odesign = MagicMock()
    odesign.GetSolutionType.return_value = "HFSS Modal Network"
    ds = DesignSolution(odesign, HfssConstants, AEDT_VERSION)

    assert ds.solution_type == "HFSS Modal Network"
    odesign.GetSolutionType.assert_called_once_with()


def test_base_getter_cached():
    """DesignSolution.solution_type getter should preserve a cached value without an AEDT design."""
    ds = DesignSolution(None, HfssConstants, AEDT_VERSION)
    ds._solution_type = "Cached solution"

    assert ds.solution_type == "Cached solution"


@pytest.mark.parametrize("solution_class", [DesignSolution, HFSSDesignSolution])
def test_getter_without_design(solution_class):
    """Solution type getters should use the design default without an AEDT design."""
    solution = solution_class(None, HfssConstants, AEDT_VERSION)

    assert solution.solution_type == HfssConstants.solution_default


def test_base_setter():
    """DesignSolution.solution_type setter should update AEDT for a valid solution."""
    odesign = MagicMock()
    ds = DesignSolution(odesign, HfssConstants, AEDT_VERSION)

    ds.solution_type = "Modal"

    assert ds._solution_type == "Modal"
    odesign.SetSolutionType.assert_called_once_with("HFSS Modal Network")


def test_base_setter_options():
    """DesignSolution.solution_type setter should support options and retry after a failed call."""
    odesign = MagicMock()
    ds = DesignSolution(odesign, HfssConstants, AEDT_VERSION)
    ds._solution_options = {
        "With options": {"name": "With options", "options": ["option"]},
        "Without options": {"name": "Without options", "options": None},
    }

    ds.solution_type = "With options"
    odesign.SetSolutionType.assert_called_once_with("With options", ["option"])

    odesign.reset_mock()
    odesign.SetSolutionType.side_effect = [RuntimeError("connection lost"), None]
    ds.solution_type = "Without options"

    assert odesign.SetSolutionType.call_args_list == [
        (("Without options",), {}),
        (("Without options", ""), {}),
    ]


@pytest.mark.parametrize(
    ("aedt_solution", "expected_solution"),
    [
        ("HFSS Modal Network", "Modal"),
        ("HFSS Terminal Network", "Terminal"),
        ("Custom solution", "Custom solution"),
    ],
)
def test_hfss_getter_normalizes(aedt_solution, expected_solution):
    """HFSSDesignSolution.solution_type getter should normalize modal and terminal values."""
    odesign = MagicMock()
    odesign.GetSolutionType.return_value = aedt_solution
    hds = HFSSDesignSolution(odesign, HfssConstants, AEDT_VERSION)

    assert hds.solution_type == expected_solution


@pytest.mark.parametrize(
    ("value", "expected_solution", "expected_call"),
    [
        ("Modal", "Modal", ("HFSS Modal Network",)),
        ("Terminal", "Terminal", ("HFSS Terminal Network",)),
        ("Transient", "Transient Network", ("Transient Network",)),
        ("Transient Composite", "Transient Composite", ("Transient Composite",)),
    ],
)
def test_hfss_setter_types(value, expected_solution, expected_call):
    """HFSSDesignSolution.solution_type setter should set each solution variant."""
    odesign = MagicMock()
    hds = HFSSDesignSolution(odesign, HfssConstants, AEDT_VERSION)

    hds.solution_type = value

    assert hds._solution_type == expected_solution
    odesign.SetSolutionType.assert_called_once_with(*expected_call)


def test_maxwell2d_getter_setter():
    """Maxwell2DDesignSolution.solution_type should normalize and set plane-specific values."""
    odesign = MagicMock()
    odesign.GetSolutionType.return_value = "EddyCurrent"
    mds = Maxwell2DDesignSolution(odesign, Maxwell2dConstants, AEDT_VERSION)

    assert mds.solution_type == "EddyCurrent"

    mds.solution_type = "EddyCurrentZ"

    assert mds._solution_type == "EddyCurrent"
    assert mds._geometry_mode == "about Z"
    odesign.SetSolutionType.assert_called_once_with("EddyCurrent", "about Z")


def test_maxwell2d_getter_error():
    """Maxwell2DDesignSolution.solution_type getter should use the default after a failed call."""
    odesign = MagicMock()
    odesign.GetSolutionType.side_effect = RuntimeError("connection lost")
    mds = Maxwell2DDesignSolution(odesign, Maxwell2dConstants, AEDT_VERSION)

    assert mds.solution_type == Maxwell2dConstants.solution_default


def test_maxwell2d_setter_normalizes():
    """Maxwell2DDesignSolution.solution_type setter should normalize XY and modal values."""
    odesign = MagicMock()
    odesign.GetSolutionType.return_value = "Modal"
    mds = Maxwell2DDesignSolution(odesign, Maxwell2dConstants, AEDT_VERSION)

    mds.solution_type = None
    assert mds._solution_type == "Modal"

    mds.solution_type = "EddyCurrentXY"

    assert mds._solution_type == "EddyCurrent"
    assert mds._geometry_mode == "XY"
    assert odesign.SetSolutionType.call_args_list[-1] == (("EddyCurrent", "XY"), {})


def test_icepak_getter_setter():
    """IcepakDesignSolution.solution_type should read and set steady-state solutions."""
    odesign = MagicMock()
    odesign.GetSolutionType.return_value = "SteadyState"
    ids = IcepakDesignSolution(odesign, IcepakConstants, AEDT_VERSION)

    assert ids.solution_type == "SteadyState"

    ids.solution_type = "SteadyStateTemperatureOnly"

    assert ids._solution_type == "SteadyState"
    assert ids._problem_type == "TemperatureOnly"
    odesign.SetSolutionType.assert_called_once_with(
        [
            "NAME:SolutionTypeOption",
            "SolutionTypeOption:=",
            "SteadyState",
            "ProblemOption:=",
            "TemperatureOnly",
        ]
    )


def test_icepak_getter_error():
    """IcepakDesignSolution.solution_type getter should use the default after a failed call."""
    odesign = MagicMock()
    odesign.GetSolutionType.side_effect = RuntimeError("connection lost")
    ids = IcepakDesignSolution(odesign, IcepakConstants, AEDT_VERSION)

    assert ids.solution_type == IcepakConstants.solution_default


def test_rmxprt_getter_setter():
    """RmXprtDesignSolution.solution_type should read and set the machine type."""
    odesign = MagicMock()
    odesign.GetMachineType.return_value = "GRM"
    rds = RmXprtDesignSolution(odesign, RmxprtConstants, AEDT_VERSION)

    assert rds.solution_type == "GRM"

    rds.solution_type = "IRIM"

    assert rds._solution_type == "IRIM"
    odesign.SetDesignFlow.assert_called_once_with(RmxprtConstants.NAME, "IRIM")


def test_rmxprt_getter_without_machine_type():
    """RmXprtDesignSolution.solution_type getter should remain unset without AEDT support."""
    odesign = MagicMock(spec=[])
    rds = RmXprtDesignSolution(odesign, RmxprtConstants, AEDT_VERSION)

    assert rds.solution_type is None


def test_rmxprt_setter_error():
    """RmXprtDesignSolution.solution_type setter should ignore empty values and log failed calls."""
    odesign = MagicMock()
    odesign.SetDesignFlow.side_effect = RuntimeError("connection lost")
    rds = RmXprtDesignSolution(odesign, RmxprtConstants, AEDT_VERSION)

    rds.solution_type = ""
    rds.solution_type = "IRIM"

    assert rds._solution_type is None
    odesign.SetDesignFlow.assert_called_once_with(RmxprtConstants.NAME, "IRIM")
