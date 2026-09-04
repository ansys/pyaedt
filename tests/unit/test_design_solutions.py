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


from ansys.aedt.core.application.design_solutions import DesignSolution
from ansys.aedt.core.application.design_solutions import HFSSDesignSolution
from ansys.aedt.core.generic.aedt_constants import HfssConstants
from ansys.aedt.core.generic.aedt_constants import Q3dConstants


class RaisingODesign:
    """Stand-in for a design whose gRPC connection to AEDT has dropped.

    ``GetSolutionType()`` raising mirrors what happens when the connection
    to AEDT is lost: the ``except Exception`` fallback in
    ``design_solutions.py`` is exercised.
    """

    def GetSolutionType(self):
        raise RuntimeError("connection lost")


def test_constants_only_define_solution_default():
    """The constant classes only ever define ``solution_default``."""
    assert hasattr(HfssConstants, "solution_default")
    assert not hasattr(HfssConstants, "default_solution")
    assert hasattr(Q3dConstants, "solution_default")
    assert not hasattr(Q3dConstants, "default_solution")


def test_design_solution_getter_falls_back_on_connection_error():
    """DesignSolution.solution_type getter should not raise on a dropped connection."""
    ds = DesignSolution.__new__(DesignSolution)
    ds._odesign = RaisingODesign()
    ds._design_type = HfssConstants
    ds._solution_type = None

    assert ds.solution_type == HfssConstants.solution_default


def test_design_solution_setter_falls_back_on_connection_error():
    """DesignSolution.solution_type setter (value=None) should not raise on a dropped connection.

    Regression test for the bug where the fallback read
    ``self._design_type.default_solution`` instead of ``solution_default``,
    turning a lost-connection error into a confusing AttributeError.
    """
    ds = DesignSolution.__new__(DesignSolution)
    ds._odesign = RaisingODesign()
    ds._design_type = HfssConstants
    ds._solution_type = None
    ds._solution_options = {
        "Modal": {"name": "HFSS Modal Network", "options": None},
        "Terminal": {"name": "HFSS Terminal Network", "options": None},
    }

    ds.solution_type = None

    assert ds._solution_type == HfssConstants.solution_default


def test_design_solution_setter_no_odesign_falls_back():
    """DesignSolution.solution_type setter with no attached design still falls back correctly."""
    ds = DesignSolution.__new__(DesignSolution)
    ds._odesign = None
    ds._design_type = Q3dConstants
    ds._solution_type = None
    ds._solution_options = {}

    ds.solution_type = None

    assert ds._solution_type == Q3dConstants.solution_default


def test_hfss_design_solution_getter_falls_back_on_connection_error():
    """HFSSDesignSolution.solution_type getter should not raise on a dropped connection."""
    hds = HFSSDesignSolution.__new__(HFSSDesignSolution)
    hds._odesign = RaisingODesign()
    hds._design_type = HfssConstants
    hds._solution_type = None

    assert hds.solution_type == HfssConstants.solution_default
