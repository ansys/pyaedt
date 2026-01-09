# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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

import os

import numpy as np
import pytest


@pytest.fixture
def h3d_potter_horn(add_app_example):
    app = add_app_example(project="Potter_Horn_242", subfolder="T12")
    yield app
    app.close_project(save=False)


def test_create_report(h3d_potter_horn):
    variations = h3d_potter_horn.available_variations.nominal_variation(dependent_params=False)
    variations["Theta"] = ["All"]
    variations["Phi"] = ["All"]
    variations["Freq"] = ["30GHz"]
    h3d_potter_horn.set_source_context(["1"])
    context = {"Context": "3D", "SourceContext": "1:1"}
    nominal_report = h3d_potter_horn.post.create_report(
        "db(GainTotal)",
        h3d_potter_horn.nominal_adaptive,
        variations=variations,
        primary_sweep_variable="Phi",
        secondary_sweep_variable="Theta",
        report_category="Far Fields",
        plot_type="3D Polar Plot",
        context=context,
    )
    assert nominal_report
    nominal_report2 = h3d_potter_horn.post.create_report(
        "db(GainTotal)",
    )
    assert nominal_report2
    h3d_potter_horn.post.delete_report(nominal_report.plot_name)


def test_create_report_sweep(h3d_potter_horn):
    variations = h3d_potter_horn.available_variations.nominal_variation(dependent_params=False)
    variations["Theta"] = ["All"]
    variations["Phi"] = ["All"]
    variations["Freq"] = ["30GHz"]
    sweep = h3d_potter_horn.setups[0].sweeps[0]
    variations["Freq"] = "30.1GHz"
    sweep_report = h3d_potter_horn.post.create_report(
        "db(GainTotal)",
        sweep.name,
        variations=variations,
        primary_sweep_variable="Phi",
        secondary_sweep_variable="Theta",
        report_category="Far Fields",
        plot_type="3D Polar Plot",
        context="3D",
    )
    assert sweep_report
    h3d_potter_horn.post.delete_report(sweep_report.plot_name)


def test_create_report_from_configuration_sweep_report(h3d_potter_horn, test_tmp_dir):
    variations = h3d_potter_horn.available_variations.nominal_variation(dependent_params=False)
    variations["Theta"] = ["All"]
    variations["Phi"] = ["All"]
    variations["Freq"] = ["30GHz"]
    sweep = h3d_potter_horn.setups[0].sweeps[0]
    variations["Freq"] = "30.1GHz"
    sweep_report = h3d_potter_horn.post.create_report(
        "db(GainTotal)",
        sweep.name,
        variations=variations,
        primary_sweep_variable="Phi",
        secondary_sweep_variable="Theta",
        report_category="Far Fields",
        plot_type="3D Polar Plot",
        context="3D",
    )
    assert sweep_report.export_config(str(test_tmp_dir / f"{sweep_report.plot_name}.json"))
    assert h3d_potter_horn.post.create_report_from_configuration(
        str(test_tmp_dir / f"{sweep_report.plot_name}.json"), solution_name=sweep.name
    )
    h3d_potter_horn.post.delete_report(sweep_report.plot_name)


def test_create_report_time(h3d_potter_horn):
    report = h3d_potter_horn.post.create_report(
        "Time",
        h3d_potter_horn.existing_analysis_sweeps[1],
        plot_name="Time Domain Report",
        domain="Time",
        primary_sweep_variable="Time",
        report_category="Modal Solution Data",
    )
    assert report
    h3d_potter_horn.post.delete_report(report.plot_name)


def test_reports_by_category_far_field(h3d_potter_horn):
    variations = h3d_potter_horn.available_variations.nominal_variation(dependent_params=False)
    variations["Theta"] = ["All"]
    variations["Phi"] = ["All"]
    variations["Freq"] = ["30GHz"]
    new_report = h3d_potter_horn.post.reports_by_category.far_field(
        "db(RealizedGainTotal)", h3d_potter_horn.nominal_adaptive
    )
    new_report.variations = variations
    new_report.report_type = "3D Polar Plot"
    new_report.far_field_sphere = "3D"
    assert new_report.create()
    h3d_potter_horn.post.delete_report(new_report.plot_name)


def test_reports_by_category_far_field_1(h3d_potter_horn):
    variations = h3d_potter_horn.available_variations.nominal_variation(dependent_params=False)
    variations["Theta"] = ["All"]
    variations["Phi"] = ["All"]
    variations["Freq"] = ["30GHz"]
    h3d_potter_horn.set_source_context(["1"])
    new_report2 = h3d_potter_horn.post.reports_by_category.far_field(
        "db(RealizedGainTotal)", h3d_potter_horn.nominal_adaptive, "3D", "1:1"
    )
    new_report2.variations = variations
    new_report2.report_type = "3D Polar Plot"
    new_report2.create()
    h3d_potter_horn.post.delete_report(new_report2.plot_name)


def test_reports_by_category_far_antenna_parameters(h3d_potter_horn):
    new_report3 = h3d_potter_horn.post.reports_by_category.antenna_parameters(
        "db(PeakRealizedGain)", h3d_potter_horn.nominal_adaptive, "3D"
    )
    new_report3.report_type = "Data Table"
    assert new_report3.create()
    h3d_potter_horn.post.delete_report(new_report3.plot_name)


def test_reports_by_category_far_antenna_parameters_1(h3d_potter_horn):
    new_report4 = h3d_potter_horn.post.reports_by_category.antenna_parameters(
        "db(PeakRealizedGain)", infinite_sphere="3D"
    )
    new_report4.report_type = "Data Table"
    assert new_report4.create()
    h3d_potter_horn.post.delete_report(new_report4.plot_name)


def test_reports_by_category_far_antenna_parameters_2(h3d_potter_horn):
    new_report4 = h3d_potter_horn.post.reports_by_category.antenna_parameters(
        "db(PeakRealizedGain)", infinite_sphere="3D"
    )
    new_report4.report_type = "Data Table"
    assert new_report4.create()
    h3d_potter_horn.post.delete_report(new_report4.plot_name)


def test_create_report_from_configuration_template(h3d_potter_horn):
    from tests import TESTS_VISUALIZATION_PATH
    from tests.conftest import config

    new_report4 = h3d_potter_horn.post.reports_by_category.antenna_parameters(
        "db(PeakRealizedGain)", infinite_sphere="3D"
    )
    new_report4.report_type = "Data Table"
    new_report4.create()
    template = os.path.join(TESTS_VISUALIZATION_PATH, "example_models", "T12", "template.rpt")
    assert os.path.exists(template)
    if not config["NonGraphical"]:
        assert new_report4.apply_report_template(template)
        template2 = os.path.join(TESTS_VISUALIZATION_PATH, "example_models", "T12", "template_invented.rpt")
        assert not new_report4.apply_report_template(template2)
        template3 = os.path.join(TESTS_VISUALIZATION_PATH, "example_models", "T12", "template.csv")
        assert not new_report4.apply_report_template(template3)
        assert not new_report4.apply_report_template(template3, property_type="Dummy")

    assert h3d_potter_horn.post.create_report_from_configuration(template)
    h3d_potter_horn.post.delete_report(new_report4.plot_name)


def test_data_plot(h3d_potter_horn, test_tmp_dir):
    variations = h3d_potter_horn.available_variations.nominal_variation(dependent_params=False)
    variations["Theta"] = ["All"]
    variations["Phi"] = ["All"]
    variations["Freq"] = ["30GHz"]
    data = h3d_potter_horn.post.get_solution_data(
        "GainTotal",
        h3d_potter_horn.nominal_adaptive,
        variations=variations,
        primary_sweep_variable="Theta",
        report_category="Far Fields",
        context="3D",
    )
    assert data.plot(snapshot_path=str(test_tmp_dir / "reportC.jpg"), show=False)


def test_data_plot_3d(h3d_potter_horn):
    variations = h3d_potter_horn.available_variations.nominal_variation(dependent_params=False)
    variations["Theta"] = ["All"]
    variations["Phi"] = ["All"]
    variations["Freq"] = ["30GHz"]
    data = h3d_potter_horn.post.get_solution_data(
        "GainTotal",
        h3d_potter_horn.nominal_adaptive,
        variations=variations,
        primary_sweep_variable="Theta",
        report_category="Far Fields",
        context="3D",
    )
    assert data.plot_3d(show=False)


def test_create_3d_plot(h3d_potter_horn, test_tmp_dir):
    variations = h3d_potter_horn.available_variations.nominal_variation(dependent_params=False)
    variations["Theta"] = ["All"]
    variations["Phi"] = ["All"]
    variations["Freq"] = ["30GHz"]
    data = h3d_potter_horn.post.get_solution_data(
        "GainTotal",
        h3d_potter_horn.nominal_adaptive,
        variations=variations,
        primary_sweep_variable="Theta",
        report_category="Far Fields",
        context="3D",
    )
    assert h3d_potter_horn.post.create_3d_plot(
        data,
        snapshot_path=str(test_tmp_dir / "reportC_3D_2.jpg"),
        show=False,
    )


def test_get_solution_data(h3d_potter_horn):
    variations = h3d_potter_horn.available_variations.nominal_variation(dependent_params=False)
    variations["Theta"] = ["All"]
    variations["Phi"] = ["All"]
    variations["Freq"] = ["30GHz"]
    context = {"Context": "3D", "SourceContext": "1:1"}
    data = h3d_potter_horn.post.get_solution_data(
        "GainTotal",
        h3d_potter_horn.nominal_adaptive,
        variations=variations,
        primary_sweep_variable="Theta",
        report_category="Far Fields",
        context=context,
    )

    assert data.primary_sweep == "Theta"
    assert len(data.get_expression_data("GainTotal", formula="magnitude")[1]) > 0
    assert not np.any(data.get_expression_data("GainTotal2")[0])


def test_create_report_nominal_sweep(h3d_potter_horn):
    variations = h3d_potter_horn.available_variations.nominal_variation(dependent_params=False)
    variations["Theta"] = ["All"]
    variations["Phi"] = ["All"]
    variations["Freq"] = ["30GHz"]

    assert h3d_potter_horn.post.create_report(
        "S(1,1)", h3d_potter_horn.nominal_sweep, variations=variations, plot_type="Smith Chart"
    )


# Improve it for Maxwell
def test_reports_by_category_fields(h3d_potter_horn):
    h3d_potter_horn.modeler.create_polyline([[0, 0, 0], [0, 5, 30]], name="Poly1", non_model=True)
    variations2 = h3d_potter_horn.available_variations.nominal_variation(dependent_params=False)
    assert h3d_potter_horn.setups[0].create_report(
        "Mag_E", primary_sweep_variable="Distance", report_category="Fields", context="Poly1"
    )
    new_report = h3d_potter_horn.post.reports_by_category.fields("Mag_H", h3d_potter_horn.nominal_adaptive)
    new_report.variations = variations2
    new_report.polyline = "Poly1"
    assert new_report.create()
    new_report = h3d_potter_horn.post.reports_by_category.fields("Mag_H")
    new_report.variations = variations2
    new_report.polyline = "Poly1"
    assert new_report.create()


def test_reports_by_category_modal_solution(h3d_potter_horn):
    variations2 = h3d_potter_horn.available_variations.nominal_variation(dependent_params=False)
    new_report = h3d_potter_horn.post.reports_by_category.modal_solution("S(1,1)")
    new_report.report_type = "Smith Chart"
    assert new_report.create()
    data = h3d_potter_horn.setups[0].get_solution_data(
        "Mag_E", variations=variations2, primary_sweep_variable="Theta", report_category="Fields", context="Poly1"
    )
    assert data.units_sweeps["Phase"] == "deg"


def test_get_far_field_data(h3d_potter_horn):
    assert h3d_potter_horn.post.get_far_field_data(expressions="RealizedGainTotal", domain="3D")
    assert h3d_potter_horn.post.get_far_field_data(
        expressions="RealizedGainTotal", setup_sweep_name=h3d_potter_horn.nominal_adaptive, domain="3D"
    )
    data_far_field2 = h3d_potter_horn.post.get_far_field_data(
        expressions="RealizedGainTotal",
        setup_sweep_name=h3d_potter_horn.nominal_adaptive,
        domain={"Context": "3D", "SourceContext": "1:1"},
    )
    assert data_far_field2.plot(formula="db20", is_polar=True, show=False)


def test_reports_by_category_terminal_solution(h3d_potter_horn):
    test = h3d_potter_horn.post.reports_by_category.terminal_solution()
    assert test


def test_get_solution_data_per_variation(h3d_potter_horn):
    assert (
        h3d_potter_horn.post.get_solution_data_per_variation(
            solution_type="Far Fields", expressions="RealizedGainTotal"
        )
        is None
    )


def test_get_efields(h3d_potter_horn):
    assert h3d_potter_horn.post.get_efields_data(ff_setup="3D")


def test_get_variations(h3d_potter_horn):
    setup = h3d_potter_horn.existing_analysis_sweeps[0]
    variations = h3d_potter_horn.available_variations.variations(setup)
    assert isinstance(variations, list)
    assert isinstance(variations[0], list)
    vars_dict = h3d_potter_horn.available_variations.variations(setup_sweep=setup, output_as_dict=True)
    assert isinstance(vars_dict, list)
    assert isinstance(vars_dict[0], dict)


def test_cleanup_solution_1(h3d_potter_horn):
    setup = h3d_potter_horn.existing_analysis_sweeps
    variations = h3d_potter_horn.available_variations._get_variation_strings(setup[0])
    assert h3d_potter_horn.cleanup_solution(variations, entire_solution=False)
    assert h3d_potter_horn.cleanup_solution(variations, entire_solution=True)
