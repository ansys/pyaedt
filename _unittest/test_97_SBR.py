import gc
import os
# Import required modules
from pyaedt import Hfss
from pyaedt.generic.filesystem import Scratch

# Setup paths for module imports
from _unittest.conftest import local_path, scratch_path

try:
    import pytest  # noqa: F401
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest  # noqa: F401

test_project_name = "Cassegrain"


class TestClass:
    def setup_class(self):
        gc.collect()
        # set a scratch directory and the environment / test data
        with Scratch(scratch_path) as self.local_scratch:
            example_project = os.path.join(local_path, "example_models", test_project_name + ".aedt")
            self.test_project = self.local_scratch.copyfile(example_project)
            self.aedtapp = Hfss(projectname=self.test_project, designname="Cassegrain_", solution_type="SBR+")
            self.source = Hfss(projectname=test_project_name, designname="feeder")

    def teardown_class(self):
        self.aedtapp._desktop.ClearMessages("", "", 3)
        assert self.source.close_project(self.source.project_name, False)
        self.local_scratch.remove()

    def test_01_open_source(self):
        assert self.aedtapp.create_sbr_linked_antenna(self.source, target_cs="feederPosition", fieldtype="farfield")
        assert len(self.aedtapp.native_components) == 1

    def test_02_add_antennas(self):
        dict1 = {"polarization": "Horizontal"}
        par_beam = self.aedtapp.create_sbr_antenna(
            self.aedtapp.SbrAntennas.ParametricBeam, parameters_dict=dict1, antenna_name="TX1"
        )
        assert self.aedtapp.create_sbr_antenna(
            self.aedtapp.SbrAntennas.ConicalHorn, parameters_dict=dict1, antenna_name="RX1"
        )
        par_beam.native_properties["Unit"] = "in"
        assert par_beam.update()
        assert len(self.aedtapp.native_components) == 3
        assert self.aedtapp.set_sbr_txrx_settings({"TX1": "RX1"})
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
        l = len(self.aedtapp.native_components)
        toberemoved.delete()
        assert len(self.aedtapp.native_components) == l - 1
        array = self.aedtapp.create_sbr_antenna(
            self.aedtapp.SbrAntennas.WireMonopole, use_current_source_representation=False, is_array=True
        )
        array.native_properties["Array Length In Wavelength"] = "10"
        assert array.update()

    def test_03_add_ffd_antenna(self):
        assert self.aedtapp.create_sbr_file_based_antenna(
            ffd_full_path=os.path.join(local_path, "example_models", "test.ffd")
        )

    def test_04_add_environment(self):
        self.aedtapp.insert_design("Environment_test")
        self.aedtapp.solution_type = "SBR+"
        env_folder = os.path.join(local_path, "example_models", "library", "environment_library", "tunnel1")
        road1 = self.aedtapp.modeler.primitives.add_environment(env_folder)
        assert road1.name

    def test_05_add_person(self):
        person_folder = os.path.join(local_path, "example_models", "library", "actor_library", "person3")
        person1 = self.aedtapp.modeler.primitives.add_person(person_folder, 1.0, [25, 1.5, 0], 180)
        assert person1.offset == [25, 1.5, 0]
        assert person1.yaw == "180deg"
        assert person1.pitch == "0deg"
        assert person1.roll == "0deg"

    def test_06_add_car(self):
        car_folder = os.path.join(local_path, "example_models", "library", "actor_library", "vehicle1")
        car1 = self.aedtapp.modeler.primitives.add_vehicle(car_folder, 1.0, [3, -2.5, 0])
        assert car1.offset == [3, -2.5, 0]
        assert car1.yaw == "0deg"
        assert car1.pitch == "0deg"
        assert car1.roll == "0deg"

    def test_07_add_bird(self):
        bird_folder = os.path.join(local_path, "example_models", "library", "actor_library", "bird1")
        bird1 = self.aedtapp.modeler.primitives.add_bird(bird_folder, 1.0, [19, 4, 3], 120, -5, flapping_rate=30)
        assert bird1.offset == [19, 4, 3]
        assert bird1.yaw == "120deg"
        assert bird1.pitch == "-5deg"
        assert bird1.roll == "0deg"
        assert bird1._flapping_rate == "30Hz"

    def test_08_add_radar(self):
        radar_lib = os.path.join(
            local_path,
            "example_models",
            "library",
            "radar_modules",
        )
        assert self.aedtapp.create_sbr_radar_from_json(radar_lib, radar_name="Example_1Tx_1Rx", speed=3)
        assert self.aedtapp.create_sbr_radar_from_json(radar_lib, radar_name="Example_1Tx_4Rx")

    def test_09_add_doppler_sweep(self):
        setup, sweep = self.aedtapp.create_sbr_pulse_doppler_setup(sweep_time_duration=30)
        assert "PulseSetup" in setup.name
        assert "PulseSweep" in sweep.name
        assert setup.props["SbrRangeDopplerWaveformType"] == "PulseDoppler"
        assert sweep.props["Sim. Setups"] == [setup.name]
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
