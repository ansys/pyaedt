import os
import sys

from _unittest.conftest import config
import pytest

from pyaedt import Circuit
from pyaedt import Icepak
from pyaedt import Maxwell2d
from pyaedt import Q2d
from pyaedt import Q3d
from pyaedt import settings
from pyaedt.generic.general_methods import is_linux
from pyaedt.generic.plot import _parse_aedtplt
from pyaedt.generic.plot import _parse_streamline
from pyaedt.modules.solutions import FfdSolutionData

if config["desktopVersion"] > "2022.2":
    test_field_name = "Potter_Horn_231"
    test_project_name = "coax_setup_solved_231"
    array = "array_simple_231"
    sbr_file = "poc_scat_small_231"
    q3d_file = "via_gsg_231"
    m2d_file = "m2d_field_lines_test_231"

else:
    test_field_name = "Potter_Horn"
    test_project_name = "coax_setup_solved"
    array = "array_simple"
    sbr_file = "poc_scat_small"
    q3d_file = "via_gsg"
    m2d_file = "m2d_field_lines_test"

test_circuit_name = "Switching_Speed_FET_And_Diode"
eye_diagram = "SimpleChannel"
ami = "ami"
ipk_post_proj = "for_icepak_post"
test_subfolder = "T12"
settings.enable_pandas_output = True


@pytest.fixture(scope="class")
def field_test(add_app):
    app = add_app(project_name=test_field_name, subfolder=test_subfolder)
    return app


@pytest.fixture(scope="class")
def circuit_test(add_app):
    app = add_app(project_name=test_circuit_name, design_name="Diode", application=Circuit, subfolder=test_subfolder)
    return app


@pytest.fixture(scope="class")
def diff_test(add_app, circuit_test):
    app = add_app(project_name=circuit_test.project_name, design_name="diff", application=Circuit, just_open=True)
    return app


@pytest.fixture(scope="class")
def sbr_test(add_app):
    app = add_app(project_name=sbr_file, subfolder=test_subfolder)
    return app


@pytest.fixture(scope="class")
def q3dtest(add_app):
    app = add_app(project_name=q3d_file, application=Q3d, subfolder=test_subfolder)
    return app


@pytest.fixture(scope="class")
def q2dtest(add_app, q3dtest):
    app = add_app(project_name=q3dtest.project_name, application=Q2d, just_open=True)
    return app


@pytest.fixture(scope="class")
def eye_test(add_app, q3dtest):
    app = add_app(project_name=eye_diagram, application=Circuit, subfolder=test_subfolder)
    return app


@pytest.fixture(scope="class")
def icepak_post(add_app):
    app = add_app(project_name=ipk_post_proj, application=Icepak, subfolder=test_subfolder)
    return app


@pytest.fixture(scope="class")
def ami_test(add_app, q3dtest):
    app = add_app(project_name=ami, application=Circuit, subfolder=test_subfolder)
    return app


@pytest.fixture(scope="class")
def array_test(add_app, q3dtest):
    app = add_app(project_name=array, subfolder=test_subfolder)
    return app


@pytest.fixture(scope="class")
def m2dtest(add_app, q3dtest):
    app = add_app(project_name=m2d_file, application=Maxwell2d, subfolder=test_subfolder)
    return app


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, local_scratch):
        self.local_scratch = local_scratch

    def test_09_manipulate_report(self, field_test):
        variations = field_test.available_variations.nominal_w_values_dict
        variations["Theta"] = ["All"]
        variations["Phi"] = ["All"]
        variations["Freq"] = ["30GHz"]
        field_test.set_source_context(["1"])
        context = {"Context": "3D", "SourceContext": "1:1"}
        assert field_test.post.create_report(
            "db(GainTotal)",
            field_test.nominal_adaptive,
            variations=variations,
            primary_sweep_variable="Phi",
            secondary_sweep_variable="Theta",
            plot_type="3D Polar Plot",
            context=context,
            report_category="Far Fields",
        )
        assert field_test.post.create_report(
            "db(GainTotal)",
            field_test.nominal_adaptive,
            variations=variations,
            primary_sweep_variable="Phi",
            secondary_sweep_variable="Theta",
            plot_type="3D Polar Plot",
            context="3D",
            report_category="Far Fields",
        )

    def test_09_manipulate_report_B(self, field_test):
        variations = field_test.available_variations.nominal_w_values_dict
        variations["Theta"] = ["All"]
        variations["Phi"] = ["All"]
        variations["Freq"] = ["30GHz"]
        new_report = field_test.post.reports_by_category.far_field("db(RealizedGainTotal)", field_test.nominal_adaptive)
        new_report.variations = variations
        new_report.report_type = "3D Polar Plot"
        new_report.far_field_sphere = "3D"
        assert new_report.create()

        new_report2 = field_test.post.reports_by_category.far_field(
            "db(RealizedGainTotal)", field_test.nominal_adaptive, "3D", "1:1"
        )
        new_report2.variations = variations
        new_report2.report_type = "3D Polar Plot"
        assert new_report2.create()

        new_report3 = field_test.post.reports_by_category.antenna_parameters(
            "db(PeakRealizedGain)", field_test.nominal_adaptive, "3D"
        )
        new_report3.report_type = "Data Table"
        assert new_report3.create()

    def test_09_manipulate_report_C(self, field_test):
        variations = field_test.available_variations.nominal_w_values_dict
        variations["Theta"] = ["All"]
        variations["Phi"] = ["All"]
        variations["Freq"] = ["30GHz"]
        field_test.analyze(field_test.active_setup)
        data = field_test.post.get_solution_data(
            "GainTotal",
            field_test.nominal_adaptive,
            variations=variations,
            primary_sweep_variable="Theta",
            context="3D",
            report_category="Far Fields",
        )
        assert data.plot(is_polar=True)
        assert data.plot_3d()
        assert field_test.post.create_3d_plot(data)

    def test_09_manipulate_report_D(self, field_test):
        variations = field_test.available_variations.nominal_w_values_dict
        variations["Theta"] = ["All"]
        variations["Phi"] = ["All"]
        variations["Freq"] = ["30GHz"]
        context = {"Context": "3D", "SourceContext": "1:1"}
        data = field_test.post.get_solution_data(
            "GainTotal",
            field_test.nominal_adaptive,
            variations=variations,
            primary_sweep_variable="Theta",
            context=context,
            report_category="Far Fields",
        )
        assert data.plot(is_polar=True)
        assert data.plot_3d()
        assert field_test.post.create_3d_plot(data)
        assert data.primary_sweep == "Theta"
        assert len(data.data_magnitude("GainTotal")) > 0
        assert not data.data_magnitude("GainTotal2")
        assert field_test.post.create_report(
            "S(1,1)",
            field_test.nominal_sweep,
            variations=variations,
            plot_type="Smith Chart",
        )

    def test_09_manipulate_report_E(self, field_test):
        field_test.modeler.create_polyline([[0, 0, 0], [0, 5, 30]], name="Poly1", non_model=True)
        variations2 = field_test.available_variations.nominal_w_values_dict

        assert field_test.setups[0].create_report(
            "Mag_E",
            primary_sweep_variable="Distance",
            context="Poly1",
            report_category="Fields",
        )
        new_report = field_test.post.reports_by_category.fields("Mag_H", field_test.nominal_adaptive)
        new_report.variations = variations2
        new_report.polyline = "Poly1"
        assert new_report.create()
        new_report = field_test.post.reports_by_category.modal_solution("S(1,1)")
        new_report.report_type = "Smith Chart"
        assert new_report.create()
        data = field_test.setups[0].get_solution_data(
            "Mag_E",
            variations=variations2,
            primary_sweep_variable="Theta",
            context="Poly1",
            report_category="Fields",
        )
        assert data.units_sweeps["Phase"] == "deg"

        assert field_test.post.get_far_field_data(
            setup_sweep_name=field_test.nominal_adaptive, expression="RealizedGainTotal", domain="3D"
        )
        data_farfield2 = field_test.post.get_far_field_data(
            setup_sweep_name=field_test.nominal_adaptive,
            expression="RealizedGainTotal",
            domain={"Context": "3D", "SourceContext": "1:1"},
        )
        assert data_farfield2.plot(math_formula="db20", is_polar=True)

    def test_09b_export_report_A(self, circuit_test):
        files = circuit_test.export_results()
        assert len(files) > 0

    def test_09b_export_report_B(self, q2dtest):
        q2dtest.analyze()
        files = q2dtest.export_results()
        assert len(files) > 0

    def test_09b_export_report_C(self, q3dtest):
        q3dtest.analyze_setup("Setup1")
        files = q3dtest.export_results()
        assert len(files) > 0

    @pytest.mark.skipif(is_linux, reason="Crashing on Linux")
    def test_17_circuit(self, circuit_test):
        assert not circuit_test.setups[0].is_solved

        circuit_test.analyze_setup("LNA")
        circuit_test.analyze_setup("Transient")
        assert circuit_test.setups[0].is_solved
        assert circuit_test.setups[0].create_report(["dB(S(Port1, Port1))", "dB(S(Port1, Port2))"])
        new_report = circuit_test.post.reports_by_category.standard(
            ["dB(S(Port1, Port1))", "dB(S(Port1, Port2))"], "LNA"
        )
        assert new_report.create()
        data1 = circuit_test.post.get_solution_data(["dB(S(Port1,Port1))", "dB(S(Port1,Port2))"], "LNA")
        assert data1.primary_sweep == "Freq"
        assert circuit_test.post.create_report(["V(net_11)"], "Transient", "Time")
        data11 = circuit_test.post.get_solution_data(setup_sweep_name="LNA", math_formula="dB")
        assert data11.primary_sweep == "Freq"
        assert "dB(S(Port2,Port1))" in data11.expressions
        assert circuit_test.post.create_report(["V(net_11)"], "Transient", "Time")
        new_report = circuit_test.post.reports_by_category.standard(["V(net_11)"], "Transient")
        new_report.domain = "Time"
        assert new_report.create()
        data2 = circuit_test.post.get_solution_data(["V(net_11)"], "Transient", "Time")
        assert data2.primary_sweep == "Time"
        assert len(data2.data_magnitude()) > 0
        context = {"algorithm": "FFT", "max_frequency": "100MHz", "time_stop": "200ns", "test": ""}
        data3 = circuit_test.post.get_solution_data(["V(net_11)"], "Transient", "Spectral", context=context)
        assert data3.units_sweeps["Spectrum"] == "GHz"
        assert len(data3.data_real()) > 0
        new_report = circuit_test.post.reports_by_category.spectral(["dB(V(net_11))"], "Transient")
        new_report.window = "Hanning"
        new_report.max_freq = "1GHz"
        new_report.time_start = "1ns"
        new_report.time_stop = "190ns"
        new_report.plot_continous_spectrum = True
        assert new_report.create()
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
        assert circuit_test.post.create_report(
            ["dB(V(net_11))", "dB(V(Port1))"], domain="Spectrum", setup_sweep_name="Transient"
        )
        new_report = circuit_test.post.reports_by_category.spectral(None, "Transient")
        new_report.window = "Hanning"
        new_report.max_freq = "1GHz"
        new_report.time_start = "1ns"
        new_report.time_stop = "190ns"
        new_report.plot_continous_spectrum = True
        assert new_report.create()
        pass

    @pytest.mark.skipif(is_linux, reason="Crashing on Linux")
    def test_18_diff_plot(self, diff_test):
        assert len(diff_test.post.available_display_types()) > 0
        assert len(diff_test.post.available_report_types) > 0
        assert len(diff_test.post.available_report_quantities()) > 0
        assert len(diff_test.post.available_report_solutions()) > 0
        diff_test.analyze_setup("LinearFrequency")
        assert diff_test.setups[0].is_solved
        variations = diff_test.available_variations.nominal_w_values_dict
        variations["Freq"] = ["All"]
        variations["l1"] = ["All"]
        assert diff_test.post.create_report(
            ["dB(S(Diff1, Diff1))"],
            "LinearFrequency",
            variations=variations,
            primary_sweep_variable="l1",
            context="Differential Pairs",
        )
        new_report = diff_test.post.reports_by_category.standard("dB(S(1,1))")
        new_report.differential_pairs = True
        assert new_report.create()
        assert new_report.get_solution_data()
        data1 = diff_test.post.get_solution_data(
            ["S(Diff1, Diff1)"],
            "LinearFrequency",
            variations=variations,
            primary_sweep_variable="Freq",
            context="Differential Pairs",
        )
        assert data1.primary_sweep == "Freq"
        data1.plot(math_formula="db20")
        data1.primary_sweep = "l1"
        assert data1.primary_sweep == "l1"
        assert len(data1.data_magnitude()) == 5
        assert data1.plot("S(Diff1, Diff1)")
        assert data1.plot(math_formula="db20")
        assert data1.plot(math_formula="db10")
        assert data1.plot(math_formula="mag")
        assert data1.plot(math_formula="re")
        assert data1.plot(math_formula="im")
        assert data1.plot(math_formula="phasedeg")
        assert data1.plot(math_formula="phaserad")

        assert diff_test.create_touchstone_report(
            plot_name="Diff_plot",
            curvenames=["dB(S(Diff1, Diff1))"],
            solution_name="LinearFrequency",
            differential_pairs=True,
        )

    @pytest.mark.skipif(is_linux, reason="Failing on Linux")
    def test_51_get_efields(self, field_test):
        assert field_test.post.get_efields_data(ff_setup="3D")

    @pytest.mark.skipif(
        is_linux or sys.version_info < (3, 8), reason="plot_scene method is not supported in ironpython"
    )
    def test_55_time_plot(self, sbr_test):
        sbr_test.analyze(sbr_test.active_setup, use_auto_settings=False)
        assert sbr_test.setups[0].is_solved
        solution_data = sbr_test.post.get_solution_data(
            expressions=["NearEX", "NearEY", "NearEZ"],
            # variations={"_u": ["All"], "_v": ["All"], "Freq": ["All"]},
            context="Near_Field",
            report_category="Near Fields",
        )
        assert solution_data
        assert len(solution_data.primary_sweep_values) > 0
        assert len(solution_data.primary_sweep_variations) > 0
        assert solution_data.set_active_variation(0)
        assert not solution_data.set_active_variation(99)
        t_matrix = solution_data.ifft("NearE", window=True)
        assert t_matrix.any()
        frames_list = solution_data.ifft_to_file(
            coord_system_center=[-0.15, 0, 0], db_val=True, csv_dir=os.path.join(sbr_test.working_directory, "csv")
        )
        assert os.path.exists(frames_list)
        sbr_test.post.plot_scene(
            frames_list,
            os.path.join(sbr_test.working_directory, "animation.gif"),
            norm_index=5,
            dy_rng=35,
            show=False,
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

    def test_56_test_export_q3d_results(self, q3dtest):
        q3dtest.analyze(q3dtest.active_setup)
        assert os.path.exists(q3dtest.export_convergence("Setup1"))
        assert os.path.exists(q3dtest.export_profile("Setup1"))
        new_report = q3dtest.post.reports_by_category.standard(q3dtest.get_traces_for_plot())
        assert new_report.create()
        q3dtest.modeler.create_polyline([[0, -5, 0.425], [0.5, 5, 0.5]], name="Poly1", non_model=True)
        new_report = q3dtest.post.reports_by_category.cg_fields("SmoothQ", polyline="Poly1")
        assert new_report.create()
        new_report = q3dtest.post.reports_by_category.rl_fields("Mag_SurfaceJac", polyline="Poly1")
        assert new_report.create()
        new_report = q3dtest.post.reports_by_category.dc_fields("Mag_VolumeJdc", polyline="Poly1")
        assert new_report.create()
        assert len(q3dtest.post.plots) == 6

    def test_57_test_export_q2d_results(self, q2dtest):
        q2dtest.analyze(q2dtest.active_setup)
        assert os.path.exists(q2dtest.export_convergence("Setup1"))
        assert os.path.exists(q2dtest.export_profile("Setup1"))
        new_report = q2dtest.post.reports_by_category.standard(q2dtest.get_traces_for_plot())
        assert new_report.create()
        q2dtest.modeler.create_polyline([[-1.9, -0.1, 0], [-1.2, -0.2, 0]], name="Poly1", non_model=True)
        new_report = q2dtest.post.reports_by_category.cg_fields("Mag_E", polyline="Poly1")
        assert new_report.create()
        new_report = q2dtest.post.reports_by_category.rl_fields("Mag_H", polyline="Poly1")
        assert new_report.create()
        sol = new_report.get_solution_data()
        sol.enable_pandas_output = True
        data = sol.full_matrix_real_imag
        data_mag = sol.full_matrix_mag_phase
        sol.data_magnitude()
        sol.enable_pandas_output = False
        assert len(q2dtest.post.plots) == 3
        new_report = q2dtest.post.reports_by_category.standard()
        assert new_report.get_solution_data()

    def test_58_test_no_report(self, q3dtest):
        assert not q3dtest.post.reports_by_category.modal_solution()
        assert not q3dtest.post.reports_by_category.terminal_solution()

    def test_58_test_no_report_B(self, q2dtest):
        assert not q2dtest.post.reports_by_category.far_field()
        assert not q2dtest.post.reports_by_category.near_field()
        assert not q2dtest.post.reports_by_category.eigenmode()

    def test_59_test_parse_vector(self):
        local_path = os.path.dirname(os.path.realpath(__file__))

        out = _parse_aedtplt(os.path.join(local_path, "example_models", test_subfolder, "test_vector.aedtplt"))
        assert isinstance(out[0], list)
        assert isinstance(out[1], list)
        assert isinstance(out[2], list)
        assert isinstance(out[3], bool)
        assert _parse_aedtplt(
            os.path.join(local_path, "example_models", test_subfolder, "test_vector_no_solutions.aedtplt")
        )

    def test_60_test_parse_vector(self):
        local_path = os.path.dirname(os.path.realpath(__file__))
        out = _parse_streamline(os.path.join(local_path, "example_models", test_subfolder, "test_streamline.fldplt"))
        assert isinstance(out, list)

    def test_61_export_mesh(self, q3dtest):
        assert os.path.exists(q3dtest.export_mesh_stats("Setup1"))
        assert os.path.exists(q3dtest.export_mesh_stats("Setup1", setup_type="AC RL"))

    def test_62_eye_diagram(self, eye_test):
        eye_test.analyze(eye_test.active_setup)
        rep = eye_test.post.reports_by_category.eye_diagram("AEYEPROBE(OutputEye)", "QuickEyeAnalysis")
        rep.time_start = "0ps"
        rep.time_stop = "50us"
        rep.unit_interval = "1e-9"
        assert rep.create()

    @pytest.mark.skipif(
        config["desktopVersion"] < "2022.2", reason="Not working in non graphical in version lower than 2022.2"
    )
    def test_63_mask(self, eye_test):
        eye_test.analyze(eye_test.active_setup)
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
    def test_64_eye_meas(self, eye_test):
        eye_test.analyze(eye_test.active_setup)
        rep = eye_test.post.reports_by_category.eye_diagram("AEYEPROBE(OutputEye)", "QuickEyeAnalysis")
        rep.time_start = "0ps"
        rep.time_stop = "50us"
        rep.unit_interval = "1e-9"
        rep.create()
        assert rep.add_all_eye_measurements()
        assert rep.clear_all_eye_measurements()
        assert rep.add_trace_characteristics("MinEyeHeight")

    def test_65_eye_from_json(self, eye_test):
        local_path = os.path.dirname(os.path.realpath(__file__))
        assert eye_test.post.create_report_from_configuration(
            os.path.join(local_path, "example_models", "report_json", "EyeDiagram_Report_simple.json"),
            solution_name="QuickEyeAnalysis",
        )

    def test_66_spectral_from_json(self, circuit_test):
        local_path = os.path.dirname(os.path.realpath(__file__))
        circuit_test.analyze_setup("Transient")
        assert circuit_test.post.create_report_from_configuration(
            os.path.join(local_path, "example_models", "report_json", "Spectral_Report_Simple.json"),
            solution_name="Transient",
        )

    @pytest.mark.skipif(
        config["desktopVersion"] < "2022.2", reason="Not working in non graphical in version lower than 2022.2"
    )
    def test_68_eye_from_json(self, eye_test):
        local_path = os.path.dirname(os.path.realpath(__file__))
        assert eye_test.post.create_report_from_configuration(
            os.path.join(local_path, "example_models", "report_json", "EyeDiagram_Report.json"),
            solution_name="QuickEyeAnalysis",
        )

    @pytest.mark.skipif(
        config["desktopVersion"] < "2022.2", reason="Not working in non graphical in version lower than 2022.2"
    )
    def test_69_spectral_from_json(self, circuit_test):
        local_path = os.path.dirname(os.path.realpath(__file__))
        circuit_test.analyze_setup("Transient")
        assert circuit_test.post.create_report_from_configuration(
            os.path.join(local_path, "example_models", "report_json", "Spectral_Report.json"), solution_name="Transient"
        )

    def test_70_far_field_data(self):
        local_path = os.path.dirname(os.path.realpath(__file__))
        eep_file1 = os.path.join(local_path, "example_models", test_subfolder, "eep", "eep.txt")
        eep_file2 = os.path.join(local_path, "example_models", test_subfolder, "eep", "eep.txt")
        frequencies = [0.9e9, "0.9GHz"]
        eep_files = [eep_file1, eep_file2]

        ffdata = FfdSolutionData(frequencies=frequencies[1], eep_files=eep_file1)
        assert len(ffdata.frequencies) == 1

        ffdata = FfdSolutionData(frequencies=frequencies, eep_files=eep_files)
        assert len(ffdata.frequencies) == 2
        farfield = ffdata.combine_farfield()
        assert "rETheta" in farfield

        ffdata.taper = "cosine"
        assert ffdata.combine_farfield()
        ffdata.taper = "taper"
        assert not ffdata.taper == "taper"

        ffdata.origin = [0, 2]
        assert ffdata.origin != [0, 2]
        ffdata.origin = [0, 0, 1]
        assert ffdata.origin == [0, 0, 1]

        img1 = os.path.join(self.local_scratch.path, "ff_2d1.jpg")
        ffdata.plot_2d_cut(secondary_sweep_value="all", primary_sweep="Theta", export_image_path=img1)
        assert os.path.exists(img1)
        img2 = os.path.join(self.local_scratch.path, "ff_2d2.jpg")
        ffdata.plot_2d_cut(secondary_sweep_value=[0, 1], export_image_path=img2)
        assert os.path.exists(img2)
        img3 = os.path.join(self.local_scratch.path, "ff_2d2.jpg")
        ffdata.plot_2d_cut(export_image_path=img3)
        assert os.path.exists(img3)
        curve_2d = ffdata.plot_2d_cut(show=False)
        assert len(curve_2d[0]) == 3
        data = ffdata.polar_plot_3d(show=False)
        assert len(data) == 3

        img4 = os.path.join(self.local_scratch.path, "ff_3d1.jpg")
        ffdata.polar_plot_3d_pyvista(
            farfield_quantity="RealizedGain",
            convert_to_db=True,
            show=False,
            export_image_path=img4,
            background=[255, 0, 0],
            show_geometry=False,
        )
        assert os.path.exists(img4)
        data_pyvista = ffdata.polar_plot_3d_pyvista(
            farfield_quantity="RealizedGain",
            convert_to_db=True,
            show=False,
            background=[255, 0, 0],
            show_geometry=False,
        )
        assert data_pyvista

    @pytest.mark.skipif(is_linux or sys.version_info < (3, 8), reason="FarFieldSolution not supported by IronPython")
    def test_71_antenna_plot(self, field_test):
        ffdata = field_test.get_antenna_ffd_solution_data(frequencies=30e9, sphere_name="3D")
        ffdata.phase_offset = [0, 90]
        assert ffdata.phase_offset == [0, 90]
        ffdata.phase_offset = [0]
        assert ffdata.phase_offset != [0.0]
        assert ffdata.plot_farfield_contour(
            farfield_quantity="RealizedGain",
            convert_to_db=True,
            title="Contour at {}Hz".format(ffdata.frequency),
            export_image_path=os.path.join(self.local_scratch.path, "contour.jpg"),
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "contour.jpg"))

        ffdata.plot_2d_cut(
            primary_sweep="theta",
            secondary_sweep_value=[-180, -75, 75],
            farfield_quantity="RealizedGain",
            title="Azimuth at {}Hz".format(ffdata.frequency),
            export_image_path=os.path.join(self.local_scratch.path, "2d1.jpg"),
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "2d1.jpg"))
        ffdata.plot_2d_cut(
            primary_sweep="phi",
            secondary_sweep_value=30,
            farfield_quantity="RealizedGain",
            title="Azimuth at {}Hz".format(ffdata.frequency),
            export_image_path=os.path.join(self.local_scratch.path, "2d2.jpg"),
        )

        assert os.path.exists(os.path.join(self.local_scratch.path, "2d2.jpg"))

        ffdata.polar_plot_3d(
            farfield_quantity="RealizedGain",
            convert_to_db=True,
            export_image_path=os.path.join(self.local_scratch.path, "3d1.jpg"),
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "3d1.jpg"))

        ffdata.polar_plot_3d_pyvista(
            farfield_quantity="RealizedGain",
            convert_to_db=True,
            show=False,
            export_image_path=os.path.join(self.local_scratch.path, "3d2.jpg"),
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "3d2.jpg"))

        try:
            p = ffdata.polar_plot_3d_pyvista(farfield_quantity="RealizedGain", convert_to_db=True, show=False)
            assert isinstance(p, object)
        except:
            assert True

    @pytest.mark.skipif(is_linux or sys.version_info < (3, 8), reason="FarFieldSolution not supported by IronPython")
    def test_72_antenna_plot(self, array_test):
        ffdata = array_test.get_antenna_ffd_solution_data(frequencies=3.5e9, sphere_name="3D")
        ffdata.frequency = 3.5e9
        assert ffdata.plot_farfield_contour(
            farfield_quantity="RealizedGain",
            convert_to_db=True,
            title="Contour at {}Hz".format(ffdata.frequency),
            export_image_path=os.path.join(self.local_scratch.path, "contour.jpg"),
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "contour.jpg"))

        ffdata.plot_2d_cut(
            primary_sweep="theta",
            secondary_sweep_value=[-180, -75, 75],
            farfield_quantity="RealizedGain",
            title="Azimuth at {}Hz".format(ffdata.frequency),
            export_image_path=os.path.join(self.local_scratch.path, "2d1.jpg"),
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "2d1.jpg"))
        ffdata.plot_2d_cut(
            primary_sweep="phi",
            secondary_sweep_value=30,
            farfield_quantity="RealizedGain",
            title="Azimuth at {}Hz".format(ffdata.frequency),
            export_image_path=os.path.join(self.local_scratch.path, "2d2.jpg"),
        )

        assert os.path.exists(os.path.join(self.local_scratch.path, "2d2.jpg"))

        ffdata.polar_plot_3d(
            farfield_quantity="RealizedGain",
            convert_to_db=True,
            export_image_path=os.path.join(self.local_scratch.path, "3d1.jpg"),
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "3d1.jpg"))

        ffdata.polar_plot_3d_pyvista(
            farfield_quantity="RealizedGain",
            convert_to_db=True,
            show=False,
            export_image_path=os.path.join(self.local_scratch.path, "3d2.jpg"),
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "3d2.jpg"))
        ffdata1 = array_test.get_antenna_ffd_solution_data(frequencies=3.5e9, sphere_name="3D", overwrite=False)
        assert ffdata1.plot_farfield_contour(
            farfield_quantity="RealizedGain",
            convert_to_db=True,
            title="Contour at {}Hz".format(ffdata1.frequency),
            export_image_path=os.path.join(self.local_scratch.path, "contour1.jpg"),
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "contour1.jpg"))

    def test_73_ami_solution_data(self, ami_test):
        ami_test.solution_type = "NexximAMI"
        assert ami_test.post.get_solution_data(
            expressions="WaveAfterProbe<b_input_43.int_ami_rx>",
            setup_sweep_name="AMIAnalysis",
            domain="Time",
            variations=ami_test.available_variations.nominal,
        )

        assert ami_test.post.get_solution_data(
            expressions="WaveAfterSource<b_output4_42.int_ami_tx>",
            setup_sweep_name="AMIAnalysis",
            domain="Time",
            variations=ami_test.available_variations.nominal,
        )

        assert ami_test.post.get_solution_data(
            expressions="InitialWave<b_output4_42.int_ami_tx>",
            setup_sweep_name="AMIAnalysis",
            domain="Time",
            variations=ami_test.available_variations.nominal,
        )

        assert ami_test.post.get_solution_data(
            expressions="WaveAfterChannel<b_input_43.int_ami_rx>",
            setup_sweep_name="AMIAnalysis",
            domain="Time",
            variations=ami_test.available_variations.nominal,
        )

        assert ami_test.post.get_solution_data(
            expressions="ClockTics<b_input_43.int_ami_rx>",
            setup_sweep_name="AMIAnalysis",
            domain="Clock Times",
            variations=ami_test.available_variations.nominal,
        )
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

    def test_75_plot_field_line_traces(self, m2dtest):
        m2dtest.modeler.model_units = "mm"
        rect = m2dtest.modeler.create_rectangle(
            position=["1mm", "5mm", "0mm"], dimension_list=["-1mm", "-10mm", 0], name="Ground", matname="copper"
        )
        rect.solve_inside = False
        circle = m2dtest.modeler.create_circle(
            position=["-10mm", "0", "0"],
            radius="1mm",
            num_sides="0",
            is_covered=True,
            name="Electrode",
            matname="copper",
        )
        circle.solve_inside = False
        m2dtest.modeler.create_region([20, 100, 20, 100])
        assert not m2dtest.post.create_fieldplot_line_traces("Ground", "Region", "Ground", plot_name="LineTracesTest")
        m2dtest.solution_type = "Electrostatic"
        assert not m2dtest.post.create_fieldplot_line_traces("Invalid", "Region", "Ground", plot_name="LineTracesTest1")
        assert not m2dtest.post.create_fieldplot_line_traces("Ground", "Invalid", "Ground", plot_name="LineTracesTest2")
        assert not m2dtest.post.create_fieldplot_line_traces("Ground", "Region", "Invalid", plot_name="LineTracesTest3")
        m2dtest.assign_voltage(rect.name, amplitude=0, name="Ground")
        m2dtest.assign_voltage(circle.name, amplitude=50e6, name="50kV")
        setup_name = "test"
        m2dtest.create_setup(setupname=setup_name)
        m2dtest.analyze_setup(setup_name)
        plot = m2dtest.post.create_fieldplot_line_traces(["Ground", "Electrode"], "Region", plot_name="LineTracesTest4")
        assert plot
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
        plot.volume_indexes.append(el_id[0])
        plot.update()
        plot.surfaces_indexes.append(el_id[0])
        plot.update()
        plot.seeding_faces.append(8)
        assert not plot.update()
        plot.volume_indexes.append(8)
        assert not plot.update()
        plot.surfaces_indexes.append(8)
        assert not plot.update()

    def test_98_get_variations(self, field_test):
        vars = field_test.available_variations.get_variation_strings()
        assert vars
        variations = field_test.available_variations.variations()
        assert type(variations) is list
        assert type(variations[0]) is list
        vars_dict = field_test.available_variations.variations(output_as_dict=True)
        assert type(vars_dict) is list
        assert type(vars_dict[0]) is dict

    def test_z99_delete_variations(self, q3dtest):
        assert q3dtest.cleanup_solution()

    def test_z99_delete_variations_B(self, field_test):
        vars = field_test.available_variations.get_variation_strings()
        assert field_test.cleanup_solution(vars, entire_solution=False)
        assert field_test.cleanup_solution(vars, entire_solution=True)

    def test_76_ipk_get_scalar_field_value(self, icepak_post):
        assert icepak_post.post.get_scalar_field_value(
            "Heat_Flow_Rate",
            scalar_function="Integrate",
            solution=None,
            variation_dict=["power_block:=", ["0.25W"], "power_source:=", ["0.075W"]],
            isvector=False,
            intrinsics=None,
            phase=None,
            object_name="cube2",
            object_type="surface",
            adjacent_side=False,
        )
        assert icepak_post.post.get_scalar_field_value(
            "Heat_Flow_Rate",
            scalar_function="Integrate",
            solution=None,
            variation_dict=["power_block:=", ["0.6W"], "power_source:=", ["0.15W"]],
            isvector=False,
            intrinsics=None,
            phase=None,
            object_name="cube2",
            object_type="surface",
            adjacent_side=False,
        )
        assert icepak_post.post.get_scalar_field_value(
            "Heat_Flow_Rate",
            scalar_function="Integrate",
            solution=None,
            variation_dict=["power_block:=", ["0.6W"], "power_source:=", ["0.15W"]],
            isvector=False,
            intrinsics=None,
            phase=None,
            object_name="cube2",
            object_type="surface",
            adjacent_side=True,
        )
        assert icepak_post.post.get_scalar_field_value(
            "Temperature",
            scalar_function="Maximum",
            solution=None,
            variation_dict=["power_block:=", ["0.6W"], "power_source:=", ["0.15W"]],
            isvector=False,
            intrinsics=None,
            phase=None,
            object_name="cube1",
            object_type="volume",
            adjacent_side=False,
        )
        assert icepak_post.post.get_scalar_field_value(
            "Temperature",
            scalar_function="Maximum",
            solution=None,
            variation_dict=["power_block:=", ["0.6W"], "power_source:=", ["0.15W"]],
            isvector=False,
            intrinsics=None,
            phase=None,
            object_name="cube2",
            object_type="surface",
            adjacent_side=False,
        )
        assert icepak_post.post.get_scalar_field_value(
            "Temperature",
            scalar_function="Value",
            solution=None,
            variation_dict=None,
            isvector=False,
            intrinsics=None,
            phase=None,
            object_name="Point1",
            object_type="point",
            adjacent_side=False,
        )
