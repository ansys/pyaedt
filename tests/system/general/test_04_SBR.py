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

from pathlib import Path
import re

import pytest

from ansys.aedt.core.hfss import Hfss

try:
    import osmnx
except ImportError:
    osmnx = None

from ansys.aedt.core.generic.settings import is_linux
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from tests import TESTS_GENERAL_PATH

test_project_name = "Cassegrain_231"
tunnel = "tunnel1_231"
person = "person3_231"
vehicle = "vehicle1_231"
bird = "bird1_231"

test_subfolder = "T04"

custom_array = Path(TESTS_GENERAL_PATH) / "example_models" / test_subfolder / "custom_array.sarr"


@pytest.fixture()
def aedtapp(add_app):
    app = add_app(
        application=Hfss,
        project_name=test_project_name,
        solution_type="SBR+",
        subfolder=test_subfolder,
    )
    yield app
    app.close_project(app.project_name)


@pytest.fixture()
def source(add_app, aedtapp):
    app = add_app(project_name=aedtapp.project_name, design_name="feeder", just_open=True)
    return app


@pytest.fixture()
def aedt_terminal(add_app):
    app = add_app(
        application=Hfss,
        solution_type="Terminal",
    )
    yield app
    app.close_project(app.project_name)


@pytest.fixture(autouse=True)
def configure_osmnx_cache(local_scratch):
    if not is_linux:
        cache_folder = Path(local_scratch.path) / "cache"
        osmnx.settings.cache_folder = str(cache_folder)


def test_open_source(aedtapp, source):
    assert aedtapp.create_sbr_linked_antenna(source, target_cs="feederPosition", field_type="farfield")
    assert len(aedtapp.native_components) == 1
    assert aedtapp.create_sbr_linked_antenna(
        source, target_cs="feederPosition", field_type="farfield", name="LinkedAntenna"
    )
    assert len(aedtapp.native_components) == 2
    assert aedtapp.create_sbr_linked_antenna(
        source, target_cs="feederPosition", name="LinkedAntennaNF1", current_conformance=True
    )
    assert len(aedtapp.native_components) == 3
    assert aedtapp.create_sbr_linked_antenna(
        source, target_cs="feederPosition", name="LinkedAntennaNF2", current_conformance=False
    )
    assert len(aedtapp.native_components) == 4

    aedtapp.create_sbr_linked_antenna(source, target_cs="feederPosition", field_type="farfield", is_array=True)
    assert len(aedtapp.native_components) == 5

    aedtapp.create_sbr_linked_antenna(
        source,
        target_cs="feederPosition",
        name="LinkedAntennaNF_array",
        current_conformance=True,
        custom_array=str(custom_array),
    )
    assert len(aedtapp.native_components) == 6


def test_add_antennas(aedtapp):
    aedtapp.insert_design("add_antennas")
    dict1 = {"Polarization": "Horizontal"}
    par_beam = aedtapp.create_sbr_antenna(aedtapp.SbrAntennas.ParametricBeam, parameters=dict1, name="TX1")
    assert par_beam.definition_name == "TX1"
    assert aedtapp.create_sbr_antenna(aedtapp.SbrAntennas.ConicalHorn, parameters=dict1, name="RX1")
    par_beam.native_properties["Unit"] = "in"
    assert par_beam.update()
    aedtapp.modeler.user_defined_components["TX1_1"].native_properties["Unit"] = "mm"

    assert len(aedtapp.native_components) == 2
    assert len(aedtapp.modeler.user_defined_components) == 2
    assert aedtapp.set_sbr_txrx_settings({"TX1_1_p1": "RX1_1_p1"})
    assert aedtapp.create_sbr_antenna(aedtapp.SbrAntennas.CrossDipole, use_current_source_representation=True)
    assert aedtapp.create_sbr_antenna(aedtapp.SbrAntennas.HalfWaveDipole, use_current_source_representation=True)
    assert aedtapp.create_sbr_antenna(aedtapp.SbrAntennas.HorizontalDipole, use_current_source_representation=True)
    assert aedtapp.create_sbr_antenna(aedtapp.SbrAntennas.ParametricSlot, use_current_source_representation=True)
    assert aedtapp.create_sbr_antenna(aedtapp.SbrAntennas.PyramidalHorn, use_current_source_representation=True)
    assert aedtapp.create_sbr_antenna(aedtapp.SbrAntennas.ShortDipole, use_current_source_representation=True)
    assert aedtapp.create_sbr_antenna(aedtapp.SbrAntennas.SmallLoop, use_current_source_representation=True)
    toberemoved = aedtapp.create_sbr_antenna(aedtapp.SbrAntennas.WireDipole, use_current_source_representation=True)

    native_components = len(aedtapp.native_components)

    toberemoved.delete()

    assert len(aedtapp.native_components) == native_components - 1
    assert len(aedtapp.modeler.user_defined_component_names) == native_components - 1
    array = aedtapp.create_sbr_antenna(
        aedtapp.SbrAntennas.WireMonopole, use_current_source_representation=False, is_array=True
    )
    array.native_properties["Array Length In Wavelength"] = "10"
    assert array.update()

    assert array.properties["Name"] == array.name

    native_components = len(aedtapp.native_component_names)
    array.name = "new_name"
    native_components_new = len(aedtapp.native_component_names)
    assert native_components_new == native_components

    assert "new_name" in aedtapp.native_component_names

    assert aedtapp.create_sbr_antenna(
        aedtapp.SbrAntennas.SmallLoop, use_current_source_representation=True, is_array=True
    )

    assert aedtapp.create_sbr_antenna(
        aedtapp.SbrAntennas.SmallLoop, use_current_source_representation=True, custom_array=str(custom_array)
    )


def test_add_ffd_antenna(aedtapp):
    aedtapp.insert_design("ffd_antenna")
    ffd_path = Path(TESTS_GENERAL_PATH) / "example_models" / test_subfolder / "test.ffd"
    assert aedtapp.create_sbr_file_based_antenna(far_field_data=str(ffd_path))

    assert aedtapp.create_sbr_file_based_antenna(far_field_data=str(ffd_path), is_array=True)

    assert aedtapp.create_sbr_file_based_antenna(
        far_field_data=str(ffd_path),
        custom_array=str(custom_array),
    )


def test_add_environment(aedtapp):
    aedtapp.insert_design("Environment_test")
    env_folder = Path(TESTS_GENERAL_PATH) / "example_models" / "library" / "environment_library" / tunnel
    road1 = aedtapp.modeler.add_environment(str(env_folder))
    assert road1.name


def test_add_person(aedtapp):
    person_folder = Path(TESTS_GENERAL_PATH) / "example_models" / "library" / "actor_library" / person
    person1 = aedtapp.modeler.add_person(str(person_folder), 1.0, [25, 1.5, 0], 180)
    assert person1.offset == [25, 1.5, 0]
    assert person1.yaw == "180deg"
    assert person1.pitch == "0deg"
    assert person1.roll == "0deg"


def test_add_car(aedtapp):
    car_folder = Path(TESTS_GENERAL_PATH) / "example_models" / "library" / "actor_library" / vehicle
    car1 = aedtapp.modeler.add_vehicle(str(car_folder), 1.0, [3, -2.5, 0])
    assert car1.offset == [3, -2.5, 0]
    assert car1.yaw == "0deg"
    assert car1.pitch == "0deg"
    assert car1.roll == "0deg"


def test_add_bird(aedtapp):
    bird_folder = Path(TESTS_GENERAL_PATH) / "example_models" / "library" / "actor_library" / bird
    bird1 = aedtapp.modeler.add_bird(str(bird_folder), 1.0, [19, 4, 3], 120, -5, flapping_rate=30)
    assert bird1.offset == [19, 4, 3]
    assert bird1.yaw == "120deg"
    assert bird1.pitch == "-5deg"
    assert bird1.roll == "0deg"
    assert bird1._flapping_rate == "30Hz"


def test_add_radar(aedtapp):
    radar_lib = Path(TESTS_GENERAL_PATH) / "example_models" / "library" / "radar_modules"
    assert aedtapp.create_sbr_radar_from_json(str(radar_lib), name="Example_1Tx_1Rx", speed=3)
    assert aedtapp.create_sbr_radar_from_json(str(radar_lib), name="Example_1Tx_4Rx")


def test_add_doppler_sweep(aedtapp):
    env_folder = Path(TESTS_GENERAL_PATH) / "example_models" / "library" / "environment_library" / tunnel
    aedtapp.modeler.add_environment(str(env_folder))
    setup, sweep = aedtapp.create_sbr_pulse_doppler_setup(sweep_time_duration=30)
    assert "PulseSetup" in setup.name
    assert "PulseSweep" in sweep.name
    assert setup.props["SbrRangeDopplerWaveformType"] == "PulseDoppler"
    assert sweep.props["Sim. Setups"] == [setup.name]


def test_add_chirp_sweep(aedtapp):
    env_folder = Path(TESTS_GENERAL_PATH) / "example_models" / "library" / "environment_library" / tunnel
    aedtapp.modeler.add_environment(str(env_folder))
    setup, sweep = aedtapp.create_sbr_chirp_i_doppler_setup(sweep_time_duration=20)
    assert setup.props["SbrRangeDopplerWaveformType"] == "ChirpSeqFmcw"
    assert setup.props["ChannelConfiguration"] == "IChannelOnly"
    assert sweep.props["Sim. Setups"] == [setup.name]
    setup, sweep = aedtapp.create_sbr_chirp_iq_doppler_setup(sweep_time_duration=10)
    assert setup.props["SbrRangeDopplerWaveformType"] == "ChirpSeqFmcw"
    assert setup.props["ChannelConfiguration"] == "IQChannels"
    assert sweep.props["Sim. Setups"] == [setup.name]


def test_add_sbr_boundaries_in_hfss_solution(aedt_terminal):
    # sbr file based antenna should only work for SBR+ solution.
    ffd_test_path = Path(TESTS_GENERAL_PATH) / "example_models" / test_subfolder / "test.ffd"
    with pytest.raises(
        AEDTRuntimeError,
        match=re.escape("This native component only applies to a SBR+ solution."),
    ):
        aedt_terminal.create_sbr_file_based_antenna(far_field_data=str(ffd_test_path))


@pytest.mark.skipif(is_linux, reason="Not supported.")
def test_import_map(aedtapp):
    aedtapp.insert_design("city")
    ansys_home = [40.273726, -80.168269]
    parts_dict = aedtapp.modeler.import_from_openstreet_map(
        ansys_home, terrain_radius=200, road_step=3, plot_before_importing=False, import_in_aedt=True
    )
    for part in parts_dict["parts"]:
        assert Path(parts_dict["parts"][part]["file_name"]).exists()


def test_create_custom_array(aedtapp):
    output_file1 = aedtapp.create_sbr_custom_array_file()
    assert Path(output_file1).is_file()

    output_file2 = aedtapp.create_sbr_custom_array_file(
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
def test_read_hdm(aedtapp, local_scratch):
    aedtapp.insert_design("hdm")
    hdm_path = Path(TESTS_GENERAL_PATH) / "example_models" / test_subfolder / "freighter_rays.hdm"
    stl_path = Path(TESTS_GENERAL_PATH) / "example_models" / test_subfolder / "freighter_ship.stl"
    aedtapp.modeler.model_units = "meter"
    aedtapp.modeler.import_3d_cad(str(stl_path))
    assert aedtapp.parse_hdm_file(str(hdm_path))
    plotter = aedtapp.get_hdm_plotter(str(hdm_path))
    assert plotter
    bounce1_path = Path(local_scratch.path) / "bounce1.jpg"
    plotter.plot_first_bounce_currents(str(bounce1_path))
    assert bounce1_path.exists()
    assert plotter
    bounce2_path = Path(local_scratch.path) / "bounce2.jpg"
    plotter.plot_rays(str(bounce2_path))
    assert bounce2_path.exists()


def test_boundary_perfect_e(aedtapp):
    aedtapp.insert_design("sbr_boundaries_perfect_e")
    b = aedtapp.modeler.create_box([0, 0, 0], [10, 20, 30])
    model_units = aedtapp.modeler.model_units

    bound = aedtapp.assign_perfect_e(name="b1", assignment=[b, b.faces[0]], height_deviation=2, roughness=0.4)
    assert bound.properties["SBR+ Rough Surface Height Standard Deviation"] == f"2{model_units}"

    bound2 = aedtapp.assign_perfect_e(assignment=[b, b.faces[0]], height_deviation="3mm")
    assert bound2.properties["SBR+ Rough Surface Height Standard Deviation"] == "3mm"

    with pytest.raises(AEDTRuntimeError):
        aedtapp.assign_perfect_e(name="b1", assignment=[b, b.faces[0]], height_deviation="3mm")

    with pytest.raises(AEDTRuntimeError):
        aedtapp.assign_perfect_e(assignment="invented")


def test_boundary_perfect_h(aedtapp):
    aedtapp.insert_design("sbr_boundaries_perfect_h")
    b = aedtapp.modeler.create_box([0, 0, 0], [10, 20, 30])
    model_units = aedtapp.modeler.model_units

    bound = aedtapp.assign_perfect_h(name="b1", assignment=[b, b.faces[0]], height_deviation=2, roughness=0.4)
    assert bound.properties["SBR+ Rough Surface Height Standard Deviation"] == f"2{model_units}"

    bound2 = aedtapp.assign_perfect_h(assignment=[b, b.faces[0]], height_deviation="3mm")
    assert bound2.properties["SBR+ Rough Surface Height Standard Deviation"] == "3mm"

    with pytest.raises(AEDTRuntimeError):
        aedtapp.assign_perfect_h(name="b1", assignment=[b, b.faces[0]], height_deviation="3mm")

    with pytest.raises(AEDTRuntimeError):
        aedtapp.assign_perfect_h(assignment="invented")


def test_boundaries_finite_conductivity(aedtapp):
    aedtapp.insert_design("hfss_finite_conductivity")
    b = aedtapp.modeler.create_box([0, 0, 0], [10, 20, 30])

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

    coat = aedtapp.assign_finite_conductivity([b.id, b.name, b.faces[0]], **args)
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

    coat2 = aedtapp.assign_finite_conductivity([b.id, b.name, b.faces[0]], **args)
    assert coat2.properties["SBR+ Rough Surface Height Standard Deviation"] == f"1{aedtapp.modeler.model_units}"

    with pytest.raises(AEDTRuntimeError):
        aedtapp.assign_finite_conductivity([b.id, b.name, b.faces[0]], **args)

    with pytest.raises(AEDTRuntimeError):
        aedtapp.assign_finite_conductivity(["insulator2"])


def test_boundaries_layered_impedance(aedtapp):
    aedtapp.insert_design("hfss_layered_impedance")
    b = aedtapp.modeler.create_box([0, 0, 0], [10, 20, 30])
    model_units = aedtapp.modeler.model_units

    # One side
    args = {
        "material": ["aluminum", "vacuum"],
        "thickness": ["0.5mm", "PerfectE"],
        "is_two_side": False,
        "is_shell_element": False,
        "height_deviation": 1,
        "roughness": 0.5,
    }

    coat = aedtapp.assign_layered_impedance([b.id, b.name, b.faces[0]], **args)
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

    coat2 = aedtapp.assign_layered_impedance([b.id, b.name, b.faces[0]], **args)
    assert coat2.properties["SBR+ Rough Surface Height Standard Deviation"] == f"1{model_units}"

    # Repeat name
    with pytest.raises(AEDTRuntimeError):
        aedtapp.assign_layered_impedance([b.id, b.name, b.faces[0]], **args)

    # Not existing assignment
    with pytest.raises(AEDTRuntimeError):
        aedtapp.assign_layered_impedance(["insulator2"])

    args = {
        "material": "aluminum",
        "thickness": "1mm",
        "is_two_side": False,
        "is_shell_element": False,
        "height_deviation": 1,
        "roughness": 0.5,
        "name": "b3",
    }

    coat3 = aedtapp.assign_layered_impedance([b.id, b.name, b.faces[0]], **args)
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
        aedtapp.assign_layered_impedance([b.id, b.name, b.faces[0]], **args)

    # Two side
    args = {
        "material": ["aluminum", "vacuum"],
        "thickness": ["0.5mm", "1um"],
        "is_two_side": True,
        "is_shell_element": False,
        "name": "b4",
    }

    coat4 = aedtapp.assign_layered_impedance([b.id, b.name, b.faces[0]], **args)
    assert coat4.properties["Layer 2/Material"] == "vacuum"
