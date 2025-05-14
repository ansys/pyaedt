# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
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
from pathlib import Path
import tempfile

from ansys.aedt.core import Circuit
from ansys.aedt.core import Icepak
from ansys.aedt.core import Maxwell2d
from ansys.aedt.core import Maxwell3d
from ansys.aedt.core import Q2d
from ansys.aedt.core import Q3d
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.visualization.plot.pyvista import _parse_aedtplt
from ansys.aedt.core.visualization.plot.pyvista import _parse_streamline
import pandas as pd
import pytest

from tests import TESTS_VISUALIZATION_PATH
from tests.system.visualization.conftest import config

test_field_name = "Potter_Horn_242"
q3d_file = "via_gsg_solved"
test_circuit_name = "Switching_Speed_FET_And_Diode_Solved"
sbr_file = "poc_scat_small_solved"
eye_diagram = "channel_solved"
ami = "ami"
m2d_file = "m2d"
m3d_file = "m3d"
test_emi_name = "EMI_RCV_251"
ipk_post_proj = "for_icepak_post_parasolid"
ipk_markers_proj = "ipk_markers"

test_subfolder = "T12"


@pytest.fixture()
def markers_test(add_app):
    app = add_app(project_name=ipk_markers_proj, application=Icepak, subfolder=test_subfolder)
    yield app
    app.close_project(save=False)


@pytest.fixture()
def field_test(add_app):
    app = add_app(project_name=test_field_name, subfolder=test_subfolder)
    yield app
    app.close_project(save=False)


@pytest.fixture()
def circuit_test(add_app):
    app = add_app(project_name=test_circuit_name, design_name="Diode", application=Circuit, subfolder=test_subfolder)
    yield app
    app.close_project(save=False)


@pytest.fixture()
def emi_receiver_test(add_app):
    app = add_app(project_name=test_emi_name, design_name="CE_band", application=Circuit, subfolder=test_subfolder)
    yield app
    app.close_project(save=False)


@pytest.fixture()
def diff_test(add_app):
    app = add_app(project_name=test_circuit_name, design_name="diff", application=Circuit, subfolder=test_subfolder)
    yield app
    app.close_project(save=False)


@pytest.fixture()
def sbr_test(add_app):
    app = add_app(project_name=sbr_file, subfolder=test_subfolder)
    yield app
    app.close_project(save=False)


@pytest.fixture()
def q3dtest(add_app):
    app = add_app(project_name=q3d_file, application=Q3d, subfolder=test_subfolder)
    yield app
    app.close_project(save=False)


@pytest.fixture()
def q2dtest(add_app):
    app = add_app(project_name=q3d_file, application=Q2d, subfolder=test_subfolder)
    yield app
    app.close_project(save=False)


@pytest.fixture()
def eye_test(add_app):
    app = add_app(project_name=eye_diagram, application=Circuit, subfolder=test_subfolder)
    yield app
    app.close_project(save=False)


@pytest.fixture()
def icepak_post(add_app):
    app = add_app(project_name=ipk_post_proj, application=Icepak, subfolder=test_subfolder)
    yield app
    app.close_project(save=False)


@pytest.fixture()
def ami_test(add_app):
    app = add_app(project_name=ami, application=Circuit, subfolder=test_subfolder)
    yield app
    app.close_project(save=False)


@pytest.fixture()
def m2dtest(add_app):
    app = add_app(project_name=m2d_file, application=Maxwell2d, subfolder=test_subfolder)
    yield app
    app.close_project(save=False)


@pytest.fixture()
def m3d_app(add_app):
    app = add_app(project_name=m3d_file, application=Maxwell3d, subfolder=test_subfolder)
    yield app
    app.close_project(save=False)


class TestClass:

    def test_create_report(self, field_test):
        variations = field_test.available_variations.get_independent_nominal_values()
        variations["Theta"] = ["All"]
        variations["Phi"] = ["All"]
        variations["Freq"] = ["30GHz"]
        field_test.set_source_context(["1"])
        context = {"Context": "3D", "SourceContext": "1:1"}
        nominal_report = field_test.post.create_report(
            "db(GainTotal)",
            field_test.nominal_adaptive,
            variations=variations,
            primary_sweep_variable="Phi",
            secondary_sweep_variable="Theta",
            report_category="Far Fields",
            plot_type="3D Polar Plot",
            context=context,
        )
        assert nominal_report

    def test_create_report_sweep(self, field_test):
        variations = field_test.available_variations.get_independent_nominal_values()
        variations["Theta"] = ["All"]
        variations["Phi"] = ["All"]
        variations["Freq"] = ["30GHz"]
        sweep = field_test.setups[0].sweeps[0]
        variations["Freq"] = "30.1GHz"
        sweep_report = field_test.post.create_report(
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

    def test_create_report_from_configuration_sweep_report(self, local_scratch, field_test):
        variations = field_test.available_variations.get_independent_nominal_values()
        variations["Theta"] = ["All"]
        variations["Phi"] = ["All"]
        variations["Freq"] = ["30GHz"]
        sweep = field_test.setups[0].sweeps[0]
        variations["Freq"] = "30.1GHz"
        sweep_report = field_test.post.create_report(
            "db(GainTotal)",
            sweep.name,
            variations=variations,
            primary_sweep_variable="Phi",
            secondary_sweep_variable="Theta",
            report_category="Far Fields",
            plot_type="3D Polar Plot",
            context="3D",
        )
        assert sweep_report.export_config(os.path.join(local_scratch.path, f"{sweep_report.plot_name}.json"))
        assert field_test.post.create_report_from_configuration(
            os.path.join(local_scratch.path, f"{sweep_report.plot_name}.json"), solution_name=sweep.name
        )

    def test_create_report_time(self, field_test):
        assert field_test.post.create_report(
            "Time",
            field_test.existing_analysis_sweeps[1],
            plot_name="Time Domain Report",
            domain="Time",
            primary_sweep_variable="Time",
            report_category="Modal Solution Data",
        )

    def test_reports_by_category_far_field(self, field_test):
        variations = field_test.available_variations.get_independent_nominal_values()
        variations["Theta"] = ["All"]
        variations["Phi"] = ["All"]
        variations["Freq"] = ["30GHz"]
        new_report = field_test.post.reports_by_category.far_field("db(RealizedGainTotal)", field_test.nominal_adaptive)
        new_report.variations = variations
        new_report.report_type = "3D Polar Plot"
        new_report.far_field_sphere = "3D"
        assert new_report.create()

    def test_reports_by_category_far_field_1(self, field_test):
        variations = field_test.available_variations.get_independent_nominal_values()
        variations["Theta"] = ["All"]
        variations["Phi"] = ["All"]
        variations["Freq"] = ["30GHz"]
        field_test.set_source_context(["1"])
        new_report2 = field_test.post.reports_by_category.far_field(
            "db(RealizedGainTotal)", field_test.nominal_adaptive, "3D", "1:1"
        )
        new_report2.variations = variations
        new_report2.report_type = "3D Polar Plot"
        assert new_report2.create()

    def test_reports_by_category_far_antenna_parameters(self, field_test):
        new_report3 = field_test.post.reports_by_category.antenna_parameters(
            "db(PeakRealizedGain)", field_test.nominal_adaptive, "3D"
        )
        new_report3.report_type = "Data Table"
        assert new_report3.create()

    def test_reports_by_category_far_antenna_parameters_1(self, field_test):
        new_report4 = field_test.post.reports_by_category.antenna_parameters(
            "db(PeakRealizedGain)", infinite_sphere="3D"
        )
        new_report4.report_type = "Data Table"
        assert new_report4.create()

    def test_reports_by_category_far_antenna_parameters_2(self, field_test):
        new_report4 = field_test.post.reports_by_category.antenna_parameters(
            "db(PeakRealizedGain)", infinite_sphere="3D"
        )
        new_report4.report_type = "Data Table"
        assert new_report4.create()

    def test_create_report_from_configuration_template(self, field_test):
        new_report4 = field_test.post.reports_by_category.antenna_parameters(
            "db(PeakRealizedGain)", infinite_sphere="3D"
        )
        new_report4.report_type = "Data Table"
        new_report4.create()
        template = os.path.join(TESTS_VISUALIZATION_PATH, "example_models", test_subfolder, "template.rpt")
        if not config["NonGraphical"]:
            assert new_report4.apply_report_template(template)
            template2 = os.path.join(
                TESTS_VISUALIZATION_PATH, "example_models", test_subfolder, "template_invented.rpt"
            )
            assert not new_report4.apply_report_template(template2)
            template3 = os.path.join(TESTS_VISUALIZATION_PATH, "example_models", test_subfolder, "template.csv")
            assert not new_report4.apply_report_template(template3)
            assert not new_report4.apply_report_template(template3, property_type="Dummy")

        assert field_test.post.create_report_from_configuration(template)

    def test_data_plot(self, local_scratch, field_test):
        variations = field_test.available_variations.get_independent_nominal_values()
        variations["Theta"] = ["All"]
        variations["Phi"] = ["All"]
        variations["Freq"] = ["30GHz"]
        data = field_test.post.get_solution_data(
            "GainTotal",
            field_test.nominal_adaptive,
            variations=variations,
            primary_sweep_variable="Theta",
            report_category="Far Fields",
            context="3D",
        )
        assert data.plot(snapshot_path=os.path.join(local_scratch.path, "reportC.jpg"), show=False)

    def test_data_plot_3d(self, field_test):
        variations = field_test.available_variations.get_independent_nominal_values()
        variations["Theta"] = ["All"]
        variations["Phi"] = ["All"]
        variations["Freq"] = ["30GHz"]
        data = field_test.post.get_solution_data(
            "GainTotal",
            field_test.nominal_adaptive,
            variations=variations,
            primary_sweep_variable="Theta",
            report_category="Far Fields",
            context="3D",
        )
        assert data.plot_3d(show=False)

    def test_create_3d_plot(self, local_scratch, field_test):
        variations = field_test.available_variations.get_independent_nominal_values()
        variations["Theta"] = ["All"]
        variations["Phi"] = ["All"]
        variations["Freq"] = ["30GHz"]
        data = field_test.post.get_solution_data(
            "GainTotal",
            field_test.nominal_adaptive,
            variations=variations,
            primary_sweep_variable="Theta",
            report_category="Far Fields",
            context="3D",
        )
        assert field_test.post.create_3d_plot(
            data,
            snapshot_path=os.path.join(local_scratch.path, "reportC_3D_2.jpg"),
            show=False,
        )

    def test_get_solution_data(self, field_test):
        variations = field_test.available_variations.get_independent_nominal_values()
        variations["Theta"] = ["All"]
        variations["Phi"] = ["All"]
        variations["Freq"] = ["30GHz"]
        context = {"Context": "3D", "SourceContext": "1:1"}
        data = field_test.post.get_solution_data(
            "GainTotal",
            field_test.nominal_adaptive,
            variations=variations,
            primary_sweep_variable="Theta",
            report_category="Far Fields",
            context=context,
        )

        assert data.primary_sweep == "Theta"
        assert len(data.data_magnitude("GainTotal")) > 0
        assert not data.data_magnitude("GainTotal2")

    def test_create_report_nominal_sweep(self, field_test):
        variations = field_test.available_variations.get_independent_nominal_values()
        variations["Theta"] = ["All"]
        variations["Phi"] = ["All"]
        variations["Freq"] = ["30GHz"]

        assert field_test.post.create_report(
            "S(1,1)", field_test.nominal_sweep, variations=variations, plot_type="Smith Chart"
        )

    # Improve it for Maxwell
    def test_reports_by_category_fields(self, field_test):
        field_test.modeler.create_polyline([[0, 0, 0], [0, 5, 30]], name="Poly1", non_model=True)
        variations2 = field_test.available_variations.get_independent_nominal_values()
        assert field_test.setups[0].create_report(
            "Mag_E", primary_sweep_variable="Distance", report_category="Fields", context="Poly1"
        )
        new_report = field_test.post.reports_by_category.fields("Mag_H", field_test.nominal_adaptive)
        new_report.variations = variations2
        new_report.polyline = "Poly1"
        assert new_report.create()
        new_report = field_test.post.reports_by_category.fields("Mag_H")
        new_report.variations = variations2
        new_report.polyline = "Poly1"
        assert new_report.create()

    def test_reports_by_category_modal_solution(self, field_test):
        variations2 = field_test.available_variations.get_independent_nominal_values()
        new_report = field_test.post.reports_by_category.modal_solution("S(1,1)")
        new_report.report_type = "Smith Chart"
        assert new_report.create()
        data = field_test.setups[0].get_solution_data(
            "Mag_E", variations=variations2, primary_sweep_variable="Theta", report_category="Fields", context="Poly1"
        )
        assert data.units_sweeps["Phase"] == "deg"

    def test_get_far_field_data(self, field_test):
        assert field_test.post.get_far_field_data(expressions="RealizedGainTotal", domain="3D")
        assert field_test.post.get_far_field_data(
            expressions="RealizedGainTotal", setup_sweep_name=field_test.nominal_adaptive, domain="3D"
        )
        data_far_field2 = field_test.post.get_far_field_data(
            expressions="RealizedGainTotal",
            setup_sweep_name=field_test.nominal_adaptive,
            domain={"Context": "3D", "SourceContext": "1:1"},
        )
        assert data_far_field2.plot(formula="db20", is_polar=True, show=False)

    def test_reports_by_category_terminal_solution(self, field_test):
        test = field_test.post.reports_by_category.terminal_solution()
        assert test

    def test_get_solution_data_per_variation(self, field_test):
        assert (
            field_test.post.get_solution_data_per_variation(solution_type="Far Fields", expressions="RealizedGainTotal")
            is None
        )

    def test_circuit_export_results(self, circuit_test):
        files = circuit_test.export_results()
        assert len(files) > 0

    def test_q2d_export_results(self, q2dtest):
        files = q2dtest.export_results()
        assert len(files) > 0

    def test_q3d_export_results(self, q3dtest):
        files = q3dtest.export_results()
        assert len(files) > 0

    def test_m3d_export_results(self, m3d_app):
        files = m3d_app.export_results()
        assert len(files) > 0

    def test_m2d_export_results(self, m2dtest):
        files = m2dtest.export_results()
        assert len(files) > 0

    def test_circuit_create_report(self, circuit_test):
        assert circuit_test.setups[0].create_report(["dB(S(Port1, Port1))", "dB(S(Port1, Port2))"])

    def test_circuit_reports_by_category_standard(self, circuit_test):
        new_report = circuit_test.post.reports_by_category.standard(
            ["dB(S(Port1, Port1))", "dB(S(Port1, Port2))"], "LNA"
        )
        assert new_report.create()

    def test_circuit_reports_by_category_standard_1(self, diff_test):
        new_report1 = diff_test.post.reports_by_category.standard()
        assert new_report1.expressions

    def test_circuit_reports_by_category_standard_3(self, diff_test):
        new_report = diff_test.post.reports_by_category.standard("dB(S(1,1))")
        new_report.differential_pairs = True
        assert new_report.create()
        assert new_report.get_solution_data()

    def test_circuit_reports_by_category_standard_4(self, diff_test):
        new_report2 = diff_test.post.reports_by_category.standard("TDRZ(1)")
        new_report2.differential_pairs = True
        new_report2.pulse_rise_time = 3e-12
        new_report2.maximum_time = 30e-12
        new_report2.step_time = 6e-13
        new_report2.time_windowing = 3
        new_report2.domain = "Time"
        assert new_report2.create()

    def test_circuit_get_solution_data(self, circuit_test):
        data = circuit_test.post.get_solution_data(["dB(S(Port1,Port1))", "dB(S(Port1,Port2))"], "LNA")
        assert data.primary_sweep == "Freq"

    def test_circuit_create_report_1(self, circuit_test):
        plot = circuit_test.post.create_report(["V(net_11)"], "Transient", "Time")
        assert plot

    def test_circuit_create_report_from_configuration(self, local_scratch, circuit_test):
        plot = circuit_test.post.create_report(["V(net_11)"], "Transient", "Time")
        assert plot.export_config(os.path.join(local_scratch.path, f"{plot.plot_name}.json"))
        assert circuit_test.post.create_report_from_configuration(
            os.path.join(local_scratch.path, f"{plot.plot_name}.json"), solution_name="Transient"
        )

    def test_circuit_get_solution_data_1(self, circuit_test):
        data11 = circuit_test.post.get_solution_data(setup_sweep_name="LNA", math_formula="dB")
        assert data11.primary_sweep == "Freq"
        assert "dB(S(Port2,Port1))" in data11.expressions

    def test_circuit_get_solution_data_2(self, circuit_test):
        data2 = circuit_test.post.get_solution_data(["V(net_11)"], "Transient", "Time")
        assert data2.primary_sweep == "Time"
        assert len(data2.data_magnitude()) > 0

    def test_circuit_get_solution_data_3(self, circuit_test):
        context = {"algorithm": "FFT", "max_frequency": "100MHz", "time_stop": "200ns", "test": ""}
        data3 = circuit_test.post.get_solution_data(["V(net_11)"], "Transient", "Spectral", context=context)
        assert data3.units_sweeps["Spectrum"] == circuit_test.units.frequency
        assert len(data3.data_real()) > 0

    def test_reports_by_category_standard_1(self, circuit_test):
        circuit_test.post.create_report(["V(net_11)"], "Transient", "Time")
        new_report = circuit_test.post.reports_by_category.standard(["V(net_11)"], "Transient")
        new_report.domain = "Time"
        assert new_report.create()

    def test_reports_by_category_spectral(self, circuit_test):
        new_report = circuit_test.post.reports_by_category.spectral(["dB(V(net_11))"], "Transient")
        new_report.window = "Hanning"
        new_report.max_freq = "1GHz"
        new_report.time_start = "1ns"
        new_report.time_stop = "190ns"
        new_report.plot_continous_spectrum = True
        assert new_report.create()

    def test_reports_by_category_spectral_2(self, circuit_test):
        new_report = circuit_test.post.reports_by_category.spectral(["dB(V(net_11))", "dB(V(Port1))"], "Transient")
        new_report.window = "Kaiser"
        new_report.adjust_coherent_gain = False
        new_report.kaiser_coeff = 2
        new_report.algorithm = "Fourier Transform"
        new_report.max_freq = "1GHz"
        new_report.time_start = "1ns"
        new_report.time_stop = "190ns"
        new_report.plot_continous_spectrum = False
        assert new_report.create()

    def test_reports_by_category_spectral_3(self, circuit_test):
        new_report = circuit_test.post.reports_by_category.spectral(None, "Transient")
        new_report.window = "Hanning"
        new_report.max_freq = "1GHz"
        new_report.time_start = "1ns"
        new_report.time_stop = "190ns"
        new_report.plot_continous_spectrum = True
        assert new_report.create()

    def test_create_report_spectrum(self, circuit_test):
        assert circuit_test.post.create_report(
            ["dB(V(net_11))", "dB(V(Port1))"], setup_sweep_name="Transient", domain="Spectrum"
        )

    def test_circuit_available_display_types(self, diff_test):
        assert len(diff_test.post.available_display_types()) > 0

    def test_circuit_available_report_quantities(self, diff_test):
        assert len(diff_test.post.available_report_quantities()) > 0

    def test_circuit_available_report_solutions(self, diff_test):
        assert len(diff_test.post.available_report_solutions()) > 0

    def test_circuit_create_report_2(self, diff_test):
        variations = diff_test.available_variations.get_independent_nominal_values()
        variations["Freq"] = ["All"]
        variations["l1"] = ["All"]
        assert diff_test.post.create_report(
            ["dB(S(Diff1, Diff1))"],
            "LinearFrequency",
            variations=variations,
            primary_sweep_variable="l1",
            context="Differential Pairs",
        )

    def test_get_efields(self, field_test):
        assert field_test.post.get_efields_data(ff_setup="3D")

    def test_sbr_get_solution_data(self, sbr_test):
        assert sbr_test.setups[0].is_solved
        solution_data = sbr_test.post.get_solution_data(
            expressions=["NearEX", "NearEY", "NearEZ"], report_category="Near Fields", context="Near_Field"
        )
        assert solution_data
        assert len(solution_data.primary_sweep_values) > 0
        assert len(solution_data.primary_sweep_variations) > 0
        assert solution_data.set_active_variation(0)
        assert not solution_data.set_active_variation(99)

    def test_sbr_solution_data_ifft(self, sbr_test):
        solution_data = sbr_test.post.get_solution_data(
            expressions=["NearEX", "NearEY", "NearEZ"], report_category="Near Fields", context="Near_Field"
        )
        t_matrix = solution_data.ifft("NearE", window=True)
        assert t_matrix.any()
        frames_list = solution_data.ifft_to_file(
            coord_system_center=[-0.15, 0, 0], db_val=True, csv_path=os.path.join(sbr_test.working_directory, "csv")
        )
        assert os.path.exists(frames_list)

    def test_sbr_plot_scene(self, sbr_test):
        solution_data = sbr_test.post.get_solution_data(
            expressions=["NearEX", "NearEY", "NearEZ"], report_category="Near Fields", context="Near_Field"
        )
        t_matrix = solution_data.ifft("NearE", window=True)
        assert t_matrix.any()
        frames_list = solution_data.ifft_to_file(
            coord_system_center=[-0.15, 0, 0], db_val=True, csv_path=os.path.join(sbr_test.working_directory, "csv")
        )

        sbr_test.post.plot_scene(
            frames_list, os.path.join(sbr_test.working_directory, "animation.gif"), norm_index=5, dy_rng=35, show=False
        )
        assert os.path.exists(os.path.join(sbr_test.working_directory, "animation.gif"))
        sbr_test.post.plot_scene(
            frames_list,
            os.path.join(sbr_test.working_directory, "animation2.gif"),
            norm_index=5,
            dy_rng=35,
            show=False,
            convert_fields_in_db=True,
            log_multiplier=20.0,
        )
        assert os.path.exists(os.path.join(sbr_test.working_directory, "animation2.gif"))

    def test_q3d_export_convergence(self, q3dtest):
        assert os.path.exists(q3dtest.export_convergence("Setup1"))

    def test_q3d_export_profile(self, q3dtest):
        assert os.path.exists(q3dtest.export_profile("Setup1"))

    def test_q3d_reports_by_category_standard(self, q3dtest):
        new_report = q3dtest.post.reports_by_category.standard(q3dtest.get_traces_for_plot())
        assert new_report.create()

    def test_q3d_reports_by_category_cg_fields(self, q3dtest):
        q3dtest.modeler.create_polyline([[0, -5, 0.425], [0.5, 5, 0.5]], name="Poly1", non_model=True)
        new_report = q3dtest.post.reports_by_category.cg_fields("SmoothQ", polyline="Poly1")
        assert new_report.create()

    def test_q3d_reports_by_category_rl_fields(self, q3dtest):
        q3dtest.modeler.create_polyline([[0, -5, 0.425], [0.5, 5, 0.5]], name="Poly1", non_model=True)
        new_report = q3dtest.post.reports_by_category.rl_fields("Mag_SurfaceJac", polyline="Poly1")
        assert new_report.create()

    def test_q3d_reports_by_category_dc_fields(self, q3dtest):
        q3dtest.modeler.create_polyline([[0, -5, 0.425], [0.5, 5, 0.5]], name="Poly1", non_model=True)
        new_report = q3dtest.post.reports_by_category.dc_fields("Mag_VolumeJdc", polyline="Poly1")
        assert new_report.create()

    def test_q2d_export_convergence(self, q2dtest):
        assert os.path.exists(q2dtest.export_convergence("Setup1"))

    def test_q2d_export_profile(self, q2dtest):
        assert os.path.exists(q2dtest.export_profile("Setup1"))

    def test_q2d_reports_by_category_standard(self, q2dtest):
        new_report = q2dtest.post.reports_by_category.standard(q2dtest.get_traces_for_plot())
        assert new_report.create()

    def test_q2d_reports_by_category_cg_fields(self, q2dtest):
        q2dtest.modeler.create_polyline([[-1.9, -0.1, 0], [-1.2, -0.2, 0]], name="Poly1", non_model=True)
        new_report = q2dtest.post.reports_by_category.cg_fields("Mag_E", polyline="Poly1")
        assert new_report.create()

    def test_q2d_reports_by_category_rl_fields(self, q2dtest):
        q2dtest.modeler.create_polyline([[-1.9, -0.1, 0], [-1.2, -0.2, 0]], name="Poly1", non_model=True)
        new_report = q2dtest.post.reports_by_category.rl_fields("Mag_H", polyline="Poly1")
        assert new_report.create()

    def test_q2d_reports_by_category_standard_2(self, q2dtest):
        q2dtest.modeler.create_polyline([[-1.9, -0.1, 0], [-1.2, -0.2, 0]], name="Poly1", non_model=True)
        new_report = q2dtest.post.reports_by_category.rl_fields("Mag_H", polyline="Poly1")
        sol = new_report.get_solution_data()
        sol.enable_pandas_output = True
        data = sol.full_matrix_real_imag
        data_mag = sol.full_matrix_mag_phase
        sol.data_magnitude()
        sol.enable_pandas_output = False
        new_report = q2dtest.post.reports_by_category.standard()
        assert new_report.get_solution_data()

    def test_q3dtest_no_report(self, q3dtest):
        assert not q3dtest.post.reports_by_category.modal_solution()
        assert not q3dtest.post.reports_by_category.terminal_solution()

    def test_q2dtest_no_report(self, q2dtest):
        assert not q2dtest.post.reports_by_category.far_field()
        assert not q2dtest.post.reports_by_category.near_field()
        assert not q2dtest.post.reports_by_category.eigenmode()

    def test_parse_vector_aedtplt(self):
        out = _parse_aedtplt(
            os.path.join(TESTS_VISUALIZATION_PATH, "example_models", test_subfolder, "test_vector.aedtplt")
        )
        assert isinstance(out[0], list)
        assert isinstance(out[1], list)
        assert isinstance(out[2], list)
        assert isinstance(out[3], bool)
        assert _parse_aedtplt(
            os.path.join(TESTS_VISUALIZATION_PATH, "example_models", test_subfolder, "test_vector_no_solutions.aedtplt")
        )

    def test_parse_vector(self):
        out = _parse_streamline(
            os.path.join(TESTS_VISUALIZATION_PATH, "example_models", test_subfolder, "test_streamline.fldplt")
        )
        assert isinstance(out, list)

    def test_export_mesh(self, q3dtest):
        assert Path(q3dtest.export_mesh_stats("Setup1")).exists()
        assert Path(q3dtest.export_mesh_stats("Setup1")).exists()

    def test_eye_diagram(self, eye_test):
        rep = eye_test.post.reports_by_category.eye_diagram("AEYEPROBE(OutputEye)", "QuickEyeAnalysis")
        rep.time_start = "0ps"
        rep.time_stop = "50us"
        rep.unit_interval = "1e-9"
        assert rep.create()

    @pytest.mark.skipif(
        config["desktopVersion"] < "2022.2", reason="Not working in non graphical in version lower than 2022.2"
    )
    def test_mask(self, eye_test):
        rep = eye_test.post.reports_by_category.eye_diagram("AEYEPROBE(OutputEye)", "QuickEyeAnalysis")
        rep.time_start = "0ps"
        rep.time_stop = "50us"
        rep.unit_interval = "1e-9"
        rep.create()
        assert rep.eye_mask([[0.5, 0], [0.62, 450], [1.2, 450], [1.42, 0], [1.2, -450], [0.62, -450], [0.5, 0]])
        assert rep.eye_mask(
            [[0.5, 0], [0.62, 450], [1.2, 450], [1.42, 0], [1.2, -450], [0.62, -450], [0.5, 0]],
            enable_limits=True,
            upper_limit=800,
            lower_limit=-800,
        )
        assert os.path.exists(rep.export_mask_violation())

    @pytest.mark.skipif(
        config["desktopVersion"] < "2022.2", reason="Not working in non graphical in version lower than 2022.2"
    )
    def test_eye_measurements(self, eye_test):
        rep = eye_test.post.reports_by_category.eye_diagram("AEYEPROBE(OutputEye)", "QuickEyeAnalysis")
        rep.time_start = "0ps"
        rep.time_stop = "50us"
        rep.unit_interval = "1e-9"
        rep.create()
        assert rep.add_all_eye_measurements()
        assert rep.clear_all_eye_measurements()
        assert rep.add_trace_characteristics("MinEyeHeight")

    def test_eye_from_json_simple(self, eye_test):
        assert eye_test.post.create_report_from_configuration(
            os.path.join(TESTS_VISUALIZATION_PATH, "example_models", "report_json", "EyeDiagram_Report_simple.json"),
            solution_name="QuickEyeAnalysis",
        )

    def test_spectral_from_json_simple(self, circuit_test):
        assert circuit_test.post.create_report_from_configuration(
            os.path.join(TESTS_VISUALIZATION_PATH, "example_models", "report_json", "Spectral_Report_Simple.json"),
            solution_name="Transient",
        )

    @pytest.mark.skipif(
        config["desktopVersion"] < "2022.2", reason="Not working in non graphical in version lower than 2022.2"
    )
    def test_eye_from_json(self, eye_test):
        assert eye_test.post.create_report_from_configuration(
            os.path.join(TESTS_VISUALIZATION_PATH, "example_models", "report_json", "EyeDiagram_Report.toml"),
            solution_name="QuickEyeAnalysis",
        )

    @pytest.mark.skipif(
        config["desktopVersion"] < "2022.2", reason="Not working in non graphical in version lower than 2022.2"
    )
    def test_spectral_from_json(self, circuit_test):
        assert circuit_test.post.create_report_from_configuration(
            os.path.join(TESTS_VISUALIZATION_PATH, "example_models", "report_json", "Spectral_Report.json"),
            solution_name="Transient",
        )

    def test_ami_solution_data(self, ami_test):
        ami_test.solution_type = "NexximAMI"
        assert ami_test.post.get_solution_data(
            expressions="WaveAfterProbe<b_input_43.int_ami_rx>",
            domain="Time",
            variations=ami_test.available_variations.nominal,
        )

        assert ami_test.post.get_solution_data(
            expressions="WaveAfterSource<b_output4_42.int_ami_tx>",
            domain="Time",
            variations=ami_test.available_variations.nominal,
        )

        assert ami_test.post.get_solution_data(
            expressions="InitialWave<b_output4_42.int_ami_tx>",
            domain="Time",
            variations=ami_test.available_variations.nominal,
        )

        assert ami_test.post.get_solution_data(
            expressions="WaveAfterChannel<b_input_43.int_ami_rx>",
            domain="Time",
            variations=ami_test.available_variations.nominal,
        )

        assert ami_test.post.get_solution_data(
            expressions="ClockTics<b_input_43.int_ami_rx>",
            domain="Clock Times",
            variations=ami_test.available_variations.nominal,
        )

    def test_ami_sample_ami_waveform(self, ami_test):
        ami_test.solution_type = "NexximAMI"
        probe_name = "b_input_43"
        source_name = "b_output4_42"
        plot_type = "WaveAfterProbe"
        setup_name = "AMIAnalysis"

        ignore_bits = 1000
        unit_interval = 0.1e-9
        assert not ami_test.post.sample_ami_waveform(
            setup_name,
            probe_name,
            source_name,
            ami_test.available_variations.nominal,
            unit_interval,
            ignore_bits,
            plot_type,
        )
        ignore_bits = 5
        unit_interval = 0.1e-9
        plot_type = "InitialWave"
        data1 = ami_test.post.sample_ami_waveform(
            setup_name,
            probe_name,
            source_name,
            ami_test.available_variations.nominal,
            unit_interval,
            ignore_bits,
            plot_type,
        )
        assert len(data1[0]) == 45

        settings.enable_pandas_output = False
        ignore_bits = 5
        unit_interval = 0.1e-9
        clock_tics = [1e-9, 2e-9, 3e-9]
        data2 = ami_test.post.sample_ami_waveform(
            setup_name,
            probe_name,
            source_name,
            ami_test.available_variations.nominal,
            unit_interval,
            ignore_bits,
            plot_type=None,
            clock_tics=clock_tics,
        )
        assert len(data2) == 4
        assert len(data2[0]) == 3
        settings.enable_pandas_output = True

    def test_m2d_plot_field_line_traces(self, m2dtest):
        m2dtest.set_active_design("field_line_trace")
        plot = m2dtest.post.create_fieldplot_line_traces(["Ground", "Electrode"], "Region")
        assert plot
        plot = m2dtest.post.create_fieldplot_line_traces(["Ground", "Electrode"], "Region", plot_name="LineTracesTest4")
        assert plot
        assert m2dtest.post.create_fieldplot_line_traces(["Ground", "Electrode"], "Region", plot_name="LineTracesTest4")
        assert m2dtest.post.create_fieldplot_line_traces(
            ["Ground", "Electrode"], "Region", "Ground", plot_name="LineTracesTest5"
        )
        assert m2dtest.post.create_fieldplot_line_traces(["Ground", "Electrode"], plot_name="LineTracesTest6")
        assert not m2dtest.post.create_fieldplot_line_traces(
            ["Ground", "Electrode"], "Region", ["Invalid"], plot_name="LineTracesTest7"
        )
        assert not m2dtest.post.create_fieldplot_line_traces(
            ["Ground", "Electrode"], ["Invalid"], plot_name="LineTracesTest8"
        )
        plot.TraceStepLength = "0.002mm"
        plot.SeedingPointsNumber = 20
        plot.LineStyle = "Cylinder"
        plot.LineWidth = 3
        assert plot.update()
        el_id = [obj.id for obj in m2dtest.modeler.object_list if obj.name == "Electrode"]
        plot.seeding_faces.append(el_id[0])
        assert plot.update()
        plot.volumes.append(el_id[0])
        plot.update()
        plot.surfaces.append(el_id[0])
        plot.update()
        plot.seeding_faces.append(8)
        assert not plot.update()
        plot.volumes.append(8)
        assert not plot.update()
        plot.surfaces.append(8)
        assert not plot.update()

    @pytest.mark.skipif(config["desktopVersion"] < "2024.1", reason="EMI receiver available from 2024R1.")
    def test_emi_receiver(self, emi_receiver_test):
        new_report = emi_receiver_test.post.reports_by_category.emi_receiver()
        new_report.band = "2"
        new_report.rbw = "2"
        new_report.rbw_factor = "0"
        new_report.emission = "RE"
        new_report.time_start = "1ns"
        new_report.time_stop = "2us"
        new_report.net = "net_invented"
        assert new_report.net != "net_invented"
        assert new_report.create()
        new_report2 = emi_receiver_test.post.reports_by_category.emi_receiver(
            ["dBu(Average[net_6])", "dBu(Peak[net_6])", "dBu(QuasiPeak[net_6])", "dBu(RMS[net_6])"], "EMItransient"
        )
        assert new_report2.net == "net_6"
        new_report2.time_stop = "2.5us"
        assert new_report2.create()

    def test_get_variations(self, field_test):
        setup = field_test.existing_analysis_sweeps[0]
        variations = field_test.available_variations.variations(setup)
        assert isinstance(variations, list)
        assert isinstance(variations[0], list)
        vars_dict = field_test.available_variations.variations(setup_sweep=setup, output_as_dict=True)
        assert isinstance(vars_dict, list)
        assert isinstance(vars_dict[0], dict)

    def test_cleanup_solution(self, q3dtest):
        assert q3dtest.cleanup_solution()

    def test_cleanup_solution_1(self, field_test):
        setup = field_test.existing_analysis_sweeps
        variations = field_test.available_variations._get_variation_strings(setup[0])
        assert field_test.cleanup_solution(variations, entire_solution=False)
        assert field_test.cleanup_solution(variations, entire_solution=True)

    def test_ipk_get_scalar_field_value(self, icepak_post):
        assert icepak_post.post.get_scalar_field_value(
            "Heat_Flow_Rate",
            scalar_function="Integrate",
            solution=None,
            variations={"power_block": "0.25W", "power_source": "0.075W"},
            is_vector=False,
            intrinsics=None,
            phase=None,
            object_name="cube2",
            object_type="surface",
            adjacent_side=False,
        )

    def test_ipk_get_scalar_field_value_1(self, icepak_post):
        assert icepak_post.post.get_scalar_field_value(
            "Heat_Flow_Rate",
            scalar_function="Integrate",
            solution=None,
            variations={"power_block": "0.6W", "power_source": "0.15W"},
            is_vector=False,
            intrinsics=None,
            phase=None,
            object_name="cube2",
            object_type="surface",
            adjacent_side=False,
        )

    def test_ipk_get_scalar_field_value_2(self, icepak_post):
        assert icepak_post.post.get_scalar_field_value(
            "Heat_Flow_Rate",
            scalar_function="Integrate",
            solution=None,
            variations={"power_block": "0.6W", "power_source": "0.15W"},
            is_vector=False,
            intrinsics=None,
            phase=None,
            object_name="cube2",
            object_type="surface",
            adjacent_side=True,
        )

    def test_ipk_get_scalar_field_valu_3(self, icepak_post):
        assert icepak_post.post.get_scalar_field_value(
            "Temperature",
            scalar_function="Maximum",
            solution=None,
            variations={"power_block": "0.6W", "power_source": "0.15W"},
            is_vector=False,
            intrinsics=None,
            phase=None,
            object_name="cube1",
            object_type="volume",
            adjacent_side=False,
        )

    def test_ipk_get_scalar_field_value_4(self, icepak_post):
        assert icepak_post.post.get_scalar_field_value(
            "Temperature",
            scalar_function="Maximum",
            solution=None,
            variations={"power_block": "0.6W", "power_source": "0.15W"},
            is_vector=False,
            intrinsics=None,
            phase=None,
            object_name="cube2",
            object_type="surface",
            adjacent_side=False,
        )

    def test_ipk_get_scalar_field_value_5(self, icepak_post):
        assert icepak_post.post.get_scalar_field_value(
            "Temperature",
            scalar_function="Value",
            solution=None,
            variations=None,
            is_vector=False,
            intrinsics=None,
            phase=None,
            object_name="Point1",
            object_type="point",
            adjacent_side=False,
        )

    @pytest.mark.skipif(config["NonGraphical"], reason="Method does not work in non-graphical mode.")
    def test_markers(self, markers_test):
        f1 = markers_test.modeler["Region"].top_face_z
        p1 = markers_test.post.create_fieldplot_surface(f1.id, "Uz")
        f1_c = f1.center
        f1_p1 = [f1_c[0] + 0.01, f1_c[1] + 0.01, f1_c[2]]
        f1_p2 = [f1_c[0] - 0.01, f1_c[1] - 0.01, f1_c[2]]
        d1 = p1.get_points_value([f1_c, f1_p1, f1_p2])
        assert isinstance(d1, pd.DataFrame)
        assert d1.index.name == "Name"
        assert all(d1.index.values == ["m1", "m2", "m3"])
        assert len(d1["X [mm]"].values) == 3
        assert len(d1.columns) == 4

        f2 = markers_test.modeler["Box1"].top_face_z
        p2 = markers_test.post.create_fieldplot_surface(f2.id, "Pressure")
        d2 = p2.get_points_value({"Center Point": f2.center})
        assert isinstance(d2, pd.DataFrame)
        assert d2.index.name == "Name"
        assert all(d2.index.values == ["Center Point"])
        assert len(d2.columns) == 4
        assert len(d2["X [mm]"].values) == 1

        f3 = markers_test.modeler["Box1"].bottom_face_y
        p3 = markers_test.post.create_fieldplot_surface(f3.id, "Temperature")
        d3 = p3.get_points_value(f3.center)
        assert isinstance(d3, pd.DataFrame)
        assert d3.index.name == "Name"
        assert all(d3.index.values == ["m1"])
        assert len(d3.columns) == 4
        assert len(d3["X [mm]"].values) == 1

        f4 = markers_test.modeler["Box1"].top_face_x
        p4 = markers_test.post.create_fieldplot_surface(f4.id, "HeatFlowRate")
        temp_file = tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".csv")
        temp_file.close()
        d4 = p4.get_points_value(f4.center, filename=temp_file.name)
        assert isinstance(d4, pd.DataFrame)
        os.path.exists(temp_file.name)

    def test_m3d_get_solution_data_reduced_matrix(self, m3d_app):
        expressions = m3d_app.post.available_report_quantities(
            report_category="EddyCurrent", display_type="Data Table", context={"Matrix1": "ReducedMatrix1"}
        )
        data = m3d_app.post.get_solution_data(expressions=expressions, context={"Matrix1": "ReducedMatrix1"})
        assert data

    def test_m3d_available_report_quantities(self, m3d_app):
        expressions = m3d_app.post.available_report_quantities(report_category="EddyCurrent", display_type="Data Table")
        assert isinstance(expressions, list)

    def test_m3d_get_solution_data_matrix(self, m3d_app):
        expressions = m3d_app.post.available_report_quantities(
            report_category="EddyCurrent", display_type="Data Table", context="Matrix1"
        )
        data = m3d_app.post.get_solution_data(expressions=expressions, context="Matrix1")
        assert data
