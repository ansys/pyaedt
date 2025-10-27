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
import re

import pytest

try:
    import osmnx
except ImportError:
    osmnx = None

from ansys.aedt.core.generic.settings import is_linux
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from tests import TESTS_GENERAL_PATH
from tests.conftest import desktop_version

if desktop_version > "2022.2":
    test_project_name = "Cassegrain_231"
    tunnel = "tunnel1_231"
    person = "person3_231"
    vehicle = "vehicle1_231"
    bird = "bird1_231"

else:
    test_project_name = "Cassegrain"
    tunnel = "tunnel1"
    person = "person3"
    vehicle = "vehicle1"
    bird = "bird1"

test_subfolder = "T04"

custom_array = os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "custom_array.sarr")


@pytest.fixture(scope="class")
def aedtapp(add_app):
    app = add_app(
        project_name=test_project_name,
        design_name="Cassegrain_reflectors",
        solution_type="SBR+",
        subfolder=test_subfolder,
    )
    return app


@pytest.fixture(scope="class")
def source(add_app, aedtapp):
    app = add_app(project_name=aedtapp.project_name, design_name="feeder", just_open=True)
    return app


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, aedtapp, local_scratch):
        self.aedtapp = aedtapp
        self.local_scratch = local_scratch
        if not is_linux:
            # this should be changed upstream to use a HOME or TEMP folder by default...
            osmnx.settings.cache_folder = os.path.join(local_scratch.path, "cache")

    def test_01_open_source(self, source):
        assert self.aedtapp.create_sbr_linked_antenna(source, target_cs="feederPosition", field_type="farfield")
        assert len(self.aedtapp.native_components) == 1
        assert self.aedtapp.create_sbr_linked_antenna(
            source, target_cs="feederPosition", field_type="farfield", name="LinkedAntenna"
        )
        assert len(self.aedtapp.native_components) == 2
        assert self.aedtapp.create_sbr_linked_antenna(
            source, target_cs="feederPosition", name="LinkedAntennaNF1", current_conformance=True
        )
        assert len(self.aedtapp.native_components) == 3
        assert self.aedtapp.create_sbr_linked_antenna(
            source, target_cs="feederPosition", name="LinkedAntennaNF2", current_conformance=False
        )
        assert len(self.aedtapp.native_components) == 4

        self.aedtapp.create_sbr_linked_antenna(source, target_cs="feederPosition", field_type="farfield", is_array=True)
        assert len(self.aedtapp.native_components) == 5

        self.aedtapp.create_sbr_linked_antenna(
            source,
            target_cs="feederPosition",
            name="LinkedAntennaNF_array",
            current_conformance=True,
            custom_array=custom_array,
        )
        assert len(self.aedtapp.native_components) == 6

    def test_02_add_antennas(self):
        self.aedtapp.insert_design("add_antennas")
        dict1 = {"Polarization": "Horizontal"}
        par_beam = self.aedtapp.create_sbr_antenna(
            self.aedtapp.SbrAntennas.ParametricBeam, parameters=dict1, name="TX1"
        )
        assert par_beam.definition_name == "TX1"
        assert self.aedtapp.create_sbr_antenna(self.aedtapp.SbrAntennas.ConicalHorn, parameters=dict1, name="RX1")
        par_beam.native_properties["Unit"] = "in"
        assert par_beam.update()
        self.aedtapp.modeler.user_defined_components["TX1_1"].native_properties["Unit"] = "mm"

        assert len(self.aedtapp.native_components) == 2
        assert len(self.aedtapp.modeler.user_defined_components) == 2
        assert self.aedtapp.set_sbr_txrx_settings({"TX1_1_p1": "RX1_1_p1"})
        assert self.aedtapp.create_sbr_antenna(
            self.aedtapp.SbrAntennas.CrossDipole, use_current_source_representation=True
        )
        assert self.aedtapp.create_sbr_antenna(
            self.aedtapp.SbrAntennas.HalfWaveDipole, use_current_source_representation=True
        )
        assert self.aedtapp.create_sbr_antenna(
            self.aedtapp.SbrAntennas.HorizontalDipole, use_current_source_representation=True
        )
        assert self.aedtapp.create_sbr_antenna(
            self.aedtapp.SbrAntennas.ParametricSlot, use_current_source_representation=True
        )
        assert self.aedtapp.create_sbr_antenna(
            self.aedtapp.SbrAntennas.PyramidalHorn, use_current_source_representation=True
        )
        assert self.aedtapp.create_sbr_antenna(
            self.aedtapp.SbrAntennas.ShortDipole, use_current_source_representation=True
        )
        assert self.aedtapp.create_sbr_antenna(
            self.aedtapp.SbrAntennas.SmallLoop, use_current_source_representation=True
        )
        toberemoved = self.aedtapp.create_sbr_antenna(
            self.aedtapp.SbrAntennas.WireDipole, use_current_source_representation=True
        )

        native_components = len(self.aedtapp.native_components)

        toberemoved.delete()

        assert len(self.aedtapp.native_components) == native_components - 1
        assert len(self.aedtapp.modeler.user_defined_component_names) == native_components - 1
        array = self.aedtapp.create_sbr_antenna(
            self.aedtapp.SbrAntennas.WireMonopole, use_current_source_representation=False, is_array=True
        )
        array.native_properties["Array Length In Wavelength"] = "10"
        assert array.update()

        assert array.properties["Name"] == array.name

        native_components = len(self.aedtapp.native_component_names)
        array.name = "new_name"
        native_components_new = len(self.aedtapp.native_component_names)
        assert native_components_new == native_components

        assert "new_name" in self.aedtapp.native_component_names

        assert self.aedtapp.create_sbr_antenna(
            self.aedtapp.SbrAntennas.SmallLoop, use_current_source_representation=True, is_array=True
        )

        assert self.aedtapp.create_sbr_antenna(
            self.aedtapp.SbrAntennas.SmallLoop, use_current_source_representation=True, custom_array=custom_array
        )

    def test_03_add_ffd_antenna(self):
        self.aedtapp.insert_design("ffd_antenna")
        assert self.aedtapp.create_sbr_file_based_antenna(
            far_field_data=os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "test.ffd")
        )

        assert self.aedtapp.create_sbr_file_based_antenna(
            far_field_data=os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "test.ffd"), is_array=True
        )

        assert self.aedtapp.create_sbr_file_based_antenna(
            far_field_data=os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "test.ffd"),
            custom_array=custom_array,
        )

    def test_04_add_environment(self):
        self.aedtapp.insert_design("Environment_test")
        self.aedtapp.solution_type = "SBR+"
        env_folder = os.path.join(TESTS_GENERAL_PATH, "example_models", "library", "environment_library", tunnel)
        road1 = self.aedtapp.modeler.add_environment(env_folder)
        assert road1.name

    def test_05_add_person(self):
        person_folder = os.path.join(TESTS_GENERAL_PATH, "example_models", "library", "actor_library", person)
        person1 = self.aedtapp.modeler.add_person(person_folder, 1.0, [25, 1.5, 0], 180)
        assert person1.offset == [25, 1.5, 0]
        assert person1.yaw == "180deg"
        assert person1.pitch == "0deg"
        assert person1.roll == "0deg"

    def test_06_add_car(self):
        car_folder = os.path.join(TESTS_GENERAL_PATH, "example_models", "library", "actor_library", vehicle)
        car1 = self.aedtapp.modeler.add_vehicle(car_folder, 1.0, [3, -2.5, 0])
        assert car1.offset == [3, -2.5, 0]
        assert car1.yaw == "0deg"
        assert car1.pitch == "0deg"
        assert car1.roll == "0deg"

    def test_07_add_bird(self):
        bird_folder = os.path.join(TESTS_GENERAL_PATH, "example_models", "library", "actor_library", bird)
        bird1 = self.aedtapp.modeler.add_bird(bird_folder, 1.0, [19, 4, 3], 120, -5, flapping_rate=30)
        assert bird1.offset == [19, 4, 3]
        assert bird1.yaw == "120deg"
        assert bird1.pitch == "-5deg"
        assert bird1.roll == "0deg"
        assert bird1._flapping_rate == "30Hz"

    def test_08_add_radar(self):
        radar_lib = os.path.join(
            TESTS_GENERAL_PATH,
            "example_models",
            "library",
            "radar_modules",
        )
        assert self.aedtapp.create_sbr_radar_from_json(radar_lib, name="Example_1Tx_1Rx", speed=3)
        assert self.aedtapp.create_sbr_radar_from_json(radar_lib, name="Example_1Tx_4Rx")

    def test_09_add_doppler_sweep(self):
        setup, sweep = self.aedtapp.create_sbr_pulse_doppler_setup(sweep_time_duration=30)
        assert "PulseSetup" in setup.name
        assert "PulseSweep" in sweep.name
        assert setup.props["SbrRangeDopplerWaveformType"] == "PulseDoppler"
        assert sweep.props["Sim. Setups"] == [setup.name]

    def test_10_add_chirp_sweep(self):
        setup, sweep = self.aedtapp.create_sbr_chirp_i_doppler_setup(sweep_time_duration=20)
        assert setup.props["SbrRangeDopplerWaveformType"] == "ChirpSeqFmcw"
        assert setup.props["ChannelConfiguration"] == "IChannelOnly"
        assert sweep.props["Sim. Setups"] == [setup.name]
        setup, sweep = self.aedtapp.create_sbr_chirp_iq_doppler_setup(sweep_time_duration=10)
        assert setup.props["SbrRangeDopplerWaveformType"] == "ChirpSeqFmcw"
        assert setup.props["ChannelConfiguration"] == "IQChannels"
        assert sweep.props["Sim. Setups"] == [setup.name]

    def test_11_add_sbr_boundaries_in_hfss_solution(self, add_app):
        hfss_terminal = add_app(solution_type="Terminal")

        # sbr file based antenna should only work for SBR+ solution.
        with pytest.raises(AEDTRuntimeError, match=re.escape("This native component only applies to a SBR+ solution.")):
            hfss_terminal.create_sbr_file_based_antenna(
                far_field_data=os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "test.ffd")
            )

    @pytest.mark.skipif(is_linux, reason="Not supported.")
    def test_12_import_map(self):
        self.aedtapp.insert_design("city")
        ansys_home = [40.273726, -80.168269]
        parts_dict = self.aedtapp.modeler.import_from_openstreet_map(
            ansys_home, terrain_radius=200, road_step=3, plot_before_importing=False, import_in_aedt=True
        )
        for part in parts_dict["parts"]:
            assert os.path.exists(parts_dict["parts"][part]["file_name"])

    def test_13_create_custom_array(self, aedtapp, local_scratch):
        output_file1 = aedtapp.create_sbr_custom_array_file()
        assert os.path.isfile(output_file1)

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
        assert os.path.isfile(output_file2)

    @pytest.mark.skipif(is_linux, reason="feature supported in Cpython")
    def test_read_hdm(self):
        self.aedtapp.insert_design("hdm")
        hdm_path = os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "freighter_rays.hdm")
        stl_path = os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "freighter_ship.stl")
        self.aedtapp.modeler.model_units = "meter"
        self.aedtapp.modeler.import_3d_cad(stl_path)
        assert self.aedtapp.parse_hdm_file(hdm_path)
        plotter = self.aedtapp.get_hdm_plotter(hdm_path)
        assert plotter
        plotter.plot_first_bounce_currents(os.path.join(self.local_scratch.path, "bounce1.jpg"))
        assert os.path.exists(os.path.join(self.local_scratch.path, "bounce1.jpg"))
        assert plotter
        plotter.plot_rays(os.path.join(self.local_scratch.path, "bounce2.jpg"))
        assert os.path.exists(os.path.join(self.local_scratch.path, "bounce2.jpg"))

    def test_boundary_perfect_e(self):
        self.aedtapp.insert_design("sbr_boundaries_perfect_e")
        b = self.aedtapp.modeler.create_box([0, 0, 0], [10, 20, 30])
        model_units = self.aedtapp.modeler.model_units

        bound = self.aedtapp.assign_perfect_e(name="b1", assignment=[b, b.faces[0]], height_deviation=2, roughness=0.4)
        assert bound.properties["SBR+ Rough Surface Height Standard Deviation"] == f"2{model_units}"

        bound2 = self.aedtapp.assign_perfect_e(assignment=[b, b.faces[0]], height_deviation="3mm")
        assert bound2.properties["SBR+ Rough Surface Height Standard Deviation"] == "3mm"

        with pytest.raises(AEDTRuntimeError):
            self.aedtapp.assign_perfect_e(name="b1", assignment=[b, b.faces[0]], height_deviation="3mm")

        with pytest.raises(AEDTRuntimeError):
            self.aedtapp.assign_perfect_e(assignment="invented")

    def test_boundary_perfect_h(self):
        self.aedtapp.insert_design("sbr_boundaries_perfect_h")
        b = self.aedtapp.modeler.create_box([0, 0, 0], [10, 20, 30])
        model_units = self.aedtapp.modeler.model_units

        bound = self.aedtapp.assign_perfect_h(name="b1", assignment=[b, b.faces[0]], height_deviation=2, roughness=0.4)
        assert bound.properties["SBR+ Rough Surface Height Standard Deviation"] == f"2{model_units}"

        bound2 = self.aedtapp.assign_perfect_h(assignment=[b, b.faces[0]], height_deviation="3mm")
        assert bound2.properties["SBR+ Rough Surface Height Standard Deviation"] == "3mm"

        with pytest.raises(AEDTRuntimeError):
            self.aedtapp.assign_perfect_h(name="b1", assignment=[b, b.faces[0]], height_deviation="3mm")

        with pytest.raises(AEDTRuntimeError):
            self.aedtapp.assign_perfect_h(assignment="invented")

    def test_boundaries_finite_conductivity(self):
        self.aedtapp.insert_design("hfss_finite_conductivity")
        b = self.aedtapp.modeler.create_box([0, 0, 0], [10, 20, 30])

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

        coat = self.aedtapp.assign_finite_conductivity([b.id, b.name, b.faces[0]], **args)
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

        coat2 = self.aedtapp.assign_finite_conductivity([b.id, b.name, b.faces[0]], **args)
        assert (
            coat2.properties["SBR+ Rough Surface Height Standard Deviation"] == f"1{self.aedtapp.modeler.model_units}"
        )

        with pytest.raises(AEDTRuntimeError):
            self.aedtapp.assign_finite_conductivity([b.id, b.name, b.faces[0]], **args)

        with pytest.raises(AEDTRuntimeError):
            self.aedtapp.assign_finite_conductivity(["insulator2"])

    def test_boundaries_layered_impedance(self):
        self.aedtapp.insert_design("hfss_layered_impedance")
        b = self.aedtapp.modeler.create_box([0, 0, 0], [10, 20, 30])
        model_units = self.aedtapp.modeler.model_units

        # One side
        args = {
            "material": ["aluminum", "vacuum"],
            "thickness": ["0.5mm", "PerfectE"],
            "is_two_side": False,
            "is_shell_element": False,
            "height_deviation": 1,
            "roughness": 0.5,
        }

        coat = self.aedtapp.assign_layered_impedance([b.id, b.name, b.faces[0]], **args)
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

        coat2 = self.aedtapp.assign_layered_impedance([b.id, b.name, b.faces[0]], **args)
        assert coat2.properties["SBR+ Rough Surface Height Standard Deviation"] == f"1{model_units}"

        # Repeat name
        with pytest.raises(AEDTRuntimeError):
            self.aedtapp.assign_layered_impedance([b.id, b.name, b.faces[0]], **args)

        # Not existing assignment
        with pytest.raises(AEDTRuntimeError):
            self.aedtapp.assign_layered_impedance(["insulator2"])

        args = {
            "material": "aluminum",
            "thickness": "1mm",
            "is_two_side": False,
            "is_shell_element": False,
            "height_deviation": 1,
            "roughness": 0.5,
            "name": "b3",
        }

        coat3 = self.aedtapp.assign_layered_impedance([b.id, b.name, b.faces[0]], **args)
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
            self.aedtapp.assign_layered_impedance([b.id, b.name, b.faces[0]], **args)

        # Two side
        args = {
            "material": ["aluminum", "vacuum"],
            "thickness": ["0.5mm", "1um"],
            "is_two_side": True,
            "is_shell_element": False,
            "name": "b4",
        }

        coat4 = self.aedtapp.assign_layered_impedance([b.id, b.name, b.faces[0]], **args)
        assert coat4.properties["Layer 2/Material"] == "vacuum"
