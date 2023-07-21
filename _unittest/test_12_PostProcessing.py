# standard imports
import os
import sys

from _unittest.conftest import BasisTest
from _unittest.conftest import config
from pyaedt import Circuit
from pyaedt import Maxwell2d
from pyaedt import Q2d
from pyaedt import Q3d
from pyaedt import settings
from pyaedt.generic.general_methods import is_ironpython
from pyaedt.generic.general_methods import is_linux
from pyaedt.generic.plot import _parse_aedtplt
from pyaedt.generic.plot import _parse_streamline

# Import required modules
# Setup paths for module imports

try:
    import pytest
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest


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
test_subfolder = "T12"
settings.enable_pandas_output = True


class TestClass(BasisTest, object):
    def setup_class(self):
        # set a scratch directory and the environment / test data
        BasisTest.my_setup(self)
        self.field_test = BasisTest.add_app(self, project_name=test_field_name, subfolder=test_subfolder)
        self.circuit_test = BasisTest.add_app(
            self, project_name=test_circuit_name, design_name="Diode", application=Circuit, subfolder=test_subfolder
        )
        self.diff_test = Circuit(
            designname="diff", projectname=self.circuit_test.project_name, specified_version=config["desktopVersion"]
        )
        self.sbr_test = BasisTest.add_app(self, project_name=sbr_file, subfolder=test_subfolder)
        self.q3dtest = BasisTest.add_app(self, project_name=q3d_file, application=Q3d, subfolder=test_subfolder)
        self.q2dtest = Q2d(projectname=self.q3dtest.project_name, specified_version=config["desktopVersion"])
        self.eye_test = BasisTest.add_app(self, project_name=eye_diagram, application=Circuit, subfolder=test_subfolder)
        self.ami_test = BasisTest.add_app(self, project_name=ami, application=Circuit, subfolder=test_subfolder)
        self.array_test = BasisTest.add_app(self, project_name=array, subfolder=test_subfolder)
        self.m2dtest = BasisTest.add_app(self, project_name=m2d_file, application=Maxwell2d, subfolder=test_subfolder)

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_09_manipulate_report(self):
        variations = self.field_test.available_variations.nominal_w_values_dict
        variations["Theta"] = ["All"]
        variations["Phi"] = ["All"]
        variations["Freq"] = ["30GHz"]
        self.field_test.set_source_context(["1"])
        context = {"Context": "3D", "SourceContext": "1:1"}
        assert self.field_test.post.create_report(
            "db(GainTotal)",
            self.field_test.nominal_adaptive,
            variations=variations,
            primary_sweep_variable="Phi",
            secondary_sweep_variable="Theta",
            plot_type="3D Polar Plot",
            context=context,
            report_category="Far Fields",
        )
        assert self.field_test.post.create_report(
            "db(GainTotal)",
            self.field_test.nominal_adaptive,
            variations=variations,
            primary_sweep_variable="Phi",
            secondary_sweep_variable="Theta",
            plot_type="3D Polar Plot",
            context="3D",
            report_category="Far Fields",
        )
        new_report = self.field_test.post.reports_by_category.far_field(
            "db(RealizedGainTotal)", self.field_test.nominal_adaptive
        )
        new_report.variations = variations
        new_report.report_type = "3D Polar Plot"
        new_report.far_field_sphere = "3D"
        assert new_report.create()

        new_report2 = self.field_test.post.reports_by_category.far_field(
            "db(RealizedGainTotal)", self.field_test.nominal_adaptive, "3D", "1:1"
        )
        new_report2.variations = variations
        new_report2.report_type = "3D Polar Plot"
        assert new_report2.create()

        new_report3 = self.field_test.post.reports_by_category.antenna_parameters(
            "db(PeakRealizedGain)", self.field_test.nominal_adaptive, "3D"
        )
        new_report3.report_type = "Data Table"
        assert new_report3.create()

        self.field_test.analyze(self.field_test.active_setup)
        data = self.field_test.post.get_solution_data(
            "GainTotal",
            self.field_test.nominal_adaptive,
            variations=variations,
            primary_sweep_variable="Theta",
            context="3D",
            report_category="Far Fields",
        )
        if not is_ironpython:
            assert data.plot(is_polar=True)
            assert data.plot_3d()
            assert self.field_test.post.create_3d_plot(data)

        context = {"Context": "3D", "SourceContext": "1:1"}
        data = self.field_test.post.get_solution_data(
            "GainTotal",
            self.field_test.nominal_adaptive,
            variations=variations,
            primary_sweep_variable="Theta",
            context=context,
            report_category="Far Fields",
        )
        if not is_ironpython:
            assert data.plot(is_polar=True)
            assert data.plot_3d()
            assert self.field_test.post.create_3d_plot(data)
        self.field_test.modeler.create_polyline([[0, 0, 0], [0, 5, 30]], name="Poly1", non_model=True)
        variations2 = self.field_test.available_variations.nominal_w_values_dict
        variations2["Theta"] = ["All"]
        variations2["Phi"] = ["All"]
        variations2["Freq"] = ["30GHz"]
        variations2["Distance"] = ["All"]
        assert self.field_test.post.create_report(
            "Mag_E",
            self.field_test.nominal_adaptive,
            variations=variations2,
            primary_sweep_variable="Distance",
            context="Poly1",
            report_category="Fields",
        )
        new_report = self.field_test.post.reports_by_category.fields("Mag_H", self.field_test.nominal_adaptive)
        new_report.variations = variations2
        new_report.polyline = "Poly1"
        assert new_report.create()
        assert data.primary_sweep == "Theta"
        assert len(data.data_magnitude("GainTotal")) > 0
        assert not data.data_magnitude("GainTotal2")
        assert self.field_test.post.create_report(
            "S(1,1)",
            self.field_test.nominal_sweep,
            variations=variations,
            plot_type="Smith Chart",
        )
        new_report = self.field_test.post.reports_by_category.modal_solution("S(1,1)")
        new_report.plot_type = "Smith Chart"
        assert new_report.create()
        data = self.field_test.post.get_solution_data(
            "Mag_E",
            self.field_test.nominal_adaptive,
            variations=variations2,
            primary_sweep_variable="Theta",
            context="Poly1",
            report_category="Fields",
        )
        assert data.units_sweeps["Phase"] == "deg"

        assert self.field_test.post.get_far_field_data(
            setup_sweep_name=self.field_test.nominal_adaptive, expression="RealizedGainTotal", domain="3D"
        )
        data_farfield2 = self.field_test.post.get_far_field_data(
            setup_sweep_name=self.field_test.nominal_adaptive,
            expression="RealizedGainTotal",
            domain={"Context": "3D", "SourceContext": "1:1"},
        )
        if not is_ironpython:
            assert data_farfield2.plot(math_formula="db20", is_polar=True)

    def test_09b_export_report(self):  # pragma: no cover
        files = self.circuit_test.export_results()
        assert len(files) > 0
        self.q2dtest.analyze()
        files = self.q2dtest.export_results()
        assert len(files) > 0
        self.q3dtest.analyze_setup("Setup1")
        files = self.q3dtest.export_results()
        assert len(files) > 0

    def test_17_circuit(self):
        assert not self.circuit_test.setups[0].is_solved

        self.circuit_test.analyze_setup("LNA")
        self.circuit_test.analyze_setup("Transient")
        assert self.circuit_test.setups[0].is_solved
        assert self.circuit_test.post.create_report(["dB(S(Port1, Port1))", "dB(S(Port1, Port2))"], "LNA")
        new_report = self.circuit_test.post.reports_by_category.standard(
            ["dB(S(Port1, Port1))", "dB(S(Port1, Port2))"], "LNA"
        )
        assert new_report.create()
        data1 = self.circuit_test.post.get_solution_data(["dB(S(Port1,Port1))", "dB(S(Port1,Port2))"], "LNA")
        assert data1.primary_sweep == "Freq"
        assert self.circuit_test.post.create_report(["V(net_11)"], "Transient", "Time")
        data11 = self.circuit_test.post.get_solution_data(setup_sweep_name="LNA", math_formula="dB")
        assert data11.primary_sweep == "Freq"
        assert "dB(S(Port2,Port1))" in data11.expressions
        assert self.circuit_test.post.create_report(["V(net_11)"], "Transient", "Time")
        new_report = self.circuit_test.post.reports_by_category.standard(["V(net_11)"], "Transient")
        new_report.domain = "Time"
        assert new_report.create()
        data2 = self.circuit_test.post.get_solution_data(["V(net_11)"], "Transient", "Time")
        assert data2.primary_sweep == "Time"
        assert len(data2.data_magnitude()) > 0
        context = {"algorithm": "FFT", "max_frequency": "100MHz", "time_stop": "200ns", "test": ""}
        data3 = self.circuit_test.post.get_solution_data(["V(net_11)"], "Transient", "Spectral", context=context)
        assert data3.units_sweeps["Spectrum"] == "GHz"
        assert len(data3.data_real()) > 0
        new_report = self.circuit_test.post.reports_by_category.spectral(["dB(V(net_11))"], "Transient")
        new_report.window = "Hanning"
        new_report.max_freq = "1GHz"
        new_report.time_start = "1ns"
        new_report.time_stop = "190ns"
        new_report.plot_continous_spectrum = True
        assert new_report.create()
        new_report = self.circuit_test.post.reports_by_category.spectral(["dB(V(net_11))", "dB(V(Port1))"], "Transient")
        new_report.window = "Kaiser"
        new_report.adjust_coherent_gain = False
        new_report.kaiser_coeff = 2
        new_report.algorithm = "Fourier Transform"
        new_report.max_freq = "1GHz"
        new_report.time_start = "1ns"
        new_report.time_stop = "190ns"
        new_report.plot_continous_spectrum = False
        assert new_report.create()
        assert self.circuit_test.post.create_report(
            ["dB(V(net_11))", "dB(V(Port1))"], domain="Spectrum", setup_sweep_name="Transient"
        )
        new_report = self.circuit_test.post.reports_by_category.spectral(None, "Transient")
        new_report.window = "Hanning"
        new_report.max_freq = "1GHz"
        new_report.time_start = "1ns"
        new_report.time_stop = "190ns"
        new_report.plot_continous_spectrum = True
        assert new_report.create()
        pass

    def test_18_diff_plot(self):
        assert len(self.diff_test.post.available_display_types()) > 0
        assert len(self.diff_test.post.available_report_types) > 0
        assert len(self.diff_test.post.available_report_quantities()) > 0
        self.diff_test.analyze_setup("LinearFrequency")
        assert self.diff_test.setups[0].is_solved
        variations = self.diff_test.available_variations.nominal_w_values_dict
        variations["Freq"] = ["All"]
        variations["l1"] = ["All"]
        assert self.diff_test.post.create_report(
            ["dB(S(Diff1, Diff1))"],
            "LinearFrequency",
            variations=variations,
            primary_sweep_variable="l1",
            context="Differential Pairs",
        )
        new_report = self.diff_test.post.reports_by_category.standard("dB(S(1,1))")
        new_report.differential_pairs = True
        assert new_report.create()
        assert new_report.get_solution_data()
        data1 = self.diff_test.post.get_solution_data(
            ["S(Diff1, Diff1)"],
            "LinearFrequency",
            variations=variations,
            primary_sweep_variable="Freq",
            context="Differential Pairs",
        )
        assert data1.primary_sweep == "Freq"
        if not is_ironpython:
            data1.plot(math_formula="db20")
        data1.primary_sweep = "l1"
        assert data1.primary_sweep == "l1"
        assert len(data1.data_magnitude()) == 5
        if is_ironpython:
            assert not data1.plot("S(Diff1, Diff1)")
        else:
            assert data1.plot("S(Diff1, Diff1)")
            assert data1.plot(math_formula="db20")
            assert data1.plot(math_formula="db10")
            assert data1.plot(math_formula="mag")
            assert data1.plot(math_formula="re")
            assert data1.plot(math_formula="im")
            assert data1.plot(math_formula="phasedeg")
            assert data1.plot(math_formula="phaserad")

        assert self.diff_test.create_touchstone_report(
            plot_name="Diff_plot",
            curvenames=["dB(S(Diff1, Diff1))"],
            solution_name="LinearFrequency",
            differential_pairs=True,
        )

    def test_51_get_efields(self):
        if is_ironpython:
            assert True
        else:
            assert self.field_test.post.get_efields_data(ff_setup="3D")

    @pytest.mark.skipif(
        is_linux or sys.version_info < (3, 8), reason="plot_scene method is not supported in ironpython"
    )
    def test_55_time_plot(self):
        self.sbr_test.analyze(self.sbr_test.active_setup, use_auto_settings=False)
        assert self.sbr_test.setups[0].is_solved
        solution_data = self.sbr_test.post.get_solution_data(
            expressions=["NearEX", "NearEY", "NearEZ"],
            variations={"_u": ["All"], "_v": ["All"], "Freq": ["All"]},
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
            coord_system_center=[-0.15, 0, 0], db_val=True, csv_dir=os.path.join(self.sbr_test.working_directory, "csv")
        )
        assert os.path.exists(frames_list)
        self.sbr_test.post.plot_scene(
            frames_list,
            os.path.join(self.sbr_test.working_directory, "animation.gif"),
            norm_index=5,
            dy_rng=35,
            show=False,
        )
        assert os.path.exists(os.path.join(self.sbr_test.working_directory, "animation.gif"))
        self.sbr_test.post.plot_scene(
            frames_list,
            os.path.join(self.sbr_test.working_directory, "animation2.gif"),
            norm_index=5,
            dy_rng=35,
            show=False,
            convert_fields_in_db=True,
            log_multiplier=20.0,
        )
        assert os.path.exists(os.path.join(self.sbr_test.working_directory, "animation2.gif"))

    def test_56_test_export_q3d_results(self):
        self.q3dtest.analyze(self.q3dtest.active_setup)
        assert os.path.exists(self.q3dtest.export_convergence("Setup1"))
        assert os.path.exists(self.q3dtest.export_profile("Setup1"))
        new_report = self.q3dtest.post.reports_by_category.standard(self.q3dtest.get_traces_for_plot())
        assert new_report.create()
        self.q3dtest.modeler.create_polyline([[0, -5, 0.425], [0.5, 5, 0.5]], name="Poly1", non_model=True)
        new_report = self.q3dtest.post.reports_by_category.cg_fields("SmoothQ", polyline="Poly1")
        assert new_report.create()
        new_report = self.q3dtest.post.reports_by_category.rl_fields("Mag_SurfaceJac", polyline="Poly1")
        assert new_report.create()
        new_report = self.q3dtest.post.reports_by_category.dc_fields("Mag_VolumeJdc", polyline="Poly1")
        assert new_report.create()
        assert len(self.q3dtest.post.plots) == 6

    def test_57_test_export_q2d_results(self):
        self.q2dtest.analyze(self.q2dtest.active_setup)
        assert os.path.exists(self.q2dtest.export_convergence("Setup1"))
        assert os.path.exists(self.q2dtest.export_profile("Setup1"))
        new_report = self.q2dtest.post.reports_by_category.standard(self.q2dtest.get_traces_for_plot())
        assert new_report.create()
        self.q2dtest.modeler.create_polyline([[-1.9, -0.1, 0], [-1.2, -0.2, 0]], name="Poly1", non_model=True)
        new_report = self.q2dtest.post.reports_by_category.cg_fields("Mag_E", polyline="Poly1")
        assert new_report.create()
        new_report = self.q2dtest.post.reports_by_category.rl_fields("Mag_H", polyline="Poly1")
        assert new_report.create()
        sol = new_report.get_solution_data()
        sol.enable_pandas_output = True
        data = sol.full_matrix_real_imag
        data_mag = sol.full_matrix_mag_phase
        sol.data_magnitude()
        sol.enable_pandas_output = False
        assert len(self.q2dtest.post.plots) == 3
        new_report = self.q2dtest.post.reports_by_category.standard()
        assert new_report.get_solution_data()

    def test_58_test_no_report(self):
        assert not self.q3dtest.post.reports_by_category.modal_solution()
        assert not self.q3dtest.post.reports_by_category.terminal_solution()
        assert not self.q2dtest.post.reports_by_category.far_field()
        assert not self.q2dtest.post.reports_by_category.near_field()
        assert not self.q2dtest.post.reports_by_category.eigenmode()

    @pytest.mark.skipif(is_ironpython, reason="Not supported in Ironpython")
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

    @pytest.mark.skipif(is_ironpython, reason="Not supported in Ironpython")
    def test_60_test_parse_vector(self):
        local_path = os.path.dirname(os.path.realpath(__file__))
        out = _parse_streamline(os.path.join(local_path, "example_models", test_subfolder, "test_streamline.fldplt"))
        assert isinstance(out, list)

    def test_61_export_mesh(self):
        assert os.path.exists(self.q3dtest.export_mesh_stats("Setup1"))
        assert os.path.exists(self.q3dtest.export_mesh_stats("Setup1", setup_type="AC RL"))

    def test_62_eye_diagram(self):
        self.eye_test.analyze(self.eye_test.active_setup)
        rep = self.eye_test.post.reports_by_category.eye_diagram("AEYEPROBE(OutputEye)", "QuickEyeAnalysis")
        rep.time_start = "0ps"
        rep.time_stop = "50us"
        rep.unit_interval = "1e-9"
        assert rep.create()

    @pytest.mark.skipif(
        config["desktopVersion"] < "2022.2", reason="Not working in non graphical in version lower than 2022.2"
    )
    def test_63_mask(self):
        self.eye_test.analyze(self.eye_test.active_setup)
        rep = self.eye_test.post.reports_by_category.eye_diagram("AEYEPROBE(OutputEye)", "QuickEyeAnalysis")
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
    def test_64_eye_meas(self):
        self.eye_test.analyze(self.eye_test.active_setup)
        rep = self.eye_test.post.reports_by_category.eye_diagram("AEYEPROBE(OutputEye)", "QuickEyeAnalysis")
        rep.time_start = "0ps"
        rep.time_stop = "50us"
        rep.unit_interval = "1e-9"
        rep.create()
        assert rep.add_all_eye_measurements()
        assert rep.clear_all_eye_measurements()
        assert rep.add_trace_characteristics("MinEyeHeight")

    def test_65_eye_from_json(self):
        local_path = os.path.dirname(os.path.realpath(__file__))
        assert self.eye_test.post.create_report_from_configuration(
            os.path.join(local_path, "example_models", "report_json", "EyeDiagram_Report_simple.json"),
            solution_name="QuickEyeAnalysis",
        )

    def test_66_spectral_from_json(self):
        local_path = os.path.dirname(os.path.realpath(__file__))
        self.circuit_test.analyze_setup("Transient")
        assert self.circuit_test.post.create_report_from_configuration(
            os.path.join(local_path, "example_models", "report_json", "Spectral_Report_Simple.json"),
            solution_name="Transient",
        )

    @pytest.mark.skipif(
        config["desktopVersion"] < "2022.2", reason="Not working in non graphical in version lower than 2022.2"
    )
    def test_68_eye_from_json(self):
        local_path = os.path.dirname(os.path.realpath(__file__))
        assert self.eye_test.post.create_report_from_configuration(
            os.path.join(local_path, "example_models", "report_json", "EyeDiagram_Report.json"),
            solution_name="QuickEyeAnalysis",
        )

    @pytest.mark.skipif(
        config["desktopVersion"] < "2022.2", reason="Not working in non graphical in version lower than 2022.2"
    )
    def test_69_spectral_from_json(self):
        local_path = os.path.dirname(os.path.realpath(__file__))
        self.circuit_test.analyze_setup("Transient")
        assert self.circuit_test.post.create_report_from_configuration(
            os.path.join(local_path, "example_models", "report_json", "Spectral_Report.json"), solution_name="Transient"
        )

    @pytest.mark.skipif(is_linux or sys.version_info < (3, 8), reason="FarFieldSolution not supported by IronPython")
    def test_71_antenna_plot(self):
        ffdata = self.field_test.get_antenna_ffd_solution_data(frequencies=30e9, sphere_name="3D")
        ffdata.phase_offset = [0, 90, 0, 90]
        assert ffdata.phase_offset == [0.0]
        ffdata.phase_offset = [90]
        assert ffdata.phase_offset != [0.0]
        assert ffdata.plot_farfield_contour(
            qty_str="RealizedGain",
            convert_to_db=True,
            title="Contour at {}Hz".format(ffdata.frequency),
            export_image_path=os.path.join(self.local_scratch.path, "contour.jpg"),
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "contour.jpg"))

        ffdata.plot_2d_cut(
            primary_sweep="theta",
            secondary_sweep_value=[-180, -75, 75],
            qty_str="RealizedGain",
            title="Azimuth at {}Hz".format(ffdata.frequency),
            convert_to_db=True,
            export_image_path=os.path.join(self.local_scratch.path, "2d1.jpg"),
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "2d1.jpg"))
        ffdata.plot_2d_cut(
            primary_sweep="phi",
            secondary_sweep_value=30,
            qty_str="RealizedGain",
            title="Azimuth at {}Hz".format(ffdata.frequency),
            convert_to_db=True,
            export_image_path=os.path.join(self.local_scratch.path, "2d2.jpg"),
        )

        assert os.path.exists(os.path.join(self.local_scratch.path, "2d2.jpg"))

        ffdata.polar_plot_3d(
            qty_str="RealizedGain",
            convert_to_db=True,
            export_image_path=os.path.join(self.local_scratch.path, "3d1.jpg"),
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "3d1.jpg"))

        ffdata.polar_plot_3d_pyvista(
            qty_str="RealizedGain",
            convert_to_db=True,
            show=False,
            export_image_path=os.path.join(self.local_scratch.path, "3d2.jpg"),
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "3d2.jpg"))

        try:
            p = ffdata.polar_plot_3d_pyvista(qty_str="RealizedGain", convert_to_db=True, show=False)
            assert isinstance(p, object)
        except:
            assert True

    @pytest.mark.skipif(is_linux or sys.version_info < (3, 8), reason="FarFieldSolution not supported by IronPython")
    def test_72_antenna_plot(self):
        ffdata = self.array_test.get_antenna_ffd_solution_data(frequencies=3.5e9, sphere_name="3D")
        ffdata.frequency = 3.5e9
        assert ffdata.plot_farfield_contour(
            qty_str="RealizedGain",
            convert_to_db=True,
            title="Contour at {}Hz".format(ffdata.frequency),
            export_image_path=os.path.join(self.local_scratch.path, "contour.jpg"),
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "contour.jpg"))

        ffdata.plot_2d_cut(
            primary_sweep="theta",
            secondary_sweep_value=[-180, -75, 75],
            qty_str="RealizedGain",
            title="Azimuth at {}Hz".format(ffdata.frequency),
            convert_to_db=True,
            export_image_path=os.path.join(self.local_scratch.path, "2d1.jpg"),
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "2d1.jpg"))
        ffdata.plot_2d_cut(
            primary_sweep="phi",
            secondary_sweep_value=30,
            qty_str="RealizedGain",
            title="Azimuth at {}Hz".format(ffdata.frequency),
            convert_to_db=True,
            export_image_path=os.path.join(self.local_scratch.path, "2d2.jpg"),
        )

        assert os.path.exists(os.path.join(self.local_scratch.path, "2d2.jpg"))

        ffdata.polar_plot_3d(
            qty_str="RealizedGain",
            convert_to_db=True,
            export_image_path=os.path.join(self.local_scratch.path, "3d1.jpg"),
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "3d1.jpg"))

        ffdata.polar_plot_3d_pyvista(
            qty_str="RealizedGain",
            convert_to_db=True,
            show=False,
            export_image_path=os.path.join(self.local_scratch.path, "3d2.jpg"),
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "3d2.jpg"))
        ffdata1 = self.array_test.get_antenna_ffd_solution_data(frequencies=3.5e9, sphere_name="3D", overwrite=False)
        assert ffdata1.plot_farfield_contour(
            qty_str="RealizedGain",
            convert_to_db=True,
            title="Contour at {}Hz".format(ffdata1.frequency),
            export_image_path=os.path.join(self.local_scratch.path, "contour1.jpg"),
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "contour1.jpg"))

    def test_73_ami_solution_data(self):
        self.ami_test.solution_type = "NexximAMI"
        assert self.ami_test.post.get_solution_data(
            expressions="WaveAfterProbe<b_input_43.int_ami_rx>",
            setup_sweep_name="AMIAnalysis",
            domain="Time",
            variations=self.ami_test.available_variations.nominal,
        )

        assert self.ami_test.post.get_solution_data(
            expressions="WaveAfterSource<b_output4_42.int_ami_tx>",
            setup_sweep_name="AMIAnalysis",
            domain="Time",
            variations=self.ami_test.available_variations.nominal,
        )

        assert self.ami_test.post.get_solution_data(
            expressions="InitialWave<b_output4_42.int_ami_tx>",
            setup_sweep_name="AMIAnalysis",
            domain="Time",
            variations=self.ami_test.available_variations.nominal,
        )

        assert self.ami_test.post.get_solution_data(
            expressions="WaveAfterChannel<b_input_43.int_ami_rx>",
            setup_sweep_name="AMIAnalysis",
            domain="Time",
            variations=self.ami_test.available_variations.nominal,
        )

        assert self.ami_test.post.get_solution_data(
            expressions="ClockTics<b_input_43.int_ami_rx>",
            setup_sweep_name="AMIAnalysis",
            domain="Clock Times",
            variations=self.ami_test.available_variations.nominal,
        )
        probe_name = "b_input_43"
        source_name = "b_output4_42"
        plot_type = "WaveAfterProbe"
        setup_name = "AMIAnalysis"

        ignore_bits = 1000
        unit_interval = 0.1e-9
        assert not self.ami_test.post.sample_ami_waveform(
            setup_name,
            probe_name,
            source_name,
            self.ami_test.available_variations.nominal,
            unit_interval,
            ignore_bits,
            plot_type,
        )
        if not is_ironpython:
            ignore_bits = 5
            unit_interval = 0.1e-9
            plot_type = "InitialWave"
            data1 = self.ami_test.post.sample_ami_waveform(
                setup_name,
                probe_name,
                source_name,
                self.ami_test.available_variations.nominal,
                unit_interval,
                ignore_bits,
                plot_type,
            )
            assert len(data1[0]) == 45

        settings.enable_pandas_output = False
        ignore_bits = 5
        unit_interval = 0.1e-9
        clock_tics = [1e-9, 2e-9, 3e-9]
        data2 = self.ami_test.post.sample_ami_waveform(
            setup_name,
            probe_name,
            source_name,
            self.ami_test.available_variations.nominal,
            unit_interval,
            ignore_bits,
            plot_type=None,
            clock_tics=clock_tics,
        )
        assert len(data2) == 4
        assert len(data2[0]) == 3

    def test_75_plot_field_line_traces(self):
        self.m2dtest.modeler.model_units = "mm"
        rect = self.m2dtest.modeler.create_rectangle(
            position=["1mm", "5mm", "0mm"], dimension_list=["-1mm", "-10mm", 0], name="Ground", matname="copper"
        )
        rect.solve_inside = False
        circle = self.m2dtest.modeler.create_circle(
            position=["-10mm", "0", "0"],
            radius="1mm",
            num_sides="0",
            is_covered=True,
            name="Electrode",
            matname="copper",
        )
        circle.solve_inside = False
        self.m2dtest.modeler.create_region([20, 100, 20, 100])
        assert not self.m2dtest.post.create_fieldplot_line_traces(
            "Ground", "Region", "Ground", plot_name="LineTracesTest"
        )
        self.m2dtest.solution_type = "Electrostatic"
        assert not self.m2dtest.post.create_fieldplot_line_traces(
            "Invalid", "Region", "Ground", plot_name="LineTracesTest1"
        )
        assert not self.m2dtest.post.create_fieldplot_line_traces(
            "Ground", "Invalid", "Ground", plot_name="LineTracesTest2"
        )
        assert not self.m2dtest.post.create_fieldplot_line_traces(
            "Ground", "Region", "Invalid", plot_name="LineTracesTest3"
        )
        self.m2dtest.assign_voltage(rect.name, amplitude=0, name="Ground")
        self.m2dtest.assign_voltage(circle.name, amplitude=50e6, name="50kV")
        setup_name = "test"
        self.m2dtest.create_setup(setupname=setup_name)
        self.m2dtest.analyze_setup(setup_name)
        plot = self.m2dtest.post.create_fieldplot_line_traces(
            ["Ground", "Electrode"], "Region", plot_name="LineTracesTest4"
        )
        assert plot
        assert self.m2dtest.post.create_fieldplot_line_traces(
            ["Ground", "Electrode"], "Region", "Ground", plot_name="LineTracesTest5"
        )
        assert self.m2dtest.post.create_fieldplot_line_traces(["Ground", "Electrode"], plot_name="LineTracesTest6")
        assert not self.m2dtest.post.create_fieldplot_line_traces(
            ["Ground", "Electrode"], "Region", ["Invalid"], plot_name="LineTracesTest7"
        )
        assert not self.m2dtest.post.create_fieldplot_line_traces(
            ["Ground", "Electrode"], ["Invalid"], plot_name="LineTracesTest8"
        )
        plot.TraceStepLength = "0.002mm"
        plot.SeedingPointsNumber = 20
        plot.LineStyle = "Cylinder"
        plot.LineWidth = 3
        assert plot.update()
        el_id = [obj.id for obj in self.m2dtest.modeler.object_list if obj.name == "Electrode"]
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

    def test_z99_delete_variations(self):
        assert self.q3dtest.cleanup_solution()
        vars = self.field_test.available_variations.get_variation_strings()
        assert self.field_test.available_variations.variations()
        assert self.field_test.cleanup_solution(vars, entire_solution=False)
        assert self.field_test.cleanup_solution(vars, entire_solution=True)
