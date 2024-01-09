import csv
import os
import sys
import time

import pytest


from _unittest_solvers.conftest import desktop_version
from _unittest_solvers.conftest import local_path


from pyaedt import is_linux
from pyaedt import Icepak
from pyaedt import Hfss3dLayout
from pyaedt import Circuit, Maxwell3d
from _unittest.conftest import config

sbr_platform_name = "satellite_231"
array_name = "array_231"
test_solve = "test_solve"
original_project_name = "Galileo_t21_231"
transient = "Transient_StrandedWindings"

if config["desktopVersion"] > "2022.2":
    component = "Circ_Patch_5GHz_232.a3dcomp"
else:
    component = "Circ_Patch_5GHz.a3dcomp"

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
def sbr_app(add_app):
    app = add_app(project_name="SBR_test", solution_type="SBR+")
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

@pytest.fixture(scope="class")
def circuit_app(add_app):
    app = add_app(original_project_name, application=Circuit, subfolder=test_subfolder)
    app.modeler.schematic_units = "mil"
    return app

@pytest.fixture(scope="class")
def m3dtransient(add_app):
    app = add_app(application=Maxwell3d, project_name=transient, subfolder=test_subfolder)
    return app


class TestClass:

    @pytest.fixture(autouse=True)
    def init(self, local_scratch, icepak_app, hfss3dl_solve):
        self.local_scratch = local_scratch
        self.icepak_app = icepak_app
        self.hfss3dl_solve = hfss3dl_solve

    @pytest.mark.skipif(is_linux or sys.version_info < (3, 8), reason="Not supported.")
    def test_01a_sbr_link_array(self, sbr_platform, array):
        assert sbr_platform.create_sbr_linked_antenna(array, target_cs="antenna_CS", fieldtype="farfield")
        sbr_platform.analyze(num_cores=6)
        ffdata = sbr_platform.get_antenna_ffd_solution_data(frequencies=12e9, sphere_name="3D")
        ffdata2 = sbr_platform.get_antenna_ffd_solution_data(frequencies=12e9, sphere_name="3D", overwrite=False)

        ffdata.plot_2d_cut(
            primary_sweep="theta",
            secondary_sweep_value=[75],
            theta_scan=20,
            farfield_quantity="RealizedGain",
            title="Azimuth at {}Hz".format(ffdata.frequency),
            quantity_format="dB10",
            export_image_path=os.path.join(self.local_scratch.path, "2d1_array.jpg"),
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "2d1_array.jpg"))

        ffdata2.polar_plot_3d_pyvista(
            farfield_quantity="RealizedGain",
            convert_to_db=True,
            show=False,
            rotation=[[1, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0]],
            export_image_path=os.path.join(self.local_scratch.path, "3d2_array.jpg"),
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "3d2_array.jpg"))

    def test_01b_sbr_create_vrt(self, sbr_app):
        sbr_app.rename_design("vtr")
        sbr_app.modeler.create_sphere([10, 10, 10], 5, matname="copper")
        vrt = sbr_app.post.create_sbr_plane_visual_ray_tracing(max_frequency="10GHz", incident_theta="40deg")
        assert vrt
        vrt.incident_phi = "30deg"
        assert vrt.update()
        assert vrt.delete()
        vrt = sbr_app.post.create_sbr_point_visual_ray_tracing(max_frequency="10GHz")
        assert vrt
        vrt.custom_location = [10, 10, 0]
        assert vrt.update()
        assert vrt.delete()

    def test_01c_sbr_create_vrt_creeping(self, sbr_app):
        sbr_app.rename_design("vtr_creeping")
        sbr_app.modeler.create_sphere([10, 10, 10], 5, matname="copper")
        vrt = sbr_app.post.create_creeping_plane_visual_ray_tracing(max_frequency="10GHz")
        assert vrt
        vrt.incident_phi = "30deg"
        assert vrt.update()
        assert vrt.delete()
        vrt = sbr_app.post.create_creeping_point_visual_ray_tracing(max_frequency="10GHz")
        assert vrt
        vrt.custom_location = [10, 10, 0]
        assert vrt.update()
        assert vrt.delete()

    @pytest.mark.skipif(
        desktop_version < "2022.2",
        reason="Not working in non-graphical in version lower than 2022.2",
    )
    def test_02_hfss_export_results(self, hfss_app):
        hfss_app.insert_design("Array_simple_resuts", "Modal")
        from pyaedt.generic.DataHandlers import json_to_dict

        if config["desktopVersion"] > "2023.1":
            dict_in = json_to_dict(
                os.path.join(local_path, "example_models", test_subfolder, "array_simple_232.json")
            )
            dict_in["Circ_Patch_5GHz_232_1"] = os.path.join(
                local_path, "example_models", test_subfolder, component
            )
            dict_in["cells"][(3, 3)] = {"name": "Circ_Patch_5GHz_232_1"}
            dict_in["cells"][(3, 3)]["rotation"] = 90
        else:
            dict_in = json_to_dict(
                os.path.join(local_path, "example_models", test_subfolder, "array_simple.json")
            )
            dict_in["Circ_Patch_5GHz1"] = os.path.join(
                local_path, "example_models", test_subfolder, component
            )
            dict_in["cells"][(3, 3)] = {"name": "Circ_Patch_5GHz1"}
            dict_in["cells"][(3, 3)]["rotation"] = 90
        hfss_app.add_3d_component_array_from_json(dict_in)
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

        assert self.icepak_app.export_summary(self.icepak_app.working_directory, geometryType="Surface", variationlist=[], filename="A") # check usage of deprecated arguments
        assert self.icepak_app.export_summary(self.icepak_app.working_directory, geometry_type="Surface", variation_list=[], filename="B")
        assert self.icepak_app.export_summary(self.icepak_app.working_directory, geometry_type="Volume", type="Boundary", filename="C")
        for file_name, entities in [("A_Temperature.csv", ["box", "Region"]), ("B_Temperature.csv", ["box", "Region"]), ("C_Temperature.csv", ["box"])]:
            with open(os.path.join(self.icepak_app.working_directory, file_name), 'r', newline='') as csv_file:
                csv_reader = csv.reader(csv_file)
                for _ in range(4):
                    _ = next(csv_reader)
                header = next(csv_reader)
                entity_index = header.index("Entity")
                csv_entities=[row[entity_index] for row in csv_reader]
                assert all(e in csv_entities for e in entities)

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
    def test_04d_3dl_export_touchstone(self):
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

    def test_05a_circuit_add_3dlayout_component(self, circuit_app):
        setup = circuit_app.create_setup("test_06b_LNA")
        setup.add_sweep_step(start_point=0, end_point=5, step_size=0.01)
        myedb = circuit_app.modeler.schematic.add_subcircuit_3dlayout("Galileo_G87173_204")
        assert type(myedb.id) is int
        ports = myedb.pins
        tx = ports
        rx = ports
        insertions = ["dB(S({},{}))".format(i.name, j.name) for i, j in zip(tx, rx)]
        assert circuit_app.post.create_report(
            insertions,
            circuit_app.nominal_adaptive,
            plotname="Insertion Losses",
            plot_type="Rectangular Plot",
            report_category="Standard",
            subdesign_id=myedb.id,
        )
        new_report = circuit_app.post.reports_by_category.standard(insertions)
        new_report.sub_design_id = myedb.id
        assert new_report.create()

    def test_05b_circuit_add_hfss_component(self, circuit_app):
        my_model, myname = circuit_app.modeler.schematic.create_field_model(
            "uUSB", "Setup1 : Sweep", ["usb_N_conn", "usb_N_pcb", "usb_P_conn", "usb_P_pcb"]
        )
        assert type(my_model) is int

    def test_05c_circuit_push_excitation(self, circuit_app):
        setup_name = "test_07a_LNA"
        setup = circuit_app.create_setup(setup_name)
        setup.add_sweep_step(start_point=0, end_point=5, step_size=0.01)
        assert circuit_app.push_excitations(instance_name="U1", setup_name=setup_name, thevenin_calculation=False)
        assert circuit_app.push_excitations(instance_name="U1", setup_name=setup_name, thevenin_calculation=True)

    def test_05d_circuit_push_excitation_time(self,circuit_app):
        setup_name = "test_07b_Transient"
        setup = circuit_app.create_setup(setup_name, setuptype="NexximTransient")
        assert circuit_app.push_time_excitations(instance_name="U1", setup_name=setup_name)

    def test_06_m3d_harmonic_forces(self, m3dtransient):
        assert m3dtransient.enable_harmonic_force(
            ["Stator"],
            force_type=2,
            window_function="Rectangular",
            use_number_of_last_cycles=True,
            last_cycles_number=3,
            calculate_force="Harmonic",
        )
        m3dtransient.save_project()
        m3dtransient.analyze(m3dtransient.active_setup, num_cores=2)
        assert m3dtransient.export_element_based_harmonic_force(
            start_frequency=1, stop_frequency=100, number_of_frequency=None
        )
        assert m3dtransient.export_element_based_harmonic_force(number_of_frequency=5)