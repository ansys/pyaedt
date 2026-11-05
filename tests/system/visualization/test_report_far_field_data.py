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

import numpy as np
import pytest

PATCH_PROJECT = "get_sol_data_test_v1"
PATCH_DESIGN = "HFSSDesign_1patch"
RCS_PROJECT = "Rectangular_GP_IE_v1"
RCS_DESIGN = "RecGP"
TEST_SUBFOLDER = "T10"


@pytest.fixture
def patch_app(add_app_example):
    app = add_app_example(project=PATCH_PROJECT, design=PATCH_DESIGN, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def rcs_app(add_app_example):
    app = add_app_example(project=RCS_PROJECT, design=RCS_DESIGN, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


def _get_plot(app, name):
    return next(plot for plot in app.post.plots if plot.plot_name == name)


def _explicit_data(app, plot, variations, primary_sweep):
    """Far field data of ``plot`` obtained by defining all the variations explicitly (no existing report)."""
    return app.post.get_solution_data(
        expressions=plot.expressions,
        setup_sweep_name=plot.setup,
        domain=plot.domain,
        variations=variations,
        primary_sweep_variable=primary_sweep,
        report_category=plot.report_category,
        context=plot._context[1],
    )


def test_ff_variations(patch_app) -> None:
    plot = _get_plot(patch_app, "Realized Gain Plot1")
    assert plot.variations["Phi"] != ["All"]
    assert plot.variations["Theta"] != ["All"]
    assert plot.variations["Freq"] == ["All"]


def test_ff_matches_explicit(patch_app) -> None:
    plot = _get_plot(patch_app, "Realized Gain Plot1")
    expression = plot.expressions[0]
    x, y = plot.get_solution_data().get_expression_data(expression, formula="real")

    variations = {"Phi": ["0deg"], "Theta": ["0deg"], "Freq": ["All"]}
    reference = _explicit_data(patch_app, plot, variations, "Freq")
    x_ref, y_ref = reference.get_expression_data(expression, formula="real")
    np.testing.assert_allclose(x, x_ref)
    np.testing.assert_allclose(y, y_ref)


def test_rcs_matches_explicit(rcs_app) -> None:
    plot = _get_plot(rcs_app, "Bistatic RCS Plot1")
    expression = plot.expressions[0]
    x, y = plot.get_solution_data().get_expression_data(expression, formula="real")

    variations = {
        "Freq": ["10GHz"],
        "IWavePhi": ["180deg"],
        "IWaveTheta": ["120deg"],
        "Phi": ["0deg"],
        "Theta": ["All"],
    }
    reference = _explicit_data(rcs_app, plot, variations, "Theta")
    x_ref, y_ref = reference.get_expression_data(expression, formula="real")
    np.testing.assert_allclose(x, x_ref)
    np.testing.assert_allclose(y, y_ref)


def test_all_curves_single(patch_app) -> None:
    plot = _get_plot(patch_app, "Realized Gain Plot1")
    curves = plot.get_expression_data_all_curves(formula="real")
    assert len(curves) == 1
    x, y = plot.get_solution_data().get_expression_data(plot.expressions[0], formula="real")
    np.testing.assert_allclose(curves[0]["x"], x)
    np.testing.assert_allclose(curves[0]["y"], y)


def test_all_curves_multiple(patch_app) -> None:
    plot = _get_plot(patch_app, "Realized Gain 3Curves")
    curves = plot.get_expression_data_all_curves(formula="real")
    assert len(curves) == 3
    assert [curve["variation"]["Theta"] for curve in curves] == [-41.0, 0.0, 64.0]
    assert all(len(curve["x"]) == len(curve["y"]) > 0 for curve in curves)
    assert not np.allclose(curves[0]["y"], curves[1]["y"])


def test_phase_units(patch_app) -> None:
    plot = _get_plot(patch_app, "S Parameter Chart1")
    data = plot.get_solution_data()
    expression = plot.expressions[0]
    _, rad = data.get_expression_data(expression, formula="phaserad")
    _, deg = data.get_expression_data(expression, formula="phasedeg")
    assert np.all(np.abs(rad) <= np.pi)
    np.testing.assert_allclose(deg, np.degrees(rad))
