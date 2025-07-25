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

from enum import Enum
import inspect

# Import required modules
import os
import sys
import tempfile
import types

import pytest

from ansys.aedt.core.generic import constants as consts
from ansys.aedt.core.generic.general_methods import is_linux
from tests.system.solvers.conftest import config

# Prior to 2025R1, the Emit API supported Python 3.8,3.9,3.10,3.11
# Starting with 2025R1, the Emit API supports Python 3.10,3.11,3.12
if ((3, 8) <= sys.version_info[0:2] <= (3, 11) and config["desktopVersion"] < "2025.1") or (
    (3, 10) <= sys.version_info[0:2] <= (3, 12) and config["desktopVersion"] > "2024.2"
):
    from ansys.aedt.core import Emit
    from ansys.aedt.core import generate_unique_project_name
    from ansys.aedt.core.emit_core.emit_constants import EmiCategoryFilter
    from ansys.aedt.core.emit_core.emit_constants import InterfererType
    from ansys.aedt.core.emit_core.emit_constants import ResultType
    from ansys.aedt.core.emit_core.emit_constants import TxRxMode
    from ansys.aedt.core.emit_core.nodes import generated
    from ansys.aedt.core.modeler.circuits.primitives_emit import EmitAntennaComponent
    from ansys.aedt.core.modeler.circuits.primitives_emit import EmitComponent
    from ansys.aedt.core.modeler.circuits.primitives_emit import EmitComponents

TEST_SUBFOLDER = "T26"
TEST_REVIEW_FLAG = True


@pytest.fixture(scope="class")
def aedtapp(add_app):
    app = add_app(application=Emit)
    return app


@pytest.mark.skipif(is_linux, reason="Emit API is not supported on linux.")
@pytest.mark.skipif(
    (sys.version_info < (3, 8) or sys.version_info > (3, 11)) and config["desktopVersion"] < "2025.1",
    reason="Emit API is only available for Python 3.8-3.11 in AEDT versions 2024.2 and prior.",
)
@pytest.mark.skipif(
    (sys.version_info < (3, 10) or sys.version_info > (3, 12)) and config["desktopVersion"] > "2024.2",
    reason="Emit API is only available for Python 3.10-3.12 in AEDT versions 2025.1 and later.",
)
class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, aedtapp, local_scratch):
        self.aedtapp = aedtapp
        self.local_scratch = local_scratch

    def test_01_objects(self):
        assert self.aedtapp.solution_type
        assert isinstance(self.aedtapp.modeler.components, EmitComponents)
        assert self.aedtapp.modeler
        assert self.aedtapp.oanalysis is None
        if self.aedtapp._aedt_version > "2023.1":
            assert (
                str(type(self.aedtapp._emit_api))
                == f"<class 'EmitApiPython{sys.version_info.major}{sys.version_info.minor}.EmitApi'>"
            )
            assert self.aedtapp.results is not None

    @pytest.mark.skipif(config["desktopVersion"] <= "2022.1", reason="Skipped on versions earlier than 2021.2")
    def test_02_create_components(self, add_app):
        self.aedtapp = add_app(application=Emit)
        radio = self.aedtapp.modeler.components.create_component("New Radio", "TestRadio")
        assert radio.name == "TestRadio"
        assert radio.composed_name == "TestRadio"
        assert isinstance(radio, EmitComponent)

        antenna = self.aedtapp.modeler.components.create_component("Antenna", "TestAntenna")
        assert antenna.name == "TestAntenna"
        assert isinstance(antenna, EmitAntennaComponent)
        emitter = self.aedtapp.modeler.components.create_component("New Emitter", "TestEmitter")
        assert emitter.name == "TestEmitter"
        assert isinstance(emitter, EmitComponent)

        # add each component type
        amplifier = self.aedtapp.modeler.components.create_component("Amplifier", "TestAmplifier")
        assert amplifier.name == "TestAmplifier"
        assert isinstance(amplifier, EmitComponent)
        cable = self.aedtapp.modeler.components.create_component("Cable", "TestCable")
        assert cable.name == "TestCable"
        assert isinstance(cable, EmitComponent)
        circulator = self.aedtapp.modeler.components.create_component("Circulator", "TestCirculator")
        assert circulator.name == "TestCirculator"
        assert isinstance(circulator, EmitComponent)
        divider = self.aedtapp.modeler.components.create_component("Divider", "TestDivider")
        assert divider.name == "TestDivider"
        assert isinstance(divider, EmitComponent)
        filter_bpf = self.aedtapp.modeler.components.create_component("Band Pass", "TestBPF")
        assert filter_bpf.name == "TestBPF"
        assert isinstance(filter_bpf, EmitComponent)
        filter_bsf = self.aedtapp.modeler.components.create_component("Band Stop", "TestBSF")
        assert filter_bsf.name == "TestBSF"
        assert isinstance(filter_bsf, EmitComponent)
        filter_file = self.aedtapp.modeler.components.create_component("File-based", "TestFilterByFile")
        assert filter_file.name == "TestFilterByFile"
        assert isinstance(filter_file, EmitComponent)
        filter_hpf = self.aedtapp.modeler.components.create_component("High Pass", "TestHPF")
        assert filter_hpf.name == "TestHPF"
        assert isinstance(filter_hpf, EmitComponent)
        filter_lpf = self.aedtapp.modeler.components.create_component("Low Pass", "TestLPF")
        assert filter_lpf.name == "TestLPF"
        assert isinstance(filter_lpf, EmitComponent)
        filter_tbpf = self.aedtapp.modeler.components.create_component("Tunable Band Pass", "TestTBPF")
        assert filter_tbpf.name == "TestTBPF"
        assert isinstance(filter_tbpf, EmitComponent)
        filter_tbsf = self.aedtapp.modeler.components.create_component("Tunable Band Stop", "TestTBSF")
        assert filter_tbsf.name == "TestTBSF"
        assert isinstance(filter_tbsf, EmitComponent)
        isolator = self.aedtapp.modeler.components.create_component("Isolator", "TestIsolator")
        assert isolator.name == "TestIsolator"
        assert isinstance(isolator, EmitComponent)
        mux3 = self.aedtapp.modeler.components.create_component("3 Port", "Test3port")
        assert mux3.name == "Test3port"
        assert isinstance(mux3, EmitComponent)
        mux4 = self.aedtapp.modeler.components.create_component("4 Port", "Test4port")
        assert mux4.name == "Test4port"
        assert isinstance(mux4, EmitComponent)
        mux5 = self.aedtapp.modeler.components.create_component("5 Port", "Test5port")
        assert mux5.name == "Test5port"
        assert isinstance(mux5, EmitComponent)
        # Multiplexer 6 port added at 2023.2
        if self.aedtapp._aedt_version > "2023.1":
            mux6 = self.aedtapp.modeler.components.create_component("6 Port", "Test6port")
            assert mux6.name == "Test6port"
            assert isinstance(mux6, EmitComponent)
        switch = self.aedtapp.modeler.components.create_component("TR Switch", "TestSwitch")
        assert switch.name == "TestSwitch"
        assert isinstance(switch, EmitComponent)
        terminator = self.aedtapp.modeler.components.create_component("Terminator", "TestTerminator")
        assert terminator.name == "TestTerminator"
        assert isinstance(terminator, EmitComponent)

    @pytest.mark.skipif(config["desktopVersion"] <= "2022.1", reason="Skipped on versions earlier than 2021.2")
    def test_03_connect_components(self, add_app):
        self.aedtapp = add_app(application=Emit)
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

    @pytest.mark.skipif(config["desktopVersion"] <= "2022.1", reason="Skipped on versions earlier than 2022 R2.")
    def test_04_radio_component(self, add_app):
        self.aedtapp = add_app(application=Emit)
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
        except Exception:
            exception_raised = True
        assert exception_raised
        # Try getting band power from the radio
        exception_raised = False
        try:
            radio.get_band_power_level()
        except Exception:
            exception_raised = True
        assert exception_raised
        # full units support added with 2023.2
        if self.aedtapp._aedt_version > "2023.1":
            # test band.set_band_power_level
            band.set_band_power_level(100)
            power = band.get_band_power_level()
            assert power == 100.0
            # test band.set_band_power_level
            band.set_band_power_level(10, "W")
            power = band.get_band_power_level("mW")
            assert power == 10000.0
            # test frequency unit conversions
            start_freq = radio.band_start_frequency(band, "MHz")
            assert start_freq == 100.0
            start_freq = radio.band_start_frequency(band, "Hz")
            assert start_freq == 100000000.0
            start_freq = radio.band_start_frequency(band, "kHz")
            assert start_freq == 100000.0
            start_freq = radio.band_start_frequency(band, "GHz")
            assert start_freq == 0.1
            start_freq = radio.band_start_frequency(band, "THz")
            assert start_freq == 0.0001
            # test band.set_band_start_frequency
            start_freq = 10
            units = "MHz"
            radio.set_band_start_frequency(band, start_freq, units=units)
            assert radio.band_start_frequency(band, units=units) == start_freq
            start_freq = 20000000
            radio.set_band_start_frequency(band, start_freq)
            assert radio.band_start_frequency(band, units="Hz") == start_freq
            # test band.set_band_stop_frequency
            stop_freq = 30
            units = "MHz"
            radio.set_band_stop_frequency(band, stop_freq, units=units)
            assert radio.band_stop_frequency(band, units=units) == stop_freq
            stop_freq = 40000000
            radio.set_band_stop_frequency(band, stop_freq)
            assert radio.band_stop_frequency(band, units="Hz") == stop_freq
            # test corner cases for band start and stop frequencies
            start_freq = 10
            stop_freq = 9
            units = "Hz"
            radio.set_band_start_frequency(band, start_freq, units=units)
            radio.set_band_stop_frequency(band, stop_freq, units=units)
            assert radio.band_start_frequency(band, units="Hz") == 8
            radio.set_band_start_frequency(band, 10, units=units)
            assert radio.band_stop_frequency(band, units="Hz") == 11
            units = "wrong"
            radio.set_band_stop_frequency(band, 10, units=units)
            assert radio.band_stop_frequency(band, units="Hz") == 10
            radio.set_band_start_frequency(band, 10, units=units)
            assert radio.band_start_frequency(band, units="Hz") == 10
            with pytest.raises(ValueError) as e:
                start_freq = 101
                units = "GHz"
                radio.set_band_start_frequency(band, start_freq, units=units)
                assert "Frequency should be within 1Hz to 100 GHz." in str(e)
                stop_freq = 102
                radio.set_band_stop_frequency(band, stop_freq, units=units)
                assert "Frequency should be within 1Hz to 100 GHz." in str(e)

            # test power unit conversions
            band_power = radio.band_tx_power(band, "dBm")
            assert band_power == 40.0
            band_power = radio.band_tx_power(band, "dBW")
            assert band_power == 10.0
            band_power = radio.band_tx_power(band, "mW")
            assert band_power == 10000.0
            band_power = radio.band_tx_power(band, "W")
            assert band_power == 10.0
            band_power = radio.band_tx_power(band, "kW")
            assert band_power == 0.01

    @pytest.mark.skipif(config["desktopVersion"] <= "2022.1", reason="Skipped on versions earlier than 2022 R2.")
    def test_05_emit_power_conversion(self):
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
        config["desktopVersion"] <= "2023.1" or config["desktopVersion"] > "2025.1",
        reason="Skipped on versions earlier than 2023 R2 and later than 2025 R1.",
    )
    def test_06_units_getters(self, add_app):
        self.aedtapp = add_app(application=Emit)

        # Set a single unit
        valid = self.aedtapp.set_units("Frequency", "Hz")
        units = self.aedtapp.get_units("Frequency")
        assert valid
        assert units == "Hz"

        # Test bad unit input
        units = self.aedtapp.get_units("Bad units")
        assert units is None

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

    @pytest.mark.skipif(config["desktopVersion"] <= "2023.1", reason="Skipped on versions earlier than 2023 R2.")
    def test_07_antenna_component(self, add_app):
        self.aedtapp = add_app(application=Emit)
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
        (config["desktopVersion"] <= "2023.1") or (config["desktopVersion"] > "2025.1"),
        reason="Skipped on versions earlier than 2023.2 or later than 2025.1",
    )
    def test_08_revision_generation(self, add_app):
        self.aedtapp = add_app(application=Emit, project_name=generate_unique_project_name())
        assert len(self.aedtapp.results.revisions) == 0
        # place components and generate the appropriate number of revisions
        rad1 = self.aedtapp.modeler.components.create_component("UE - Handheld")
        ant1 = self.aedtapp.modeler.components.create_component("Antenna")
        ant1.move_and_connect_to(rad1)
        rad2 = self.aedtapp.modeler.components.create_component("Bluetooth")
        ant2 = self.aedtapp.modeler.components.create_component("Antenna")
        ant2.move_and_connect_to(rad2)
        rad3 = self.aedtapp.modeler.components.create_component("Bluetooth")
        ant3 = self.aedtapp.modeler.components.create_component("Antenna")
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
        ant4.move_and_connect_to(rad4)
        rev2 = self.aedtapp.results.analyze()
        assert len(self.aedtapp.results.revisions) == 2
        rad5 = self.aedtapp.modeler.components.create_component("HAVEQUICK Airborne")
        self.aedtapp.modeler.components.create_component("Antenna")
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

        # test result_mode_error(), try to access unloaded revision
        receivers = rev2.get_receiver_names()
        assert receivers is None
        transmitters = rev2.get_interferer_names()
        assert transmitters is None
        bands = rev2.get_band_names(rad5)
        assert bands is None
        freqs = rev2.get_active_frequencies(rad5, "Band", TxRxMode.TX)
        assert freqs is None

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
        config["desktopVersion"] < "2025.2",
        reason="Skipped on versions earlier than 2025.2",
    )
    def test_08b_revision_generation(self, add_app):
        self.aedtapp = add_app(application=Emit, project_name=generate_unique_project_name())
        assert len(self.aedtapp.results.revisions) == 0
        # place components and generate the appropriate number of revisions
        rad1 = self.aedtapp.modeler.components.create_component("UE - Handheld")
        ant1 = self.aedtapp.modeler.components.create_component("Antenna")
        ant1.move_and_connect_to(rad1)
        rad2 = self.aedtapp.modeler.components.create_component("Bluetooth")
        ant2 = self.aedtapp.modeler.components.create_component("Antenna")
        ant2.move_and_connect_to(rad2)
        rad3 = self.aedtapp.modeler.components.create_component("Bluetooth")
        ant3 = self.aedtapp.modeler.components.create_component("Antenna")
        ant3.move_and_connect_to(rad3)
        rev = self.aedtapp.results.analyze()
        assert len(self.aedtapp.results.revisions) == 1
        assert rev.name == "Current"
        self.aedtapp.results.analyze()
        assert len(self.aedtapp.results.revisions) == 1
        rad4 = self.aedtapp.modeler.components.create_component("Bluetooth")
        ant4 = self.aedtapp.modeler.components.create_component("Antenna")
        ant4.move_and_connect_to(rad4)
        rev2 = self.aedtapp.results.analyze()
        assert len(self.aedtapp.results.revisions) == 1
        rad5 = self.aedtapp.modeler.components.create_component("HAVEQUICK Airborne")
        _ = self.aedtapp.modeler.components.create_component("Antenna")
        ant4.move_and_connect_to(rad5)
        assert len(self.aedtapp.results.revisions) == 1
        assert rev2.name == "Current"

        # get the revision
        rev3 = self.aedtapp.results.get_revision()
        assert rev3.name == "Current"

    @pytest.mark.skipif(
        config["desktopVersion"] <= "2023.1",
        reason="Skipped on versions earlier than 2023.2",
    )
    def test_09_manual_revision_access_test_getters(self, add_app):
        self.aedtapp = add_app(application=Emit, project_name=generate_unique_project_name())
        rad1 = self.aedtapp.modeler.components.create_component("UE - Handheld")
        ant1 = self.aedtapp.modeler.components.create_component("Antenna")
        rad2 = self.aedtapp.modeler.components.create_component("Bluetooth")
        ant1.move_and_connect_to(rad1)
        ant2 = self.aedtapp.modeler.components.create_component("Antenna")
        ant2.move_and_connect_to(rad2)
        rad3 = self.aedtapp.modeler.components.create_component("Bluetooth")
        ant3 = self.aedtapp.modeler.components.create_component("Antenna")
        ant3.move_and_connect_to(rad3)
        # Change the sampling
        modeRx = TxRxMode.RX
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
        rx_frequencies = rev.get_active_frequencies(radiosRX[0], bandsRX[0], modeRx, "MHz")
        assert rx_frequencies[0] == 2402.0
        assert rx_frequencies[1] == 2403.0
        # Change the units globally
        rx_frequencies = rev.get_active_frequencies(radiosRX[0], bandsRX[0], modeRx, "GHz")
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
        rx_frequencies = rev3.get_active_frequencies(radiosRX[1], bandsRX[0], modeRx, "GHz")
        assert len(rx_frequencies) == 75
        assert rx_frequencies[0] == 2.402
        assert rx_frequencies[1] == 2.403

        sampling.set_channel_sampling("Random", percentage=25, seed=100)
        rev4 = self.aedtapp.results.analyze()
        rx_frequencies = rev4.get_active_frequencies(radiosRX[1], bandsRX[0], modeRx, "GHz")
        assert len(rx_frequencies) == 19
        assert rx_frequencies[0] == 2.402
        assert rx_frequencies[1] == 2.411

        sampling.set_channel_sampling("all")
        rev5 = self.aedtapp.results.analyze()
        rx_frequencies = rev5.get_active_frequencies(radiosRX[1], bandsRX[0], modeRx)
        assert len(rx_frequencies) == 79

    @pytest.mark.skipif(
        config["desktopVersion"] <= "2023.1",
        reason="Skipped on versions earlier than 2023.2",
    )
    def test_10_radio_band_getters(self, add_app):
        self.aedtapp = add_app(application=Emit, project_name=generate_unique_project_name())
        rad1, ant1 = self.aedtapp.modeler.components.create_radio_antenna("New Radio")
        rad2, ant2 = self.aedtapp.modeler.components.create_radio_antenna("Bluetooth Low Energy (LE)")
        rad3, ant3 = self.aedtapp.modeler.components.create_radio_antenna("WiFi - 802.11-2012")
        rad4, ant4 = self.aedtapp.modeler.components.create_radio_antenna("WiFi 6")

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

        # Set all Bands for WiFi radios, enabled
        band_nodes = rad3.bands()
        for bn in band_nodes:
            bn.enabled = True
        band_nodes = rad4.bands()
        for bn in band_nodes:
            bn.enabled = True

        band_node = rad4.band_node("Invalid")
        assert band_node is None
        band_node = rad4.band_node("U-NII-5-8 QPSK R=0.75 (Bw 80 MHz)")
        assert band_node.enabled

        # Set up the results
        rev = self.aedtapp.results.analyze()

        # Get Tx Radios
        radios = rev.get_interferer_names()
        assert radios == ["Radio", "Bluetooth Low Energy (LE)", "WiFi - 802.11-2012", "WiFi 6"]

        # Get the Bands
        bands = rev.get_band_names(radios[0], TxRxMode.RX)
        assert bands == ["Band"]

        # Get the Freqs
        freqs = rev.get_active_frequencies(radios[0], bands[0], TxRxMode.RX, "MHz")
        assert freqs == [100.0]

        # Test error for trying to get BOTH tx and rx freqs
        exception_raised = False
        try:
            freqs = rev.get_active_frequencies(radios[0], bands[0], TxRxMode.BOTH, "MHz")
        except Exception:
            exception_raised = True
        assert exception_raised

        # Get WiFi 2012 Rx Bands
        bands = rev.get_band_names(radios[2], TxRxMode.RX)
        assert len(bands) == 16

        # Get WiFi 2012 Tx Bands
        bands = rev.get_band_names(radios[2], TxRxMode.TX)
        assert len(bands) == 16

        # Get WiFi 2012 All Bands
        bands = rev.get_band_names(radios[2], TxRxMode.BOTH)
        assert len(bands) == 32

        # Get WiFi 2012 All Bands (default args)
        bands = rev.get_band_names(radios[2])
        assert len(bands) == 32

        # Get WiFi 6 All Bands (default args)
        bands = rev.get_band_names(radios[3])
        assert len(bands) == 192

        # Get WiFi 6 Rx Bands
        bands = rev.get_band_names(radios[3], TxRxMode.RX)
        assert len(bands) == 192

        # Get WiFi 6 Tx Bands
        bands = rev.get_band_names(radios[3], TxRxMode.TX)
        assert len(bands) == 192

        # Get WiFi 6 All Bands
        bands = rev.get_band_names(radios[3], TxRxMode.BOTH)
        assert len(bands) == 192

        # Add an emitter
        self.aedtapp.modeler.components.create_component("USB_3.x")
        rev2 = self.aedtapp.results.analyze()

        # Get emitters only
        emitters = rev2.get_interferer_names(InterfererType.EMITTERS)
        assert emitters == ["USB_3.x"]

        # Get transmitters only
        transmitters = rev2.get_interferer_names(InterfererType.TRANSMITTERS)
        assert transmitters == ["Radio", "Bluetooth Low Energy (LE)", "WiFi - 802.11-2012", "WiFi 6"]

        # Get all interferers
        all_ix = rev2.get_interferer_names(InterfererType.TRANSMITTERS_AND_EMITTERS)
        assert all_ix == ["Radio", "Bluetooth Low Energy (LE)", "WiFi - 802.11-2012", "WiFi 6", "USB_3.x"]

    @pytest.mark.skipif(config["desktopVersion"] <= "2022.1", reason="Skipped on versions earlier than 2021.2")
    def test_11_sampling_getters(self, add_app):
        self.aedtapp = add_app(application=Emit)
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
        except Exception:
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

    @pytest.mark.skipif(config["desktopVersion"] <= "2022.1", reason="Skipped on versions earlier than 2021.2")
    def test_12_radio_getters(self, add_app):
        self.aedtapp = add_app(application=Emit)
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
        config["desktopVersion"] <= "2023.1",
        reason="Skipped on versions earlier than 2023.2",
    )
    def test_13_static_type_generation(self):
        domain = self.aedtapp.results.interaction_domain()
        py_version = f"EmitApiPython{sys.version_info[0]}{sys.version_info[1]}"
        assert str(type(domain)) == f"<class '{py_version}.InteractionDomain'>"

        # assert str(type(TxRxMode)) == "<class '{}.tx_rx_mode'>".format(py_version)
        assert str(type(TxRxMode.RX)) == f"<class '{py_version}.tx_rx_mode'>"
        assert str(type(TxRxMode.TX)) == f"<class '{py_version}.tx_rx_mode'>"
        assert str(type(TxRxMode.BOTH)) == f"<class '{py_version}.tx_rx_mode'>"
        # assert str(type(ResultType)) == "<class '{}.result_type'>".format(py_version)
        assert str(type(ResultType.SENSITIVITY)) == f"<class '{py_version}.result_type'>"
        assert str(type(ResultType.EMI)) == f"<class '{py_version}.result_type'>"
        assert str(type(ResultType.DESENSE)) == f"<class '{py_version}.result_type'>"
        assert str(type(ResultType.POWER_AT_RX)) == f"<class '{py_version}.result_type'>"

    @pytest.mark.skipif(config["desktopVersion"] <= "2023.1", reason="Skipped on versions earlier than 2023.2")
    def test_14_version(self, add_app):
        self.aedtapp = add_app(application=Emit)
        less_info = self.aedtapp.version(False)
        more_info = self.aedtapp.version(True)
        if less_info:
            assert str(type(less_info)) == "<class 'str'>"
            assert str(type(more_info)) == "<class 'str'>"
            assert len(more_info) > len(less_info)

    @pytest.mark.skipif(
        config["desktopVersion"] <= "2023.1" or config["desktopVersion"] > "2025.1",
        reason="Skipped on versions earlier than 2023.2 or later than 2025.1",
    )
    def test_15_basic_run(self, add_app):
        self.aedtapp = add_app(application=Emit, project_name=generate_unique_project_name())
        assert len(self.aedtapp.results.revisions) == 0
        # place components and generate the appropriate number of revisions
        rad1 = self.aedtapp.modeler.components.create_component("UE - Handheld")
        ant1 = self.aedtapp.modeler.components.create_component("Antenna")
        ant1.move_and_connect_to(rad1)
        bands = rad1.bands()
        for band in bands:
            band.enabled = True
        rad2 = self.aedtapp.modeler.components.create_component("Bluetooth Low Energy (LE)")
        ant2 = self.aedtapp.modeler.components.create_component("Antenna")
        ant2.move_and_connect_to(rad2)
        rad3 = self.aedtapp.modeler.components.create_component("Bluetooth Low Energy (LE)")
        ant3 = self.aedtapp.modeler.components.create_component("Antenna")
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
            interaction_unrun = rev.get_interaction(domain)
            assert interaction_unrun is not None
            assert not interaction_unrun.is_valid()
            interaction = engine.run(domain)
            assert interaction is not None
            assert interaction.is_valid()
            interaction2 = rev.run(domain)
            assert interaction2 is not None
            assert interaction2.is_valid()
            self.aedtapp.results.delete_revision(rev.name)
            assert not interaction.is_valid()
            assert not interaction2.is_valid()
            domain.set_receiver("dummy")
            assert rev.name not in self.aedtapp.results.revision_names()
            assert not engine.is_domain_valid(domain)
            assert not rev.is_domain_valid(domain)
            rad4 = self.aedtapp.modeler.components.create_component("MD400C")
            ant4 = self.aedtapp.modeler.components.create_component("Antenna")
            ant4.move_and_connect_to(rad4)
            self.aedtapp.oeditor.Delete([rad1.name, ant1.name])
            rev2 = self.aedtapp.results.analyze()
            domain2 = self.aedtapp.results.interaction_domain()
            domain2.set_receiver("MD400C")
            domain2.set_interferer(rad3.name)
            if config["desktopVersion"] >= "2024.1":
                rev2.n_to_1_limit = 0
            assert rev2.is_domain_valid(domain2)
            interaction3 = rev2.run(domain2)
            assert interaction3 is not None
            assert interaction3.is_valid()
            worst_domain = interaction3.get_worst_instance(ResultType.EMI).get_domain()
            assert worst_domain.receiver_name == rad4.name
            assert len(worst_domain.interferer_names) == 1
            assert worst_domain.interferer_names[0] == rad3.name
            domain2.set_receiver(rad3.name)
            domain2.set_interferer(rad2.name)
            assert rev2.is_domain_valid(domain2)
            interaction3 = rev2.run(domain2)
            assert interaction3 is not None
            assert interaction3.is_valid()
            worst_domain = interaction3.get_worst_instance(ResultType.EMI).get_domain()
            assert worst_domain.receiver_name == rad3.name
            assert len(worst_domain.interferer_names) == 1
            assert worst_domain.interferer_names[0] == rad2.name  # rad3 is the receiver in this domain

    @pytest.mark.skipif(
        config["desktopVersion"] < "2024.1",
        reason="Skipped on versions earlier than 2024.1",
    )
    def test_16_optimal_n_to_1_feature(self, add_app):
        self.aedtapp = add_app(application=Emit, project_name=generate_unique_project_name())
        # place components and generate the appropriate number of revisions
        rad1 = self.aedtapp.modeler.components.create_component("Bluetooth")
        ant1 = self.aedtapp.modeler.components.create_component("Antenna")
        ant1.move_and_connect_to(rad1)
        rad2 = self.aedtapp.modeler.components.create_component("MD401C")
        ant2 = self.aedtapp.modeler.components.create_component("Antenna")
        ant2.move_and_connect_to(rad2)
        rad3 = self.aedtapp.modeler.components.create_component("MD400C")
        ant3 = self.aedtapp.modeler.components.create_component("Antenna")
        ant3.move_and_connect_to(rad3)
        rad4 = self.aedtapp.modeler.components.create_component("LT401")
        ant4 = self.aedtapp.modeler.components.create_component("Antenna")
        ant4.move_and_connect_to(rad4)
        assert len(self.aedtapp.results.revisions) == 0
        rev = self.aedtapp.results.analyze()
        assert len(self.aedtapp.results.revisions) == 1
        radiosRX = rev.get_receiver_names()
        bandsRX = rev.get_band_names(radiosRX[0], TxRxMode.RX)
        radiosTX = rev.get_interferer_names()
        domain = self.aedtapp.results.interaction_domain()
        domain.set_receiver(radiosRX[0], bandsRX[0])

        # check n_to_1_limit can be set to different values
        self.aedtapp.results.revisions[-1].n_to_1_limit = 1
        assert self.aedtapp.results.revisions[-1].n_to_1_limit == 1
        self.aedtapp.results.revisions[-1].n_to_1_limit = 0
        assert self.aedtapp.results.revisions[-1].n_to_1_limit == 0

        # get number of 1-1 instances
        assert self.aedtapp.results.revisions[-1].get_instance_count(domain) == 52851
        interaction = self.aedtapp.results.revisions[-1].run(domain)
        instance = interaction.get_worst_instance(ResultType.EMI)
        assert instance.get_value(ResultType.EMI) == 76.02

        # rerun with N-1
        self.aedtapp.results.revisions[-1].n_to_1_limit = 2**20
        assert self.aedtapp.results.revisions[-1].n_to_1_limit == 2**20
        assert self.aedtapp.results.revisions[-1].get_instance_count(domain) == 11652816
        interaction = self.aedtapp.results.revisions[-1].run(domain)
        instance = interaction.get_worst_instance(ResultType.EMI)
        domain2 = instance.get_domain()
        assert len(domain2.interferer_names) == 2
        assert instance.get_value(ResultType.EMI) == 82.04
        # rerun with 1-1 only (forced by domain)
        domain.set_interferer(radiosTX[0])
        assert self.aedtapp.results.revisions[-1].get_instance_count(domain) == 19829
        interaction = self.aedtapp.results.revisions[-1].run(domain)
        instance = interaction.get_worst_instance(ResultType.EMI)
        assert instance.get_value(ResultType.EMI) == 76.02

    @pytest.mark.skipif(
        config["desktopVersion"] <= "2023.1" or config["desktopVersion"] > "2025.1",
        reason="Skipped on versions earlier than 2023.2 or later than 2025.1",
    )
    def test_17_availability_1_to_1(self, add_app):
        self.aedtapp = add_app(application=Emit, project_name=generate_unique_project_name())
        # place components and generate the appropriate number of revisions
        rad1 = self.aedtapp.modeler.components.create_component("MD400C")
        ant1 = self.aedtapp.modeler.components.create_component("Antenna")
        ant1.move_and_connect_to(rad1)
        rad2 = self.aedtapp.modeler.components.create_component("MD400C")
        ant2 = self.aedtapp.modeler.components.create_component("Antenna")
        ant2.move_and_connect_to(rad2)

        assert len(self.aedtapp.results.revisions) == 0
        rev = self.aedtapp.results.analyze()
        assert len(self.aedtapp.results.revisions) == 1

        rad3 = self.aedtapp.modeler.components.create_component("Mini UAS Video RT Airborne")
        ant3 = self.aedtapp.modeler.components.create_component("Antenna")
        ant3.move_and_connect_to(rad3)

        rad4 = self.aedtapp.modeler.components.create_component("GPS Airborne Receiver")
        ant4 = self.aedtapp.modeler.components.create_component("Antenna")
        ant4.move_and_connect_to(rad4)

        rev2 = self.aedtapp.results.analyze()
        assert len(self.aedtapp.results.revisions) == 2
        domain = self.aedtapp.results.interaction_domain()
        radiosRX = rev2.get_receiver_names()
        bandsRX = rev2.get_band_names(radiosRX[0], TxRxMode.RX)
        domain.set_receiver(radiosRX[0], bandsRX[0])
        radiosTX = rev2.get_interferer_names(InterfererType.TRANSMITTERS)
        bandsTX = rev2.get_band_names(radiosTX[0], TxRxMode.TX)
        domain.set_interferer(radiosTX[0], bandsTX[0])
        assert len(self.aedtapp.results.revisions) == 2
        radiosRX = rev2.get_receiver_names()
        bandsRX = rev2.get_band_names(radiosRX[0], TxRxMode.RX)
        domain.set_receiver(radiosRX[0], bandsRX[0])
        radiosTX = rev2.get_interferer_names(InterfererType.TRANSMITTERS)
        bandsTX = rev2.get_band_names(radiosTX[0], TxRxMode.TX)
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
        radiosTX = rev3.get_interferer_names(InterfererType.TRANSMITTERS)
        radiosRX = rev3.get_receiver_names()
        assert len(radiosTX) == 3
        assert len(radiosRX) == 4

        rev4 = self.aedtapp.results.get_revision(rev.name)
        assert len(self.aedtapp.results.revisions) == 2
        radiosTX = rev4.get_interferer_names(InterfererType.TRANSMITTERS)
        radiosRX = rev4.get_receiver_names()
        assert len(radiosTX) == 2
        assert len(radiosRX) == 2

    @pytest.mark.skipif(
        config["desktopVersion"] <= "2023.1",
        reason="Skipped on versions earlier than 2023.2",
    )
    @pytest.mark.skipif(
        TEST_REVIEW_FLAG,
        reason="Test under review",
    )
    def test_18_interference_scripts_no_filter(self, add_app):
        self.aedtapp = add_app(project_name="interference", application=Emit, subfolder=TEST_SUBFOLDER)

        # Generate a revision
        rev = self.aedtapp.results.analyze()

        # Test with no filtering
        expected_interference_colors = [["white", "green", "yellow"], ["red", "green", "white"]]
        expected_interference_power = [["N/A", 16.64, 56.0], [60.0, 16.64, "N/A"]]
        expected_protection_colors = [["white", "yellow", "yellow"], ["yellow", "yellow", "white"]]
        expected_protection_power = [["N/A", -20.0, -20.0], [-20.0, -20.0, "N/A"]]

        domain = self.aedtapp.results.interaction_domain()
        interference_colors = []
        interference_power_matrix = []
        protection_colors = []
        protection_power_matrix = []
        interference_colors, interference_power_matrix = rev.interference_type_classification(domain)
        protection_colors, protection_power_matrix = rev.protection_level_classification(
            domain, global_protection_level=True, global_levels=[30, -4, -30, -104]
        )

        assert interference_colors == expected_interference_colors
        assert interference_power_matrix == expected_interference_power
        assert protection_colors == expected_protection_colors
        assert protection_power_matrix == expected_protection_power

    @pytest.mark.skipif(
        TEST_REVIEW_FLAG,
        reason="Test under review in 2024.1",
    )
    def test_19_radio_protection_levels(self, add_app):
        self.aedtapp = add_app(project_name="interference", application=Emit, subfolder=TEST_SUBFOLDER)

        # Generate a revision
        rev = self.aedtapp.results.analyze()
        domain = self.aedtapp.results.interaction_domain()

        # Test protection level with radio-specific protection levels
        expected_protection_colors = [["white", "orange", "red"], ["yellow", "orange", "white"]]
        expected_protection_power = [["N/A", -20.0, -20.0], [-20.0, -20.0, "N/A"]]
        protection_levels = {
            "Global": [30.0, -4.0, -30.0, -104.0],
            "Bluetooth": [30.0, -4.0, -22.0, -104.0],
            "GPS": [30.0, -22.0, -30.0, -104.0],
            "WiFi": [-22.0, -25.0, -30.0, -104.0],
        }

        protection_colors = []
        protection_power_matrix = []
        protection_colors, protection_power_matrix = rev.protection_level_classification(
            domain, global_protection_level=False, protection_levels=protection_levels
        )

        assert protection_colors == expected_protection_colors
        assert protection_power_matrix == expected_protection_power

    @pytest.mark.skipif(
        config["desktopVersion"] <= "2023.1",
        reason="Skipped on versions earlier than 2023.2",
    )
    @pytest.mark.skipif(
        TEST_REVIEW_FLAG,
        reason="Test under review",
    )
    def test_20_interference_filtering(self, add_app):
        self.aedtapp = add_app(project_name="interference", application=Emit, subfolder=TEST_SUBFOLDER)
        # Generate a revision
        rev = self.aedtapp.results.analyze()

        # Test with active filtering
        domain = self.aedtapp.results.interaction_domain()
        interference_colors = []
        interference_power_matrix = []
        all_interference_colors = [
            [["white", "green", "yellow"], ["orange", "green", "white"]],
            [["white", "green", "yellow"], ["red", "green", "white"]],
            [["white", "green", "green"], ["red", "green", "white"]],
            [["white", "white", "yellow"], ["red", "white", "white"]],
        ]
        all_interference_power = [
            [["N/A", 16.64, 56.0], [-3.96, 16.64, "N/A"]],
            [["N/A", 16.64, 56.0], [60.0, 16.64, "N/A"]],
            [["N/A", 16.64, 2.45], [60.0, 16.64, "N/A"]],
            [["N/A", "<= -200", 56.0], [60.0, "<= -200", "N/A"]],
        ]
        interference_filters = [
            "TxFundamental:In-band",
            ["TxHarmonic/Spurious:In-band", "Intermod:In-band", "Broadband:In-band"],
            "TxFundamental:Out-of-band",
            ["TxHarmonic/Spurious:Out-of-band", "Intermod:Out-of-band", "Broadband:Out-of-band"],
        ]

        for ind in range(4):
            expected_interference_colors = all_interference_colors[ind]
            expected_interference_power = all_interference_power[ind]
            interference_filter = interference_filters[:ind] + interference_filters[ind + 1 :]

            interference_colors, interference_power_matrix = rev.interference_type_classification(
                domain, use_filter=True, filter_list=interference_filter
            )

            assert interference_colors == expected_interference_colors
            assert interference_power_matrix == expected_interference_power

    @pytest.mark.skipif(
        TEST_REVIEW_FLAG,
        reason="Test under review in 2024.1",
    )
    def test_21_protection_filtering(self, add_app):
        self.aedtapp = add_app(project_name="interference", application=Emit, subfolder=TEST_SUBFOLDER)

        # Generate a revision
        rev = self.aedtapp.results.analyze()

        # Test with active filtering
        domain = self.aedtapp.results.interaction_domain()
        protection_colors = []
        protection_power_matrix = []
        all_protection_colors = [
            [["white", "yellow", "yellow"], ["yellow", "yellow", "white"]],
            [["white", "yellow", "yellow"], ["yellow", "yellow", "white"]],
            [["white", "white", "white"], ["white", "white", "white"]],
            [["white", "yellow", "yellow"], ["yellow", "yellow", "white"]],
        ]
        all_protection_power = [
            [["N/A", -20.0, -20.0], [-20.0, -20.0, "N/A"]],
            [["N/A", -20.0, -20.0], [-20.0, -20.0, "N/A"]],
            [["N/A", "< -200", "< -200"], ["< -200", "< -200", "N/A"]],
            [["N/A", -20.0, -20.0], [-20.0, -20.0, "N/A"]],
        ]
        protection_filters = ["damage", "overload", "intermodulation", "desensitization"]

        for ind in range(4):
            expected_protection_colors = all_protection_colors[ind]
            expected_protection_power = all_protection_power[ind]
            protection_filter = protection_filters[:ind] + protection_filters[ind + 1 :]

            protection_colors, protection_power_matrix = rev.protection_level_classification(
                domain,
                global_protection_level=True,
                global_levels=[30, -4, -30, -104],
                use_filter=True,
                filter_list=protection_filter,
            )

            assert protection_colors == expected_protection_colors
            assert protection_power_matrix == expected_protection_power

    """
    .. note::
    The following test should be maintained as the last test within this file to ensure
    that the AEDT app functions as intended.

    """

    @pytest.mark.skipif(config["desktopVersion"] <= "2022.1", reason="Skipped on versions earlier than 2021.2")
    @pytest.mark.skipif(config["desktopVersion"] <= "2026.1", reason="Not stable test")
    def test_22_couplings(self, add_app):
        self.aedtapp = add_app(project_name="Cell Phone RFI Desense", application=Emit, subfolder=TEST_SUBFOLDER)

        links = self.aedtapp.couplings.linkable_design_names
        assert len(links) == 0
        for link in self.aedtapp.couplings.coupling_names:
            assert link == "ATA_Analysis"
            self.aedtapp.couplings.update_link(link)

        # test deleting a link
        self.aedtapp.couplings.delete_link("ATA_Analysis")
        links = self.aedtapp.couplings.linkable_design_names
        assert len(links) == 1

        # test adding a link
        self.aedtapp.couplings.add_link("ATA_Analysis")
        links = self.aedtapp.couplings.linkable_design_names
        assert len(links) == 0
        for link in self.aedtapp.couplings.coupling_names:
            assert link == "ATA_Analysis"

        self.aedtapp.close_project()

        self.aedtapp = add_app(project_name="Tutorial 4 - Completed", application=Emit, subfolder=TEST_SUBFOLDER)

        # test CAD nodes
        cad_nodes = self.aedtapp.couplings.cad_nodes
        assert len(cad_nodes) == 1
        for key in cad_nodes.keys():
            assert cad_nodes[key]["Name"] == "Fighter_Jet"

        # test antenna nodes
        antenna_nodes = self.aedtapp.couplings.antenna_nodes
        assert len(antenna_nodes) == 4
        antenna_names = ["GPS", "UHF-1", "UHF-2", "VHF-UHF"]
        i = 0
        for key in antenna_nodes.keys():
            assert antenna_nodes[key].name == antenna_names[i]
            i += 1

    @pytest.mark.skipif(
        config["desktopVersion"] < "2024.1" or config["desktopVersion"] > "2025.1",
        reason="Skipped on versions earlier than 2024.1 or later than 2025.1",
    )
    def test_23_result_categories(self, add_app):
        # set up project and run
        self.aedtapp = add_app(application=Emit, project_name=generate_unique_project_name())
        rad1 = self.aedtapp.modeler.components.create_component("GPS Receiver")
        ant1 = self.aedtapp.modeler.components.create_component("Antenna")
        ant1.move_and_connect_to(rad1)
        for band in rad1.bands():
            band.enabled = True
        rad2 = self.aedtapp.modeler.components.create_component("Bluetooth Low Energy (LE)")
        ant2 = self.aedtapp.modeler.components.create_component("Antenna")
        ant2.move_and_connect_to(rad2)
        rev = self.aedtapp.results.analyze()
        domain = self.aedtapp.results.interaction_domain()
        interaction = rev.run(domain)

        # initially all categories are enabled
        for category in EmiCategoryFilter.members():
            assert rev.get_emi_category_filter_enabled(category)

        # confirm the emi value when all categories are enabled
        instance = interaction.get_worst_instance(ResultType.EMI)
        assert instance.get_value(ResultType.EMI) == 16.64
        assert instance.get_largest_emi_problem_type() == "In-Channel: Broadband"

        # disable one category and confirm the emi value changes
        rev.set_emi_category_filter_enabled(EmiCategoryFilter.IN_CHANNEL_TX_BROADBAND, False)
        instance = interaction.get_worst_instance(ResultType.EMI)
        assert instance.get_value(ResultType.EMI) == 2.0
        assert instance.get_largest_emi_problem_type() == "Out-of-Channel: Tx Fundamental"

        # disable another category and confirm the emi value changes
        rev.set_emi_category_filter_enabled(EmiCategoryFilter.OUT_OF_CHANNEL_TX_FUNDAMENTAL, False)
        instance = interaction.get_worst_instance(ResultType.EMI)
        assert instance.get_value(ResultType.EMI) == -58.0
        assert instance.get_largest_emi_problem_type() == "Out-of-Channel: Tx Harmonic/Spurious"

        # disable last existing category and confirm expected exceptions and error messages
        rev.set_emi_category_filter_enabled(EmiCategoryFilter.OUT_OF_CHANNEL_TX_HARMONIC_SPURIOUS, False)
        instance = interaction.get_worst_instance(ResultType.EMI)
        with pytest.raises(RuntimeError) as e:
            instance.get_value(ResultType.EMI)
            assert "Unable to evaluate value: No power received." in str(e)
        with pytest.raises(RuntimeError) as e:
            instance.get_largest_emi_problem_type()
            assert "An EMI value is not available so the largest EMI problem type is undefined." in str(e)

    @pytest.mark.skipif(config["desktopVersion"] < "2024.2", reason="Skipped on versions earlier than 2024 R2.")
    @pytest.mark.skipif(config["desktopVersion"] <= "2026.1", reason="Not stable test")
    def test_24_license_session(self, add_app):
        self.aedtapp = add_app(project_name="interference", application=Emit, subfolder=TEST_SUBFOLDER)

        # Generate a revision
        results = self.aedtapp.results
        revision = self.aedtapp.results.analyze()

        def do_run():
            domain = results.interaction_domain()
            rev = results.current_revision
            rev.run(domain)

        number_of_runs = 5

        # Do a run to ensure the license log exists
        do_run()

        # Find the license log for this process
        appdata_local_path = tempfile.gettempdir()
        pid = os.getpid()
        dot_ansys_directory = os.path.join(appdata_local_path, ".ansys")

        license_file_path = ""
        with os.scandir(dot_ansys_directory) as directory:
            for file in directory:
                filename_pieces = file.name.split(".")
                # Since machine names can contain periods, there may be over five splits here
                # We only care about the first split and last three splits
                if len(filename_pieces) >= 5:
                    if (
                        filename_pieces[0] == "ansyscl"
                        and filename_pieces[-3] == str(pid)
                        and filename_pieces[-2].isnumeric()
                        and filename_pieces[-1] == "log"
                    ):
                        license_file_path = os.path.join(dot_ansys_directory, file.name)
                        break

        assert license_file_path != ""

        def count_license_actions(license_file_path):
            # Count checkout/checkins in most recent license connection
            checkouts = 0
            checkins = 0
            with open(license_file_path, "r") as license_file:
                lines = license_file.read().strip().split("\n")
                for line in lines:
                    if "NEW_CONNECTION" in line:
                        checkouts = 0
                        checkins = 0
                    elif "CHECKOUT" in line or "SPLIT_CHECKOUT" in line:
                        checkouts += 1
                    elif "CHECKIN" in line:
                        checkins += 1
            return (checkouts, checkins)

        # Figure out how many checkouts and checkins per run we expect
        # This could change depending on the user's EMIT HPC settings
        pre_first_run_checkouts, pre_first_run_checkins = count_license_actions(license_file_path)
        do_run()
        post_first_run_checkouts, post_first_run_checkins = count_license_actions(license_file_path)

        checkouts_per_run = post_first_run_checkouts - pre_first_run_checkouts
        checkins_per_run = post_first_run_checkins - pre_first_run_checkins

        start_checkouts, start_checkins = count_license_actions(license_file_path)

        # Run without license session
        for i in range(number_of_runs):
            do_run()

        # Run with license session
        with revision.get_license_session():
            for i in range(number_of_runs):
                do_run()

        end_checkouts, end_checkins = count_license_actions(license_file_path)

        checkouts = end_checkouts - start_checkouts
        checkins = end_checkins - start_checkins

        expected_checkouts = checkouts_per_run * (number_of_runs + 1)
        expected_checkins = checkins_per_run * (number_of_runs + 1)

        assert checkouts == expected_checkouts and checkins == expected_checkins

    @pytest.mark.skipif(config["desktopVersion"] < "2025.2", reason="Skipped on versions earlier than 2025 R2.")
    def test_25_emit_nodes(self, add_app):
        self.aedtapp = add_app(project_name="interference", application=Emit, subfolder=TEST_SUBFOLDER)

        # Generate and run a revision
        results = self.aedtapp.results
        revision = self.aedtapp.results.analyze()

        domain = results.interaction_domain()
        _ = revision.run(domain)

        nodes = revision.get_all_nodes()
        assert len(nodes) > 0

        # Test various properties of the Scene node
        scene_node = revision.get_scene_node()
        assert scene_node

        assert scene_node.valid
        assert scene_node.name

        assert scene_node.properties

        assert len(scene_node.allowed_child_types) > 0

        assert not scene_node._is_component

        assert scene_node == scene_node

    @pytest.mark.skipif(config["desktopVersion"] < "2025.2", reason="Skipped on versions earlier than 2025 R2.")
    def test_26_all_generated_emit_node_properties(self, add_app):
        # Define enum for result types
        class Result(Enum):
            SKIPPED = 0
            VALUE = 1
            EXCEPTION = 2
            NEEDS_PARAMETERS = 3

        def get_value_for_parameter(arg_type, docstring):
            value = None

            if arg_type in (int, float):
                value = 0

                # If there's a min or max in the docstring, use it.
                if docstring:
                    if "Value should be between" in docstring:
                        range_part = docstring.split("Value should be between")[1]
                        min_val = float(range_part.split("and")[0].strip())
                        max_val = float(range_part.split("and")[1].split(".")[0].strip())
                        value = min_val
                    elif "Value should be less than" in docstring:
                        max_val = float(docstring.split("Value should be less than")[1].split(".")[0].strip())
                        value = max_val
                    elif "Value should be greater than" in docstring:
                        min_val = float(docstring.split("Value should be greater than")[1].split(".")[0].strip())
                        value = min_val
            elif isinstance(arg_type, str):
                value = "TestString"
            elif isinstance(arg_type, bool):
                value = True
            elif isinstance(arg_type, type) and issubclass(arg_type, Enum):
                # Type is an Enum
                first_enum_value = list(arg_type.__members__.values())[0]
                value = first_enum_value
            elif isinstance(arg_type, types.UnionType):
                # Type is a Union
                possible_arg_types = arg_type.__args__
                if int in possible_arg_types or float in possible_arg_types:
                    value = 0

            return value

        def test_all_members(node, results, results_of_get_props):
            # Dynamically get list of properties and methods
            members = dir(node)

            # Initialize property map
            property_value_map = {}
            for member in members:
                key = f"{type(node).__name__}.{member}"

                if member.startswith("_"):
                    continue

                if member.startswith("delete"):
                    continue

                if member.startswith("rename"):
                    continue

                class_attr = getattr(node.__class__, member)
                if isinstance(class_attr, property):
                    has_fget = class_attr.fget is not None
                    has_fset = class_attr.fset is not None

                    if has_fget and has_fset:
                        arg_type = str
                        annotations = class_attr.fset.__annotations__
                        if "value" in annotations:
                            arg_type = annotations["value"]

                        value_index = 0
                        value_count = 1
                        if isinstance(arg_type, bool):
                            value_count = 2
                        elif isinstance(arg_type, type) and issubclass(arg_type, Enum):
                            value_count = len(list(arg_type.__members__.values()))

                        value = {
                            "value_index": value_index,
                            "value_count": value_count,
                            "arg_type": arg_type,
                        }

                        property_value_map[key] = value

            anything_was_set = True
            while anything_was_set:
                anything_was_set = False
                for member in members:
                    key = f"{type(node).__name__}.{member}"

                    try:
                        if member.startswith("_"):
                            results[key] = (Result.SKIPPED, "Skipping private member")
                            continue

                        if member.startswith("delete"):
                            results[key] = (Result.SKIPPED, "Skipping delete method")
                            continue

                        if member.startswith("rename"):
                            results[key] = (Result.SKIPPED, "Skipping rename method")
                            continue

                        class_attr = getattr(node.__class__, member)
                        if isinstance(class_attr, property):
                            # Member is a property

                            has_fget = class_attr.fget is not None
                            has_fset = class_attr.fset is not None

                            if has_fget and has_fset:
                                property_value_map_record = property_value_map[key]

                                arg_type = property_value_map_record["arg_type"]
                                docstring = class_attr.fget.__doc__

                                value = None
                                value_index = property_value_map_record["value_index"]
                                value_count = property_value_map_record["value_count"]
                                if isinstance(arg_type, bool):
                                    if value_index == 0:
                                        value = False
                                    elif value_index == 1:
                                        value = True
                                    else:
                                        # We've already used both bool values, skip.
                                        continue
                                elif isinstance(arg_type, type) and issubclass(arg_type, Enum):
                                    if value_index < value_count:
                                        value = list(arg_type.__members__.values())[
                                            property_value_map_record["value_index"]
                                        ]
                                    else:
                                        # We've already used all enum values, skip.
                                        continue
                                else:
                                    if value_index == 0:
                                        value = get_value_for_parameter(arg_type, docstring)
                                    else:
                                        # We've already used a value, skip.
                                        continue

                                exception = None

                                # If value is None here, we failed to find a suitable value to call the setter with.
                                # Just call the getter, and put that in the results.
                                try:
                                    if value is not None:
                                        class_attr.fset(node, value)
                                except Exception as e:
                                    exception = e

                                try:
                                    result = class_attr.fget(node)
                                except Exception as e:
                                    exception = e

                                if exception:
                                    raise exception

                                if value:
                                    assert value == result

                                # We successfully set the current value. Next iteration, try the next value
                                property_value_map_record["value_index"] += 1
                                anything_was_set = True

                                results[key] = (Result.VALUE, result)
                                results_of_get_props[class_attr] = result
                            elif has_fget:
                                result = class_attr.fget(node)
                                results[key] = (Result.VALUE, result)
                                results_of_get_props[class_attr] = result
                        else:
                            attr = getattr(node, member)

                            if inspect.ismethod(attr) or inspect.isfunction(attr):
                                # Member is a function
                                signature = inspect.signature(attr)

                                values = []
                                bad_param = None
                                for parameter in signature.parameters:
                                    arg_type = type(parameter)
                                    docstring = attr.__doc__

                                    value = get_value_for_parameter(arg_type, docstring)
                                    if value is not None:
                                        values.append(value)
                                    else:
                                        bad_param = parameter
                                        break

                                if len(values) == len(signature.parameters):
                                    result = attr(*values)
                                    results[key] = (Result.VALUE, result)
                                else:
                                    results[key] = (
                                        Result.NEEDS_PARAMETERS,
                                        f'Could not find valid value for parameter "{bad_param}".',
                                    )
                            else:
                                results[key] = (Result.VALUE, attr)
                    except Exception as e:
                        results[key] = (Result.EXCEPTION, f"{e}")

        def test_nodes_from_top_level(nodes, nodes_tested, results, results_of_get_props, add_untested_children=True):
            # Test every method on every node, but add node children to list while iterating
            child_node_add_exceptions = {}
            for node in nodes:
                node_type = type(node).__name__
                if node_type not in nodes_tested:
                    nodes_tested.append(node_type)

                    if add_untested_children:
                        exception = None

                        # Add any untested child nodes
                        try:
                            for child_type in node.allowed_child_types:
                                # Skip any nodes that end in ..., as they open a dialog
                                if child_type not in nodes_tested and not child_type.endswith("..."):
                                    try:
                                        node._add_child_node(child_type)
                                    except Exception as e:
                                        exception = e
                        except Exception as e:
                            exception = e

                        # Add this node's children to the list of nodes to test
                        try:
                            nodes.extend(node.children)
                        except Exception as e:
                            exception = e

                        if exception:
                            child_node_add_exceptions[node_type] = exception

                    test_all_members(node, results, results_of_get_props)

        self.aedtapp = add_app(project_name="interference", application=Emit, subfolder=TEST_SUBFOLDER)

        # Add some components
        self.aedtapp.modeler.components.create_component("Antenna", "TestAntenna")
        self.aedtapp.modeler.components.create_component("New Emitter", "TestEmitter")
        self.aedtapp.modeler.components.create_component("Amplifier", "TestAmplifier")
        self.aedtapp.modeler.components.create_component("Cable", "TestCable")
        self.aedtapp.modeler.components.create_component("Circulator", "TestCirculator")
        self.aedtapp.modeler.components.create_component("Divider", "TestDivider")
        self.aedtapp.modeler.components.create_component("Band Pass", "TestBPF")
        self.aedtapp.modeler.components.create_component("Band Stop", "TestBSF")
        self.aedtapp.modeler.components.create_component("File-based", "TestFilterByFile")
        self.aedtapp.modeler.components.create_component("High Pass", "TestHPF")
        self.aedtapp.modeler.components.create_component("Low Pass", "TestLPF")
        self.aedtapp.modeler.components.create_component("Tunable Band Pass", "TestTBPF")
        self.aedtapp.modeler.components.create_component("Tunable Band Stop", "TestTBSF")
        self.aedtapp.modeler.components.create_component("Isolator", "TestIsolator")
        self.aedtapp.modeler.components.create_component("TR Switch", "TestSwitch")
        self.aedtapp.modeler.components.create_component("Terminator", "TestTerminator")
        self.aedtapp.modeler.components.create_component("3 Port", "Test3port")

        # Generate and run a revision
        results = self.aedtapp.results
        revision = self.aedtapp.results.analyze()

        domain = results.interaction_domain()
        revision.run(domain)

        results_dict = {}
        results_of_get_props = {}
        nodes_tested = []

        # Test all nodes of the current revision
        current_revision_all_nodes = revision.get_all_nodes()

        test_nodes_from_top_level(current_revision_all_nodes, nodes_tested, results_dict, results_of_get_props)

        # Keep the current revision, then test all nodes of the kept result
        # kept_result_name = self.aedtapp.odesign.KeepResult()
        # self.aedtapp.odesign.SaveEmitProject()
        # kept_revision = results.get_revision(kept_result_name)

        # readonly_results_dict = {} readonly_results_of_get_props = {} test_nodes_from_top_level(
        # kept_revision.get_all_nodes(), nodes_tested, readonly_results_dict, readonly_results_of_get_props,
        # add_untested_children=False, )

        # Categorize results from all node member calls
        results_by_type = {Result.SKIPPED: {}, Result.VALUE: {}, Result.EXCEPTION: {}, Result.NEEDS_PARAMETERS: {}}

        for key, value in results_dict.items():
            results_by_type[value[0]][key] = value[1]

        # Verify we tested most of the generated nodes
        all_nodes = [node for node in generated.__all__ if ("ReadOnly" not in node)]
        nodes_untested = [node for node in all_nodes if (node not in nodes_tested)]

        assert len(nodes_tested) > len(nodes_untested)

    @pytest.mark.skipif(config["desktopVersion"] < "2025.1", reason="Skipped on versions earlier than 2024 R2.")
    @pytest.mark.skipif(config["desktopVersion"] <= "2026.1", reason="Not stable test")
    def test_27_components_catalog(self, add_app):
        self.aedtapp = add_app(project_name="catalog-list", application=Emit)
        comp_list = self.aedtapp.modeler.components.components_catalog["LTE"]
        assert len(comp_list) == 14
        assert comp_list[12].name == "LTE BTS"
        assert comp_list[13].name == "LTE Mobile Station"
