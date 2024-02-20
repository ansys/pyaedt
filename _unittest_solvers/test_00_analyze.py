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
from pyaedt.generic.spisim import SpiSim

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
erl_project_name = "erl_unit_test"
com_project_name = "com_unit_test_23r2"


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
def circuit_erl(add_app):
    app = add_app(erl_project_name, design_name="2ports", application=Circuit, subfolder=test_subfolder)
    return app


@pytest.fixture(scope="class")
def circuit_com(add_app):
    app = add_app(com_project_name, design_name="0_simple_channel", application=Circuit, subfolder=test_subfolder)
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
        from pyaedt.generic.general_methods import read_json

        if config["desktopVersion"] > "2023.1":
            dict_in = read_json(os.path.join(local_path, "example_models", test_subfolder, "array_simple_232.json"))
            dict_in["Circ_Patch_5GHz_232_1"] = os.path.join(local_path, "example_models", test_subfolder, component)
            dict_in["cells"][(3, 3)] = {"name": "Circ_Patch_5GHz_232_1"}
            dict_in["cells"][(3, 3)]["rotation"] = 90
        else:
            dict_in = read_json(os.path.join(local_path, "example_models", test_subfolder, "array_simple.json"))
            dict_in["Circ_Patch_5GHz1"] = os.path.join(local_path, "example_models", test_subfolder, component)
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

        fld_file1 = os.path.join(self.local_scratch.path, "test_fld_hfss1.fld")
        assert hfss_app.post.export_field_file(
            quantity_name="Mag_E", filename=fld_file1, obj_list="Box1", intrinsics="1GHz", phase="5deg"
        )
        assert os.path.exists(fld_file1)
        fld_file2 = os.path.join(self.local_scratch.path, "test_fld_hfss2.fld")
        assert hfss_app.post.export_field_file(
            quantity_name="Mag_E", filename=fld_file2, obj_list="Box1", intrinsics="1GHz"
        )
        assert os.path.exists(fld_file2)

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

        assert self.icepak_app.export_summary(
            self.icepak_app.working_directory, geometryType="Surface", variationlist=[], filename="A"
        )  # check usage of deprecated arguments
        assert self.icepak_app.export_summary(
            self.icepak_app.working_directory, geometry_type="Surface", variation_list=[], filename="B"
        )
        assert self.icepak_app.export_summary(
            self.icepak_app.working_directory, geometry_type="Volume", type="Boundary", filename="C"
        )
        for file_name, entities in [
            ("A_Temperature.csv", ["box", "Region"]),
            ("B_Temperature.csv", ["box", "Region"]),
            ("C_Temperature.csv", ["box"]),
        ]:
            with open(os.path.join(self.icepak_app.working_directory, file_name), "r", newline="") as csv_file:
                csv_reader = csv.reader(csv_file)
                for _ in range(4):
                    _ = next(csv_reader)
                header = next(csv_reader)
                entity_index = header.index("Entity")
                csv_entities = [row[entity_index] for row in csv_reader]
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
        fld_file = os.path.join(self.local_scratch.path, "test_fld.fld")
        self.icepak_app.post.export_field_file(
            quantity_name="Temp",
            solution=self.icepak_app.nominal_sweep,
            variation_dict={},
            filename=fld_file,
            obj_list="box",
        )
        assert os.path.exists(fld_file)
        fld_file_1 = os.path.join(self.local_scratch.path, "test_fld_1.fld")
        sample_points_file = os.path.join(local_path, "example_models", test_subfolder, "temp_points.pts")
        self.icepak_app.post.export_field_file(
            quantity_name="Temp",
            solution=self.icepak_app.nominal_sweep,
            variation_dict=self.icepak_app.available_variations.nominal_w_values_dict,
            filename=fld_file_1,
            obj_list="box",
            sample_points_file=sample_points_file,
        )
        assert os.path.exists(fld_file_1)
        fld_file_2 = os.path.join(self.local_scratch.path, "test_fld_2.fld")
        self.icepak_app.post.export_field_file(
            quantity_name="Temp",
            solution=self.icepak_app.nominal_sweep,
            variation_dict=self.icepak_app.available_variations.nominal_w_values_dict,
            filename=fld_file_2,
            obj_list="box",
            sample_points_lists=[[0, 0, 0], [3, 6, 8], [4, 7, 9]],
        )
        assert os.path.exists(fld_file_2)

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

    def test_05d_circuit_push_excitation_time(self, circuit_app):
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

    def test_07_export_maxwell_fields(self, m3dtransient):
        m3dtransient.analyze(m3dtransient.active_setup, num_cores=2)
        fld_file_3 = os.path.join(self.local_scratch.path, "test_fld_3.fld")
        assert m3dtransient.post.export_field_file(
            quantity_name="Mag_B",
            solution=m3dtransient.nominal_sweep,
            variation_dict={},
            filename=fld_file_3,
            obj_list="Coil_A2",
            intrinsics="10ms",
            obj_type="Surf",
        )
        assert os.path.exists(fld_file_3)
        fld_file_4 = os.path.join(self.local_scratch.path, "test_fld_4.fld")
        assert not m3dtransient.post.export_field_file(
            quantity_name="Mag_B",
            solution=m3dtransient.nominal_sweep,
            variation_dict=m3dtransient.available_variations.nominal_w_values_dict,
            filename=fld_file_4,
            obj_list="Coil_A2",
            obj_type="invalid",
        )
        setup = m3dtransient.setups[0]
        m3dtransient.setups[0].delete()
        assert not m3dtransient.post.export_field_file(
            quantity_name="Mag_B", variation_dict={}, filename=fld_file_4, obj_list="Coil_A2"
        )

        new_setup = m3dtransient.create_setup(setupname=setup.name, setuptype=setup.setuptype)
        new_setup.props = setup.props
        new_setup.update()

    def test_08_compute_erl(self, circuit_erl):
        touchstone_file = circuit_erl.export_touchstone()
        spisim = SpiSim(touchstone_file)

        erl_data2 = spisim.compute_erl(
            port_order="EvenOdd",
            bandwidth="40g",
            tdr_duration=4,
            z_terminations=50,
            transition_time="10p",
            fixture_delay=400e-12,
            input_amplitude=1.0,
            ber=1e-4,
        )
        assert erl_data2
        circuit_erl.set_active_design("4_ports")
        touchstone_file2 = circuit_erl.export_touchstone()
        spisim.touchstone_file = touchstone_file2
        erl_data_3 = spisim.compute_erl(specify_through_ports=[1, 2, 3, 4])
        assert erl_data_3

    def test_09a_compute_com(self, local_scratch, circuit_com):
        touchstone_file = circuit_com.export_touchstone()
        spisim = SpiSim(touchstone_file)
        assert spisim.com_standards
        assert spisim.com_parameters()

        report_dir = os.path.join(spisim.working_directory, "50GAUI-1_C2C")
        os.mkdir(report_dir)
        com_0, com_1 = spisim.compute_com(
            standard="50GAUI-1_C2C",
            out_folder=report_dir,
        )
        assert com_0 and com_1

        report_dir = os.path.join(spisim.working_directory, "100GBASE-KR4")
        os.mkdir(report_dir)
        com_0, com_1 = spisim.compute_com(
            standard="100GBASE-KR4",
            fext_s4p=[touchstone_file, touchstone_file],
            next_s4p=touchstone_file,
            out_folder=report_dir,
        )
        assert com_0 and com_1

    def test_09b_compute_com(self, local_scratch):
        com_example_file_folder = os.path.join(local_path, "example_models", test_subfolder, "com_unit_test_sparam")
        thru_s4p = local_scratch.copyfile(os.path.join(com_example_file_folder, "SerDes_Demo_02_Thru.s4p"))
        fext_s4p = local_scratch.copyfile(
            os.path.join(com_example_file_folder, "FCI_CC_Long_Link_Pair_2_to_Pair_9_FEXT.s4p")
        )
        next_s4p = local_scratch.copyfile(
            os.path.join(com_example_file_folder, "FCI_CC_Long_Link_Pair_11_to_Pair_9_NEXT.s4p")
        )

        report_dir = os.path.join(local_scratch.path, "custom")
        os.mkdir(report_dir)

        spisim = SpiSim(thru_s4p)
        spisim.export_com_configure_file(os.path.join(spisim.working_directory, "custom.cfg"))
        com_0, com_1 = spisim.compute_com(
            standard="custom",
            config_file=os.path.join(spisim.working_directory, "custom.cfg"),
            port_order="[1 3 2 4]",
            fext_s4p=fext_s4p,
            next_s4p=next_s4p,
            out_folder=report_dir,
        )
        assert com_0 and com_1

    def test_09c_compute_com(self, local_scratch):
        com_example_file_folder = os.path.join(local_path, "example_models", test_subfolder, "com_unit_test_sparam")
        snp = local_scratch.copyfile(os.path.join(com_example_file_folder, "5_C50.s20p"))

        spisim = SpiSim(snp)
        com_0, com_1 = spisim.compute_com_from_snp(
            standard="100GBASE-KR4",
            port_order="[1 3 2 4]",
            tx_rx_port="(1,2);(3,4)",
            fext_port="(5,6);(7,8);(9,10);(11,12)",
            next_port="(13,14);(15,16);(17,18);(19,20)",
        )
        assert com_0 and com_1
