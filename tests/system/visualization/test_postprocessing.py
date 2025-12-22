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

import pandas as pd
import pytest

from ansys.aedt.core import Circuit
from ansys.aedt.core import Icepak
from ansys.aedt.core import Maxwell2d
from ansys.aedt.core import Maxwell3d
from ansys.aedt.core import Q2d
from ansys.aedt.core import Q3d
from ansys.aedt.core import TwinBuilder
from ansys.aedt.core.generic.general_methods import is_linux
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.visualization.plot.pyvista import _parse_aedtplt
from ansys.aedt.core.visualization.plot.pyvista import _parse_streamline
from tests import TESTS_VISUALIZATION_PATH
from tests.conftest import DESKTOP_VERSION
from tests.conftest import NON_GRAPHICAL

TEST_FIELD_NAME = "Potter_Horn_242"
Q3D_FILE = "via_gsg_solved"
TEST_CIRCUIT_NAME = "Switching_Speed_FET_And_Diode_Solved"
SBR_FILE = "poc_scat_small_solved"
EYE_DIAGRAM = "channel_solved"
AMI = "ami"
M2D_FILE = "m2d"
M3D_FILE = "m3d"
TEST_EMI_NAME = "EMI_RCV_251"
IPK_POST_PROJ = "for_icepak_post_parasolid"
IPK_MARKERS_PROJ = "ipk_markers"
TB_SPECTRAL = "TB_excitation_model"

TEST_SUBFOLDER = "T12"


@pytest.fixture
def markers_test(add_app_example):
    app = add_app_example(project=IPK_MARKERS_PROJ, application=Icepak, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(save=False)


@pytest.fixture
def field_test(add_app_example):
    app = add_app_example(project=TEST_FIELD_NAME, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(save=False)


@pytest.fixture()
def circuit_test(add_app_example):
    app = add_app_example(project=TEST_CIRCUIT_NAME, design="Diode", application=Circuit, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(save=False)


@pytest.fixture()
def emi_receiver_test(add_app_example):
    app = add_app_example(project=TEST_EMI_NAME, design="CE_band", application=Circuit, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(save=False)


@pytest.fixture
def diff_test(add_app_example):
    app = add_app_example(project=TEST_CIRCUIT_NAME, design="diff", application=Circuit, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(save=False)


@pytest.fixture
def sbr_test(add_app_example):
    app = add_app_example(project=SBR_FILE, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(save=False)


@pytest.fixture()
def q3dtest(add_app_example):
    app = add_app_example(project=Q3D_FILE, application=Q3d, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(save=False)


@pytest.fixture()
def q2dtest(add_app_example):
    app = add_app_example(project=Q3D_FILE, application=Q2d, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(save=False)


@pytest.fixture()
def eye_test(add_app_example):
    app = add_app_example(project=EYE_DIAGRAM, application=Circuit, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(save=False)


@pytest.fixture()
def icepak_post(add_app_example):
    app = add_app_example(project=IPK_POST_PROJ, application=Icepak, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(save=False)


@pytest.fixture()
def ami_test(add_app_example):
    app = add_app_example(project=AMI, application=Circuit, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(save=False)


@pytest.fixture()
def m2dtest(add_app_example):
    app = add_app_example(project=M2D_FILE, application=Maxwell2d, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(save=False)


@pytest.fixture()
def m3d_app(add_app_example):
    app = add_app_example(project=M3D_FILE, application=Maxwell3d, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(save=False)


@pytest.fixture()
def tb_app(add_app_example):
    app = add_app_example(project=TB_SPECTRAL, application=TwinBuilder, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(save=False)


def test_circuit_export_results(circuit_test):
    files = circuit_test.export_results()
    assert len(files) > 0


def test_q2d_export_results(q2dtest):
    files = q2dtest.export_results()
    assert len(files) > 0


def test_q3d_export_results(q3dtest):
    files = q3dtest.export_results()
    assert len(files) > 0


def test_m3d_export_results(m3d_app):
    files = m3d_app.export_results()
    assert len(files) > 0


def test_m2d_export_results(m2dtest):
    files = m2dtest.export_results()
    assert len(files) > 0


def test_circuit_create_report(circuit_test):
    assert circuit_test.setups[0].create_report(["dB(S(Port1, Port1))", "dB(S(Port1, Port2))"])


def test_circuit_reports_by_category_standard(circuit_test):
    new_report = circuit_test.post.reports_by_category.standard(["dB(S(Port1, Port1))", "dB(S(Port1, Port2))"], "LNA")
    assert new_report.create()


def test_circuit_reports_by_category_standard_1(diff_test):
    new_report1 = diff_test.post.reports_by_category.standard()
    assert new_report1.expressions


def test_circuit_reports_by_category_standard_3(diff_test):
    new_report = diff_test.post.reports_by_category.standard("dB(S(1,1))")
    new_report.differential_pairs = True
    assert new_report.create()
    assert new_report.get_solution_data()


def test_circuit_reports_by_category_standard_4(diff_test):
    new_report2 = diff_test.post.reports_by_category.standard("TDRZ(1)")
    new_report2.differential_pairs = True
    new_report2.pulse_rise_time = 3e-12
    new_report2.maximum_time = 30e-12
    new_report2.step_time = 6e-13
    new_report2.time_windowing = 3
    new_report2.domain = "Time"
    assert new_report2.create()


def test_circuit_get_solution_data(circuit_test):
    data = circuit_test.post.get_solution_data(["dB(S(Port1,Port1))", "dB(S(Port1,Port2))"], "LNA")
    assert data.primary_sweep == "Freq"


def test_circuit_create_report_1(circuit_test):
    plot = circuit_test.post.create_report(["V(net_11)"], "Transient", "Time")
    assert plot


def test_circuit_create_report_from_configuration(circuit_test, test_tmp_dir):
    plot = circuit_test.post.create_report(["V(net_11)"], "Transient", "Time")
    assert plot.export_config(str(test_tmp_dir / f"{plot.plot_name}.json"))
    assert circuit_test.post.create_report_from_configuration(
        str(test_tmp_dir / f"{plot.plot_name}.json"), solution_name="Transient"
    )


def test_circuit_get_solution_data_1(circuit_test):
    data11 = circuit_test.post.get_solution_data(setup_sweep_name="LNA", math_formula="dB")
    assert data11.primary_sweep == "Freq"
    assert "dB(S(Port2,Port1))" in data11.expressions


def test_circuit_get_solution_data_2(circuit_test):
    data2 = circuit_test.post.get_solution_data(["V(net_11)"], "Transient", "Time")
    assert data2.primary_sweep == "Time"
    assert len(data2.get_expression_data(formula="magnitude", sweeps=["Time"])[1]) > 0


def test_circuit_get_solution_data_3(circuit_test):
    context = {"algorithm": "FFT", "max_frequency": "100MHz", "time_stop": "200ns", "test": ""}
    data3 = circuit_test.post.get_solution_data(["V(net_11)"], "Transient", "Spectral", context=context)
    assert data3.units_sweeps["Spectrum"] == circuit_test.units.frequency
    assert len(data3.get_expression_data()[1]) > 0


def test_reports_by_category_standard_1(circuit_test):
    circuit_test.post.create_report(["V(net_11)"], "Transient", "Time")
    new_report = circuit_test.post.reports_by_category.standard(["V(net_11)"], "Transient")
    new_report.domain = "Time"
    assert new_report.create()


def test_reports_by_category_spectral(circuit_test):
    new_report = circuit_test.post.reports_by_category.spectral(["dB(V(net_11))"], "Transient")
    new_report.window = "Hanning"
    new_report.max_freq = "1GHz"
    new_report.time_start = "1ns"
    new_report.time_stop = "190ns"
    new_report.plot_continous_spectrum = True
    assert new_report.create()


def test_reports_by_category_spectral_2(circuit_test):
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


def test_reports_by_category_spectral_3(circuit_test):
    new_report = circuit_test.post.reports_by_category.spectral(None, "Transient")
    new_report.window = "Hanning"
    new_report.max_freq = "1GHz"
    new_report.time_start = "1ns"
    new_report.time_stop = "190ns"
    new_report.plot_continous_spectrum = True
    assert new_report.create()


def test_create_report_spectrum(circuit_test):
    assert circuit_test.post.create_report(
        ["dB(V(net_11))", "dB(V(Port1))"], setup_sweep_name="Transient", domain="Spectrum"
    )


def test_circuit_available_display_types(diff_test):
    assert len(diff_test.post.available_display_types()) > 0


def test_circuit_available_report_quantities(diff_test):
    assert len(diff_test.post.available_report_quantities()) > 0


def test_circuit_available_report_solutions(diff_test):
    assert len(diff_test.post.available_report_solutions()) > 0


def test_circuit_create_report_2(diff_test):
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


def test_sbr_get_solution_data(sbr_test):
    assert sbr_test.setups[0].is_solved
    solution_data = sbr_test.post.get_solution_data(
        expressions=["NearEX", "NearEY", "NearEZ"], report_category="Near Fields", context="Near_Field"
    )
    assert solution_data
    assert len(solution_data.primary_sweep_values) > 0
    assert solution_data.set_active_variation(0)
    assert not solution_data.set_active_variation(99)


def test_sbr_solution_data_ifft(sbr_test, test_tmp_dir):
    solution_data = sbr_test.post.get_solution_data(
        expressions=["NearEX", "NearEY", "NearEZ"], report_category="Near Fields", context="Near_Field"
    )
    t_matrix = solution_data.ifft("NearE", window=True)
    assert t_matrix.any()
    frames_list = solution_data.ifft_to_file(coord_system_center=[-0.15, 0, 0], db_val=True, csv_path=str(test_tmp_dir))
    assert Path(frames_list).exists()
    solution_data2 = sbr_test.post.get_solution_data(expressions=["NearEX", "NearEY", "NearEZ"])
    assert solution_data2


@pytest.mark.avoid_ansys_load
def test_sbr_plot_scene(sbr_test):
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


def test_q3d_export_convergence(q3dtest):
    assert os.path.exists(q3dtest.export_convergence("Setup1"))


def test_q3d_export_profile(q3dtest):
    assert Path(q3dtest.export_profile("Setup1")).exists()


def test_q3d_reports_by_category_standard(q3dtest):
    new_report = q3dtest.post.reports_by_category.standard(q3dtest.get_traces_for_plot())
    assert new_report.create()


def test_q3d_reports_by_category_cg_fields(q3dtest):
    q3dtest.modeler.create_polyline([[0, -5, 0.425], [0.5, 5, 0.5]], name="Poly1", non_model=True)
    new_report = q3dtest.post.reports_by_category.cg_fields("SmoothQ", polyline="Poly1")
    assert new_report.create()


def test_q3d_reports_by_category_rl_fields(q3dtest):
    q3dtest.modeler.create_polyline([[0, -5, 0.425], [0.5, 5, 0.5]], name="Poly1", non_model=True)
    new_report = q3dtest.post.reports_by_category.rl_fields("Mag_SurfaceJac", polyline="Poly1")
    assert new_report.create()


def test_q3d_reports_by_category_dc_fields(q3dtest):
    q3dtest.modeler.create_polyline([[0, -5, 0.425], [0.5, 5, 0.5]], name="Poly1", non_model=True)
    new_report = q3dtest.post.reports_by_category.dc_fields("Mag_VolumeJdc", polyline="Poly1")
    assert new_report.create()


def test_q2d_export_convergence(q2dtest):
    assert os.path.exists(q2dtest.export_convergence("Setup1"))


def test_q2d_export_profile(q2dtest):
    assert Path(q2dtest.export_profile("Setup1")).exists()


def test_q2d_reports_by_category_standard(q2dtest):
    new_report = q2dtest.post.reports_by_category.standard(q2dtest.get_traces_for_plot())
    assert new_report.create()


def test_q2d_reports_by_category_cg_fields(q2dtest):
    q2dtest.modeler.create_polyline([[-1.9, -0.1, 0], [-1.2, -0.2, 0]], name="Poly1", non_model=True)
    new_report = q2dtest.post.reports_by_category.cg_fields("Mag_E", polyline="Poly1")
    assert new_report.create()


def test_q2d_reports_by_category_rl_fields(q2dtest):
    q2dtest.modeler.create_polyline([[-1.9, -0.1, 0], [-1.2, -0.2, 0]], name="Poly1", non_model=True)
    new_report = q2dtest.post.reports_by_category.rl_fields("Mag_H", polyline="Poly1")
    assert new_report.create()


def test_q2d_reports_by_category_standard_2(q2dtest):
    q2dtest.modeler.create_polyline([[-1.9, -0.1, 0], [-1.2, -0.2, 0]], name="Poly1", non_model=True)
    new_report = q2dtest.post.reports_by_category.rl_fields("Mag_H", polyline="Poly1")
    sol = new_report.get_solution_data()
    sol.enable_pandas_output = True
    assert sol.get_expression_data(formula="magnitude", convert_to_SI=True, use_quantity=True)
    sol.enable_pandas_output = False
    new_report = q2dtest.post.reports_by_category.standard()
    assert new_report.get_solution_data()


def test_q3dtest_no_report(q3dtest):
    assert not q3dtest.post.reports_by_category.modal_solution()
    assert not q3dtest.post.reports_by_category.terminal_solution()


def test_q2dtest_no_report(q2dtest):
    assert not q2dtest.post.reports_by_category.far_field()
    assert not q2dtest.post.reports_by_category.near_field()
    assert not q2dtest.post.reports_by_category.eigenmode()


def test_parse_vector_aedtplt():
    out = _parse_aedtplt(
        os.path.join(TESTS_VISUALIZATION_PATH, "example_models", TEST_SUBFOLDER, "test_vector.aedtplt")
    )
    assert isinstance(out[0], list)
    assert isinstance(out[1], list)
    assert isinstance(out[2], list)
    assert isinstance(out[3], bool)
    assert _parse_aedtplt(
        os.path.join(TESTS_VISUALIZATION_PATH, "example_models", TEST_SUBFOLDER, "test_vector_no_solutions.aedtplt")
    )


def test_parse_vector():
    out = _parse_streamline(
        os.path.join(TESTS_VISUALIZATION_PATH, "example_models", TEST_SUBFOLDER, "test_streamline.fldplt")
    )
    assert isinstance(out, list)


def test_export_mesh(q3dtest):
    assert Path(q3dtest.export_mesh_stats("Setup1")).exists()
    assert Path(q3dtest.export_mesh_stats("Setup1")).exists()


def test_eye_diagram(eye_test):
    rep = eye_test.post.reports_by_category.eye_diagram("AEYEPROBE(OutputEye)", "QuickEyeAnalysis")
    rep.time_start = "0ps"
    rep.time_stop = "50us"
    rep.unit_interval = "1e-9"
    assert rep.create()


@pytest.mark.skipif(DESKTOP_VERSION < "2022.2", reason="Not working in non graphical in version lower than 2022.2")
def test_mask(eye_test):
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


@pytest.mark.skipif(DESKTOP_VERSION < "2022.2", reason="Not working in non graphical in version lower than 2022.2")
def test_eye_measurements(eye_test):
    rep = eye_test.post.reports_by_category.eye_diagram("AEYEPROBE(OutputEye)", "QuickEyeAnalysis")
    rep.time_start = "0ps"
    rep.time_stop = "50us"
    rep.unit_interval = "1e-9"
    rep.create()
    assert rep.add_all_eye_measurements()
    assert rep.clear_all_eye_measurements()
    assert rep.add_trace_characteristics("MinEyeHeight")


def test_eye_from_json_simple(eye_test):
    assert eye_test.post.create_report_from_configuration(
        os.path.join(TESTS_VISUALIZATION_PATH, "example_models", "report_json", "EyeDiagram_Report_simple.json"),
        solution_name="QuickEyeAnalysis",
    )


def test_spectral_from_json_simple(circuit_test):
    assert circuit_test.post.create_report_from_configuration(
        os.path.join(TESTS_VISUALIZATION_PATH, "example_models", "report_json", "Spectral_Report_Simple.json"),
        solution_name="Transient",
    )


@pytest.mark.skipif(DESKTOP_VERSION < "2022.2", reason="Not working in non graphical in version lower than 2022.2")
def test_eye_from_json(eye_test):
    assert eye_test.post.create_report_from_configuration(
        os.path.join(TESTS_VISUALIZATION_PATH, "example_models", "report_json", "EyeDiagram_Report.toml"),
        solution_name="QuickEyeAnalysis",
    )


@pytest.mark.skipif(DESKTOP_VERSION < "2022.2", reason="Not working in non graphical in version lower than 2022.2")
def test_spectral_from_json(circuit_test):
    assert circuit_test.post.create_report_from_configuration(
        os.path.join(TESTS_VISUALIZATION_PATH, "example_models", "report_json", "Spectral_Report.json"),
        solution_name="Transient",
    )


def test_ami_solution_data(ami_test):
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


def test_ami_sample_ami_waveform(ami_test):
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


def test_m2d_plot_field_line_traces(m2dtest):
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
    with pytest.raises(AEDTRuntimeError):
        m2dtest.post.create_fieldplot_line_traces(
            ["Ground", "Electrode"], "Region", ["Invalid"], plot_name="LineTracesTest7"
        )
    with pytest.raises(AEDTRuntimeError):
        m2dtest.post.create_fieldplot_line_traces("Invalid", "Region", plot_name="LineTracesTest8")
    with pytest.raises(AEDTRuntimeError):
        m2dtest.post.create_fieldplot_line_traces(["Ground", "Electrode"], ["Invalid"], plot_name="LineTracesTest9")
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


@pytest.mark.skipif(DESKTOP_VERSION < "2024.1", reason="EMI receiver available from 2024R1.")
def test_emi_receiver(emi_receiver_test):
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


def test_cleanup_solution(q3dtest):
    assert q3dtest.cleanup_solution()


def test_ipk_get_scalar_field_value(icepak_post):
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


def test_ipk_get_scalar_field_value_1(icepak_post):
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


def test_ipk_get_scalar_field_value_2(icepak_post):
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


def test_ipk_get_scalar_field_valu_3(icepak_post):
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


def test_ipk_get_scalar_field_value_4(icepak_post):
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


def test_ipk_get_scalar_field_value_5(icepak_post):
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


@pytest.mark.skipif(NON_GRAPHICAL, reason="Method does not work in non-graphical mode.")
def test_markers(markers_test):
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


def test_m3d_get_solution_data_reduced_matrix(m3d_app):
    expressions = m3d_app.post.available_report_quantities(
        report_category="EddyCurrent", display_type="Data Table", context={"Matrix1": "ReducedMatrix1"}
    )
    data = m3d_app.post.get_solution_data(expressions=expressions, context={"Matrix1": "ReducedMatrix1"})
    assert data


def test_m3d_available_report_quantities(m3d_app):
    expressions = m3d_app.post.available_report_quantities(report_category="EddyCurrent", display_type="Data Table")
    assert isinstance(expressions, list)


def test_m3d_get_solution_data_matrix(m3d_app):
    expressions = m3d_app.post.available_report_quantities(
        report_category="EddyCurrent", display_type="Data Table", context="Matrix1"
    )
    data = m3d_app.post.get_solution_data(expressions=expressions, context="Matrix1")
    assert data


@pytest.mark.skipif(is_linux, reason="Twinbuilder is only available in Windows OS.")
def test_twinbuilder_spectral(tb_app):
    assert tb_app.post.create_report(
        expressions="mag(E1.I)", primary_sweep_variable="Spectrum", plot_name="Spectral domain", domain="Spectral"
    )
    new_report = tb_app.post.reports_by_category.spectral("mag(E1.I)", "TR")
    new_report.window = "Rectangular"
    new_report.max_frequency = "2.5MHz"
    new_report.time_start = "0ns"
    new_report.time_stop = "40ms"
    assert new_report.create()


@pytest.mark.skipif(DESKTOP_VERSION < "2026.1", reason="Method not available before 2026.1")
def test_m2d_evaluate_inception_voltage(m2dtest):
    m2dtest.set_active_design("field_line_trace")
    with pytest.raises(AEDTRuntimeError):
        m2dtest.post.evaluate_inception_voltage("my_plot", [1, 2, 4])
    plot = m2dtest.post.create_fieldplot_line_traces(["Ground", "Electrode"], "Region")
    assert m2dtest.post.evaluate_inception_voltage(plot.name)
    assert m2dtest.post.evaluate_inception_voltage(plot.name, [1, 2, 4])
    m2dtest.solution_type = "Magnetostatic"
    with pytest.raises(AEDTRuntimeError):
        m2dtest.post.evaluate_inception_voltage("my_plot", [1, 2, 4])


@pytest.mark.skipif(DESKTOP_VERSION < "2026.1", reason="Method not available before 2026.1")
def test_m2d_export_inception_voltage(m2dtest):
    m2dtest.set_active_design("field_line_trace")
    file_path = str(Path(m2dtest.working_directory, "my_file.txt"))
    with pytest.raises(AEDTRuntimeError):
        m2dtest.post.export_inception_voltage("my_plot", file_path, [1, 2, 4])
    plot = m2dtest.post.create_fieldplot_line_traces(["Ground", "Electrode"], "Region", plot_name="my_plot")
    m2dtest.post.evaluate_inception_voltage("my_plot", [1, 2, 4])
    assert m2dtest.post.export_inception_voltage(plot.name, file_path)
    assert m2dtest.post.export_inception_voltage(
        plot.name, str(Path(m2dtest.working_directory, "my_file.txt")), [1, 2, 4]
    )
    m2dtest.solution_type = "Magnetostatic"
    with pytest.raises(AEDTRuntimeError):
        m2dtest.post.export_inception_voltage("my_plot", file_path, [1, 2, 4])
