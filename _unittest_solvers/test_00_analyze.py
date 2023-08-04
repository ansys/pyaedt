import os
import sys
import time

import pytest


from _unittest_solvers.conftest import desktop_version
from _unittest_solvers.conftest import local_path


from pyaedt import is_linux
from pyaedt import Icepak
from pyaedt import Hfss3dLayout


sbr_platform_name = "satellite_231"
array_name = "array_231"
test_solve = "test_solve"


test_subfolder = "T00"


@pytest.fixture()
def sbr_platform(add_app):
    app = add_app(project_name=sbr_platform_name, subfolder=test_subfolder)
    yield app
    app.close_project(save_project=False)


@pytest.fixture()
def array(add_app):
    app = add_app(project_name=array_name, subfolder=test_subfolder)
    yield app
    app.close_project(save_project=False)


@pytest.fixture()
def hfss_app(add_app):
    app = add_app(project_name="Hfss_test")
    yield app
    app.close_project(save_project=False)

    
@pytest.fixture(scope="class")
def icepak_app(add_app):
    app = add_app(application=Icepak, design_name="SolveTest")
    return app


@pytest.fixture(scope="class")
def hfss3dl_solve(add_app):
    app = add_app(project_name=test_solve, application=Hfss3dLayout, subfolder=test_subfolder)
    return app


class TestClass:

    @pytest.fixture(autouse=True)
    def init(self, local_scratch, icepak_app, hfss3dl_solve):
        self.local_scratch = local_scratch
        self.icepak_app = icepak_app
        self.hfss3dl_solve = hfss3dl_solve

    @pytest.mark.skipif(is_linux or sys.version_info < (3, 8), reason="Not supported.")
    def test_01_sbr_link_array(self, sbr_platform, array):
        assert sbr_platform.create_sbr_linked_antenna(array, target_cs="antenna_CS", fieldtype="farfield")
        sbr_platform.analyze(num_cores=6)
        ffdata = sbr_platform.get_antenna_ffd_solution_data(frequencies=12e9, sphere_name="3D")
        ffdata2 = sbr_platform.get_antenna_ffd_solution_data(frequencies=12e9, sphere_name="3D", overwrite=False)

        ffdata.plot_2d_cut(
            primary_sweep="theta",
            secondary_sweep_value=[75],
            theta_scan=20,
            qty_str="RealizedGain",
            title="Azimuth at {}Hz".format(ffdata.frequency),
            convert_to_db=True,
            export_image_path=os.path.join(self.local_scratch.path, "2d1_array.jpg"),
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "2d1_array.jpg"))

        ffdata2.polar_plot_3d_pyvista(
            qty_str="RealizedGain",
            convert_to_db=True,
            show=False,
            position=[-0.11749961434125, -1.68, 0.20457438854331],
            rotation=[[1, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0]],
            export_image_path=os.path.join(self.local_scratch.path, "3d2_array.jpg"),
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "3d2_array.jpg"))

    @pytest.mark.skipif(
        desktop_version < "2022.2",
        reason="Not working in non-graphical in version lower than 2022.2",
    )
    # @pytest.mark.timeout(100)
    def test_02_hfss_export_results(self, hfss_app):
        hfss_app.insert_design("Array_simple_resuts", "Modal")
        from pyaedt.generic.DataHandlers import json_to_dict

        dict_in = json_to_dict(
            os.path.join(local_path, "../_unittest_solvers/example_models", test_subfolder, "array_simple.json"))
        dict_in["Circ_Patch_5GHz1"] = os.path.join(
            local_path, "../_unittest_solvers/example_models", test_subfolder, "Circ_Patch_5GHz.a3dcomp"
        )
        dict_in["cells"][(3, 3)] = {"name": "Circ_Patch_5GHz1"}
        assert hfss_app.add_3d_component_array_from_json(dict_in)
        dict_in["cells"][(3, 3)]["rotation"] = 90
        exported_files = hfss_app.export_results()
        assert len(exported_files) == 0
        setup = hfss_app.create_setup(setupname="test")
        setup.props["Frequency"] = "1GHz"
        exported_files = hfss_app.export_results()
        assert len(exported_files) == 0
        hfss_app.analyze_setup(name="test", num_cores=6)
        exported_files = hfss_app.export_results()
        assert len(exported_files) == 3
        exported_files = hfss_app.export_results(
            matrix_type="Y",
        )
        assert len(exported_files) > 0

    def test_03a_icepak_analyze_and_export_summary(self):
        self.icepak_app.solution_type = self.icepak_app.SOLUTIONS.Icepak.SteadyFlowOnly
        self.icepak_app.problem_type = "TemperatureAndFlow"
        self.icepak_app.modeler.create_box([0, 0, 0], [10, 10, 10], "box", "copper")
        self.icepak_app.create_source_block("box", "1W", False)
        setup = self.icepak_app.create_setup("SetupIPK")
        new_props = {"Convergence Criteria - Max Iterations": 3}
        setup.update(update_dictionary=new_props)
        airfaces = [i.id for i in self.icepak_app.modeler["Region"].faces]
        self.icepak_app.assign_openings(airfaces)
        self.icepak_app["Variable1"] = "0.5"
        assert self.icepak_app.create_output_variable("OutputVariable1", "abs(Variable1)")  # test creation
        assert self.icepak_app.create_output_variable("OutputVariable1", "asin(Variable1)")  # test update
        self.icepak_app.monitor.assign_point_monitor_in_object(
            "box", monitor_quantity="Temperature", monitor_name="test_monitor"
        )
        self.icepak_app.monitor.assign_face_monitor(
            self.icepak_app.modeler.get_object_from_name("box").faces[0].id,
            monitor_quantity=["Temperature", "HeatFlowRate"],
            monitor_name="test_monitor2",
        )
        self.icepak_app.analyze("SetupIPK", num_cores=6)
        self.icepak_app.save_project()
        self.icepak_app.export_summary(self.icepak_app.working_directory)
        box = [i.id for i in self.icepak_app.modeler["box"].faces]
        assert os.path.exists(
            self.icepak_app.eval_surface_quantity_from_field_summary(box, savedir=self.icepak_app.working_directory)
        )

    def test_03b_icepak_get_output_variable(self):
        value = self.icepak_app.get_output_variable("OutputVariable1")
        tol = 1e-9
        assert abs(value - 0.5235987755982988) < tol

    def test_03c_icepak_get_monitor_output(self):
        assert self.icepak_app.monitor.all_monitors["test_monitor"].value()
        assert self.icepak_app.monitor.all_monitors["test_monitor"].value(quantity="Temperature")
        assert self.icepak_app.monitor.all_monitors["test_monitor"].value(
            setup_name=self.icepak_app.existing_analysis_sweeps[0]
        )
        assert self.icepak_app.monitor.all_monitors["test_monitor2"].value(quantity="HeatFlowRate")

    def test_03d_icepak_eval_tempc(self):
        assert os.path.exists(
            self.icepak_app.eval_volume_quantity_from_field_summary(
                ["box"], "Temperature", savedir=self.icepak_app.working_directory
            )
        )

    def test_03e_icepak_ExportFLDFil(self):
        object_list = "box"
        fld_file = os.path.join(self.icepak_app.working_directory, "test_fld.fld")
        self.icepak_app.post.export_field_file(
            "Temp", self.icepak_app.nominal_sweep, [], filename=fld_file, obj_list=object_list
        )
        assert os.path.exists(fld_file)

    def test_04a_3dl_generate_mesh(self):
        assert self.hfss3dl_solve.mesh.generate_mesh("Setup1")

    @pytest.mark.skipif(desktop_version < "2023.2", reason="Working only from 2023 R2")
    def test_04b_3dl_analyze_setup(self):
        assert self.hfss3dl_solve.analyze_setup("Setup1", blocking=False, num_cores=6)
        assert self.hfss3dl_solve.are_there_simulations_running
        assert self.hfss3dl_solve.stop_simulations()
        while self.hfss3dl_solve.are_there_simulations_running:
            time.sleep(1)

    def test_04c_3dl_analyze_setup(self):
        assert self.hfss3dl_solve.analyze_setup("Setup1", num_cores=6)
        self.hfss3dl_solve.save_project()
        assert os.path.exists(self.hfss3dl_solve.export_profile("Setup1"))
        assert os.path.exists(self.hfss3dl_solve.export_mesh_stats("Setup1"))

    @pytest.mark.skipif(is_linux, reason="To be investigated on linux.")
    def test_04d_3dl_export_touchsthone(self):
        filename = os.path.join(self.local_scratch.path, "touchstone.s2p")
        solution_name = "Setup1"
        sweep_name = "Sweep1"
        assert self.hfss3dl_solve.export_touchstone(solution_name, sweep_name, filename)
        assert os.path.exists(filename)
        assert self.hfss3dl_solve.export_touchstone(solution_name)
        sweep_name = None
        assert self.hfss3dl_solve.export_touchstone(solution_name, sweep_name)

    def test_04e_3dl_export_results(self):
        files = self.hfss3dl_solve.export_results()
        assert len(files) > 0

    def test_04f_3dl_set_export_touchstone(self):
        assert self.hfss3dl_solve.set_export_touchstone(True)
        assert self.hfss3dl_solve.set_export_touchstone(False)

    def test_04g_3dl_get_all_sparameter_list(self):
        assert self.hfss3dl_solve.get_all_sparameter_list == ["S(Port1,Port1)", "S(Port1,Port2)", "S(Port2,Port2)"]

    def test_04h_3dl_get_all_return_loss_list(self):
        assert self.hfss3dl_solve.get_all_return_loss_list() == ["S(Port1,Port1)", "S(Port2,Port2)"]

    def test_04i_3dl_get_all_insertion_loss_list(self):
        assert self.hfss3dl_solve.get_all_insertion_loss_list() == ["S(Port1,Port1)", "S(Port2,Port2)"]

    def test_04j_3dl_get_next_xtalk_list(self):
        assert self.hfss3dl_solve.get_next_xtalk_list() == ["S(Port1,Port2)"]

    def test_04k_3dl_get_fext_xtalk_list(self):
        assert self.hfss3dl_solve.get_fext_xtalk_list() == ["S(Port1,Port2)", "S(Port2,Port1)"]
