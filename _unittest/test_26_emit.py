# Import required modules
import os
import sys

from _unittest.conftest import BasisTest
from _unittest.conftest import config
from _unittest.conftest import is_ironpython

from pyaedt import Emit
from pyaedt.emit_core import EmitConstants as econsts
from pyaedt.generic import constants as consts
from pyaedt.generic.general_methods import is_linux
from pyaedt.modeler.circuits.PrimitivesEmit import EmitAntennaComponent
from pyaedt.modeler.circuits.PrimitivesEmit import EmitComponent
from pyaedt.modeler.circuits.PrimitivesEmit import EmitComponents

try:
    import pytest
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest

test_subfolder = "T26"


@pytest.mark.skipif(is_linux, reason="Emit API fails on linux.")
class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, application=Emit)

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_objects(self):
        assert self.aedtapp.solution_type
        assert isinstance(self.aedtapp.modeler.components, EmitComponents)
        assert self.aedtapp.modeler
        assert self.aedtapp.oanalysis is None
        if self.aedtapp._aedt_version >= "2023.1" and sys.version_info.major == 3 and sys.version_info.minor == 7:
            assert str(type(self.aedtapp._emit_api)) == "<class 'EmitApiPython.EmitApi'>"
            assert self.aedtapp.results is not None

    @pytest.mark.skipif(
        config["desktopVersion"] <= "2022.1" or is_ironpython, reason="Skipped on versions earlier than 2021.2"
    )
    def test_create_components(self):
        self.aedtapp = BasisTest.add_app(self, application=Emit)
        radio = self.aedtapp.modeler.components.create_component("New Radio", "TestRadio")
        assert radio.name == "TestRadio"
        assert isinstance(radio, EmitComponent)
        antenna = self.aedtapp.modeler.components.create_component("Antenna", "TestAntenna")
        assert antenna.name == "TestAntenna"
        assert isinstance(antenna, EmitAntennaComponent)

    @pytest.mark.skipif(
        config["desktopVersion"] <= "2022.1" or is_ironpython, reason="Skipped on versions earlier than 2021.2"
    )
    def test_connect_components(self):
        self.aedtapp = BasisTest.add_app(self, application=Emit)
        radio = self.aedtapp.modeler.components.create_component("New Radio")
        antenna = self.aedtapp.modeler.components.create_component("Antenna")
        antenna.move_and_connect_to(radio)
        antenna_port = antenna.port_names()[0]  # antennas have 1 port
        radio_port = radio.port_names()[0]  # radios have 1 port
        connected_comp, connected_port = antenna.port_connection(antenna_port)
        assert connected_comp == radio.name
        assert connected_port == radio_port
        # Test get_connected_components()
        connected_components_list = radio.get_connected_components()
        assert antenna in connected_components_list
        # Verify None,None is returned for an unconnected port
        radio2 = self.aedtapp.modeler.components.create_component("New Radio")
        radio2_port = radio2.port_names()[0]
        connected_comp, connected_port = radio2.port_connection(radio2_port)
        assert connected_comp is None
        assert connected_port is None
        # Test create_radio_antenna
        radio3, antenna3 = self.aedtapp.modeler.components.create_radio_antenna("New Radio")
        ant3_port = antenna3.port_names()[0]
        rad3_port = radio3.port_names()[0]
        connected_comp, connected_port = antenna3.port_connection(ant3_port)
        assert connected_comp == radio3.name
        assert connected_port == rad3_port

    @pytest.mark.skipif(
        config["desktopVersion"] <= "2022.1" or is_ironpython, reason="Skipped on versions earlier than 2022 R2."
    )
    def test_radio_component(self):
        self.aedtapp = BasisTest.add_app(self, application=Emit)
        radio = self.aedtapp.modeler.components.create_component("New Radio")
        # default radio has 1 Tx channel and 1 Rx channel
        assert radio.has_rx_channels()
        assert radio.has_tx_channels()
        # test band.enabled to confirm component properties can be get/set
        assert len(radio.bands()) > 0
        band = radio.bands()[0]
        assert band.enabled
        band.enabled = False
        assert not band.enabled
        # Try set band power from the radio
        exception_raised = False
        try:
            radio.set_band_power_level(100)
        except:
            exception_raised = True
        assert exception_raised
        # Try getting band power from the radio
        exception_raised = False
        try:
            radio.get_band_power_level()
        except:
            exception_raised = True
        assert exception_raised
        # test band.set_band_power_level
        band.set_band_power_level(100)
        power = band.get_band_power_level()
        assert power == 100.0
        # test band.set_band_power_level
        band.set_band_power_level(10, "W")
        power = band.get_band_power_level("mW")
        assert power == 10000.0
        # test frequency unit conversions
        start_freq = radio.band_start_frequency(band)
        assert start_freq == 100.0
        start_freq = radio.band_start_frequency(band, "Hz")
        assert start_freq == 100000000.0
        start_freq = radio.band_start_frequency(band, "kHz")
        assert start_freq == 100000.0
        start_freq = radio.band_start_frequency(band, "GHz")
        assert start_freq == 0.1
        start_freq = radio.band_start_frequency(band, "THz")
        assert start_freq == 0.0001
        # test power unit conversions
        band_power = radio.band_tx_power(band)
        assert band_power == 40.0
        band_power = radio.band_tx_power(band, "dBW")
        assert band_power == 10.0
        band_power = radio.band_tx_power(band, "mW")
        assert band_power == 10000.0
        band_power = radio.band_tx_power(band, "W")
        assert band_power == 10.0
        band_power = radio.band_tx_power(band, "kW")
        assert band_power == 0.01

    @pytest.mark.skipif(
        config["desktopVersion"] <= "2022.1" or is_ironpython, reason="Skipped on versions earlier than 2022 R2."
    )
    def test_emit_power_conversion(self):
        # Test power unit conversions (dBm to user_units)
        powers = [10, 20, 30, 40, 50]
        converted_powers = consts.unit_converter(powers, "Power", "dBm", "dBm")
        assert converted_powers == powers
        converted_powers = consts.unit_converter(powers, "Power", "dBm", "dBW")
        assert converted_powers == [-20, -10, 0, 10, 20]
        converted_powers = consts.unit_converter(powers, "Power", "dBm", "mW")
        assert converted_powers == [10, 100, 1000, 10000, 100000]
        converted_powers = consts.unit_converter(powers, "Power", "dBm", "W")
        assert converted_powers == [0.01, 0.1, 1, 10, 100]
        converted_powers = consts.unit_converter(powers, "Power", "dBm", "kW")
        assert converted_powers == [0.00001, 0.0001, 0.001, 0.01, 0.1]

        # Test power conversions (user units to dBm)
        powers = [0.00001, 0.0001, 0.001, 0.01, 0.1]
        converted_powers = consts.unit_converter(powers, "Power", "kW", "dBm")
        assert converted_powers == [10, 20, 30, 40, 50]
        powers = [0.01, 0.1, 1, 10, 100]
        converted_powers = consts.unit_converter(powers, "Power", "W", "dBm")
        assert converted_powers == [10, 20, 30, 40, 50]
        powers = [10, 100, 1000, 10000, 100000]
        converted_powers = consts.unit_converter(powers, "Power", "mW", "dBm")
        assert converted_powers == [10, 20, 30, 40, 50]
        powers = [-20, -10, 0, 10, 20]
        converted_powers = consts.unit_converter(powers, "Power", "dBW", "dBm")
        assert converted_powers == [10, 20, 30, 40, 50]
        powers = [10, 20, 30, 40, 50]
        converted_powers = consts.unit_converter(powers, "Power", "dBm", "dBm")
        assert converted_powers == [10, 20, 30, 40, 50]
        power = 10
        converted_power = consts.unit_converter(power, "Power", "dBW", "dBm")
        assert converted_power == 40
        power = 10
        converted_power = consts.unit_converter(power, "Power", "mW", "dBm")
        assert converted_power == 10
        power = 0.1
        converted_power = consts.unit_converter(power, "Power", "kW", "dBm")
        assert converted_power == 50

        # Test bad units
        power = 10
        bad_units = consts.unit_converter(power, "Power", "dbw", "dBm")
        assert bad_units == power
        power = 30
        bad_units = consts.unit_converter(power, "Power", "w", "dBm")
        assert bad_units == power

    @pytest.mark.skipif(
        config["desktopVersion"] <= "2023.2" or is_ironpython, reason="Skipped on versions earlier than 2023 R2."
    )
    def test_units_getters(self):
        self.aedtapp = BasisTest.add_app(self, application=Emit)

        # Set a single unit
        valid = self.aedtapp.set_units("Frequency", "Hz")
        units = self.aedtapp.get_units("Frequency")
        assert valid
        assert units == "Hz"

        # Test bad unit input
        units = self.aedtapp.get_units("Bad units")
        assert units == None

        valid = self.aedtapp.set_units("Bad units", "Hz")
        assert valid is False

        valid = self.aedtapp.set_units("Frequency", "hertz")
        assert valid is False

        # Set a list of units
        unit_system = ["Power", "Frequency", "Length", "Time", "Voltage", "Data Rate", "Resistance"]
        units = ["mW", "GHz", "nm", "ps", "mV", "Gbps", "uOhm"]
        valid = self.aedtapp.set_units(unit_system, units)
        updated_units = self.aedtapp.get_units()
        assert valid
        assert updated_units == {
            "Power": "mW",
            "Frequency": "GHz",
            "Length": "nm",
            "Time": "ps",
            "Voltage": "mV",
            "Data Rate": "Gbps",
            "Resistance": "uOhm",
        }

        # Set a bad list of units
        unit_system = ["Por", "Frequency", "Length", "Time", "Voltage", "Data Rate", "Resistance"]
        units = ["mW", "GHz", "nm", "ps", "mV", "Gbps", "uOhm"]
        valid = self.aedtapp.set_units(unit_system, units)
        assert valid is False

        unit_system = ["Power", "Frequency", "Length", "Time", "Voltage", "Data Rate", "Resistance"]
        units = ["mW", "f", "nm", "ps", "mV", "Gbps", "uOhm"]
        valid = self.aedtapp.set_units(unit_system, units)
        assert valid is False

    @pytest.mark.skipif(
        config["desktopVersion"] <= "2022.1" or is_ironpython, reason="Skipped on versions earlier than 2021 R2."
    )
    def test_antenna_component(self):
        self.aedtapp = BasisTest.add_app(self, application=Emit)
        antenna = self.aedtapp.modeler.components.create_component("Antenna")
        # Default pattern filename is empty string
        pattern_filename = antenna.get_pattern_filename()
        assert pattern_filename == ""
        # Default orientation is 0 0 0
        orientation = antenna.get_orientation_rpy()
        assert orientation == (0.0, 0.0, 0.0)
        # Default position is 0 0 0
        position = antenna.get_position()
        assert position == (0.0, 0.0, 0.0)

    @pytest.mark.skipif(
        config["desktopVersion"] <= "2023.1" or is_ironpython,
        reason="Skipped on versions earlier than 2023.2",
    )
    def test_revision_generation(self):
        self.aedtapp = BasisTest.add_app(self, application=Emit)
        assert len(self.aedtapp.results.revisions) == 0
        # place components and generate the appropriate number of revisions
        rad1 = self.aedtapp.modeler.components.create_component("UE - Handheld")
        ant1 = self.aedtapp.modeler.components.create_component("Antenna")
        if rad1 and ant1:
            ant1.move_and_connect_to(rad1)
        rad2 = self.aedtapp.modeler.components.create_component("Bluetooth")
        ant2 = self.aedtapp.modeler.components.create_component("Antenna")
        if rad2 and ant2:
            ant2.move_and_connect_to(rad2)
        rad3 = self.aedtapp.modeler.components.create_component("Bluetooth")
        ant3 = self.aedtapp.modeler.components.create_component("Antenna")
        if rad3 and ant3:
            ant3.move_and_connect_to(rad3)
        rev = self.aedtapp.results.analyze()
        assert len(self.aedtapp.results.revisions) == 1
        assert rev.name == "Revision 10"
        assert rev.revision_number == 10
        rev_timestamp = rev.timestamp
        assert rev_timestamp
        self.aedtapp.results.analyze()
        assert len(self.aedtapp.results.revisions) == 1
        rad4 = self.aedtapp.modeler.components.create_component("Bluetooth")
        ant4 = self.aedtapp.modeler.components.create_component("Antenna")
        if rad4 and ant4:
            ant4.move_and_connect_to(rad4)
        rev2 = self.aedtapp.results.analyze()
        assert len(self.aedtapp.results.revisions) == 2
        rad5 = self.aedtapp.modeler.components.create_component("HAVEQUICK Airborne")
        ant5 = self.aedtapp.modeler.components.create_component("Antenna")
        if rad5 and ant5:
            ant4.move_and_connect_to(rad5)
        assert len(self.aedtapp.results.revisions) == 2
        # validate notes can be get/set
        rev2.notes = "Added Bluetooth and an antenna"
        notes = rev2.notes
        assert rev2.name == "Revision 13"
        assert notes == "Added Bluetooth and an antenna"
        # get the initial revision
        rev3 = self.aedtapp.results.get_revision("Revision 10")
        assert rev3.name == "Revision 10"
        assert rev3.revision_number == 10
        assert rev_timestamp == rev3.timestamp
        # get the most recent revision
        # there are changes, so it should be a new revision
        rev4 = self.aedtapp.results.analyze()
        assert rev4.name == "Revision 16"
        # get the initial revision
        rev5 = self.aedtapp.results.get_revision("Revision 10")
        assert rev5.name == "Revision 10"
        # get the most recent revision
        # no changes, so it should be the most recent revision
        rev6 = self.aedtapp.results.analyze()
        assert rev6.name == "Revision 16"

    @pytest.mark.skipif(
        config["desktopVersion"] <= "2023.1" or is_ironpython,
        reason="Skipped on versions earlier than 2023.2",
    )
    def test_manual_revision_access_test_getters(self):
        self.aedtapp = BasisTest.add_app(self, application=Emit)
        rad1 = self.aedtapp.modeler.components.create_component("UE - Handheld")
        ant1 = self.aedtapp.modeler.components.create_component("Antenna")
        rad2 = self.aedtapp.modeler.components.create_component("Bluetooth")
        if rad1 and ant1:
            ant1.move_and_connect_to(rad1)
        ant2 = self.aedtapp.modeler.components.create_component("Antenna")
        if rad2 and ant2:
            ant2.move_and_connect_to(rad2)
        rad3 = self.aedtapp.modeler.components.create_component("Bluetooth")
        ant3 = self.aedtapp.modeler.components.create_component("Antenna")
        if rad3 and ant3:
            ant3.move_and_connect_to(rad3)
        # Change the sampling
        modeRx = econsts.tx_rx_mode().rx
        sampling = rad3.get_sampling()
        assert sampling.node_name == "NODE-*-RF Systems-*-RF System-*-Radios-*-Bluetooth-*-Sampling"
        sampling.set_channel_sampling(percentage=25)
        rev = self.aedtapp.results.analyze()
        radiosRX = rev.get_receiver_names()
        assert radiosRX[0] == "Bluetooth"
        assert radiosRX[1] == "Bluetooth 2"
        bandsRX = rev.get_band_names(radiosRX[0], modeRx)
        assert bandsRX[0] == "Rx - Base Data Rate"
        assert bandsRX[1] == "Rx - Enhanced Data Rate"
        rx_frequencies = rev.get_active_frequencies(radiosRX[0], bandsRX[0], modeRx)
        assert rx_frequencies[0] == 2402.0
        assert rx_frequencies[1] == 2403.0
        # Change the units globally
        self.aedtapp.set_units("Frequency", "GHz")
        rx_frequencies = rev.get_active_frequencies(radiosRX[0], bandsRX[0], modeRx)
        assert rx_frequencies[0] == 2.402
        assert rx_frequencies[1] == 2.403
        # Change the return units only
        rx_frequencies = rev.get_active_frequencies(radiosRX[0], bandsRX[0], modeRx, "Hz")
        assert rx_frequencies[0] == 2402000000.0
        assert rx_frequencies[1] == 2403000000.0

        # Test set_sampling
        bandsRX = rev.get_band_names(radiosRX[1], modeRx)
        rx_frequencies = rev.get_active_frequencies(radiosRX[1], bandsRX[0], modeRx)
        assert len(rx_frequencies) == 20

        sampling.set_channel_sampling(max_channels=10)
        rev2 = self.aedtapp.results.analyze()
        rx_frequencies = rev2.get_active_frequencies(radiosRX[1], bandsRX[0], modeRx)
        assert len(rx_frequencies) == 10

        sampling.set_channel_sampling("Random", max_channels=75)
        rev3 = self.aedtapp.results.analyze()
        rx_frequencies = rev3.get_active_frequencies(radiosRX[1], bandsRX[0], modeRx)
        assert len(rx_frequencies) == 75
        assert rx_frequencies[0] == 2.402
        assert rx_frequencies[1] == 2.403

        sampling.set_channel_sampling("Random", percentage=25, seed=100)
        rev4 = self.aedtapp.results.analyze()
        rx_frequencies = rev4.get_active_frequencies(radiosRX[1], bandsRX[0], modeRx)
        assert len(rx_frequencies) == 19
        assert rx_frequencies[0] == 2.402
        assert rx_frequencies[1] == 2.411

        sampling.set_channel_sampling("all")
        rev5 = self.aedtapp.results.analyze()
        rx_frequencies = rev5.get_active_frequencies(radiosRX[1], bandsRX[0], modeRx)
        assert len(rx_frequencies) == 79

    @pytest.mark.skipif(
        config["desktopVersion"] <= "2023.1" or is_ironpython,
        reason="Skipped on versions earlier than 2023.2",
    )
    def test_radio_band_getters(self):
        self.aedtapp = BasisTest.add_app(self, application=Emit)
        rad1, ant1 = self.aedtapp.modeler.components.create_radio_antenna("New Radio")
        rad2, ant2 = self.aedtapp.modeler.components.create_radio_antenna("Bluetooth Low Energy (LE)")

        # Check type
        rad_type = rad1.get_type()
        assert rad_type == "RadioNode"
        ant_type = ant1.get_type()
        assert ant_type == "AntennaNode"

        # Check antenna connections
        ants = rad1.get_connected_antennas()
        assert ants[0].name == "Antenna"
        ants = rad2.get_connected_antennas()
        assert ants[0].name == "Antenna 2"

        # Set up the results
        rev = self.aedtapp.results.analyze()

        # Get Tx Radios
        radios = rev.get_interferer_names()
        assert radios == ["Radio", "Bluetooth Low Energy (LE)"]

        # Get the Bands
        bands = rev.get_band_names(radios[0], econsts.tx_rx_mode().rx)
        assert bands == ["Band"]

        # Get the Freqs
        freqs = rev.get_active_frequencies(radios[0], bands[0], econsts.tx_rx_mode().rx, "MHz")
        assert freqs == [100.0]

        # Add an emitter
        emitter1 = self.aedtapp.modeler.components.create_component("USB_3.x")
        rev2 = self.aedtapp.results.analyze()

        # Get emitters only
        emitters = rev2.get_interferer_names(econsts.interferer_type().emitters)
        assert emitters == ["USB_3.x"]

        # Get transmitters only
        transmitters = rev2.get_interferer_names(econsts.interferer_type().transmitters)
        assert transmitters == ["Radio", "Bluetooth Low Energy (LE)"]

        # Get all interferers
        all_ix = rev2.get_interferer_names(econsts.interferer_type().transmitters_and_emitters)
        assert all_ix == ["Radio", "Bluetooth Low Energy (LE)", "USB_3.x"]

    @pytest.mark.skipif(
        config["desktopVersion"] <= "2022.1" or is_ironpython, reason="Skipped on versions earlier than 2021.2"
    )
    def test_sampling_getters(self):
        self.aedtapp = BasisTest.add_app(self, application=Emit)
        rad, ant = self.aedtapp.modeler.components.create_radio_antenna("New Radio")

        # Check type
        rad_type = rad.get_type()
        assert rad_type == "RadioNode"
        ant_type = ant.get_type()
        assert ant_type == "AntennaNode"

        # Check sampling
        exception_raised = False
        try:
            rad.set_channel_sampling()
        except:
            exception_raised = True
        assert exception_raised

        # Get sampling node
        sampling = rad.get_sampling()
        assert sampling.node_name == "NODE-*-RF Systems-*-RF System-*-Radios-*-Radio-*-Sampling"

        # Test sampling params
        sampling.set_channel_sampling("All")
        assert sampling.props["SamplingType"] == "SampleAllChannels"

        sampling.set_channel_sampling("Uniform", percentage=25)
        assert sampling.props["SamplingType"] == "UniformSampling"
        assert sampling.props["SpecifyPercentage"] == "true"
        assert sampling.props["PercentageChannels"] == "25"

        sampling.set_channel_sampling("Uniform", max_channels=50)
        assert sampling.props["SamplingType"] == "UniformSampling"
        assert sampling.props["SpecifyPercentage"] == "false"
        assert sampling.props["NumberChannels"] == "50"

        sampling.set_channel_sampling("Random", percentage=33)
        assert sampling.props["SamplingType"] == "RandomSampling"
        assert sampling.props["SpecifyPercentage"] == "true"
        assert sampling.props["PercentageChannels"] == "33"
        assert sampling.props["RandomSeed"] == "0"

        sampling.set_channel_sampling("Random", max_channels=75, seed=37)
        assert sampling.props["SamplingType"] == "RandomSampling"
        assert sampling.props["SpecifyPercentage"] == "false"
        assert sampling.props["NumberChannels"] == "75"
        assert sampling.props["RandomSeed"] == "37"

        sampling.set_channel_sampling("Uniform")
        assert sampling.props["SamplingType"] == "UniformSampling"
        assert sampling.props["SpecifyPercentage"] == "false"
        assert sampling.props["NumberChannels"] == "1000"

    @pytest.mark.skipif(
        config["desktopVersion"] <= "2022.1" or is_ironpython, reason="Skipped on versions earlier than 2021.2"
    )
    def test_radio_getters(self):
        self.aedtapp = BasisTest.add_app(self, application=Emit)
        rad, ant = self.aedtapp.modeler.components.create_radio_antenna("New Radio")
        rad2, ant2 = self.aedtapp.modeler.components.create_radio_antenna("Bluetooth")
        emitter = self.aedtapp.modeler.components.create_component("USB_3.x")

        # get the radio nodes
        radios = self.aedtapp.modeler.components.get_radios()
        assert radios[rad.name] == rad
        assert radios[rad2.name] == rad2
        assert radios[emitter.name] == emitter

        # validate is_emitter function
        assert not rad.is_emitter()
        assert not rad2.is_emitter()
        assert emitter.is_emitter()

    @pytest.mark.skipif(
        config["desktopVersion"] <= "2023.1" or is_ironpython,
        reason="Skipped on versions earlier than 2023.2",
    )
    def test_static_type_generation(self):
        domain = self.aedtapp.results.interaction_domain()
        assert str(type(domain)) == "<class 'EmitApiPython.InteractionDomain'>"

        mode = econsts.tx_rx_mode()
        mode_rx = econsts.tx_rx_mode().rx
        mode_tx = econsts.tx_rx_mode().tx
        mode_both = econsts.tx_rx_mode().both
        assert str(type(mode)) == "<class 'EmitApiPython.tx_rx_mode'>"
        assert str(type(mode_rx)) == "<class 'EmitApiPython.tx_rx_mode'>"
        assert str(type(mode_tx)) == "<class 'EmitApiPython.tx_rx_mode'>"
        assert str(type(mode_both)) == "<class 'EmitApiPython.tx_rx_mode'>"
        result_type = econsts.result_type()
        result_type_sensitivity = econsts.result_type().sensitivity
        result_type_emi = econsts.result_type().emi
        result_type_desense = econsts.result_type().desense
        assert str(type(result_type)) == "<class 'EmitApiPython.result_type'>"
        assert str(type(result_type_sensitivity)) == "<class 'EmitApiPython.result_type'>"
        assert str(type(result_type_emi)) == "<class 'EmitApiPython.result_type'>"
        assert str(type(result_type_desense)) == "<class 'EmitApiPython.result_type'>"

    @pytest.mark.skipif(
        config["desktopVersion"] <= "2023.1" or is_ironpython, reason="Skipped on versions earlier than 2023.2"
    )
    def test_version(self):
        self.aedtapp = BasisTest.add_app(self, application=Emit)
        less_info = self.aedtapp.version(False)
        more_info = self.aedtapp.version(True)
        if less_info:
            assert str(type(less_info)) == "<class 'str'>"
            assert str(type(more_info)) == "<class 'str'>"
            assert len(more_info) > len(less_info)

    @pytest.mark.skipif(
        config["desktopVersion"] <= "2023.1" or is_ironpython,
        reason="Skipped on versions earlier than 2023.2",
    )
    def test_InteractionDomain(self):
        self.aedtapp = BasisTest.add_app(self, application=Emit)
        testable_id = self.aedtapp.results.interaction_domain()
        assert str(type(testable_id)) == "<class 'EmitApiPython.InteractionDomain'>"

    @pytest.mark.skipif(
        config["desktopVersion"] <= "2023.1" or is_ironpython,
        reason="Skipped on versions earlier than 2023.2",
    )
    def test_analyze_manually(self):
        self.aedtapp = BasisTest.add_app(self, application=Emit)
        assert len(self.aedtapp.results.revisions) == 0
        # place components and generate the appropriate number of revisions
        rad1 = self.aedtapp.modeler.components.create_component("UE - Handheld")
        ant1 = self.aedtapp.modeler.components.create_component("Antenna")
        if rad1 and ant1:
            ant1.move_and_connect_to(rad1)
        rad2 = self.aedtapp.modeler.components.create_component("Bluetooth")
        ant2 = self.aedtapp.modeler.components.create_component("Antenna")
        if rad2 and ant2:
            ant2.move_and_connect_to(rad2)
        rad3 = self.aedtapp.modeler.components.create_component("Bluetooth")
        ant3 = self.aedtapp.modeler.components.create_component("Antenna")
        if rad3 and ant3:
            ant3.move_and_connect_to(rad3)
        rev = self.aedtapp.results.analyze()
        assert len(self.aedtapp.results.revisions) == 1
        if self.aedtapp._emit_api is not None:
            path = self.aedtapp.oproject.GetPath()
            subfolder = ""
            for f in os.scandir(path):
                if os.path.splitext(f.name)[1].lower() in ".aedtresults":
                    subfolder = os.path.join(f.path, "EmitDesign1")
            file = max([f for f in os.scandir(subfolder)], key=lambda x: x.stat().st_mtime)
            self.aedtapp._emit_api.load_project(file.path)
            assert rev.revision_loaded
            domain = self.aedtapp.results.interaction_domain()
            assert domain is not None
            engine = self.aedtapp._emit_api.get_engine()
            assert engine is not None
            assert engine.is_domain_valid(domain)
            assert rev.is_domain_valid(domain)
            interaction = engine.run(domain)
            assert interaction is not None
            interaction2 = rev.run(domain)
            assert interaction2 is not None
            assert interaction2.is_valid()
            self.aedtapp.results.delete_revision(rev.name)
            assert not interaction.is_valid()
            assert not interaction2.is_valid()
            domain.set_receiver("dummy")
            assert not rev.name in self.aedtapp.results.revision_names()
            assert not engine.is_domain_valid(domain)
            assert not rev.is_domain_valid(domain)

    @pytest.mark.skipif(
        config["desktopVersion"] <= "2023.1" or is_ironpython,
        reason="Skipped on versions earlier than 2023.2",
    )
    def test_N_to_1_feature(self):
        self.aedtapp = BasisTest.add_app(self, application=Emit)
        # place components and generate the appropriate number of revisions
        rad1 = self.aedtapp.modeler.components.create_component("Bluetooth")
        ant1 = self.aedtapp.modeler.components.create_component("Antenna")
        if rad1 and ant1:
            ant1.move_and_connect_to(rad1)
        rad2 = self.aedtapp.modeler.components.create_component("MD401C")
        ant2 = self.aedtapp.modeler.components.create_component("Antenna")
        if rad2 and ant2:
            ant2.move_and_connect_to(rad2)
        rad3 = self.aedtapp.modeler.components.create_component("MD400C")
        ant3 = self.aedtapp.modeler.components.create_component("Antenna")
        if rad3 and ant3:
            ant3.move_and_connect_to(rad3)
        rad4 = self.aedtapp.modeler.components.create_component("LT401")
        ant4 = self.aedtapp.modeler.components.create_component("Antenna")
        if rad4 and ant4:
            ant4.move_and_connect_to(rad4)
        assert len(self.aedtapp.results.revisions) == 0
        rev = self.aedtapp.results.analyze()
        assert len(self.aedtapp.results.revisions) == 1
        radiosRX = rev.get_receiver_names()
        bandsRX = rev.get_band_names(radiosRX[0], econsts.tx_rx_mode().rx)
        domain = self.aedtapp.results.interaction_domain()
        domain.set_receiver(radiosRX[0], bandsRX[0])
        interaction = self.aedtapp.results.revisions[-1].run(domain)
        instance = interaction.get_worst_instance(econsts.result_type().sensitivity)
        assert instance.get_value(econsts.result_type().emi) == 82.04
        assert instance.get_value(econsts.result_type().desense) == 13.42
        assert instance.get_value(econsts.result_type().sensitivity) == -56.58
        assert instance.get_value(econsts.result_type().powerAtRx) == 62.03
        assert instance.get_largest_problem_type(econsts.result_type().emi) == "Out-of-Channel: Tx Fundamental"
        domain2 = self.aedtapp.results.interaction_domain()
        rx_frequencies = rev.get_active_frequencies(radiosRX[0], bandsRX[0], econsts.tx_rx_mode().rx, "Hz")
        domain2.set_receiver(radiosRX[0], bandsRX[0], rx_frequencies[0], "Hz")
        radiosTX = rev.get_interferer_names(econsts.interferer_type().transmitters)
        bandsTX = rev.get_band_names(radiosTX[0], econsts.tx_rx_mode().tx)
        tx_frequencies = rev.get_active_frequencies(radiosTX[0], bandsTX[0], econsts.tx_rx_mode().tx, "Hz")
        domain2.set_interferer(radiosTX[0], bandsTX[0], tx_frequencies[0], "Hz")
        exception_raised = False
        try:
            instance = interaction.get_instance(domain2)
        except RuntimeError as e:
            exception_raised = True
            assert e.args[0] == "ERROR: Instance data for multiple simultaneous interferers not available."
        assert exception_raised

    @pytest.mark.skipif(
        config["desktopVersion"] <= "2023.1" or is_ironpython,
        reason="Skipped on versions earlier than 2023.2",
    )
    def test_availability_1_to_1(self):
        self.aedtapp = BasisTest.add_app(self, application=Emit)
        # place components and generate the appropriate number of revisions
        rad1 = self.aedtapp.modeler.components.create_component("MD400C")
        ant1 = self.aedtapp.modeler.components.create_component("Antenna")
        if rad1 and ant1:
            ant1.move_and_connect_to(rad1)
        rad2 = self.aedtapp.modeler.components.create_component("MD400C")
        ant2 = self.aedtapp.modeler.components.create_component("Antenna")
        if rad2 and ant2:
            ant2.move_and_connect_to(rad2)

        assert len(self.aedtapp.results.revisions) == 0
        rev = self.aedtapp.results.analyze()
        assert len(self.aedtapp.results.revisions) == 1

        rad3 = self.aedtapp.modeler.components.create_component("Mini UAS Video RT Airborne")
        ant3 = self.aedtapp.modeler.components.create_component("Antenna")
        if rad3 and ant3:
            ant3.move_and_connect_to(rad3)

        rad4 = self.aedtapp.modeler.components.create_component("GPS Airborne Receiver")
        ant4 = self.aedtapp.modeler.components.create_component("Antenna")
        if rad4 and ant4:
            ant4.move_and_connect_to(rad4)

        rev2 = self.aedtapp.results.analyze(rev.name)
        assert len(self.aedtapp.results.revisions) == 1

        rev2 = self.aedtapp.results.analyze()
        domain = self.aedtapp.results.interaction_domain()
        radiosRX = rev2.get_receiver_names()
        bandsRX = rev2.get_band_names(radiosRX[0], econsts.tx_rx_mode().rx)
        domain.set_receiver(radiosRX[0], bandsRX[0])
        radiosTX = rev2.get_interferer_names(econsts.interferer_type().transmitters)
        bandsTX = rev2.get_band_names(radiosTX[0], econsts.tx_rx_mode().tx)
        domain.set_interferer(radiosTX[0], bandsTX[0])
        assert len(self.aedtapp.results.revisions) == 2
        radiosRX = rev2.get_receiver_names()
        bandsRX = rev2.get_band_names(radiosRX[0], econsts.tx_rx_mode().rx)
        domain.set_receiver(radiosRX[0], bandsRX[0])
        radiosTX = rev2.get_interferer_names(econsts.interferer_type().transmitters)
        bandsTX = rev2.get_band_names(radiosTX[0], econsts.tx_rx_mode().tx)
        domain.set_interferer(radiosTX[0], bandsTX[0])
        assert domain.receiver_name == "MD400C"
        assert domain.receiver_band_name == "Rx"
        assert domain.receiver_channel_frequency == -1.0
        assert domain.interferer_names == ["MD400C"]
        assert domain.interferer_band_names == ["Tx"]
        assert domain.interferer_channel_frequencies == [-1.0]
        revision = self.aedtapp.results.revisions[0]
        assert revision.get_instance_count(domain) == 31626
        interaction = revision.run(domain)
        available_warning = interaction.get_availability_warning(domain)
        assert available_warning == ""
        availability = interaction.get_availability(domain)
        assert availability == 1.0
        valid_availability = interaction.has_valid_availability(domain)
        assert valid_availability

        rev3 = self.aedtapp.results.analyze()
        assert len(self.aedtapp.results.revisions) == 2
        radiosTX = rev3.get_interferer_names(econsts.interferer_type().transmitters)
        radiosRX = rev3.get_receiver_names()
        assert len(radiosTX) == 3
        assert len(radiosRX) == 4

        rev4 = self.aedtapp.results.analyze(rev.name)
        assert len(self.aedtapp.results.revisions) == 2
        radiosTX = rev4.get_interferer_names(econsts.interferer_type().transmitters)
        radiosRX = rev4.get_receiver_names()
        assert len(radiosTX) == 2
        assert len(radiosRX) == 2

    """
    .. note::
    The following test should be maintained as the last test within this file to ensure
    that the AEDT app functions as intended.

    """

    @pytest.mark.skipif(
        config["desktopVersion"] <= "2022.1" or is_ironpython, reason="Skipped on versions earlier than 2021.2"
    )
    def test_couplings(self):
        self.aedtapp = BasisTest.add_app(
            self, project_name="Cell Phone RFI Desense", application=Emit, subfolder=test_subfolder
        )
        links = self.aedtapp.couplings.linkable_design_names
        assert len(links) == 0
        for link in self.aedtapp.couplings.coupling_names:
            assert link == "ATA_Analysis"
            self.aedtapp.couplings.update_link(link)
