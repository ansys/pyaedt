import os

from _unittest.conftest import BasisTest
from _unittest.conftest import desktop_version
from _unittest.conftest import local_path
from pyaedt import Hfss
from pyaedt import is_ironpython

try:
    import pytest  # noqa: F401
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest  # noqa: F401

if desktop_version > "2022.2":
    test_project_name = "Cassegrain_231"
    tunnel = "tunnel1_231"
    person = "person3_231"
    vehicle = "vehicle1_231"
    bird = "bird1_231"
    sbr_platform = "satellite_231"
    array = "array_231"

else:
    test_project_name = "Cassegrain"
    tunnel = "tunnel1"
    person = "person3"
    vehicle = "vehicle1"
    bird = "bird1"
    sbr_platform = "satellite"
    array = "array"
test_subfolder = "T17"


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(
            self,
            project_name=test_project_name,
            design_name="Cassegrain_reflectors",
            solution_type="SBR+",
            subfolder=test_subfolder,
        )
        self.source = Hfss(self.aedtapp.project_name, "feeder", specified_version=desktop_version)
        self.sbr_platform = BasisTest.add_app(self, project_name=sbr_platform, subfolder=test_subfolder)
        self.array = BasisTest.add_app(self, project_name=array, subfolder=test_subfolder)

    def teardown_class(self):
        BasisTest.my_teardown(self)

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
        self.aedtapp.modeler.user_defined_components["TX1_1"].native_properties["Unit"] = "mm"

        assert len(self.aedtapp.native_components) == 3
        assert len(self.aedtapp.modeler.user_defined_components) == 3
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
        l = len(self.aedtapp.native_components)
        toberemoved.delete()
        assert len(self.aedtapp.native_components) == l - 1
        assert len(self.aedtapp.modeler.user_defined_component_names) == l - 1
        array = self.aedtapp.create_sbr_antenna(
            self.aedtapp.SbrAntennas.WireMonopole, use_current_source_representation=False, is_array=True
        )
        array.native_properties["Array Length In Wavelength"] = "10"
        assert array.update()

    def test_03_add_ffd_antenna(self):
        assert self.aedtapp.create_sbr_file_based_antenna(
            ffd_full_path=os.path.join(local_path, "example_models", test_subfolder, "test.ffd")
        )

    def test_04_add_environment(self):
        self.aedtapp.insert_design("Environment_test")
        self.aedtapp.solution_type = "SBR+"
        env_folder = os.path.join(local_path, "example_models", "library", "environment_library", tunnel)
        road1 = self.aedtapp.modeler.add_environment(env_folder)
        assert road1.name

    def test_05_add_person(self):
        person_folder = os.path.join(local_path, "example_models", "library", "actor_library", person)
        person1 = self.aedtapp.modeler.add_person(person_folder, 1.0, [25, 1.5, 0], 180)
        assert person1.offset == [25, 1.5, 0]
        assert person1.yaw == "180deg"
        assert person1.pitch == "0deg"
        assert person1.roll == "0deg"

    def test_06_add_car(self):
        car_folder = os.path.join(local_path, "example_models", "library", "actor_library", vehicle)
        car1 = self.aedtapp.modeler.add_vehicle(car_folder, 1.0, [3, -2.5, 0])
        assert car1.offset == [3, -2.5, 0]
        assert car1.yaw == "0deg"
        assert car1.pitch == "0deg"
        assert car1.roll == "0deg"

    def test_07_add_bird(self):
        bird_folder = os.path.join(local_path, "example_models", "library", "actor_library", bird)
        bird1 = self.aedtapp.modeler.add_bird(bird_folder, 1.0, [19, 4, 3], 120, -5, flapping_rate=30)
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

    def test_10_add_chirp_sweep(self):
        setup, sweep = self.aedtapp.create_sbr_chirp_i_doppler_setup(sweep_time_duration=20)
        assert setup.props["SbrRangeDopplerWaveformType"] == "ChirpSeqFmcw"
        assert setup.props["ChannelConfiguration"] == "IChannelOnly"
        assert sweep.props["Sim. Setups"] == [setup.name]
        setup, sweep = self.aedtapp.create_sbr_chirp_iq_doppler_setup(sweep_time_duration=10)
        assert setup.props["SbrRangeDopplerWaveformType"] == "ChirpSeqFmcw"
        assert setup.props["ChannelConfiguration"] == "IQChannels"
        assert sweep.props["Sim. Setups"] == [setup.name]

    def test_11_add_sbr_boundaries_in_hfss_solution(self):
        hfss_terminal = Hfss(solution_type="Terminal")

        # sbr file based antenna should only work for SBR+ solution.
        assert not hfss_terminal.create_sbr_file_based_antenna(
            ffd_full_path=os.path.join(local_path, "example_models", test_subfolder, "test.ffd")
        )

    @pytest.mark.skipif(is_ironpython, reason="Not supported.")
    def test_12_import_map(self):
        self.aedtapp.insert_design("city")
        ansys_home = [40.273726, -80.168269]
        parts_dict = self.aedtapp.modeler.import_from_openstreet_map(
            ansys_home, terrain_radius=100, road_step=3, plot_before_importing=False, import_in_aedt=True
        )
        for part in parts_dict["parts"]:
            assert os.path.exists(parts_dict["parts"][part]["file_name"])

    @pytest.mark.skipif(sys.version_info < (3, 8), reason="Not supported.")
    def test_13_link_array(self):
        assert self.sbr_platform.create_sbr_linked_antenna(self.array, target_cs="antenna_CS", fieldtype="farfield")
        self.sbr_platform.analyze_all()
        ffdata = self.sbr_platform.get_antenna_ffd_solution_data(frequencies=12e9, sphere_name="3D")
        self.array.close_project()
        ffdata2 = self.sbr_platform.get_antenna_ffd_solution_data(frequencies=12e9, sphere_name="3D", overwrite=False)

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
