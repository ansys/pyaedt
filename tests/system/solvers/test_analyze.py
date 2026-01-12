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

import csv
from datetime import timedelta
from pathlib import Path
import shutil
import sys
import time

import pytest

from ansys.aedt.core import Circuit
from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core import Icepak
from ansys.aedt.core import Maxwell3d
from ansys.aedt.core import Rmxprt
from ansys.aedt.core.generic.settings import is_linux
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modules.profile import MemoryGB
from ansys.aedt.core.modules.profile import Profiles
from ansys.aedt.core.modules.profile import SimulationProfile
from ansys.aedt.core.visualization.post.spisim import SpiSim
from tests import TESTS_SOLVERS_PATH
from tests.conftest import DESKTOP_VERSION

TEST_SUBFOLDER = "T00"

SBR_PLATFORM = "satellite_231"
ICEPAK_SOLVED = "icepak_summary_solved"
SBR_PLATFORM_SOLVED = "satellite_solved"
ARRAY_ANTENNA = "array_231"
TEST_SOLVE = "test_solve"
TEST_3LD_SOLVE = "h3dl_test_solved"
ANSYS_HSD_V1 = "ANSYS-HSD_V1"
TRANSIENT = "Transient_StrandedWindings"
ERL_PROJECT = "erl_unit_test"
COM_PROJECT = "com_unit_test_23r2"
COMPONENT = "Circ_Patch_5GHz_232.a3dcomp"


@pytest.fixture
def icepak_solved(add_app_example):
    app = add_app_example(project=ICEPAK_SOLVED, subfolder=TEST_SUBFOLDER, application=Icepak)
    yield app
    app.close_project(save=False)


@pytest.fixture
def sbr_platform(add_app_example):
    app = add_app_example(project=SBR_PLATFORM, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(save=False)


@pytest.fixture
def sbr_platform_solved(add_app_example):
    app = add_app_example(project=SBR_PLATFORM_SOLVED, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(save=False)


@pytest.fixture
def sbr_app(add_app):
    app = add_app(project="SBR_test", solution_type="SBR+")
    yield app
    app.close_project(save=False)


@pytest.fixture
def hfss_app(add_app):
    app = add_app(project="Hfss_test")
    yield app
    app.close_project(save=False)


@pytest.fixture
def hfss3dl_solve(add_app_example):
    app = add_app_example(project=TEST_SOLVE, application=Hfss3dLayout, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(save=False)


@pytest.fixture
def hfss3dl_solved(add_app_example):
    app = add_app_example(project=TEST_3LD_SOLVE, application=Hfss3dLayout, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(save=False)


@pytest.fixture
def circuit_app(add_app_example):
    app = add_app_example(project=ANSYS_HSD_V1, application=Circuit, subfolder=TEST_SUBFOLDER)
    app.modeler.schematic_units = "mil"
    yield app
    app.close_project(save=False)


@pytest.fixture
def circuit_erl(add_app_example):
    app = add_app_example(project=ERL_PROJECT, design="2ports", application=Circuit, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(save=False)


@pytest.fixture
def circuit_com(add_app_example):
    app = add_app_example(project=COM_PROJECT, design="0_simple_channel", application=Circuit, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(save=False)


@pytest.fixture
def m3dtransient(add_app_example):
    app = add_app_example(application=Maxwell3d, project=TRANSIENT, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(save=False)


def test_3dl_generate_mesh(hfss3dl_solve):
    assert hfss3dl_solve.mesh.generate_mesh("Setup1")


@pytest.mark.skipif(DESKTOP_VERSION < "2023.2", reason="Working only from 2023 R2")
def test_3dl_analyze_setup(hfss3dl_solve):
    assert hfss3dl_solve.export_touchstone_on_completion(export=False)
    assert hfss3dl_solve.export_touchstone_on_completion(export=True)
    if DESKTOP_VERSION > "2024.2":
        assert hfss3dl_solve.set_export_touchstone()
    else:
        with pytest.raises(AEDTRuntimeError):
            hfss3dl_solve.set_export_touchstone()
    assert hfss3dl_solve.analyze_setup("Setup1", cores=4, blocking=False)
    assert hfss3dl_solve.are_there_simulations_running
    assert hfss3dl_solve.stop_simulations()
    while hfss3dl_solve.are_there_simulations_running:
        time.sleep(1)
    profile = hfss3dl_solve.setups[0].get_profile()
    key0 = list(profile.keys())[0]
    assert key0 == "Setup1"
    assert isinstance(profile[key0], SimulationProfile)
    assert profile[key0].elapsed_time > timedelta(0)
    assert profile[key0].product == "HFSS3DLayout"
    assert profile[key0].max_memory() > MemoryGB(0.01)


def test_3dl_export_profile(hfss3dl_solved, test_tmp_dir):
    profile_file = test_tmp_dir / "temp.prof"
    profile_file = Path(hfss3dl_solved.export_profile("Setup1", output_file=profile_file))
    assert profile_file.exists()
    mesh_file = test_tmp_dir / "temp.msh"
    mesh_file = Path(hfss3dl_solved.export_mesh_stats("Setup1", output_file=mesh_file))
    assert mesh_file.exists()

    setup = hfss3dl_solved.setups[0]
    profiles = setup.get_profile()
    key0 = list(profiles.keys())[0]
    profile = profiles[key0]
    assert profile
    assert profile.max_memory() > MemoryGB(0.0)

    assert profile.elapsed_time > timedelta(seconds=0)
    assert profile.product == "HFSS3DLayout"
    sweep_names = list(profile.frequency_sweeps.keys())
    assert len(sweep_names) == 1
    sweep_name = sweep_names[0]
    assert (
        len(profile.frequency_sweeps[sweep_name].frequencies) > 0
    )  # This value depends on AEDT version used to solve.
    assert profile.frequency_sweeps[sweep_name].elapsed_time > timedelta(seconds=1)
    assert profile.num_adaptive_passes
    adaptive_passes = profile.num_adaptive_passes
    assert profile.max_memory() > profile.max_memory(adaptive_passes - 1)


@pytest.mark.skipif(is_linux or sys.version_info < (3, 8), reason="Not supported.")
def test_sbr_link_array(sbr_platform, add_app_example):
    app = add_app_example(project=ARRAY_ANTENNA, subfolder=TEST_SUBFOLDER, close_projects=False)
    assert sbr_platform.create_sbr_linked_antenna(app, target_cs="antenna_CS", field_type="farfield")
    profile = sbr_platform.setups[0].get_profile()
    assert profile is None
    app.close_project(save=False)


@pytest.mark.skipif(is_linux or sys.version_info < (3, 8), reason="Not supported.")
def test_sbr_link_array_solved(sbr_platform_solved, test_tmp_dir):
    profile = sbr_platform_solved.setups[0].get_profile()
    assert isinstance(profile, Profiles)
    key0 = list(profile.keys())[0]
    assert profile[key0].elapsed_time > timedelta(0)
    assert isinstance(profile[key0], SimulationProfile)
    assert not sbr_platform_solved.get_profile("Invented_setup")
    solution_data = sbr_platform_solved.setups[0].get_solution_data()

    ffdata = sbr_platform_solved.get_antenna_data(frequencies=solution_data.intrinsics["Freq"], sphere="3D")
    ffdata2 = sbr_platform_solved.get_antenna_data(
        frequencies=solution_data.intrinsics["Freq"][0], sphere="3D", overwrite=False
    )

    ffdata.farfield_data.plot_cut(
        quantity="RealizedGain",
        primary_sweep="theta",
        secondary_sweep_value=[75],
        theta=20,
        title=f"Azimuth at {ffdata.farfield_data.frequency}Hz",
        quantity_format="dB10",
        show=False,
        output_file=test_tmp_dir / "2d1_array.jpg",
    )
    assert (test_tmp_dir / "2d1_array.jpg").exists()
    assert Path(ffdata2.metadata_file).is_file()


def test_sbr_create_vrt(sbr_app):
    sbr_app.rename_design("vtr")
    sbr_app.modeler.create_sphere([10, 10, 10], 5, material="copper")
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


def test_sbr_create_vrt_creeping(sbr_app):
    sbr_app.rename_design("vtr_creeping")
    sbr_app.modeler.create_sphere([10, 10, 10], 5, material="copper")
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
    DESKTOP_VERSION < "2022.2",
    reason="Not working in non-graphical in version lower than 2022.2",
)
def test_hfss_export_results(hfss_app, test_tmp_dir):
    hfss_app.insert_design("Array_simple_resuts", "Modal")
    from ansys.aedt.core.generic.file_utils import read_json

    if DESKTOP_VERSION > "2023.1":
        dict_in = read_json(Path(TESTS_SOLVERS_PATH) / "example_models" / TEST_SUBFOLDER / "array_simple_232.json")
        dict_in["Circ_Patch_5GHz_232_1"] = Path(TESTS_SOLVERS_PATH) / "example_models" / TEST_SUBFOLDER / COMPONENT
        dict_in["cells"][(3, 3)] = {"name": "Circ_Patch_5GHz_232_1"}
        dict_in["cells"][(3, 3)]["rotation"] = 90
    else:
        dict_in = read_json(Path(TESTS_SOLVERS_PATH) / "example_models" / TEST_SUBFOLDER / "array_simple.json")
        dict_in["Circ_Patch_5GHz1"] = Path(TESTS_SOLVERS_PATH) / "example_models" / TEST_SUBFOLDER / COMPONENT
        dict_in["cells"][(3, 3)] = {"name": "Circ_Patch_5GHz1"}
        dict_in["cells"][(3, 3)]["rotation"] = 90
    hfss_app.create_3d_component_array(dict_in)
    exported_files = hfss_app.export_results()
    assert len(exported_files) == 0
    setup_driven = hfss_app.create_setup(name="test", setup_type="HFSSDriven", MaximumPasses=1)
    exported_files = hfss_app.export_results()
    solve_freq = setup_driven.props["Frequency"]
    assert len(exported_files) == 0
    hfss_app.analyze_setup(name="test", cores=4)
    assert setup_driven.is_solved
    exported_files = hfss_app.export_results()
    assert len(exported_files) == 3
    exported_files = hfss_app.export_results(
        matrix_type="Y",
    )
    assert len(exported_files) > 0
    fld_file1 = test_tmp_dir / "test_fld_hfss1.fld"
    assert hfss_app.post.export_field_file(
        quantity="Mag_E", output_file=fld_file1, assignment="Box1", intrinsics=solve_freq, phase="5deg"
    )
    assert fld_file1.exists()
    fld_file2 = test_tmp_dir / "test_fld_hfss2.fld"
    assert hfss_app.post.export_field_file(
        quantity="Mag_E", output_file=fld_file2, assignment="Box1", intrinsics={"frequency": solve_freq}
    )
    assert fld_file2.exists()
    fld_file2 = test_tmp_dir / "test_fld_hfss3.fld"
    assert hfss_app.post.export_field_file(
        quantity="Mag_E",
        output_file=fld_file2,
        assignment="Box1",
        intrinsics={"frequency": solve_freq, "phase": "30deg"},
    )
    assert fld_file2.exists()
    fld_file2 = test_tmp_dir / "test_fld_hfss4.fld"
    assert hfss_app.post.export_field_file(
        quantity="Mag_E",
        output_file=fld_file2,
        assignment="Box1",
        intrinsics={"frequency": solve_freq},
        phase="30deg",
    )
    assert fld_file2.exists()
    fld_file2 = test_tmp_dir / "test_fld_hfss5.fld"
    assert hfss_app.post.export_field_file(
        quantity="Mag_E",
        output_file=fld_file2,
        assignment="Box1",
    )
    assert fld_file2.exists()
    fld_file2 = test_tmp_dir / "test_fld_hfss6.fld"
    with pytest.raises(TypeError):
        hfss_app.post.export_field_file(quantity="Mag_E", output_file=fld_file2, assignment="Box1", intrinsics=[])
    assert not fld_file2.exists()

    hfss_app.variable_manager.set_variable(name="dummy", expression=1, is_post_processing=True)
    hfss_app.parametrics.add(variable="dummy", start_point=0, end_point=1, step=2)
    assert hfss_app.export_touchstone_on_completion(export=False)
    assert hfss_app.export_touchstone_on_completion(export=True)


def test_icepak_analyze_and_export_summary(icepak_solved):
    assert icepak_solved.create_output_variable("OutputVariable2", "abs(Variable1)")  # test creation
    assert icepak_solved.create_output_variable("OutputVariable2", "asin(Variable1)")  # test update
    icepak_solved.save_project()
    assert icepak_solved.export_summary(
        icepak_solved.working_directory, geometry_type="Surface", variation=[], filename="A"
    )  # check usage of deprecated arguments
    assert icepak_solved.export_summary(
        icepak_solved.working_directory, geometry_type="Surface", variation=[], filename="B"
    )
    assert icepak_solved.export_summary(
        icepak_solved.working_directory, geometry_type="Volume", type="Boundary", filename="C"
    )
    for file_name, entities in [
        ("A_Temperature.csv", ["box", "Region"]),
        ("B_Temperature.csv", ["box", "Region"]),
        ("C_Temperature.csv", ["box"]),
    ]:
        with open(Path(icepak_solved.working_directory) / file_name, "r", newline="") as csv_file:
            csv_reader = csv.reader(csv_file)
            for _ in range(4):
                _ = next(csv_reader)
            header = next(csv_reader)
            entity_index = header.index("Entity")
            csv_entities = [row[entity_index] for row in csv_reader]
            assert all(e in csv_entities for e in entities)

    box = [i.id for i in icepak_solved.modeler["box"].faces]
    assert Path(
        icepak_solved.eval_surface_quantity_from_field_summary(box, savedir=icepak_solved.working_directory)
    ).exists()
    opening = [i for i in icepak_solved.boundaries if i.type == "Opening"][0]
    # new post class
    out = icepak_solved.post.evaluate_faces_quantity(box, "HeatFlowRate")
    assert out["Total"]
    with pytest.raises(AttributeError):
        icepak_solved.post.evaluate_faces_quantity(box, "HeatFlowwwRate")
    out = icepak_solved.post.evaluate_object_quantity("box", "Temperature", volume=True)
    assert out["Mean"]
    out = icepak_solved.post.evaluate_boundary_quantity(opening.name, "Ux")
    assert out["Mean"]
    if icepak_solved.settings.aedt_version < "2024.1":
        with pytest.raises(AEDTRuntimeError):
            icepak_solved.post.evaluate_monitor_quantity("test_monitor2", "Temperature")
    else:
        out = icepak_solved.post.evaluate_monitor_quantity("test_monitor2", "Temperature")
        assert out["Mean"]
        with pytest.raises(AttributeError):
            icepak_solved.post.evaluate_monitor_quantity("no_test_monitor2", "Temperature")
    fs = icepak_solved.post.create_field_summary()
    fs.add_calculation("Boundary", "Surface", opening.name, "Ux")
    fs.add_calculation("Object", "Volume", "box", "Temperature")
    df = fs.get_field_summary_data(pandas_output=True)
    assert not df["Mean"].empty
    d = fs.get_field_summary_data()
    assert d["Mean"]
    profiles = icepak_solved.setups[0].get_profile()
    key0 = list(profiles.keys())[0]
    profile = profiles[key0]
    assert profile
    assert profile.max_memory() > MemoryGB(0.1)
    assert profile.real_time() > timedelta(seconds=1)
    assert profile.elapsed_time > timedelta(seconds=1)
    assert profile.product == "Icepak"


def test_icepak_get_output_variable(icepak_solved):
    with pytest.raises(KeyError):
        icepak_solved.get_output_variable("invalid")
    value = icepak_solved.get_output_variable("OutputVariable1")
    tol = 1e-9
    assert abs(value - 0.5235987755982988) < tol


def test_icepak_get_monitor_output(icepak_solved):
    assert icepak_solved.monitor.all_monitors["test_monitor"].value()
    assert icepak_solved.monitor.all_monitors["test_monitor"].value(quantity="Temperature")
    assert icepak_solved.monitor.all_monitors["test_monitor"].value(setup=icepak_solved.existing_analysis_sweeps[0])
    assert icepak_solved.monitor.all_monitors["test_monitor2"].value(quantity="HeatFlowRate")


def test_icepak_eval_tempc(icepak_solved):
    assert Path(
        icepak_solved.eval_volume_quantity_from_field_summary(
            ["box"], "Temperature", savedir=icepak_solved.working_directory
        )
    ).exists()


def test_icepak_export_fld(icepak_solved, test_tmp_dir):
    fld_file = test_tmp_dir / "test_fld.fld"
    icepak_solved.post.export_field_file(
        quantity="Temp",
        solution=icepak_solved.nominal_sweep,
        variations={},
        output_file=fld_file,
        assignment="box",
    )
    assert fld_file.exists()
    fld_file_1 = test_tmp_dir / "test_fld_1.fld"
    sample_points_file = Path(TESTS_SOLVERS_PATH) / "example_models" / TEST_SUBFOLDER / "temp_points.pts"
    icepak_solved.available_variations.independent = True
    icepak_solved.post.export_field_file(
        quantity="Temp",
        solution=icepak_solved.nominal_sweep,
        variations=icepak_solved.available_variations.nominal_values,
        output_file=fld_file_1,
        assignment="box",
        sample_points_file=sample_points_file,
    )
    assert fld_file_1.exists()
    fld_file_2 = test_tmp_dir / "test_fld_2.fld"
    icepak_solved.post.export_field_file(
        quantity="Temp",
        solution=icepak_solved.nominal_sweep,
        variations=icepak_solved.available_variations.nominal_values,
        output_file=fld_file_2,
        assignment="box",
        sample_points=[[0, 0, 0], [3, 6, 8], [4, 7, 9]],
    )
    assert fld_file_2.exists()
    cs = icepak_solved.modeler.create_coordinate_system()
    fld_file_3 = test_tmp_dir / "test_fld_3.fld"
    icepak_solved.post.export_field_file(
        quantity="Temp",
        solution=icepak_solved.nominal_sweep,
        variations=icepak_solved.available_variations.nominal_values,
        output_file=fld_file_3,
        assignment="box",
        sample_points=[[0, 0, 0], [3, 6, 8], [4, 7, 9]],
        reference_coordinate_system=cs.name,
        export_in_si_system=False,
        export_field_in_reference=False,
    )
    assert fld_file_3.exists()


@pytest.mark.skipif(is_linux, reason="To be investigated on linux.")
def test_3dl_export_touchstone(hfss3dl_solved, test_tmp_dir):
    filename = Path(test_tmp_dir) / "touchstone.s2p"
    solution_name = "Setup1"
    sweep_name = "Sweep1"
    assert hfss3dl_solved.export_touchstone(solution_name, sweep_name, filename)
    assert filename.exists()
    assert hfss3dl_solved.export_touchstone(solution_name)
    sweep_name = None
    assert hfss3dl_solved.export_touchstone(solution_name, sweep_name)


def test_3dl_export_results(hfss3dl_solved):
    files = hfss3dl_solved.export_results()
    assert len(files) > 0


def test_3dl_set_export_touchstone(hfss3dl_solved):
    assert hfss3dl_solved.export_touchstone_on_completion(True)
    assert hfss3dl_solved.export_touchstone_on_completion(False)
    if DESKTOP_VERSION > "2024.2":
        assert hfss3dl_solved.set_export_touchstone()


def test_3dl_touchstone_results(hfss3dl_solved):
    assert hfss3dl_solved.get_all_return_loss_list() == ["S(Port1,Port1)", "S(Port2,Port2)"]
    assert hfss3dl_solved.get_all_sparameter_list == ["S(Port1,Port1)", "S(Port1,Port2)", "S(Port2,Port2)"]
    assert hfss3dl_solved.get_all_insertion_loss_list(drivers_prefix_name="Port1", receivers_prefix_name="Port2") == [
        "S(Port1,Port2)"
    ]
    assert hfss3dl_solved.get_next_xtalk_list() == ["S(Port1,Port2)"]
    assert hfss3dl_solved.get_fext_xtalk_list() == ["S(Port1,Port2)", "S(Port2,Port1)"]


def test_circuit_add_3dlayout_component(circuit_app):
    setup = circuit_app.create_setup("test_06b_LNA")
    setup.add_sweep_step(start=0, stop=5, step_size=0.01)
    myedb = circuit_app.modeler.schematic.add_subcircuit_3dlayout("main")
    assert isinstance(myedb.id, int)
    ports = myedb.pins
    tx = ports
    rx = ports
    insertions = [f"dB(S({i.name},{j.name}))" for i, j in zip(tx, rx)]

    if DESKTOP_VERSION < "2026.1":
        assert not circuit_app.post.create_report(
            insertions,
            circuit_app.nominal_adaptive,
            report_category="Standard",
            plot_type="Rectangular Plot",
            subdesign_id=myedb.id,
        )
    else:
        # BUG in AEDT
        assert circuit_app.post.create_report(
            insertions,
            circuit_app.nominal_adaptive,
            report_category="Standard",
            plot_type="Rectangular Plot",
            subdesign_id=myedb.id,
        )
    new_report = circuit_app.post.reports_by_category.standard(insertions)
    new_report.sub_design_id = myedb.id
    assert new_report.create()


def test_circuit_add_hfss_component(circuit_app):
    my_model, _ = circuit_app.modeler.schematic.create_field_model(
        "uUSB", "Setup1 : Sweep", ["usb_N_conn", "usb_N_pcb", "usb_P_conn", "usb_P_pcb"]
    )
    assert isinstance(my_model, int)


def test_circuit_push_excitation(circuit_app):
    setup_name = "test_07a_LNA"
    circuit_app.modeler.schematic.add_subcircuit_3dlayout("main")
    setup = circuit_app.create_setup(setup_name)
    setup.add_sweep_step(start=0, stop=5, step_size=0.01)
    assert circuit_app.push_excitations(instance="U1", thevenin_calculation=False, setup=setup_name)
    assert circuit_app.push_excitations(instance="U1", thevenin_calculation=True, setup=setup_name)


def test_circuit_push_excitation_time(circuit_app):
    setup_name = "test_07b_Transient"
    circuit_app.modeler.schematic.add_subcircuit_3dlayout("main")
    circuit_app.create_setup(setup_name, setup_type="NexximTransient")
    assert circuit_app.push_time_excitations(instance="U1", setup=setup_name)


def test_m3d_harmonic_forces(m3dtransient):
    assert m3dtransient.export_element_based_harmonic_force(
        start_frequency=1, stop_frequency=100, number_of_frequency=None
    )
    assert m3dtransient.export_element_based_harmonic_force(number_of_frequency=5)


def test_export_maxwell_fields(m3dtransient, test_tmp_dir):
    fld_file_3 = test_tmp_dir / "test_fld_3.fld"
    assert m3dtransient.post.export_field_file(
        quantity="Mag_B",
        solution=m3dtransient.nominal_sweep,
        variations={},
        output_file=fld_file_3,
        assignment="Coil_A2",
        objects_type="Surf",
        intrinsics="10ms",
    )
    assert fld_file_3.exists()
    fld_file_4 = test_tmp_dir / "test_fld_4.fld"
    m3dtransient.available_variations.independent = True
    assert not m3dtransient.post.export_field_file(
        quantity="Mag_B",
        solution=m3dtransient.nominal_sweep,
        variations=m3dtransient.available_variations.nominal_values,
        output_file=fld_file_4,
        assignment="Coil_A2",
        objects_type="invalid",
    )
    setup = m3dtransient.setups[0]
    m3dtransient.setups[0].delete()
    assert not m3dtransient.post.export_field_file(
        quantity="Mag_B", variations={}, output_file=fld_file_4, assignment="Coil_A2"
    )

    new_setup = m3dtransient.create_setup(name=setup.name, setup_type=setup.setuptype)
    new_setup.props = setup.props
    new_setup.update()


def test_compute_erl(circuit_erl):
    sp = circuit_erl.export_touchstone()
    spisim = SpiSim(sp)

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


def test_compute_com_exported_touchstone(circuit_com):
    sp = circuit_com.export_touchstone()
    spisim = SpiSim(sp)

    report_dir = Path(spisim.working_directory) / "50GAUI-1_C2C"
    report_dir.mkdir(parents=True, exist_ok=True)
    com = spisim.compute_com(
        standard=1,
        out_folder=report_dir,
    )
    assert com


def test_compute_com(test_tmp_dir):
    com_example_file_folder = Path(TESTS_SOLVERS_PATH) / "example_models" / TEST_SUBFOLDER / "com_unit_test_sparam"

    thru_s4p = shutil.copy2(com_example_file_folder / "SerDes_Demo_02_Thru.s4p", test_tmp_dir / "thru.s4p")
    fext_s4p = shutil.copy2(
        com_example_file_folder / "FCI_CC_Long_Link_Pair_2_to_Pair_9_FEXT.s4p", test_tmp_dir / "fext_s4p.s4p"
    )
    next_s4p = shutil.copy2(
        com_example_file_folder / "FCI_CC_Long_Link_Pair_11_to_Pair_9_NEXT.s4p", test_tmp_dir / "next_s4p.s4p"
    )

    report_dir = Path(test_tmp_dir) / "custom"
    report_dir.mkdir(parents=True, exist_ok=True)
    spisim = SpiSim(thru_s4p)
    spisim.working_directory = test_tmp_dir

    com_0, com_1 = spisim.compute_com(
        standard=3,
        port_order="EvenOdd",
        fext_s4p=fext_s4p,
        next_s4p=next_s4p,
        out_folder=report_dir,
    )
    assert com_0 and com_1


def test_compute_com_parameter_ver_3p4(test_tmp_dir):
    com_example_file_folder = Path(TESTS_SOLVERS_PATH) / "example_models" / TEST_SUBFOLDER / "com_unit_test_sparam"
    thru_s4p = shutil.copy2(com_example_file_folder / "SerDes_Demo_02_Thru.s4p", test_tmp_dir / "thru.s4p")
    spisim = SpiSim(thru_s4p)

    spisim.export_com_configure_file(Path(spisim.working_directory) / "custom.json")

    from ansys.aedt.core.visualization.post.spisim_com_configuration_files.com_parameters import COMParametersVer3p4

    com_param = COMParametersVer3p4()
    com_param.load(
        Path(spisim.working_directory) / "custom.json",
    )
    com_param.export_spisim_cfg(str(test_tmp_dir / "test.cfg"))
    com_0, com_1 = spisim.compute_com(0, test_tmp_dir / "test.cfg")
    assert com_0 and com_1


def test_export_to_maxwell(add_app_example, add_app, test_tmp_dir):
    app = add_app_example(
        project="assm_test", design="assm-1", application=Rmxprt, subfolder="T00", solution_type="ASSM"
    )
    app.analyze(cores=4)
    m2d = app.create_maxwell_design("Setup1")
    assert m2d.design_type == "Maxwell 2D"
    config = app.export_configuration(test_tmp_dir / "assm.json")
    app2 = add_app(project="assm_test2", application=Rmxprt, solution_type="ASSM")
    app2.import_configuration(config)
    assert app2.circuit


def test_output_variables_3dlayout(hfss3dl_solved):
    hfss3dl_solved.set_differential_pair(
        assignment="Port1", reference="Port2", differential_mode="Diff", common_mode="Comm"
    )
    assert hfss3dl_solved.create_output_variable(
        variable="outputvar_diff", expression="S(Comm,Diff)", is_differential=True
    )
    assert hfss3dl_solved.create_output_variable(variable="outputvar_terminal", expression="dB(S(Port1,Port1))")
    assert len(hfss3dl_solved.output_variables) == 2
    with pytest.raises(AEDTRuntimeError):
        hfss3dl_solved.create_output_variable(
            variable="outputvar_diff2", expression="S(Comm,Diff)", is_differential=False
        )


def test_spisim_advanced_report_ucie(test_tmp_dir):
    spisim_advanced_report_exmaple_folder = (
        Path(TESTS_SOLVERS_PATH) / "example_models" / TEST_SUBFOLDER / "spisim_advanced_report"
    )
    fpath_snp = shutil.copy2(spisim_advanced_report_exmaple_folder / "5_C50.s20p", test_tmp_dir / "5_C50.s20p")
    spisim = SpiSim(fpath_snp)
    assert spisim.compute_ucie([0, 2, 4, 6, 8, 10], [1, 3, 5, 7, 9, 11], [1, 3])


def test_set_hpc_from_file(hfss3dl_solve):
    acf_file = Path(hfss3dl_solve.pyaedt_dir) / "misc" / "pyaedt_local_config.acf"
    with pytest.raises(AEDTRuntimeError):
        hfss3dl_solve.set_hpc_from_file()

    assert hfss3dl_solve.set_hpc_from_file(acf_file=acf_file)
    assert hfss3dl_solve.set_hpc_from_file(configuration_name="Local")


def test_custom_hpc_from_file(icepak_solved):
    allowed_distributed = ["Variations", "Frequencies", "Transient Excitations", "Domain Solver"]
    assert icepak_solved.set_custom_hpc_options()

    assert icepak_solved.set_custom_hpc_options(
        cores=4, gpus=1, tasks=4, num_variations_to_distribute=4, allowed_distribution_types=allowed_distributed
    )
