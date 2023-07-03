# standard imports
import os
import sys
import uuid

from _unittest.conftest import BasisTest
from _unittest.conftest import config

from pyaedt import Circuit
from pyaedt import Hfss
from pyaedt import Maxwell2d
from pyaedt import Q2d
from pyaedt import Q3d
from pyaedt import settings
from pyaedt.generic.DataHandlers import json_to_dict
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

try:
    from IPython.display import Image

    ipython_available = True
except ImportError:
    ipython_available = False

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
        self.aedtapp = BasisTest.add_app(self, project_name=test_project_name, subfolder=test_subfolder)
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

    def test_01B_Field_Plot(self):
        assert len(self.aedtapp.post.available_display_types()) > 0
        assert len(self.aedtapp.post.available_report_types) > 0
        assert len(self.aedtapp.post.available_report_quantities()) > 0
        cutlist = ["Global:XY", "Global:XZ", "Global:YZ"]
        setup_name = self.aedtapp.existing_analysis_sweeps[0]
        assert self.aedtapp.setups[0].is_solved
        quantity_name = "ComplexMag_E"
        intrinsic = {"Freq": "5GHz", "Phase": "180deg"}
        min_value = self.aedtapp.post.get_scalar_field_value(quantity_name, "Minimum", setup_name, intrinsics="5GHz")
        plot1 = self.aedtapp.post.create_fieldplot_cutplane(cutlist, quantity_name, setup_name, intrinsic)
        plot1.IsoVal = "Tone"
        plot1.update_field_plot_settings()
        plot1.update()
        assert self.aedtapp.post.field_plots[plot1.name].IsoVal == "Tone"
        assert plot1.change_plot_scale(min_value, "30000")
        assert self.aedtapp.post.create_fieldplot_volume("inner", "Vector_E", setup_name, intrinsic)

        assert self.aedtapp.post.create_fieldplot_surface(
            self.aedtapp.modeler["outer"].faces[0].id, "Mag_E", setup_name, intrinsic
        )
        assert self.aedtapp.post.create_fieldplot_surface(self.aedtapp.modeler["outer"], "Mag_E", setup_name, intrinsic)
        assert self.aedtapp.post.create_fieldplot_surface(
            self.aedtapp.modeler["outer"].faces, "Mag_E", setup_name, intrinsic
        )
        assert len(self.aedtapp.setups[0].sweeps[0].frequencies) > 0
        assert isinstance(self.aedtapp.setups[0].sweeps[0].basis_frequencies, list)

    @pytest.mark.skipif(is_linux or sys.version_info < (3, 8), reason="Not running in ironpython")
    def test_01_Animate_plt(self):
        cutlist = ["Global:XY"]
        phases = [str(i * 5) + "deg" for i in range(2)]
        model_gif = self.aedtapp.post.animate_fields_from_aedtplt_2(
            quantityname="Mag_E",
            object_list=cutlist,
            plottype="CutPlane",
            meshplot=False,
            setup_name=self.aedtapp.nominal_adaptive,
            intrinsic_dict={"Freq": "5GHz", "Phase": "0deg"},
            project_path=self.local_scratch.path,
            variation_variable="Phase",
            variation_list=phases,
            show=False,
            export_gif=True,
        )
        assert os.path.exists(model_gif.gif_file)
        model_gif2 = self.aedtapp.post.animate_fields_from_aedtplt_2(
            quantityname="Mag_E",
            object_list=cutlist,
            plottype="CutPlane",
            meshplot=False,
            setup_name=self.aedtapp.nominal_adaptive,
            intrinsic_dict={"Freq": "5GHz", "Phase": "0deg"},
            project_path=self.local_scratch.path,
            variation_variable="Phase",
            variation_list=phases,
            show=False,
            export_gif=False,
        )
        model_gif2.gif_file = os.path.join(self.aedtapp.working_directory, "test2.gif")
        model_gif2.camera_position = [0, 50, 200]
        model_gif2.focal_point = [0, 50, 0]
        model_gif2.animate()
        assert os.path.exists(model_gif2.gif_file)

    @pytest.mark.skipif(config["NonGraphical"] == True, reason="Not running in non-graphical mode")
    def test_02_export_fields(self):
        quantity_name2 = "ComplexMag_H"
        setup_name = "Setup1 : LastAdaptive"
        intrinsic = {"Freq": "5GHz", "Phase": "180deg"}
        vollist = ["NewObject_IJD39Q"]
        plot2 = self.aedtapp.post.create_fieldplot_volume(vollist, quantity_name2, setup_name, intrinsic)

        self.aedtapp.post.export_field_jpg(
            os.path.join(self.local_scratch.path, "prova2.jpg"),
            plot2.name,
            plot2.plotFolder,
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "prova2.jpg"))
        assert os.path.exists(
            plot2.export_image(os.path.join(self.local_scratch.path, "test_x.jpg"), orientation="top")
        )

    def test_03_create_scattering(self):
        setup_name = "Setup1 : Sweep"
        portnames = ["1", "2"]
        assert self.aedtapp.create_scattering("MyTestScattering")
        setup_name = "Setup2 : Sweep"
        assert not self.aedtapp.create_scattering("MyTestScattering2", setup_name, portnames, portnames)

    def test_03_get_solution_data(self):
        self.aedtapp.analyze(self.aedtapp.active_setup)
        trace_names = []
        portnames = ["1", "2"]
        for el in portnames:
            for el2 in portnames:
                trace_names.append("S(" + el + "," + el2 + ")")
        cxt = ["Domain:=", "Sweep"]
        families = {"Freq": ["All"]}
        for el in self.aedtapp.available_variations.nominal_w_values_dict:
            families[el] = self.aedtapp.available_variations.nominal_w_values_dict[el]

        my_data = self.aedtapp.post.get_solution_data(expressions=trace_names, variations=families)
        assert my_data
        assert my_data.expressions
        assert len(my_data.data_db10(trace_names[0])) > 0
        assert len(my_data.data_imag(trace_names[0])) > 0
        assert len(my_data.data_real(trace_names[0])) > 0
        assert len(my_data.data_magnitude(trace_names[0])) > 0
        assert my_data.export_data_to_csv(os.path.join(self.local_scratch.path, "output.csv"))
        assert os.path.exists(os.path.join(self.local_scratch.path, "output.csv"))
        if not is_ironpython:
            assert self.aedtapp.get_touchstone_data("Setup1")

    def test_04_export_touchstone(self):
        setup_name = "Setup1"
        sweep_name = "Sweep"
        self.aedtapp.export_touchstone(
            setup_name, sweep_name, os.path.join(self.local_scratch.path, "Setup1_Sweep.S2p")
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "Setup1_Sweep.S2p"))

        sweep_name = None
        self.aedtapp.export_touchstone(
            setup_name, sweep_name, os.path.join(self.local_scratch.path, "Setup1_Sweep2.S2p")
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "Setup1_Sweep2.S2p"))
        setup_name = None
        self.aedtapp.export_touchstone(
            setup_name, sweep_name, os.path.join(self.local_scratch.path, "Setup1_Sweep3.S2p")
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "Setup1_Sweep3.S2p"))

        assert self.aedtapp.export_touchstone(setup_name, sweep_name)

    @pytest.mark.skipif(config["desktopVersion"] != "2023.1", reason="Not running in non-graphical mode")
    def test_05_export_report_to_jpg(self):
        self.aedtapp.post.export_report_to_jpg(self.local_scratch.path, "MyTestScattering")
        assert os.path.exists(os.path.join(self.local_scratch.path, "MyTestScattering.jpg"))

    def test_06_export_report_to_csv(self):
        self.aedtapp.post.export_report_to_csv(self.local_scratch.path, "MyTestScattering")
        assert os.path.exists(os.path.join(self.local_scratch.path, "MyTestScattering.csv"))

    def test_06_export_report_to_rdat(self):
        self.aedtapp.post.export_report_to_file(self.local_scratch.path, "MyTestScattering", ".rdat")
        assert os.path.exists(os.path.join(self.local_scratch.path, "MyTestScattering.rdat"))

    def test_07_export_fields_from_Calculator(self):
        self.aedtapp.post.export_field_file_on_grid(
            "E",
            "Setup1 : LastAdaptive",
            self.aedtapp.available_variations.nominal_w_values,
            os.path.join(self.local_scratch.path, "Efield.fld"),
            grid_stop=[5, 5, 5],
            grid_step=[0.5, 0.5, 0.5],
            isvector=True,
            intrinsics="5GHz",
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "Efield.fld"))

        self.aedtapp.post.export_field_file_on_grid(
            "Mag_E",
            "Setup1 : LastAdaptive",
            self.aedtapp.available_variations.nominal_w_values,
            os.path.join(self.local_scratch.path, "MagEfieldSph.fld"),
            gridtype="Spherical",
            grid_stop=[5, 300, 300],
            grid_step=[5, 50, 50],
            isvector=False,
            intrinsics="5GHz",
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "MagEfieldSph.fld"))

        self.aedtapp.post.export_field_file_on_grid(
            "Mag_E",
            "Setup1 : LastAdaptive",
            self.aedtapp.available_variations.nominal_w_values,
            os.path.join(self.local_scratch.path, "MagEfieldCyl.fld"),
            gridtype="Cylindrical",
            grid_stop=[5, 300, 5],
            grid_step=[5, 50, 5],
            isvector=False,
            intrinsics="5GHz",
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "MagEfieldCyl.fld"))

    # @pytest.mark.skipif(
    #     config["NonGraphical"], reason="Skipped because it cannot run on build machine in non-graphical mode"
    # )
    def test_07_copydata(self):
        assert self.aedtapp.post.copy_report_data("MyTestScattering")

    def test_08_manipulate_report(self):
        assert self.aedtapp.post.rename_report("MyTestScattering", "MyNewScattering")
        assert [plot for plot in self.aedtapp.post.plots if plot.plot_name == "MyNewScattering"]
        assert not self.aedtapp.post.rename_report("invalid", "MyNewScattering")

    def test_09_manipulate_report(self):
        assert self.aedtapp.post.create_report("dB(S(1,1))")
        assert self.aedtapp.post.create_report(
            expressions="MaxMagDeltaS",
            variations={"Pass": ["All"]},
            setup_sweep_name="Setup1 : AdaptivePass",
            primary_sweep_variable="Pass",
            report_category="Modal Solution Data",
            plot_type="Rectangular Plot",
            plotname="Solution Convergence Plot",
        )
        new_report = self.aedtapp.post.reports_by_category.modal_solution("dB(S(1,1))")
        assert new_report.create()

        data = self.aedtapp.post.get_solution_data("S(1,1)")
        assert data.primary_sweep == "Freq"
        assert data.expressions[0] == "S(1,1)"
        assert len(self.aedtapp.post.all_report_names) > 0

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
        files = self.aedtapp.export_results()
        assert len(files) > 0
        files = self.circuit_test.export_results()
        assert len(files) > 0
        self.q2dtest.analyze()
        files = self.q2dtest.export_results()
        assert len(files) > 0
        self.q3dtest.analyze_setup("Setup1")
        files = self.q3dtest.export_results()
        assert len(files) > 0

    def test_09c_import_into_report(self):
        new_report = self.aedtapp.create_scattering("import_test")
        csv_file_path = self.aedtapp.post.export_report_to_csv(self.local_scratch.path, "import_test")
        rdat_file_path = self.aedtapp.post.export_report_to_file(self.local_scratch.path, "import_test", ".rdat")
        plot_name = new_report.plot_name

        trace_names = []
        trace_names.append(new_report.expressions[0])
        families = {"Freq": ["All"]}
        for el in self.aedtapp.available_variations.nominal_w_values_dict:
            families[el] = self.aedtapp.available_variations.nominal_w_values_dict[el]

        # get solution data and save in .csv file
        my_data = self.aedtapp.post.get_solution_data(expressions=trace_names, variations=families)
        my_data.export_data_to_csv(os.path.join(self.local_scratch.path, "output.csv"))
        csv_solution_data_file_path = os.path.join(self.local_scratch.path, "output.csv")
        assert not new_report.import_traces(csv_solution_data_file_path, plot_name)

        # test import with correct inputs from csv
        assert new_report.import_traces(csv_file_path, plot_name)
        # test import with correct inputs from rdat
        assert new_report.import_traces(rdat_file_path, plot_name)
        # test import with not existing plot_name
        if not is_ironpython:
            with pytest.raises(ValueError):
                new_report.import_traces(csv_file_path, "plot_name")
            # test import with random file path
            with pytest.raises(FileExistsError):
                new_report.import_traces(str(uuid.uuid4()), plot_name)
            # test import without plot_name
            with pytest.raises(ValueError):
                new_report.import_traces(csv_file_path, None)

    def test_09d_delete_traces_from_report(self):
        new_report = self.aedtapp.create_scattering("delete_traces_test")
        traces_to_delete = [new_report.expressions[0]]
        plot_name = new_report.plot_name
        assert new_report.delete_traces(plot_name, traces_to_delete)
        if not is_ironpython:
            with pytest.raises(ValueError):
                new_report.delete_traces("plot_name", traces_to_delete)
            with pytest.raises(ValueError):
                new_report.delete_traces(plot_name, ["V(out)_Test"])

    def test_09e_add_traces_to_report(self):
        new_report = self.aedtapp.create_scattering("add_traces_test")
        traces = new_report.get_solution_data().expressions
        assert new_report.add_trace_to_report(traces)
        setup = self.aedtapp.post.plots[0].setup
        variations = self.aedtapp.post.plots[0].variations["height"] = "10mm"
        assert not new_report.add_trace_to_report(traces, setup, variations)
        variations = self.aedtapp.post.plots[0].variations
        assert new_report.add_trace_to_report(traces, setup, variations)
        setup = "Transient"
        assert not new_report.add_trace_to_report(traces, setup, variations)

    def test_09f_update_trace_name(self):
        report = [plot for plot in self.aedtapp.post.plots if plot.plot_name == "add_traces_test"][0]
        old_trace_name = report.traces[0].name
        assert old_trace_name in report.traces[0].aedt_name
        new_name = "update_trace_name_test"
        report.traces[0].name = new_name
        assert new_name in report.traces[0].aedt_name

    def test_09g_update_traces_in_report(self):
        new_report = self.aedtapp.create_scattering("update_traces_test")
        traces = new_report.get_solution_data().expressions
        assert new_report.update_trace_in_report(traces)
        setup = self.aedtapp.post.plots[0].setup
        variations = self.aedtapp.post.plots[0].variations["height"] = "10mm"
        assert not new_report.add_trace_to_report(traces, setup, variations)
        variations = self.aedtapp.post.plots[0].variations
        assert new_report.update_trace_in_report(traces, setup, variations)

    @pytest.mark.skipif(
        config["desktopVersion"] < "2022.2", reason="Not working in non-graphical mode in version earlier than 2022.2."
    )
    def test_09h_create_monitor(self):  # pragma: no cover
        assert self.aedtapp.post.create_report("dB(S(1,1))")
        new_report = self.aedtapp.post.reports_by_category.modal_solution("dB(S(1,1))")
        assert new_report.create()

        assert new_report.add_cartesian_x_marker("3GHz")
        assert new_report.add_cartesian_y_marker("-55")

    @pytest.mark.skipif(
        config["desktopVersion"] < "2022.2",
        reason="Skipped because it cannot run on build machine in non-graphical mode",
    )
    def test_09i_add_line_from_point(self):  # pragma: no cover
        new_report = self.aedtapp.post.reports_by_category.modal_solution("dB(S(1,1))")
        assert new_report.create()
        assert new_report.add_limit_line_from_points([3, 5, 5, 3], [-50, -50, -60, -60], "GHz")

    @pytest.mark.skipif(
        config["desktopVersion"] < "2022.2", reason="Not working in non-graphical mode in version earlier than 2022.2."
    )
    def test_09l_add_line_from_equation(self):
        new_report = self.aedtapp.post.reports_by_category.modal_solution("dB(S(1,1))")
        assert new_report.create()
        assert new_report.add_limit_line_from_equation(start_x=1, stop_x=20, step=0.5, units="GHz")

    @pytest.mark.skipif(
        config["desktopVersion"] < "2022.2", reason="Not working in non-graphical mode in version earlier than 2022.2."
    )
    def test_09m_edit_properties(self):
        report = self.aedtapp.post.create_report("dB(S(1,1))")
        assert report.edit_grid()
        assert report.edit_grid(minor_x=False)
        assert report.edit_grid(major_y=False)
        assert report.edit_grid(major_color=(0, 0, 125))
        assert report.edit_grid(major_color=(0, 255, 0))
        assert report.edit_grid(style_major="Dot")
        assert report.edit_x_axis(font="Courier", font_size=14, italic=True, bold=False, color=(0, 128, 0))
        assert report.edit_y_axis(font="Courier", font_size=14, italic=True, bold=False, color=(0, 128, 0))
        assert report.edit_x_axis(
            font="Courier", font_size=14, italic=True, bold=False, color=(0, 128, 0), label="Freq"
        )
        assert report.edit_y_axis(
            font="Courier", font_size=14, italic=True, bold=False, color=(0, 128, 0), label="Touchstone"
        )

        assert report.edit_x_axis_scaling(
            linear_scaling=True,
            min_scale="1GHz",
            max_scale="5GHz",
            minor_tick_divs=10,
            min_spacing="0.5GHz",
            units="MHz",
        )
        assert report.edit_y_axis_scaling(
            linear_scaling=False, min_scale="-50", max_scale="10", minor_tick_divs=10, min_spacing="5"
        )
        assert report.edit_legend(
            show_solution_name=True, show_variation_key=False, show_trace_name=False, back_color=(255, 255, 255)
        )
        assert report.edit_header(
            company_name="PyAEDT",
            show_design_name=True,
            font="Arial",
            title_size=12,
            subtitle_size=12,
            italic=False,
            bold=False,
            color=(0, 125, 125),
        )
        assert report.edit_general_settings(
            background_color=(128, 255, 255),
            plot_color=(255, 0, 255),
            enable_y_stripes=True,
            field_width=6,
            precision=6,
            use_scientific_notation=True,
        )

    @pytest.mark.skipif(
        config["desktopVersion"] < "2022.2", reason="Not working in non-graphical mode in version earlier than 2022.2."
    )
    def test_09n_add_line_from_point(self):  # pragma: no cover
        new_report = self.aedtapp.post.reports_by_category.modal_solution("dB(S(1,1))")
        new_report.create()
        style = new_report.traces[0].LINESTYLE
        trace = new_report.traces[0].TRACETYPE
        symbols = new_report.traces[0].SYMBOLSTYLE

        assert new_report.traces[0].set_trace_properties(
            trace_style=style.Dot, width=5, trace_type=trace.Digital, color=(0, 255, 0)
        )
        assert new_report.traces[0].set_symbol_properties(
            show=True, style=symbols.Box, show_arrows=False, fill=False, color=(0, 0, 255)
        )
        new_report.add_limit_line_from_points([3, 5, 5, 3], [-50, -50, -60, -60], "GHz")
        assert new_report.limit_lines[0].set_line_properties(
            style=style.Dot, width=4, hatch_above=False, violation_emphasis=True, hatch_pixels=1, color=(255, 255, 0)
        )
        pass

    @pytest.mark.skipif(
        config["desktopVersion"] < "2022.2", reason="Not working in non-graphical mode in version earlier than 2022.2."
    )
    def test_09o_add_note(self):  # pragma: no cover
        new_report = self.aedtapp.post.reports_by_category.modal_solution()
        new_report.create()

        new_report.add_note("Test", 8000, 1500)
        assert new_report.notes[0].set_note_properties(
            back_color=(0, 0, 255),
            border_visibility=False,
            border_width=3,
            font="Cambria",
            italic=True,
            bold=True,
            font_size=10,
            color=(255, 0, 0),
        )
        pass

    def test_10_delete_report(self):
        plots_number = len(self.aedtapp.post.plots)
        assert self.aedtapp.post.delete_report("MyNewScattering")
        assert len(self.aedtapp.post.plots) == plots_number - 1
        assert self.aedtapp.post.delete_report()
        assert len(self.aedtapp.post.plots) == 0

    def test_12_steal_on_focus(self):
        assert self.aedtapp.post.steal_focus_oneditor()

    def test_13_export_model_picture(self):
        path = self.aedtapp.post.export_model_picture(full_name=os.path.join(self.local_scratch.path, "images1.jpg"))
        assert path
        path = self.aedtapp.post.export_model_picture(show_axis=True, show_grid=False, show_ruler=True)
        assert path
        path = self.aedtapp.post.export_model_picture()
        assert path

    @pytest.mark.skipif(is_linux or sys.version_info < (3, 8), reason="Not running in ironpython")
    def test_14_Field_Ploton_cutplanedesignname(self):
        cutlist = ["Global:XY"]
        setup_name = self.aedtapp.existing_analysis_sweeps[0]
        quantity_name = "ComplexMag_E"
        intrinsic = {"Freq": "5GHz", "Phase": "180deg"}
        self.aedtapp.logger.info("Generating the plot")
        plot1 = self.aedtapp.post.create_fieldplot_cutplane(cutlist, quantity_name, setup_name, intrinsic)
        plot1.IsoVal = "Tone"
        assert plot1.update_field_plot_settings()
        self.aedtapp.logger.info("Generating the image")
        plot_obj = self.aedtapp.post.plot_field_from_fieldplot(
            plot1.name,
            project_path=self.local_scratch.path,
            meshplot=False,
            imageformat="jpg",
            view="isometric",
            show=False,
        )
        assert os.path.exists(plot_obj.image_file)
        os.unlink(plot_obj.image_file)
        plot_obj.x_scale = 1.1
        plot_obj.y_scale = 0.9
        plot_obj.z_scale = 0.3
        assert plot_obj.x_scale == 1.1
        assert plot_obj.y_scale == 0.9
        assert plot_obj.z_scale == 0.3

        plot_obj.background_image = r"c:\filenot_exist.jpg"
        assert not plot_obj.background_image
        plot_obj.convert_fields_in_db = True
        plot_obj.log_multiplier = 20
        plot_obj.plot(plot_obj.image_file)
        assert os.path.exists(plot_obj.image_file)

    @pytest.mark.skipif(is_linux or sys.version_info < (3, 8), reason="Not running in ironpython")
    def test_14B_Field_Ploton_Vector(self):
        cutlist = ["Global:XY"]
        setup_name = self.aedtapp.existing_analysis_sweeps[0]
        quantity_name = "Vector_E"
        intrinsic = {"Freq": "5GHz", "Phase": "180deg"}
        self.aedtapp.logger.info("Generating the plot")
        plot1 = self.aedtapp.post.create_fieldplot_cutplane(cutlist, quantity_name, setup_name, intrinsic)
        plot1.IsoVal = "Tone"
        assert plot1.update_field_plot_settings()
        self.aedtapp.logger.info("Generating the image")
        plot_obj = self.aedtapp.post.plot_field(
            "Vector_E",
            cutlist,
            "CutPlane",
            setup_name=setup_name,
            intrinsics=intrinsic,
            export_path=self.local_scratch.path,
            mesh_on_fields=False,
            imageformat="jpg",
            view="isometric",
            show=False,
        )
        assert os.path.exists(plot_obj.image_file)

    @pytest.mark.skipif(is_linux or sys.version_info < (3, 8), reason="Not running in ironpython")
    def test_15_export_plot(self):
        obj = self.aedtapp.post.plot_model_obj(
            show=False, export_path=os.path.join(self.local_scratch.path, "image.jpg")
        )
        assert os.path.exists(obj.image_file)

    @pytest.mark.skipif(is_linux or sys.version_info < (3, 8), reason="Not running in ironpython")
    def test_16_create_field_plot(self):
        cutlist = ["Global:XY"]
        plot = self.aedtapp.post._create_fieldplot(
            objlist=cutlist,
            quantityName="Mag_E",
            setup_name=self.aedtapp.nominal_adaptive,
            intrinsics={},
            listtype="CutPlane",
        )
        assert plot

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

    @pytest.mark.skipif(not ipython_available, reason="plot_scene method is not supported in ironpython")
    def test_52_display(self):
        img = self.aedtapp.post.nb_display(show_axis=True, show_grid=True, show_ruler=True)
        assert isinstance(img, Image)

    def test_53_line_plot(self):
        udp1 = [0, 0, 0]
        udp2 = [1, 0, 0]
        setup_name = "Setup1 : LastAdaptive"
        intrinsic = {"Freq": "5GHz", "Phase": "180deg"}
        self.aedtapp.modeler.create_polyline([udp1, udp2], name="Poly1")
        assert self.aedtapp.post.create_fieldplot_line("Poly1", "Mag_E", setup_name, intrinsic)

    def test_54_reload(self):
        self.aedtapp.save_project()
        app2 = Hfss(self.aedtapp.project_name, specified_version=config["desktopVersion"])
        assert len(app2.post.field_plots) == len(self.aedtapp.post.field_plots)

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
        assert not self.aedtapp.post.reports_by_category.eye_diagram()
        assert not self.q3dtest.post.reports_by_category.modal_solution()
        assert not self.q3dtest.post.reports_by_category.terminal_solution()
        assert not self.q2dtest.post.reports_by_category.far_field()
        assert not self.q2dtest.post.reports_by_category.near_field()
        assert self.aedtapp.post.reports_by_category.eigenmode()
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
        assert os.path.exists(self.aedtapp.export_mesh_stats("Setup1"))

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

    def test_67_sweep_from_json(self):
        local_path = os.path.dirname(os.path.realpath(__file__))
        dict_vals = json_to_dict(os.path.join(local_path, "example_models", "report_json", "Modal_Report_Simple.json"))
        assert self.aedtapp.post.create_report_from_configuration(input_dict=dict_vals)

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

    @pytest.mark.skipif(
        config["desktopVersion"] < "2022.2", reason="Not working in non graphical in version lower than 2022.2"
    )
    def test_70_sweep_from_json(self):
        local_path = os.path.dirname(os.path.realpath(__file__))
        assert self.aedtapp.post.create_report_from_configuration(
            os.path.join(local_path, "example_models", "report_json", "Modal_Report.json")
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

        p = ffdata.polar_plot_3d_pyvista(qty_str="RealizedGain", convert_to_db=True, show=False)
        assert isinstance(p, object)

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

    def test_74_dynamic_update(self):
        val = self.aedtapp.post.update_report_dynamically
        self.aedtapp.post.update_report_dynamically = not val
        assert self.aedtapp.post.update_report_dynamically != val

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
