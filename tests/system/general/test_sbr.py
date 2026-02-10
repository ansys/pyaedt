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
from pathlib import Path
import re
import shutil

import pytest

from ansys.aedt.core.generic.settings import is_linux
from ansys.aedt.core.hfss import Hfss
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from tests import TESTS_GENERAL_PATH

TEST_PROJECT_NAME = "Cassegrain_231"
TUNNEL = "tunnel1_231"
PERSON = "person3_231"
VEHICLE = "vehicle1_231"
BIRD = "bird1_231"
FARFIELD_DATA = "test.ffd"
TEST_SUBFOLDER = "T04"

custom_array = Path(TESTS_GENERAL_PATH) / "example_models" / TEST_SUBFOLDER / "custom_array.sarr"
on_ci = os.getenv("ON_CI", "false").lower() == "true"


@pytest.fixture
def aedt_app(add_app_example):
    app = add_app_example(
        application=Hfss,
        project=TEST_PROJECT_NAME,
        solution_type="SBR+",
        subfolder=TEST_SUBFOLDER,
    )
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def aedt_terminal(add_app):
    app = add_app(
        application=Hfss,
        solution_type="Terminal",
    )
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def aedt_sbr(add_app):
    app = add_app(
        application=Hfss,
        solution_type="SBR+",
    )
    yield app
    app.close_project(save=False)


def test_open_source(aedt_app, add_app):
    source = add_app(project=aedt_app.project_name, design="feeder", close_projects=False)
    assert aedt_app.create_sbr_linked_antenna(source, target_cs="feederPosition", field_type="farfield")
    assert len(aedt_app.native_components) == 1
    assert aedt_app.create_sbr_linked_antenna(
        source, target_cs="feederPosition", field_type="farfield", name="LinkedAntenna"
    )
    assert len(aedt_app.native_components) == 2
    assert aedt_app.create_sbr_linked_antenna(
        source, target_cs="feederPosition", name="LinkedAntennaNF1", current_conformance=True
    )
    assert len(aedt_app.native_components) == 3
    assert aedt_app.create_sbr_linked_antenna(
        source, target_cs="feederPosition", name="LinkedAntennaNF2", current_conformance=False
    )
    assert len(aedt_app.native_components) == 4

    aedt_app.create_sbr_linked_antenna(source, target_cs="feederPosition", field_type="farfield", is_array=True)
    assert len(aedt_app.native_components) == 5

    aedt_app.create_sbr_linked_antenna(
        source,
        target_cs="feederPosition",
        name="LinkedAntennaNF_array",
        current_conformance=True,
        custom_array=str(custom_array),
    )
    assert len(aedt_app.native_components) == 6


def test_add_antennas(aedt_sbr):
    dict1 = {"Polarization": "Horizontal"}
    par_beam = aedt_sbr.create_sbr_antenna(aedt_sbr.SbrAntennas.ParametricBeam, parameters=dict1, name="TX1")
    assert par_beam.definition_name == "TX1"
    assert aedt_sbr.create_sbr_antenna(aedt_sbr.SbrAntennas.ConicalHorn, parameters=dict1, name="RX1")
    par_beam.native_properties["Unit"] = "in"
    assert par_beam.update()
    aedt_sbr.modeler.user_defined_components["TX1_1"].native_properties["Unit"] = "mm"

    assert len(aedt_sbr.native_components) == 2
    assert len(aedt_sbr.modeler.user_defined_components) == 2
    assert aedt_sbr.set_sbr_txrx_settings({"TX1_1_p1": "RX1_1_p1"})
    assert aedt_sbr.create_sbr_antenna(aedt_sbr.SbrAntennas.CrossDipole, use_current_source_representation=True)
    assert aedt_sbr.create_sbr_antenna(aedt_sbr.SbrAntennas.HalfWaveDipole, use_current_source_representation=True)
    assert aedt_sbr.create_sbr_antenna(aedt_sbr.SbrAntennas.HorizontalDipole, use_current_source_representation=True)
    assert aedt_sbr.create_sbr_antenna(aedt_sbr.SbrAntennas.ParametricSlot, use_current_source_representation=True)
    assert aedt_sbr.create_sbr_antenna(aedt_sbr.SbrAntennas.PyramidalHorn, use_current_source_representation=True)
    assert aedt_sbr.create_sbr_antenna(aedt_sbr.SbrAntennas.ShortDipole, use_current_source_representation=True)
    assert aedt_sbr.create_sbr_antenna(aedt_sbr.SbrAntennas.SmallLoop, use_current_source_representation=True)
    toberemoved = aedt_sbr.create_sbr_antenna(aedt_sbr.SbrAntennas.WireDipole, use_current_source_representation=True)

    native_components = len(aedt_sbr.native_components)

    toberemoved.delete()

    assert len(aedt_sbr.native_components) == native_components - 1
    assert len(aedt_sbr.modeler.user_defined_component_names) == native_components - 1
    array = aedt_sbr.create_sbr_antenna(
        aedt_sbr.SbrAntennas.WireMonopole, use_current_source_representation=False, is_array=True
    )
    array.native_properties["Array Length In Wavelength"] = "10"
    assert array.update()

    assert array.properties["Name"] == array.name

    native_components = len(aedt_sbr.native_component_names)
    array.name = "new_name"
    native_components_new = len(aedt_sbr.native_component_names)
    assert native_components_new == native_components

    assert "new_name" in aedt_sbr.native_component_names

    assert aedt_sbr.create_sbr_antenna(
        aedt_sbr.SbrAntennas.SmallLoop, use_current_source_representation=True, is_array=True
    )

    assert aedt_sbr.create_sbr_antenna(
        aedt_sbr.SbrAntennas.SmallLoop, use_current_source_representation=True, custom_array=str(custom_array)
    )


def test_add_ffd_antenna(aedt_sbr, test_tmp_dir):
    ffd_path = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / FARFIELD_DATA
    file = shutil.copy2(ffd_path, test_tmp_dir / FARFIELD_DATA)

    assert aedt_sbr.create_sbr_file_based_antenna(far_field_data=str(file))

    assert aedt_sbr.create_sbr_file_based_antenna(far_field_data=str(file), is_array=True)

    assert aedt_sbr.create_sbr_file_based_antenna(
        far_field_data=str(file),
        custom_array=str(custom_array),
    )


def test_add_environment(aedt_sbr, test_tmp_dir):
    env_folder = TESTS_GENERAL_PATH / "example_models" / "library" / "environment_library" / TUNNEL
    env_dir = shutil.copytree(env_folder, test_tmp_dir / TUNNEL)

    road1 = aedt_sbr.modeler.add_environment(str(env_dir))
    assert road1.name


def test_add_person(aedt_sbr, test_tmp_dir):
    person_folder = TESTS_GENERAL_PATH / "example_models" / "library" / "actor_library" / PERSON
    person_dir = shutil.copytree(person_folder, test_tmp_dir / PERSON)

    person1 = aedt_sbr.modeler.add_person(str(person_dir), 1.0, [25, 1.5, 0], 180)
    assert person1.offset == [25, 1.5, 0]
    assert person1.yaw == "180deg"
    assert person1.pitch == "0deg"
    assert person1.roll == "0deg"


def test_add_car(aedt_sbr, test_tmp_dir):
    car_folder = TESTS_GENERAL_PATH / "example_models" / "library" / "actor_library" / VEHICLE
    car_dir = shutil.copytree(car_folder, test_tmp_dir / VEHICLE)

    car1 = aedt_sbr.modeler.add_vehicle(str(car_dir), 1.0, [3, -2.5, 0])
    assert car1.offset == [3, -2.5, 0]
    assert car1.yaw == "0deg"
    assert car1.pitch == "0deg"
    assert car1.roll == "0deg"


def test_add_bird(aedt_sbr, test_tmp_dir):
    bird_folder = TESTS_GENERAL_PATH / "example_models" / "library" / "actor_library" / BIRD
    bird_dir = shutil.copytree(bird_folder, test_tmp_dir / VEHICLE)

    bird1 = aedt_sbr.modeler.add_bird(str(bird_dir), 1.0, [19, 4, 3], 120, -5, flapping_rate=30)
    assert bird1.offset == [19, 4, 3]
    assert bird1.yaw == "120deg"
    assert bird1.pitch == "-5deg"
    assert bird1.roll == "0deg"
    assert bird1._flapping_rate == "30Hz"


def test_add_radar(aedt_sbr, test_tmp_dir):
    radar_lib = TESTS_GENERAL_PATH / "example_models" / "library" / "radar_modules"
    radar_dir = shutil.copytree(radar_lib, test_tmp_dir / "radar_modules")
    assert aedt_sbr.create_sbr_radar_from_json(str(radar_dir), name="Example_1Tx_1Rx", speed=3)
    assert aedt_sbr.create_sbr_radar_from_json(str(radar_dir), name="Example_1Tx_4Rx")


def test_add_doppler_sweep(aedt_sbr, test_tmp_dir):
    env_folder = TESTS_GENERAL_PATH / "example_models" / "library" / "environment_library" / TUNNEL
    env_dir = shutil.copytree(env_folder, test_tmp_dir / TUNNEL)

    aedt_sbr.modeler.add_environment(str(env_dir))
    setup, sweep = aedt_sbr.create_sbr_pulse_doppler_setup(sweep_time_duration=30)
    assert "PulseSetup" in setup.name
    assert "PulseSweep" in sweep.name
    assert setup.props["SbrRangeDopplerWaveformType"] == "PulseDoppler"
    assert sweep.props["Sim. Setups"] == [setup.name]


def test_add_chirp_sweep(aedt_sbr, test_tmp_dir):
    env_folder = Path(TESTS_GENERAL_PATH) / "example_models" / "library" / "environment_library" / TUNNEL
    env_dir = shutil.copytree(env_folder, test_tmp_dir / TUNNEL)

    aedt_sbr.modeler.add_environment(str(env_dir))
    setup, sweep = aedt_sbr.create_sbr_chirp_i_doppler_setup(sweep_time_duration=20)
    assert setup.props["SbrRangeDopplerWaveformType"] == "ChirpSeqFmcw"
    assert setup.props["ChannelConfiguration"] == "IChannelOnly"
    assert sweep.props["Sim. Setups"] == [setup.name]
    setup, sweep = aedt_sbr.create_sbr_chirp_iq_doppler_setup(sweep_time_duration=10)
    assert setup.props["SbrRangeDopplerWaveformType"] == "ChirpSeqFmcw"
    assert setup.props["ChannelConfiguration"] == "IQChannels"
    assert sweep.props["Sim. Setups"] == [setup.name]


def test_add_sbr_boundaries_in_hfss_solution(aedt_terminal):
    # sbr file based antenna should only work for SBR+ solution.
    ffd_test_path = Path(TESTS_GENERAL_PATH) / "example_models" / TEST_SUBFOLDER / "test.ffd"
    with pytest.raises(
        AEDTRuntimeError,
        match=re.escape("This native component only applies to a SBR+ solution."),
    ):
        aedt_terminal.create_sbr_file_based_antenna(far_field_data=str(ffd_test_path))


@pytest.mark.skipif(on_ci, reason="Map download takes too long for unit test.")
@pytest.mark.skipif(is_linux, reason="Not supported.")
def test_import_map(aedt_sbr):
    ansys_home = [40.273726, -80.168269]
    parts_dict = aedt_sbr.modeler.import_from_openstreet_map(
        ansys_home, terrain_radius=200, road_step=3, plot_before_importing=False, import_in_aedt=True
    )
    for part in parts_dict["parts"]:
        assert Path(parts_dict["parts"][part]["file_name"]).exists()


def test_create_custom_array(aedt_sbr):
    output_file1 = aedt_sbr.create_sbr_custom_array_file()
    assert Path(output_file1).is_file()

    output_file2 = aedt_sbr.create_sbr_custom_array_file(
        frequencies=[1.0, 2.0, 5.0],
        element_number=4,
        state_number=2,
        position=[[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0]],
        x_axis=[[1.0, 0.0, 0.0]] * 4,
        y_axis=[[0.0, 1.0, 0.0]] * 4,
        weight=[
            [complex(1.0, 0.0), complex(1.0, 0.0), complex(1.1, 0.0), complex(1.0, 0.0)],
            [complex(1.0, 0.0), complex(1.0, 0.0), complex(1.0, 0.0), complex(1.0, 0.0)],
            [complex(1.0, 0.0), complex(1.0, 0.0), complex(1.0, 1.0), complex(1.0, 0.0)],
            [complex(1.0, 0.0), complex(1.0, 0.0), complex(1.0, 0.0), complex(1.0, 0.0)],
            [complex(1.0, 0.0), complex(1.0, 0.0), complex(1.0, 0.0), complex(1.0, 0.0)],
            [complex(1.0, 0.0), complex(1.0, 0.0), complex(1.0, 0.0), complex(1.0, 0.0)],
        ],
    )
    assert Path(output_file2).is_file()


@pytest.mark.skipif(is_linux, reason="feature supported in Cpython")
def test_read_hdm(aedt_sbr, test_tmp_dir):
    hdm_path = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / "freighter_rays.hdm"
    hdm_local = shutil.copy2(hdm_path, test_tmp_dir / "freighter_rays.hdm")

    stl_path = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / "freighter_ship.stl"
    stl_local = shutil.copy2(stl_path, test_tmp_dir / "freighter_ship.stl")

    aedt_sbr.modeler.model_units = "meter"
    aedt_sbr.modeler.import_3d_cad(str(stl_local))
    assert aedt_sbr.parse_hdm_file(str(hdm_local))
    plotter = aedt_sbr.get_hdm_plotter(str(hdm_path))
    assert plotter
    bounce1_path = test_tmp_dir / "bounce1.jpg"
    plotter.plot_first_bounce_currents(str(bounce1_path))
    assert bounce1_path.exists()
    assert plotter
    bounce2_path = test_tmp_dir / "bounce2.jpg"
    plotter.plot_rays(str(bounce2_path))
    assert bounce2_path.exists()


def test_boundary_perfect_e(aedt_sbr):
    b = aedt_sbr.modeler.create_box([0, 0, 0], [10, 20, 30])
    model_units = aedt_sbr.modeler.model_units

    bound = aedt_sbr.assign_perfect_e(name="b1", assignment=[b, b.faces[0]], height_deviation=2, roughness=0.4)
    assert bound.properties["SBR+ Rough Surface Height Standard Deviation"] == f"2{model_units}"

    bound2 = aedt_sbr.assign_perfect_e(assignment=[b, b.faces[0]], height_deviation="3mm")
    assert bound2.properties["SBR+ Rough Surface Height Standard Deviation"] == "3mm"

    with pytest.raises(AEDTRuntimeError):
        aedt_sbr.assign_perfect_e(name="b1", assignment=[b, b.faces[0]], height_deviation="3mm")

    with pytest.raises(AEDTRuntimeError):
        aedt_sbr.assign_perfect_e(assignment="invented")


def test_boundary_perfect_h(aedt_sbr):
    b = aedt_sbr.modeler.create_box([0, 0, 0], [10, 20, 30])
    model_units = aedt_sbr.modeler.model_units

    bound = aedt_sbr.assign_perfect_h(name="b1", assignment=[b, b.faces[0]], height_deviation=2, roughness=0.4)
    assert bound.properties["SBR+ Rough Surface Height Standard Deviation"] == f"2{model_units}"

    bound2 = aedt_sbr.assign_perfect_h(assignment=[b, b.faces[0]], height_deviation="3mm")
    assert bound2.properties["SBR+ Rough Surface Height Standard Deviation"] == "3mm"

    with pytest.raises(AEDTRuntimeError):
        aedt_sbr.assign_perfect_h(name="b1", assignment=[b, b.faces[0]], height_deviation="3mm")

    with pytest.raises(AEDTRuntimeError):
        aedt_sbr.assign_perfect_h(assignment="invented")


def test_boundaries_finite_conductivity(aedt_sbr):
    b = aedt_sbr.modeler.create_box([0, 0, 0], [10, 20, 30])

    args = {
        "material": "aluminum",
        "use_thickness": True,
        "thickness": "0.5mm",
        "is_two_side": True,
        "is_shell_element": True,
        "use_huray": True,
        "radius": "0.75um",
        "ratio": "3",
        "height_deviation": 1,
        "roughness": 0.5,
    }

    coat = aedt_sbr.assign_finite_conductivity([b.id, b.name, b.faces[0]], **args)
    coat.name = "Coating1inner"
    assert coat.update()
    assert coat.properties
    material = coat.props.get("Material", "")
    assert material == "aluminum"

    args = {
        "material": None,
        "use_thickness": False,
        "thickness": "0.5mm",
        "is_two_side": False,
        "is_shell_element": False,
        "use_huray": False,
        "radius": "0.75um",
        "ratio": "3",
        "height_deviation": 1,
        "roughness": 0.5,
        "name": "b2",
    }

    coat2 = aedt_sbr.assign_finite_conductivity([b.id, b.name, b.faces[0]], **args)
    assert coat2.properties["SBR+ Rough Surface Height Standard Deviation"] == f"1{aedt_sbr.modeler.model_units}"

    with pytest.raises(AEDTRuntimeError):
        aedt_sbr.assign_finite_conductivity([b.id, b.name, b.faces[0]], **args)

    with pytest.raises(AEDTRuntimeError):
        aedt_sbr.assign_finite_conductivity(["insulator2"])


def test_boundaries_layered_impedance(aedt_sbr):
    b = aedt_sbr.modeler.create_box([0, 0, 0], [10, 20, 30])
    model_units = aedt_sbr.modeler.model_units

    # One side
    args = {
        "material": ["aluminum", "vacuum"],
        "thickness": ["0.5mm", "PerfectE"],
        "is_two_side": False,
        "is_shell_element": False,
        "height_deviation": 1,
        "roughness": 0.5,
    }

    coat = aedt_sbr.assign_layered_impedance([b.id, b.name, b.faces[0]], **args)
    coat.name = "Coating1inner"
    assert coat.update()
    assert coat.properties["Layer 2/Type"] == "PerfectE"

    args = {
        "material": None,
        "thickness": None,
        "is_two_side": False,
        "is_shell_element": False,
        "height_deviation": 1,
        "roughness": 0.5,
        "name": "b2",
    }

    coat2 = aedt_sbr.assign_layered_impedance([b.id, b.name, b.faces[0]], **args)
    assert coat2.properties["SBR+ Rough Surface Height Standard Deviation"] == f"1{model_units}"

    # Repeat name
    with pytest.raises(AEDTRuntimeError):
        aedt_sbr.assign_layered_impedance([b.id, b.name, b.faces[0]], **args)

    # Not existing assignment
    with pytest.raises(AEDTRuntimeError):
        aedt_sbr.assign_layered_impedance(["insulator2"])

    args = {
        "material": "aluminum",
        "thickness": "1mm",
        "is_two_side": False,
        "is_shell_element": False,
        "height_deviation": 1,
        "roughness": 0.5,
        "name": "b3",
    }

    coat3 = aedt_sbr.assign_layered_impedance([b.id, b.name, b.faces[0]], **args)
    assert coat3.properties["SBR+ Rough Surface Height Standard Deviation"] == f"1{model_units}"

    args = {
        "material": ["aluminum", "aluminum"],
        "thickness": ["1mm"],
        "is_two_side": False,
        "is_shell_element": False,
        "height_deviation": 1,
        "roughness": 0.5,
        "name": "b3",
    }
    with pytest.raises(AttributeError):
        aedt_sbr.assign_layered_impedance([b.id, b.name, b.faces[0]], **args)

    # Two side
    args = {
        "material": ["aluminum", "vacuum"],
        "thickness": ["0.5mm", "1um"],
        "is_two_side": True,
        "is_shell_element": False,
        "name": "b4",
    }

    coat4 = aedt_sbr.assign_layered_impedance([b.id, b.name, b.faces[0]], **args)
    assert coat4.properties["Layer 2/Material"] == "vacuum"
